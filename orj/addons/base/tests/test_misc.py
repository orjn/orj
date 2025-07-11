# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import base64
import datetime
from dateutil.relativedelta import relativedelta
import os.path
import pytz

from orj.tools import (
    config,
    date_utils,
    file_open,
    file_path,
    merge_sequences,
    misc,
    remove_accents,
)
from orj.tools.mail import validate_url
from orj.tests.common import TransactionCase, BaseCase


class TestMergeSequences(BaseCase):
    def test_merge_sequences(self):
        # base case
        seq = merge_sequences(['A', 'B', 'C'])
        self.assertEqual(seq, ['A', 'B', 'C'])

        # 'Z' can be anywhere
        seq = merge_sequences(['A', 'B', 'C'], ['Z'])
        self.assertEqual(seq, ['A', 'B', 'C', 'Z'])

        # 'Y' must precede 'C';
        seq = merge_sequences(['A', 'B', 'C'], ['Y', 'C'])
        self.assertEqual(seq, ['A', 'B', 'Y', 'C'])

        # 'X' must follow 'A' and precede 'C'
        seq = merge_sequences(['A', 'B', 'C'], ['A', 'X', 'C'])
        self.assertEqual(seq, ['A', 'B', 'X', 'C'])

        # all cases combined
        seq = merge_sequences(
            ['A', 'B', 'C'],
            ['Z'],                  # 'Z' can be anywhere
            ['Y', 'C'],             # 'Y' must precede 'C';
            ['A', 'X', 'Y'],        # 'X' must follow 'A' and precede 'Y'
        )
        self.assertEqual(seq, ['A', 'B', 'X', 'Y', 'C', 'Z'])


