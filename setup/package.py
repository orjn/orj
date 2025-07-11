#!/usr/bin/env python3
# Part of Orj. See LICENSE file for full copyright and licensing details.

import argparse
import logging
import os
import pexpect
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import traceback

from pathlib import Path
from xmlrpc import client as xmlrpclib

from glob import glob

#----------------------------------------------------------
# Utils
#----------------------------------------------------------

ROOTDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TSTAMP = time.strftime("%Y%m%d", time.gmtime())
TSEC = time.strftime("%H%M%S", time.gmtime())
# Get some variables from release.py
version = ...
version_info = ...
nt_service_name = ...
exec(open(os.path.join(ROOTDIR, 'orj', 'release.py'), 'rb').read())
VERSION = version.split('-')[0].replace('saas~', '')
GPGPASSPHRASE = os.getenv('GPGPASSPHRASE')
GPGID = os.getenv('GPGID')
DOCKERVERSION = VERSION.replace('+', '')
INSTALL_TIMEOUT = 600

DOCKERUSER = """
RUN mkdir /var/lib/orj && \
    groupadd -g %(group_id)s orj && \
    useradd -u %(user_id)s -g orj orj -d /var/lib/orj && \
    mkdir /data && \
    chown orj:orj /var/lib/orj /data
USER orj
""" % {'group_id': os.getgid(), 'user_id': os.getuid()}


class OrjTestTimeoutError(Exception):
    pass


class OrjTestError(Exception):
    pass


def run_cmd(cmd, chdir=None, timeout=None):
    logging.info("Running command: '%s'", ' '.join(cmd))
    return subprocess.run(cmd, cwd=chdir, timeout=timeout)


def _rpc_count_modules(addr='http://127.0.0.1', port=8069, dbname='mycompany'):
    time.sleep(5)
    uid = xmlrpclib.ServerProxy('%s:%s/xmlrpc/2/common' % (addr, port)).authenticate(
        dbname, 'admin', 'admin', {}
    )
    modules = xmlrpclib.ServerProxy('%s:%s/xmlrpc/2/object' % (addr, port)).execute(
        dbname, uid, 'admin', 'ir.module.module', 'search', [('state', '=', 'installed')]
    )
    if len(modules) > 1:
        time.sleep(1)
        toinstallmodules = xmlrpclib.ServerProxy('%s:%s/xmlrpc/2/object' % (addr, port)).execute(
            dbname, uid, 'admin', 'ir.module.module', 'search', [('state', '=', 'to install')]
        )
        if toinstallmodules:
            logging.error("Package test: FAILED. Not able to install dependencies of base.")
            raise OrjTestError("Installation of package failed")
        else:
            logging.info("Package test: successfuly installed %s modules" % len(modules))
    else:
        logging.error("Package test: FAILED. Not able to install base.")
        raise OrjTestError("Package test: FAILED. Not able to install base.")


def publish(args, pub_type, extensions):
    """Publish builded package (move builded files and generate a symlink to the latests)
    :args: parsed program args
    :pub_type: one of [deb, rpm, src, exe]
    :extensions: list of extensions to publish
    :returns: published files
    """
    def _publish(release):
        build_path = os.path.join(args.build_dir, release)
        filename = release.split(os.path.sep)[-1]
        release_dir = os.path.join(args.pub, pub_type)
        release_path = os.path.join(release_dir, filename)
        os.renames(build_path, release_path)

        # Latest/symlink handler
        release_abspath = os.path.abspath(release_path)
        latest_abspath = release_abspath.replace(TSTAMP, 'latest')

        if os.path.islink(latest_abspath):
            os.unlink(latest_abspath)
        os.symlink(release_abspath, latest_abspath)

        return release_path

    published = []
    for extension in extensions:
        release = glob("%s/orj_*.%s" % (args.build_dir, extension))
        if release:
            published.append(_publish(release[0]))
    return published


