# -*- encoding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import logging
import operator
import re
import secrets
from io import BytesIO
from unittest.mock import patch

import requests

import orj
from orj.modules.registry import Registry
from orj.tests.common import BaseCase, HttpCase, tagged
from orj.tools import config


class TestDatabaseManager(HttpCase):
    def test_database_manager(self):
        if not config['list_db']:
            return
        res = self.url_open('/web/database/manager')
        self.assertEqual(res.status_code, 200)

        # check that basic existing db actions are present
        self.assertIn('.o_database_backup', res.text)
        self.assertIn('.o_database_duplicate', res.text)
        self.assertIn('.o_database_delete', res.text)

        # check that basic db actions are present
        self.assertIn('.o_database_create', res.text)
        self.assertIn('.o_database_restore', res.text)


@tagged('-at_install', 'post_install', '-standard', 'database_operations')
class TestDatabaseOperations(BaseCase):
    def setUp(self):
        self.password = secrets.token_hex()

        # monkey-patch password verification
        self.verify_admin_password_patcher = patch(
            'orj.tools.config.verify_admin_password', self.password.__eq__,
        )
        self.startPatcher(self.verify_admin_password_patcher)

        self.db_name = config['db_name']
        self.assertTrue(self.db_name)

        # monkey-patch db-filter
        self.addCleanup(operator.setitem, config, 'dbfilter', config['dbfilter'])
        config['dbfilter'] = self.db_name + '.*'

        self.base_databases = self.list_dbs_filtered()
        self.session = requests.Session()
        self.session.get(self.url('/web/database/manager'))

    def tearDown(self):
        self.assertEqual(
            self.list_dbs_filtered(),
            self.base_databases,
            'No database should have been created or removed at the end of this test',
        )

    def list_dbs_filtered(self):
        return set(db for db in orj.service.db.list_dbs(True) if re.match(config['dbfilter'], db))

    def url(self, path):
        return HttpCase.base_url() + path

    def assertDbs(self, dbs):
        self.assertEqual(self.list_dbs_filtered() - self.base_databases, set(dbs))

    def url_open_drop(self, dbname):
        res = self.session.post(self.url('/web/database/drop'), data={
            'master_pwd': self.password,
            'name': dbname,
        }, allow_redirects=False)
        res.raise_for_status()
        return res

    def test_database_creation(self):
        # check verify_admin_password patch
        self.assertTrue(orj.tools.config.verify_admin_password(self.password))

        # create a database
        test_db_name = self.db_name + '-test-database-creation'
        self.assertNotIn(test_db_name, self.list_dbs_filtered())
        res = self.session.post(self.url('/web/database/create'), data={
            'master_pwd': self.password,
            'name': test_db_name,
            'login': 'admin',
            'password': 'admin',
            'lang': 'en_US',
            'phone': '',
        }, allow_redirects=False)
        self.assertEqual(res.status_code, 303)
        self.assertIn('/orj', res.headers['Location'])
        self.assertDbs([test_db_name])

        # delete the created database
        res = self.url_open_drop(test_db_name)
        self.assertEqual(res.status_code, 303)
        self.assertIn('/web/database/manager', res.headers['Location'])
        self.assertDbs([])

    def test_database_duplicate(self):
        # duplicate this database
        test_db_name = self.db_name + '-test-database-duplicate'
        self.assertNotIn(test_db_name, self.list_dbs_filtered())
        res = self.session.post(self.url('/web/database/duplicate'), data={
            'master_pwd': self.password,
            'name': self.db_name,
            'new_name': test_db_name,
        }, allow_redirects=False)
        self.assertEqual(res.status_code, 303)
        self.assertIn('/web/database/manager', res.headers['Location'])
        self.assertDbs([test_db_name])

        # delete the created database
        res = self.url_open_drop(test_db_name)
        self.assertIn('/web/database/manager', res.headers['Location'])
        self.assertDbs([])

    def test_database_restore(self):
        test_db_name = self.db_name + '-test-database-restore'
        self.assertNotIn(test_db_name, self.list_dbs_filtered())

        # backup the current database inside a temporary zip file
        res = self.session.post(
            self.url('/web/database/backup'),
            data={
                'master_pwd': self.password,
                'name': self.db_name,
            },
            allow_redirects=False,
            stream=True,
        )
        res.raise_for_status()
        datetime_pattern = r'\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d'
        self.assertRegex(
            res.headers.get('Content-Disposition'),
            fr"attachment; filename\*=UTF-8''{self.db_name}_{datetime_pattern}\.zip"
        )
        backup_file = BytesIO()
        backup_file.write(res.content)
        self.assertGreater(backup_file.tell(), 0, "The backup seems corrupted")

        # upload the backup under a new name (create a duplicate)
        with self.subTest(DEFAULT_MAX_CONTENT_LENGTH=None), \
             patch.object(orj.http, 'DEFAULT_MAX_CONTENT_LENGTH', None):
            backup_file.seek(0)
            self.session.post(
                self.url('/web/database/restore'),
                data={
                    'master_pwd': self.password,
                    'name': test_db_name,
                    'copy': True,
                },
                files={
                    'backup_file': backup_file,
                },
                allow_redirects=False
            ).raise_for_status()
            self.assertDbs([test_db_name])
            self.url_open_drop(test_db_name)

        # upload the backup again, this time simulating that the file is
        # too large under the default size limit, the default size limit
        # shouldn't apply to /web/database URLs
        with self.subTest(DEFAULT_MAX_CONTENT_LENGTH=1024), \
             patch.object(orj.http, 'DEFAULT_MAX_CONTENT_LENGTH', 1024):
            backup_file.seek(0)
            self.session.post(
                self.url('/web/database/restore'),
                data={
                    'master_pwd': self.password,
                    'name': test_db_name,
                    'copy': True,
                },
                files={
                    'backup_file': backup_file,
                },
                allow_redirects=False
            ).raise_for_status()
        self.assertDbs([test_db_name])
        self.url_open_drop(test_db_name)


    def test_database_http_registries(self):
        # This test is about dropping a connection inside one worker and
        # make sure that the other workers behave correctly.

        #
        # Setup
        #

        # duplicate this database
        test_db_name = self.db_name + '-test-database-duplicate'
        res = self.session.post(self.url('/web/database/duplicate'), data={
            'master_pwd': self.password,
            'name': self.db_name,
            'new_name': test_db_name,
        }, allow_redirects=False)

        # get a registry and a cursor on that new database
        registry = Registry(test_db_name)
        cr = registry.cursor()
        self.assertIn(test_db_name, Registry.registries)

        # delete the created database but keep the cursor
        with patch('orj.sql_db.close_db') as close_db:
            res = self.url_open_drop(test_db_name)
        close_db.assert_called_once_with(test_db_name)

        # simulate that some customers were connected to that dropped db
        session_store = orj.http.root.session_store
        session = session_store.new()
        session.update(orj.http.get_default_session(), db=test_db_name)
        session.context['lang'] = orj.http.DEFAULT_LANG
        self.session.cookies['session_id'] = session.sid

        # make it possible to inject the registry back
        patcher = patch.dict(Registry.registries.d, {test_db_name: registry})
        registries = patcher.start()
        self.addCleanup(patcher.stop)

        #
        # Tests
        #

        # The other worker doesn't have a registry in its LRU cache for
        # that session database.
        with self.subTest(msg="Registry.init() fails"):
            session_store.save(session)
            registries.pop('test_db_name', None)
            with self.assertLogs('orj.sql_db', logging.INFO) as capture:
                res = self.session.get(self.url('/web/health'))
            self.assertEqual(res.status_code, 200)
            self.assertEqual(session_store.get(session.sid)['db'], None)
            self.assertEqual(capture.output, [
                "INFO:orj.sql_db:Connection to the database failed",
            ])


        # The other worker has a registry in its LRU cache for that
        # session database. But it doesn't have a connection to the sql
        # database.
        with self.subTest(msg="Registry.cursor() fails"):
            session_store.save(session)
            registries[test_db_name] = registry
            with self.assertLogs('orj.sql_db', logging.INFO) as capture, \
                 patch.object(Registry, '__new__', return_value=registry):
                res = self.session.get(self.url('/web/health'))
            self.assertEqual(res.status_code, 200)
            self.assertEqual(session_store.get(session.sid)['db'], None)
            self.assertEqual(capture.output, [
                "INFO:orj.sql_db:Connection to the database failed",
            ])

        # The other worker has a registry in its LRU cache for that
        # session database. It also has a (now broken) connection to the
        # sql database.
        with self.subTest(msg="Registry.check_signaling() fails"):
            session_store.save(session)
            registries[test_db_name] = registry
            with self.assertLogs('orj.sql_db', logging.ERROR) as capture, \
                 patch.object(Registry, '__new__', return_value=registry), \
                 patch.object(Registry, 'cursor', return_value=cr):
                res = self.session.get(self.url('/web/health'))
            self.assertEqual(res.status_code, 200)
            self.assertEqual(session_store.get(session.sid)['db'], None)
            self.maxDiff = None
            self.assertRegex(capture.output[0], (
                r"^ERROR:orj\.sql_db:bad query:(?s:.*?)"
                r"ERROR: terminating connection due to administrator command\s+"
                r"server closed the connection unexpectedly\s+"
                r"This probably means the server terminated abnormally\s+"
                r"before or while processing the request\.$"
            ))