class TestDateRangeFunction(BaseCase):
    """ Test on date_range generator. """

    def test_date_range_with_naive_datetimes(self):
        """ Check date_range with naive datetimes. """
        start = datetime.datetime(1985, 1, 1)
        end = datetime.datetime(1986, 1, 1)

        expected = [
            datetime.datetime(1985, 1, 1, 0, 0),
            datetime.datetime(1985, 2, 1, 0, 0),
            datetime.datetime(1985, 3, 1, 0, 0),
            datetime.datetime(1985, 4, 1, 0, 0),
            datetime.datetime(1985, 5, 1, 0, 0),
            datetime.datetime(1985, 6, 1, 0, 0),
            datetime.datetime(1985, 7, 1, 0, 0),
            datetime.datetime(1985, 8, 1, 0, 0),
            datetime.datetime(1985, 9, 1, 0, 0),
            datetime.datetime(1985, 10, 1, 0, 0),
            datetime.datetime(1985, 11, 1, 0, 0),
            datetime.datetime(1985, 12, 1, 0, 0),
            datetime.datetime(1986, 1, 1, 0, 0)
        ]

        dates = [date for date in date_utils.date_range(start, end)]

        self.assertEqual(dates, expected)

    def test_date_range_with_date(self):
        """ Check date_range with naive datetimes. """
        start = datetime.date(1985, 1, 1)
        end = datetime.date(1986, 1, 1)

        expected = [
            datetime.date(1985, 1, 1),
            datetime.date(1985, 2, 1),
            datetime.date(1985, 3, 1),
            datetime.date(1985, 4, 1),
            datetime.date(1985, 5, 1),
            datetime.date(1985, 6, 1),
            datetime.date(1985, 7, 1),
            datetime.date(1985, 8, 1),
            datetime.date(1985, 9, 1),
            datetime.date(1985, 10, 1),
            datetime.date(1985, 11, 1),
            datetime.date(1985, 12, 1),
            datetime.date(1986, 1, 1),
        ]

        self.assertEqual(list(date_utils.date_range(start, end)), expected)

    def test_date_range_with_timezone_aware_datetimes_other_than_utc(self):
        """ Check date_range with timezone-aware datetimes other than UTC."""
        timezone = pytz.timezone('Europe/Brussels')

        start = datetime.datetime(1985, 1, 1)
        end = datetime.datetime(1986, 1, 1)
        start = timezone.localize(start)
        end = timezone.localize(end)

        expected = [datetime.datetime(1985, 1, 1, 0, 0),
                    datetime.datetime(1985, 2, 1, 0, 0),
                    datetime.datetime(1985, 3, 1, 0, 0),
                    datetime.datetime(1985, 4, 1, 0, 0),
                    datetime.datetime(1985, 5, 1, 0, 0),
                    datetime.datetime(1985, 6, 1, 0, 0),
                    datetime.datetime(1985, 7, 1, 0, 0),
                    datetime.datetime(1985, 8, 1, 0, 0),
                    datetime.datetime(1985, 9, 1, 0, 0),
                    datetime.datetime(1985, 10, 1, 0, 0),
                    datetime.datetime(1985, 11, 1, 0, 0),
                    datetime.datetime(1985, 12, 1, 0, 0),
                    datetime.datetime(1986, 1, 1, 0, 0)]

        expected = [timezone.localize(e) for e in expected]

        dates = [date for date in date_utils.date_range(start, end)]

        self.assertEqual(expected, dates)

    def test_date_range_with_mismatching_zones(self):
        """ Check date_range with mismatching zone should raise an exception."""
        start_timezone = pytz.timezone('Europe/Brussels')
        end_timezone = pytz.timezone('America/Recife')

        start = datetime.datetime(1985, 1, 1)
        end = datetime.datetime(1986, 1, 1)
        start = start_timezone.localize(start)
        end = end_timezone.localize(end)

        with self.assertRaises(ValueError):
            dates = [date for date in date_utils.date_range(start, end)]

    def test_date_range_with_inconsistent_datetimes(self):
        """ Check date_range with a timezone-aware datetime and a naive one."""
        context_timezone = pytz.timezone('Europe/Brussels')

        start = datetime.datetime(1985, 1, 1)
        end = datetime.datetime(1986, 1, 1)
        end = context_timezone.localize(end)

        with self.assertRaises(ValueError):
            dates = [date for date in date_utils.date_range(start, end)]

    def test_date_range_with_hour(self):
        """ Test date range with hour and naive datetime."""
        start = datetime.datetime(2018, 3, 25)
        end = datetime.datetime(2018, 3, 26)
        step = relativedelta(hours=1)

        expected = [
            datetime.datetime(2018, 3, 25, 0, 0),
            datetime.datetime(2018, 3, 25, 1, 0),
            datetime.datetime(2018, 3, 25, 2, 0),
            datetime.datetime(2018, 3, 25, 3, 0),
            datetime.datetime(2018, 3, 25, 4, 0),
            datetime.datetime(2018, 3, 25, 5, 0),
            datetime.datetime(2018, 3, 25, 6, 0),
            datetime.datetime(2018, 3, 25, 7, 0),
            datetime.datetime(2018, 3, 25, 8, 0),
            datetime.datetime(2018, 3, 25, 9, 0),
            datetime.datetime(2018, 3, 25, 10, 0),
            datetime.datetime(2018, 3, 25, 11, 0),
            datetime.datetime(2018, 3, 25, 12, 0),
            datetime.datetime(2018, 3, 25, 13, 0),
            datetime.datetime(2018, 3, 25, 14, 0),
            datetime.datetime(2018, 3, 25, 15, 0),
            datetime.datetime(2018, 3, 25, 16, 0),
            datetime.datetime(2018, 3, 25, 17, 0),
            datetime.datetime(2018, 3, 25, 18, 0),
            datetime.datetime(2018, 3, 25, 19, 0),
            datetime.datetime(2018, 3, 25, 20, 0),
            datetime.datetime(2018, 3, 25, 21, 0),
            datetime.datetime(2018, 3, 25, 22, 0),
            datetime.datetime(2018, 3, 25, 23, 0),
            datetime.datetime(2018, 3, 26, 0, 0)
        ]

        dates = [date for date in date_utils.date_range(start, end, step)]

        self.assertEqual(dates, expected)