# ---------------------------------------------------------
# Generates Packages, Sources and Release files of debian package
# ---------------------------------------------------------
def gen_deb_package(args, published_files):
    # Executes command to produce file_name in path, and moves it to args.pub/deb
    def _gen_file(args, command, file_name, path):
        cur_tmp_file_path = os.path.join(path, file_name)
        with open(cur_tmp_file_path, 'w') as out:
            subprocess.call(command, stdout=out, cwd=path)
        shutil.copy(cur_tmp_file_path, os.path.join(args.pub, 'deb', file_name))

    # Copy files to a temp directory (required because the working directory must contain only the
    # files of the last release)
    temp_path = tempfile.mkdtemp(suffix='debPackages')
    for pub_file_path in published_files:
        shutil.copy(pub_file_path, temp_path)

    commands = [
        (['dpkg-scanpackages', '--multiversion', '.'], "Packages"),  # Generate Packages file
        (['dpkg-scansources', '.'], "Sources"),  # Generate Sources file
        (['apt-ftparchive', 'release', '.'], "Release")  # Generate Release file
    ]
    # Generate files
    for command in commands:
        _gen_file(args, command[0], command[-1], temp_path)
    # Remove temp directory
    shutil.rmtree(temp_path)

    if args.sign:
        # Generate Release.gpg (= signed Release)
        # Options -abs: -a (Create ASCII armored output), -b (Make a detach signature), -s (Make a signature)
        subprocess.call(['gpg', '--default-key', GPGID, '--passphrase', GPGPASSPHRASE, '--yes', '-abs', '--no-tty', '-o', 'Release.gpg', 'Release'], cwd=os.path.join(args.pub, 'deb'))


# ---------------------------------------------------------
# Generates an RPM repo
# ---------------------------------------------------------
def rpm_sign(args, file_name):
    """Genereate a rpm repo in publish directory"""
    # Sign the RPM
    rpmsign = pexpect.spawn('/bin/bash', ['-c', 'rpm --resign %s' % file_name], cwd=os.path.join(args.pub, 'rpm'))
    rpmsign.expect_exact('Enter passphrase: ')
    rpmsign.send(GPGPASSPHRASE + '\r\n')
    rpmsign.expect(pexpect.EOF)


def _prepare_build_dir(args, win32=False, move_addons=True):
    """Copy files to the build directory"""
    logging.info('Preparing build dir "%s"', args.build_dir)
    cmd = ['rsync', '-a', '--delete', '--exclude', '.git', '--exclude', '*.pyc', '--exclude', '*.pyo']
    if win32 is False:
        cmd += ['--exclude', 'setup/win32']

    run_cmd(cmd + ['%s/' % args.orj_dir, args.build_dir])
    if not move_addons:
        return
    for addon_path in glob(os.path.join(args.build_dir, 'addons/*')):
        if args.blacklist is None or os.path.basename(addon_path) not in args.blacklist:
            try:
                shutil.move(addon_path, os.path.join(args.build_dir, 'orj/addons'))
            except shutil.Error as e:
                logging.warning("Warning '%s' while moving addon '%s", e, addon_path)
                if addon_path.startswith(args.build_dir) and os.path.isdir(addon_path):
                    logging.info("Removing '{}'".format(addon_path))
                    try:
                        shutil.rmtree(addon_path)
                    except shutil.Error as rm_error:
                        logging.warning("Cannot remove '{}': {}".format(addon_path, rm_error))