class TestFormatLangDate(TransactionCase):
    def test_00_accepted_types(self):
        self.env.user.tz = 'Europe/Brussels'
        datetime_str = '2017-01-31 12:00:00'
        date_datetime = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        date_date = date_datetime.date()
        date_str = '2017-01-31'
        time_part = datetime.time(16, 30, 22)
        t_medium = 'h:mm:ss a'
        medium = f'MMM d, YYYY, {t_medium}'

        self.assertEqual(misc.format_date(self.env, date_datetime), '01/31/2017')
        self.assertEqual(misc.format_date(self.env, date_date), '01/31/2017')
        self.assertEqual(misc.format_date(self.env, date_str), '01/31/2017')
        self.assertEqual(misc.format_date(self.env, ''), '')
        self.assertEqual(misc.format_date(self.env, False), '')
        self.assertEqual(misc.format_date(self.env, None), '')

        self.assertEqual(misc.format_datetime(self.env, date_datetime, dt_format=medium), 'Jan 31, 2017, 1:00:00 PM')
        self.assertEqual(misc.format_datetime(self.env, datetime_str, dt_format=medium), 'Jan 31, 2017, 1:00:00 PM')
        self.assertEqual(misc.format_datetime(self.env, '', dt_format=medium), '')
        self.assertEqual(misc.format_datetime(self.env, False, dt_format=medium), '')
        self.assertEqual(misc.format_datetime(self.env, None, dt_format=medium), '')

        self.assertEqual(misc.format_time(self.env, time_part, time_format=t_medium), '4:30:22 PM')
        self.assertEqual(misc.format_time(self.env, '', time_format=t_medium), '')
        self.assertEqual(misc.format_time(self.env, False, time_format=t_medium), '')
        self.assertEqual(misc.format_time(self.env, None, time_format=t_medium), '')

    def test_01_code_and_format(self):
        date_str = '2017-01-31'
        lang = self.env['res.lang']

        # Activate French and Simplified Chinese (test with non-ASCII characters)
        lang._activate_lang('fr_FR')
        lang._activate_lang('zh_CN')

        # -- test `date`
        # Change a single parameter
        self.assertEqual(misc.format_date(lang.with_context(lang='fr_FR').env, date_str), '31/01/2017')
        self.assertEqual(misc.format_date(lang.env, date_str, lang_code='fr_FR'), '31/01/2017')
        self.assertEqual(misc.format_date(lang.env, date_str, date_format='MMM d, y'), 'Jan 31, 2017')

        # Change 2 parameters
        self.assertEqual(misc.format_date(lang.with_context(lang='zh_CN').env, date_str, lang_code='fr_FR'), '31/01/2017')
        self.assertEqual(misc.format_date(lang.with_context(lang='zh_CN').env, date_str, date_format='MMM d, y'), u'1\u6708 31, 2017')
        self.assertEqual(misc.format_date(lang.env, date_str, lang_code='fr_FR', date_format='MMM d, y'), 'janv. 31, 2017')

        # Change 3 parameters
        self.assertEqual(misc.format_date(lang.with_context(lang='zh_CN').env, date_str, lang_code='en_US', date_format='MMM d, y'), 'Jan 31, 2017')

        # -- test `datetime`
        datetime_str = '2017-01-31 10:33:00'
        # Change languages and timezones
        datetime_us_str = misc.format_datetime(lang.with_context(lang='en_US').env, datetime_str, tz='Europe/Brussels')
        self.assertNotEqual(misc.format_datetime(lang.with_context(lang='fr_FR').env, datetime_str, tz='Europe/Brussels'), datetime_us_str)
        self.assertNotEqual(misc.format_datetime(lang.with_context(lang='zh_CN').env, datetime_str, tz='America/New_York'), datetime_us_str)

        # Change language, timezone and format
        self.assertEqual(misc.format_datetime(lang.with_context(lang='fr_FR').env, datetime_str, tz='America/New_York', dt_format='dd/MM/YYYY HH:mm'), '31/01/2017 05:33')
        self.assertEqual(misc.format_datetime(lang.with_context(lang='en_US').env, datetime_str, tz='Europe/Brussels', dt_format='MMM d, y'), 'Jan 31, 2017')

        # Check given `lang_code` overwites context lang
        fmt_fr = 'dd MMMM YYYY à HH:mm:ss Z'
        fmt_us = "MMMM dd, YYYY 'at' hh:mm:ss a Z"
        self.assertEqual(misc.format_datetime(lang.env, datetime_str, tz='Europe/Brussels', dt_format=fmt_fr, lang_code='fr_FR'), '31 janvier 2017 à 11:33:00 +0100')
        self.assertEqual(misc.format_datetime(lang.with_context(lang='zh_CN').env, datetime_str, tz='Europe/Brussels', dt_format=fmt_us, lang_code='en_US'), 'January 31, 2017 at 11:33:00 AM +0100')

        # -- test `time`
        time_part = datetime.time(16, 30, 22)
        time_part_tz = datetime.time(16, 30, 22, tzinfo=pytz.timezone('America/New_York'))  # 4:30 PM timezoned

        self.assertEqual(misc.format_time(lang.with_context(lang='fr_FR').env, time_part, time_format='HH:mm:ss'), '16:30:22')
        self.assertEqual(misc.format_time(lang.with_context(lang='zh_CN').env, time_part, time_format="ah:m:ss"), '\u4e0b\u53484:30:22')

        # Check format in different languages
        self.assertEqual(misc.format_time(lang.with_context(lang='fr_FR').env, time_part, time_format='HH:mm'), '16:30')
        self.assertEqual(misc.format_time(lang.with_context(lang='zh_CN').env, time_part, time_format='ah:mm'), '\u4e0b\u53484:30')

        # Check timezoned time part
        self.assertEqual(misc.format_time(lang.with_context(lang='fr_FR').env, time_part_tz, time_format='HH:mm:ss Z'), '16:30:22 -0504')
        self.assertEqual(misc.format_time(lang.with_context(lang='zh_CN').env, time_part_tz, time_format='zzzz ah:mm:ss'), '\u5317\u7f8e\u4e1c\u90e8\u6807\u51c6\u65f6\u95f4\u0020\u4e0b\u53484:30:22')

        #Check timezone conversion in format_time
        self.assertEqual(misc.format_time(lang.with_context(lang='fr_FR').env, datetime_str, 'Europe/Brussels', time_format='HH:mm:ss Z'), '11:33:00 +0100')
        self.assertEqual(misc.format_time(lang.with_context(lang='fr_FR').env, datetime_str, 'America/New_York', time_format='HH:mm:ss Z'), '05:33:00 -0500')

        # Check given `lang_code` overwites context lang
        self.assertEqual(misc.format_time(lang.with_context(lang='fr_FR').env, time_part, time_format='ah:mm', lang_code='zh_CN'), '\u4e0b\u53484:30')
        self.assertEqual(misc.format_time(lang.with_context(lang='zh_CN').env, time_part, time_format='ah:mm', lang_code='fr_FR'), 'PM4:30')

    def test_02_tz(self):
        self.env.user.tz = 'Europe/Brussels'
        datetime_str = '2016-12-31 23:55:00'
        date_datetime = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        # While London is still in 2016, Brussels is already in 2017
        self.assertEqual(misc.format_date(self.env, date_datetime), '01/01/2017')

        # Force London timezone
        date_datetime = date_datetime.replace(tzinfo=pytz.UTC)
        self.assertEqual(misc.format_date(self.env, date_datetime), '12/31/2016', "User's tz must be ignored when tz is specifed in datetime object")


class TestCallbacks(BaseCase):
    def test_callback(self):
        log = []
        callbacks = misc.Callbacks()

        # add foo
        def foo():
            log.append("foo")

        callbacks.add(foo)

        # add bar
        @callbacks.add
        def bar():
            log.append("bar")

        # add foo again
        callbacks.add(foo)

        # this should call foo(), bar(), foo()
        callbacks.run()
        self.assertEqual(log, ["foo", "bar", "foo"])

        # this should do nothing
        callbacks.run()
        self.assertEqual(log, ["foo", "bar", "foo"])

    def test_aggregate(self):
        log = []
        callbacks = misc.Callbacks()

        # register foo once
        @callbacks.add
        def foo():
            log.append(callbacks.data["foo"])

        # aggregate data
        callbacks.data.setdefault("foo", []).append(1)
        callbacks.data.setdefault("foo", []).append(2)
        callbacks.data.setdefault("foo", []).append(3)

        # foo() is called once
        callbacks.run()
        self.assertEqual(log, [[1, 2, 3]])
        self.assertFalse(callbacks.data)

        callbacks.run()
        self.assertEqual(log, [[1, 2, 3]])

    def test_reentrant(self):
        log = []
        callbacks = misc.Callbacks()

        # register foo that runs callbacks
        @callbacks.add
        def foo():
            log.append("foo1")
            callbacks.run()
            log.append("foo2")

        @callbacks.add
        def bar():
            log.append("bar")

        # both foo() and bar() are called once
        callbacks.run()
        self.assertEqual(log, ["foo1", "bar", "foo2"])

        callbacks.run()
        self.assertEqual(log, ["foo1", "bar", "foo2"])