#  Docker stuffs
class Docker():
    """Base Docker class. Must be inherited by specific Docker builder class"""
    arch = None

    def __init__(self, args):
        """
        :param args: argparse parsed arguments
        """
        self.args = args
        self.tag = 'orj-%s-%s-nightly-tests' % (DOCKERVERSION, self.arch)
        self.container_name = None
        self.exposed_port = None
        docker_templates = {
            'tgz': os.path.join(args.build_dir, 'setup/package.dfsrc'),
            'deb': os.path.join(args.build_dir, 'setup/package.dfdebian'),
            'rpm': os.path.join(args.build_dir, 'setup/package.dffedora'),
            'win': os.path.join(args.build_dir, 'setup/package.dfwine'),
        }
        self.docker_template = Path(docker_templates[self.arch]).read_text(encoding='utf-8').replace('USER orj', DOCKERUSER)
        self.test_log_file = '/data/src/test-%s.log' % self.arch
        self.docker_dir = Path(self.args.build_dir) / 'docker'
        if not self.docker_dir.exists():
            self.docker_dir.mkdir()
        self.build_image()

    def build_image(self):
        """Build the dockerimage by copying Dockerfile into build_dir/docker"""
        docker_file = self.docker_dir / 'Dockerfile'
        docker_file.write_text(self.docker_template)
        shutil.copy(os.path.join(self.args.build_dir, 'requirements.txt'), self.docker_dir)
        run_cmd(["docker", "build", "--rm=True", "-t", self.tag, "."], chdir=self.docker_dir, timeout=1200).check_returncode()
        shutil.rmtree(self.docker_dir)

    def run(self, cmd, build_dir, container_name, user='orj', exposed_port=None, detach=False, timeout=None):
        self.container_name = container_name
        docker_cmd = [
            "docker",
            "run",
            "--user=%s" % user,
            "--name=%s" % container_name,
            "--rm",
            "--volume=%s:/data/src" % build_dir
        ]

        if exposed_port:
            docker_cmd.extend(['-p', '127.0.0.1:%s:%s' % (exposed_port, exposed_port)])
            self.exposed_port = exposed_port
        if detach:
            docker_cmd.append('-d')
            # preserve logs in case of detached docker container
            cmd = '(%s) > %s 2>&1' % (cmd, self.test_log_file)

        docker_cmd.extend([
            self.tag,
            "/bin/bash",
            "-c",
            "cd /data/src && %s" % cmd
        ])
        run_cmd(docker_cmd, timeout=timeout).check_returncode()

    def is_running(self):
        dinspect = subprocess.run(['docker', 'container', 'inspect', self.container_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        return True if dinspect.returncode == 0 else False

    def stop(self):
        run_cmd(["docker", "stop", self.container_name]).check_returncode()

    def test_orj(self):
        logging.info('Starting to test Orj install test')
        start_time = time.time()
        while self.is_running() and (time.time() - start_time) < INSTALL_TIMEOUT:
            time.sleep(5)
            if os.path.exists(os.path.join(args.build_dir, 'orj.pid')):
                try:
                    _rpc_count_modules(port=self.exposed_port)
                finally:
                    self.stop()
                return
        if self.is_running():
            self.stop()
            raise OrjTestTimeoutError('Orj pid file never appeared after %s sec' % INSTALL_TIMEOUT)
        raise OrjTestError('Error while installing/starting Orj after %s sec.\nSee testlogs.txt in build dir' % int(time.time() - start_time))

    def build(self):
        """To be overriden by specific builder"""
        pass

    def start_test(self):
        """To be overriden by specific builder"""
        pass


class DockerTgz(Docker):
    """Docker class to build python src package"""

    arch = 'tgz'

    def build(self):
        logging.info('Start building python tgz package')
        self.run('python3 setup.py sdist --quiet --formats=gztar,zip', self.args.build_dir, 'orj-src-build-%s' % TSTAMP)
        os.rename(glob('%s/dist/orj-*.tar.gz' % self.args.build_dir)[0], '%s/orj_%s.%s.tar.gz' % (self.args.build_dir, VERSION, TSTAMP))
        os.rename(glob('%s/dist/orj-*.zip' % self.args.build_dir)[0], '%s/orj_%s.%s.zip' % (self.args.build_dir, VERSION, TSTAMP))
        logging.info('Finished building python tgz package')

    def start_test(self):
        if not self.args.test:
            return
        logging.info('Start testing python tgz package')
        cmds = [
            'service postgresql start',
            'su postgres -s /bin/bash -c "createuser -s orj"',
            'su orj -s /bin/bash -c "python3 -m venv /var/lib/orj/orjvenv"',
            'su orj -s /bin/bash -c "/var/lib/orj/orjvenv/bin/python3 -m pip install --upgrade pip"',
            'su orj -s /bin/bash -c "/var/lib/orj/orjvenv/bin/python3 -m pip install -r /opt/release/requirements.txt"',
            f'su orj -s /bin/bash -c "/var/lib/orj/orjvenv/bin/python3 -m pip install /data/src/orj_{VERSION}.{TSTAMP}.tar.gz"',
            'su orj -s /bin/bash -c "createdb mycompany"',
            'su orj -s /bin/bash -c "/var/lib/orj/orjvenv/bin/orj -d mycompany -i base --stop-after-init"',
            'su orj -s /bin/bash -c "/var/lib/orj/orjvenv/bin/orj -d mycompany --pidfile=/data/src/orj.pid"',
        ]
        self.run(' && '.join(cmds), self.args.build_dir, 'orj-src-test-%s' % TSTAMP, user='root', detach=True, exposed_port=8069, timeout=300)
        self.test_orj()
        logging.info('Finished testing tgz package')


class DockerDeb(Docker):
    """Docker class to build debian package"""

    arch = 'deb'

    def build(self):
        logging.info('Start building debian package')
        # Append timestamp to version for the .dsc to refer the right .tar.gz
        cmds = ["sed -i '1s/^.*$/orj (%s.%s) stable; urgency=low/' debian/changelog" % (VERSION, TSTAMP)]
        cmds.append('dpkg-buildpackage -rfakeroot -uc -us -tc')
        # As the packages are built in the parent of the buildir, we move them back to build_dir
        cmds.append('mv ../orj_* ./')
        self.run(' && '.join(cmds), self.args.build_dir, 'orj-deb-build-%s' % TSTAMP)
        logging.info('Finished building debian package')

    def start_test(self):
        if not self.args.test:
            return
        logging.info('Start testing debian package')
        cmds = [
            'service postgresql start',
            '/usr/bin/apt-get update -y',
            f'/usr/bin/apt-get install -y /data/src/orj_{VERSION}.{TSTAMP}_all.deb',
            'su orj -s /bin/bash -c "orj -d mycompany -i base --pidfile=/data/src/orj.pid"',
        ]
        self.run(' && '.join(cmds), self.args.build_dir, 'orj-deb-test-%s' % TSTAMP, user='root', detach=True, exposed_port=8069, timeout=300)
        self.test_orj()
        logging.info('Finished testing debian package')


class DockerRpm(Docker):
    """Docker class to build rpm package"""

    arch = 'rpm'

    def build(self):
        logging.info('Start building fedora rpm package')
        rpmbuild_dir = '/var/lib/orj/rpmbuild'
        cmds = [
            'cd /data/src',
            'mkdir -p dist',
            'rpmdev-setuptree -d',
            f'cp -a /data/src/setup/rpm/orj.spec {rpmbuild_dir}/SPECS/',
            f'tar --transform "s/^\\./orj-{VERSION}/" -c -z -f {rpmbuild_dir}/SOURCES/orj-{VERSION}.tar.gz .',
            f'rpmbuild -bb --define="%version {VERSION}" /data/src/setup/rpm/orj.spec',
            f'mv {rpmbuild_dir}/RPMS/noarch/orj*.rpm /data/src/dist/'
        ]
        self.run(' && '.join(cmds), self.args.build_dir, f'orj-rpm-build-{TSTAMP}')
        os.rename(glob('%s/dist/orj-*.noarch.rpm' % self.args.build_dir)[0], '%s/orj_%s.%s.rpm' % (self.args.build_dir, VERSION, TSTAMP))
        logging.info('Finished building fedora rpm package')

    def start_test(self):
        if not self.args.test:
            return
        logging.info('Start testing rpm package')
        cmds = [
            'su postgres -c "/usr/bin/pg_ctl -D /var/lib/postgres/data start"',
            'sleep 5',
            'su postgres -c "createuser -s orj"',
            'su orj -c "createdb mycompany"',
            'dnf install -d 0 -e 0 /data/src/orj_%s.%s.rpm -y' % (VERSION, TSTAMP),
            'su orj -s /bin/bash -c "orj -c /etc/orj/orj.conf -d mycompany -i base --stop-after-init"',
            'su orj -s /bin/bash -c "orj -c /etc/orj/orj.conf -d mycompany --pidfile=/data/src/orj.pid"',
        ]
        self.run(' && '.join(cmds), args.build_dir, 'orj-rpm-test-%s' % TSTAMP, user='root', detach=True, exposed_port=8069, timeout=300)
        self.test_orj()
        logging.info('Finished testing rpm package')

    def gen_rpm_repo(self, args, rpm_filepath):
        pub_repodata_path = os.path.join(args.pub, 'rpm', 'repodata')
        # Removes the old repodata
        if os.path.isdir(pub_repodata_path):
            shutil.rmtree(pub_repodata_path)

        # Copy files to a temp directory (required because the working directory must contain only the
        # files of the last release)
        temp_path = tempfile.mkdtemp(suffix='rpmPackages')
        shutil.copy(rpm_filepath, temp_path)

        logging.info('Start creating rpm repo')
        self.run('createrepo /data/src/', temp_path, 'orj-rpm-createrepo-%s' % TSTAMP)
        shutil.copytree(os.path.join(temp_path, "repodata"), pub_repodata_path)

        # Remove temp directory
        shutil.rmtree(temp_path)


class DockerWine(Docker):
    """Docker class to build Windows package"""

    arch = 'win'

    def build_image(self):
        shutil.copy(os.path.join(self.args.build_dir, 'setup/win32/requirements-local-proxy.txt'), self.docker_dir)
        super().build_image()

    def build(self):
        logging.info('Start building windows package')
        winver = "%s.%s" % (VERSION.replace('~', '_').replace('+', ''), TSTAMP)
        container_python = '/var/lib/orj/.wine/drive_c/orjbuild/WinPy64/python-3.12.3.amd64/python.exe'
        nsis_args = f'/DVERSION={winver} /DMAJOR_VERSION={version_info[0]} /DMINOR_VERSION={version_info[1]} /DSERVICENAME={nt_service_name} /DPYTHONVERSION=3.12.3'
        cmds = [
            rf'wine {container_python} -m pip install --upgrade pip',
            rf'cat /data/src/requirements*.txt  | while read PACKAGE; do wine {container_python} -m pip install "${{PACKAGE%%#*}}" ; done',
            rf'wine "c:\nsis-3.11\makensis.exe" {nsis_args} "c:\orjbuild\server\setup\win32\setup.nsi"',
            rf'wine {container_python} -m pip list'
        ]
        self.run(' && '.join(cmds), self.args.build_dir, 'orj-win-build-%s' % TSTAMP)
        logging.info('Finished building Windows package')

def parse_args():
    ap = argparse.ArgumentParser()
    build_dir = "%s-%s-%s" % (ROOTDIR, TSEC, TSTAMP)
    log_levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARN, "error": logging.ERROR, "critical": logging.CRITICAL}

    ap.add_argument("-b", "--build-dir", default=build_dir, help="build directory (%(default)s)", metavar="DIR")
    ap.add_argument("-p", "--pub", default=None, help="pub directory %(default)s", metavar="DIR")
    ap.add_argument("--logging", action="store", choices=list(log_levels.keys()), default="info", help="Logging level")
    ap.add_argument("--build-deb", action="store_true")
    ap.add_argument("--build-rpm", action="store_true")
    ap.add_argument("--build-tgz", action="store_true")
    ap.add_argument("--build-win", action="store_true")

    ap.add_argument("-t", "--test", action="store_true", default=False, help="Test built packages")
    ap.add_argument("-s", "--sign", action="store_true", default=False, help="Sign Debian package / generate Rpm repo")
    ap.add_argument("--no-remove", action="store_true", help="don't remove build dir")
    ap.add_argument("--blacklist", nargs="*", help="Modules to blacklist in package")

    parsed_args = ap.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=log_levels[parsed_args.logging])
    parsed_args.orj_dir = ROOTDIR
    return parsed_args