class TestRemoveAccents(BaseCase):
    def test_empty_string(self):
        self.assertEqual(remove_accents(False), False)
        self.assertEqual(remove_accents(''), '')
        self.assertEqual(remove_accents(None), None)

    def test_latin(self):
        self.assertEqual(remove_accents('Niño Hernández'), 'Nino Hernandez')
        self.assertEqual(remove_accents('Anaïs Clémence'), 'Anais Clemence')

    def test_non_latin(self):
        self.assertEqual(remove_accents('العربية'), 'العربية')
        self.assertEqual(remove_accents('русский алфавит'), 'русскии алфавит')


class TestAddonsFileAccess(BaseCase):

    def assertCannotAccess(self, path, ExceptionType=FileNotFoundError, filter_ext=None):
        with self.assertRaises(ExceptionType):
            file_path(path, filter_ext=filter_ext)

    def assertCanRead(self, path, needle='', mode='r', filter_ext=None):
        with file_open(path, mode, filter_ext) as f:
            self.assertIn(needle, f.read())

    def assertCannotRead(self, path, ExceptionType=FileNotFoundError, filter_ext=None):
        with self.assertRaises(ExceptionType):
            file_open(path, filter_ext=filter_ext)

    def test_file_path(self):
        # absolute path
        self.assertEqual(__file__, file_path(__file__))
        self.assertEqual(__file__, file_path(__file__, filter_ext=None)) # means "no filter" too
        self.assertEqual(__file__, file_path(__file__, filter_ext=('.py',)))

        # directory target is ok
        self.assertEqual(os.path.dirname(__file__), file_path(os.path.join(__file__, '..')))

        # relative path
        relpath = os.path.join(*(__file__.split(os.sep)[-3:])) # 'base/tests/test_misc.py'
        self.assertEqual(__file__, file_path(relpath))
        self.assertEqual(__file__, file_path(relpath, filter_ext=('.py',)))

        # leading 'addons/' is ignored if present
        self.assertTrue(file_path("addons/web/__init__.py"))
        relpath = os.path.join('addons', relpath) # 'addons/base/tests/test_misc.py'
        self.assertEqual(__file__, file_path(relpath))

        # files in root_path are allowed
        self.assertTrue(file_path('tools/misc.py'))

        # errors when outside addons_paths
        self.assertCannotAccess('/doesnt/exist')
        self.assertCannotAccess('/tmp')
        self.assertCannotAccess('../../../../../../../../../tmp')
        self.assertCannotAccess(os.path.join(__file__, '../../../../../'))

        # data_dir is forbidden
        self.assertCannotAccess(config['data_dir'])

        # errors for illegal extensions
        self.assertCannotAccess(__file__, ValueError, filter_ext=('.png',))
        # file doesnt exist but has wrong extension
        self.assertCannotAccess(__file__.replace('.py', '.foo'), ValueError, filter_ext=('.png',))

    def test_file_open(self):
        # The needle includes UTF8 so we test reading non-ASCII files at the same time.
        # This depends on the system locale and is harder to unit test, but if you manage to run the
        # test with a non-UTF8 locale (`LC_ALL=fr_FR.iso8859-1 python3...`) it should not crash ;-)
        test_needle = "A needle with non-ascii bytes: ♥"

        # absolute path
        self.assertCanRead(__file__, test_needle)
        self.assertCanRead(__file__, test_needle.encode(), mode='rb')
        self.assertCanRead(__file__, test_needle.encode(), mode='rb', filter_ext=('.py',))

        # directory target *is* an error
        with self.assertRaises(FileNotFoundError):
            file_open(os.path.join(__file__, '..'))

        # relative path
        relpath = os.path.join(*(__file__.split(os.sep)[-3:])) # 'base/tests/test_misc.py'
        self.assertCanRead(relpath, test_needle)
        self.assertCanRead(relpath, test_needle.encode(), mode='rb')
        self.assertCanRead(relpath, test_needle.encode(), mode='rb', filter_ext=('.py',))

        # leading 'addons/' is ignored if present
        self.assertCanRead("addons/web/__init__.py", "import")
        relpath = os.path.join('addons', relpath) # 'addons/base/tests/test_misc.py'
        self.assertCanRead(relpath, test_needle)

        # files in root_path are allowed
        self.assertCanRead('tools/misc.py')

        # errors when outside addons_paths
        self.assertCannotRead('/doesnt/exist')
        self.assertCannotRead('')
        self.assertCannotRead('/tmp')
        self.assertCannotRead('../../../../../../../../../tmp')
        self.assertCannotRead(os.path.join(__file__, '../../../../../'))

        # data_dir is forbidden
        self.assertCannotRead(config['data_dir'])

        # errors for illegal extensions
        self.assertCannotRead(__file__, ValueError, filter_ext=('.png',))
        # file doesnt exist but has wrong extension
        self.assertCannotRead(__file__.replace('.py', '.foo'), ValueError, filter_ext=('.png',))


class TestDictTools(BaseCase):
    def test_readonly_dict(self):
        d = misc.ReadonlyDict({'foo': 'bar'})
        with self.assertRaises(TypeError):
            d['baz'] = 'xyz'
        with self.assertRaises(AttributeError):
            d.update({'baz': 'xyz'})
        with self.assertRaises(TypeError):
            dict.update(d, {'baz': 'xyz'})


class TestFormatLang(TransactionCase):
    def test_value_and_digits(self):
        self.assertEqual(misc.formatLang(self.env, 100.23, digits=1), '100.2')
        self.assertEqual(misc.formatLang(self.env, 100.23, digits=3), '100.230')

        self.assertEqual(misc.formatLang(self.env, ''), '', 'If value is an empty string, it should return an empty string (not 0)')

        self.assertEqual(misc.formatLang(self.env, 100), '100.00', 'If digits is None (default value), it should default to 2')

        # Default rounding is 'HALF_EVEN'
        self.assertEqual(misc.formatLang(self.env, 100.205), '100.20')
        self.assertEqual(misc.formatLang(self.env, 100.215), '100.22')

    def test_grouping(self):
        self.env["res.lang"].create({
            "name": "formatLang Lang",
            "code": "fLT",
            "grouping": "[3,2,-1]",
            "decimal_point": "!",
            "thousands_sep": "?",
        })

        self.env['res.lang']._activate_lang('fLT')

        self.assertEqual(misc.formatLang(self.env['res.lang'].with_context(lang='fLT').env, 1000000000, grouping=True), '10000?00?000!00')
        self.assertEqual(misc.formatLang(self.env['res.lang'].with_context(lang='fLT').env, 1000000000, grouping=False), '1000000000.00')

    def test_decimal_precision(self):
        decimal_precision = self.env['decimal.precision'].create({
            'name': 'formatLang Decimal Precision',
            'digits': 3,  # We want .001 decimals to make sure the decimal precision parameter 'dp' is chosen.
        })

        self.assertEqual(misc.formatLang(self.env, 100, dp=decimal_precision.name), '100.000')

    def test_currency_object(self):
        currency_object = self.env['res.currency'].create({
            'name': 'formatLang Currency',
            'symbol': 'fL',
            'rounding': 0.1,  # We want .1 decimals to make sure 'currency_obj' is chosen.
            'position': 'after',
        })

        self.assertEqual(misc.formatLang(self.env, 100, currency_obj=currency_object), '100.0%sfL' % u'\N{NO-BREAK SPACE}')

        currency_object.write({'position': 'before'})

        self.assertEqual(misc.formatLang(self.env, 100, currency_obj=currency_object), 'fL%s100.0' % u'\N{NO-BREAK SPACE}')

    def test_decimal_precision_and_currency_object(self):
        decimal_precision = self.env['decimal.precision'].create({
            'name': 'formatLang Decimal Precision',
            'digits': 3,
        })

        currency_object = self.env['res.currency'].create({
            'name': 'formatLang Currency',
            'symbol': 'fL',
            'rounding': 0.1,
            'position': 'after',
        })

        # If we have a 'dp' and 'currency_obj', we use the decimal precision of 'dp' and the format of 'currency_obj'.
        self.assertEqual(misc.formatLang(self.env, 100, dp=decimal_precision.name, currency_obj=currency_object), '100.000%sfL' % u'\N{NO-BREAK SPACE}')

    def test_rounding_method(self):
        self.assertEqual(misc.formatLang(self.env, 100.205), '100.20')  # Default is 'HALF-EVEN'
        self.assertEqual(misc.formatLang(self.env, 100.215), '100.22')  # Default is 'HALF-EVEN'

        self.assertEqual(misc.formatLang(self.env, 100.205, rounding_method='HALF-UP'), '100.21')
        self.assertEqual(misc.formatLang(self.env, 100.215, rounding_method='HALF-UP'), '100.22')

        self.assertEqual(misc.formatLang(self.env, 100.205, rounding_method='HALF-DOWN'), '100.20')
        self.assertEqual(misc.formatLang(self.env, 100.215, rounding_method='HALF-DOWN'), '100.21')

    def test_rounding_unit(self):
        self.assertEqual(misc.formatLang(self.env, 1000000.00), '1,000,000.00')
        self.assertEqual(misc.formatLang(self.env, 1000000.00, rounding_unit='units'), '1,000,000')
        self.assertEqual(misc.formatLang(self.env, 1000000.00, rounding_unit='thousands'), '1,000')
        self.assertEqual(misc.formatLang(self.env, 1000000.00, rounding_unit='lakhs'), '10')
        self.assertEqual(misc.formatLang(self.env, 1000000.00, rounding_unit="millions"), '1')

    def test_rounding_method_and_rounding_unit(self):
        self.assertEqual(misc.formatLang(self.env, 1822060000, rounding_method='HALF-UP', rounding_unit='lakhs'), '18,221')
        self.assertEqual(misc.formatLang(self.env, 1822050000, rounding_method='HALF-UP', rounding_unit='lakhs'), '18,221')
        self.assertEqual(misc.formatLang(self.env, 1822049900, rounding_method='HALF-UP', rounding_unit='lakhs'), '18,220')