def main(args):
    try:
        if args.build_tgz:
            _prepare_build_dir(args)
            docker_tgz = DockerTgz(args)
            docker_tgz.build()
            try:
                docker_tgz.start_test()
                published_files = publish(args, 'tgz', ['tar.gz', 'zip'])
            except Exception as e:
                logging.error("Won't publish the tgz release.\n Exception: %s" % str(e))
        if args.build_rpm:
            _prepare_build_dir(args)
            docker_rpm = DockerRpm(args)
            docker_rpm.build()
            try:
                docker_rpm.start_test()
                published_files = publish(args, 'rpm', ['rpm'])
                if args.sign:
                    logging.info('Signing rpm package')
                    rpm_sign(args, published_files[0])
                    logging.info('Generate rpm repo')
                    docker_rpm.gen_rpm_repo(args, published_files[0])
            except Exception as e:
                logging.error("Won't publish the rpm release.\n Exception: %s" % str(e))
        if args.build_deb:
            _prepare_build_dir(args, move_addons=False)
            docker_deb = DockerDeb(args)
            docker_deb.build()
            try:
                docker_deb.start_test()
                published_files = publish(args, 'deb', ['deb', 'dsc', 'changes', 'tar.xz'])
                gen_deb_package(args, published_files)
            except Exception as e:
                logging.error("Won't publish the deb release.\n Exception: %s" % str(e))
        if args.build_win:
            _prepare_build_dir(args, win32=True)
            docker_wine = DockerWine(args)
            docker_wine.build()
            try:
                published_files = publish(args, 'windows', ['exe'])
            except Exception as e:
                logging.error("Won't publish the exe release.\n Exception: %s" % str(e))
    except Exception as e:
        logging.error('Something bad happened ! : {}'.format(e))
        traceback.print_exc()
    finally:
        if args.no_remove:
            logging.info('Build dir "{}" not removed'.format(args.build_dir))
        else:
            if os.path.exists(args.build_dir):
                shutil.rmtree(args.build_dir)
                logging.info('Build dir %s removed' % args.build_dir)


if __name__ == '__main__':
    args = parse_args()
    if os.path.exists(args.build_dir):
        logging.error('Build dir "%s" already exists.', args.build_dir)
        sys.exit(1)
    main(args)