class TestUrlValidate(BaseCase):
    def test_url_validate(self):
        for case, truth in [
            # full URLs should be preserved
            ('http://example.com', 'http://example.com'),
            ('http://example.com/index.html', 'http://example.com/index.html'),
            ('http://example.com?debug=1', 'http://example.com?debug=1'),
            ('http://example.com#h3', 'http://example.com#h3'),

            # URLs with a domain should get a http scheme
            ('example.com', 'http://example.com'),
            ('example.com/index.html', 'http://example.com/index.html'),
            ('example.com?debug=1', 'http://example.com?debug=1'),
            ('example.com#h3', 'http://example.com#h3'),
        ]:
            with self.subTest(case=case):
                self.assertEqual(validate_url(case), truth)

        # broken cases, do we really want that?
        self.assertEqual(validate_url('/index.html'), 'http:///index.html')
        self.assertEqual(validate_url('?debug=1'), 'http://?debug=1')
        self.assertEqual(validate_url('#model=project.task&id=3603607'), 'http://#model=project.task&id=3603607')


class TestMiscToken(TransactionCase):

    def test_expired_token(self):
        payload = {'test': True, 'value': 123456, 'some_string': 'hello', 'some_dict': {'name': 'New Dict'}}
        expiration = datetime.datetime.now() - datetime.timedelta(days=1)
        token = misc.hash_sign(self.env, 'test', payload, expiration=expiration)
        self.assertIsNone(misc.verify_hash_signed(self.env, 'test', token))

    def test_long_payload(self):
        payload = {'test': True, 'value':123456, 'some_string': 'hello', 'some_dict': {'name': 'New Dict'}}
        token = misc.hash_sign(self.env, 'test', payload, expiration_hours=24)
        self.assertEqual(misc.verify_hash_signed(self.env, 'test', token), payload)

    def test_None_payload(self):
        with self.assertRaises(Exception):
            misc.hash_sign(self.env, 'test', None, expiration_hours=24)

    def test_list_payload(self):
        payload = ["str1", "str2", "str3", 4, 5]
        token = misc.hash_sign(self.env, 'test', payload, expiration_hours=24)
        self.assertEqual(misc.verify_hash_signed(self.env, 'test', token), payload)

    def test_modified_payload(self):
        payload = ["str1", "str2", "str3", 4, 5]
        token = base64.urlsafe_b64decode(misc.hash_sign(self.env, 'test', payload, expiration_hours=24) + '===')
        new_timestamp = datetime.datetime.now() + datetime.timedelta(days=7)
        new_timestamp = int(new_timestamp.timestamp())
        new_timestamp = new_timestamp.to_bytes(8, byteorder='little')
        token = base64.urlsafe_b64encode(token[:1] + new_timestamp + token[9:]).decode()
        self.assertIsNone(misc.verify_hash_signed(self.env, 'test', token))
