# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import ast
import collections.abc
import copy
import functools
import importlib
import importlib.metadata
import logging
import os
import re
import sys
import traceback
import warnings
from os.path import join as opj, normpath

import orj
import orj.tools as tools
import orj.release as release
from orj.tools.misc import file_path

try:
    from packaging.requirements import InvalidRequirement, Requirement
except ImportError:
    class InvalidRequirement(Exception):
        ...

    class Requirement:
        def __init__(self, pydep):
            if not re.fullmatch(r'[\w\-]+', pydep):  # check that we have no versions or marker in pydep
                msg = f"Package `packaging` is required to parse `{pydep}` external dependency and is not installed"
                raise Exception(msg)
            self.marker = None
            self.specifier = None
            self.name = pydep


MANIFEST_NAMES = ('__manifest__.py', '__orj__.py')
README = ['README.rst', 'README.md', 'README.txt']

_DEFAULT_MANIFEST = {
    #addons_path: f'/path/to/the/addons/path/of/{module}',  # automatic
    'application': False,
    'bootstrap': False,  # web
    'assets': {},
    'author': 'Orj S.A.',
    'auto_install': False,
    'category': 'Uncategorized',
    'cloc_exclude': [],
    'configurator_snippets': {},  # website themes
    'countries': [],
    'data': [],
    'demo': [],
    'demo_xml': [],
    'depends': [],
    'description': '',
    'external_dependencies': {},
    #icon: f'/{module}/static/description/icon.png',  # automatic
    'init_xml': [],
    'installable': True,
    'images': [],  # website
    'images_preview_theme': {},  # website themes
    #license, mandatory
    'live_test_url': '',  # website themes
    'new_page_templates': {},  # website themes
    #name, mandatory
    'post_init_hook': '',
    'post_load': '',
    'pre_init_hook': '',
    'sequence': 100,
    'summary': '',
    'test': [],
    'update_xml': [],
    'uninstall_hook': '',
    'version': '1.0',
    'web': False,
    'website': '',
}

# matches field definitions like
#     partner_id: base.ResPartner = fields.Many2one
#     partner_id = fields.Many2one[base.ResPartner]
TYPED_FIELD_DEFINITION_RE = re.compile(r'''
    \b (?P<field_name>\w+) \s*
    (:\s*(?P<field_type>[^ ]*))? \s*
    = \s*
    fields\.(?P<field_class>Many2one|One2many|Many2many)
    (\[(?P<type_param>[^\]]+)\])?
''', re.VERBOSE)

_logger = logging.getLogger(__name__)


class UpgradeHook(object):
    """Makes the legacy `migrations` package being `orj.upgrade`"""

    def find_spec(self, fullname, path=None, target=None):
        if re.match(r"^orj\.addons\.base\.maintenance\.migrations\b", fullname):
            # We can't trigger a DeprecationWarning in this case.
            # In order to be cross-versions, the multi-versions upgrade scripts (0.0.0 scripts),
            # the tests, and the common files (utility functions) still needs to import from the
            # legacy name.
            return importlib.util.spec_from_loader(fullname, self)

    def load_module(self, name):
        assert name not in sys.modules

        canonical_upgrade = name.replace("orj.addons.base.maintenance.migrations", "orj.upgrade")

        if canonical_upgrade in sys.modules:
            mod = sys.modules[canonical_upgrade]
        else:
            mod = importlib.import_module(canonical_upgrade)

        sys.modules[name] = mod

        return sys.modules[name]


def initialize_sys_path():
    """
    Setup the addons path ``orj.addons.__path__`` with various defaults
    and explicit directories.
    """
    # hook orj.addons on data dir
    dd = os.path.normcase(tools.config.addons_data_dir)
    if os.access(dd, os.R_OK) and dd not in orj.addons.__path__:
        orj.addons.__path__.append(dd)

    # hook orj.addons on addons paths
    for ad in tools.config['addons_path'].split(','):
        ad = os.path.normcase(os.path.abspath(ad.strip()))
        if ad not in orj.addons.__path__:
            orj.addons.__path__.append(ad)

    # hook orj.addons on base module path
    base_path = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'addons')))
    if base_path not in orj.addons.__path__ and os.path.isdir(base_path):
        orj.addons.__path__.append(base_path)

    # hook orj.upgrade on upgrade-path
    from orj import upgrade
    legacy_upgrade_path = os.path.join(base_path, 'base', 'maintenance', 'migrations')
    for up in (tools.config['upgrade_path'] or legacy_upgrade_path).split(','):
        up = os.path.normcase(os.path.abspath(up.strip()))
        if os.path.isdir(up) and up not in upgrade.__path__:
            upgrade.__path__.append(up)

    # create decrecated module alias from orj.addons.base.maintenance.migrations to orj.upgrade
    spec = importlib.machinery.ModuleSpec("orj.addons.base.maintenance", None, is_package=True)
    maintenance_pkg = importlib.util.module_from_spec(spec)
    maintenance_pkg.migrations = upgrade
    sys.modules["orj.addons.base.maintenance"] = maintenance_pkg
    sys.modules["orj.addons.base.maintenance.migrations"] = upgrade

    # hook deprecated module alias from orj to orj and "crm"-like to orj.addons
    if not getattr(initialize_sys_path, 'called', False): # only initialize once
        sys.meta_path.insert(0, UpgradeHook())
        initialize_sys_path.called = True


def get_module_path(module, downloaded=False, display_warning=True):
    """Return the path of the given module.

    Search the addons paths and return the first path where the given
    module is found. If downloaded is True, return the default addons
    path if nothing else is found.

    """
    if re.search(r"[\/\\]", module):
        return False
    for adp in orj.addons.__path__:
        files = [opj(adp, module, manifest) for manifest in MANIFEST_NAMES] +\
                [opj(adp, module + '.zip')]
        if any(os.path.exists(f) for f in files):
            return opj(adp, module)

    if downloaded:
        return opj(tools.config.addons_data_dir, module)
    if display_warning:
        _logger.warning('module %s: module not found', module)
    return False

def get_resource_path(module, *args):
    """Return the full path of a resource of the given module.

    :param module: module name
    :param list(str) args: resource path components within module

    :rtype: str
    :return: absolute path to the resource
    """
    warnings.warn(
        f"Since 17.0: use tools.misc.file_path instead of get_resource_path({module}, {args})",
        DeprecationWarning,
    )
    resource_path = opj(module, *args)
    try:
        return file_path(resource_path)
    except (FileNotFoundError, ValueError):
        return False

# backwards compatibility
get_module_resource = get_resource_path
check_resource_path = get_resource_path

def get_resource_from_path(path):
    """Tries to extract the module name and the resource's relative path
    out of an absolute resource path.

    If operation is successful, returns a tuple containing the module name, the relative path
    to the resource using '/' as filesystem seperator[1] and the same relative path using
    os.path.sep seperators.

    [1] same convention as the resource path declaration in manifests

    :param path: absolute resource path

    :rtype: tuple
    :return: tuple(module_name, relative_path, os_relative_path) if possible, else None
    """
    resource = False
    sorted_paths = sorted(orj.addons.__path__, key=len, reverse=True)
    for adpath in sorted_paths:
        # force trailing separator
        adpath = os.path.join(adpath, "")
        if os.path.commonprefix([adpath, path]) == adpath:
            resource = path.replace(adpath, "", 1)
            break

    if resource:
        relative = resource.split(os.path.sep)
        if not relative[0]:
            relative.pop(0)
        module = relative.pop(0)
        return (module, '/'.join(relative), os.path.sep.join(relative))
    return None

def get_module_icon(module):
    fpath = f"{module}/static/description/icon.png"
    try:
        file_path(fpath)
        return "/" + fpath
    except FileNotFoundError:
        return "/base/static/description/icon.png"

def get_module_icon_path(module):
    try:
        return file_path(f"{module}/static/description/icon.png")
    except FileNotFoundError:
        return file_path("base/static/description/icon.png")

def module_manifest(path):
    """Returns path to module manifest if one can be found under `path`, else `None`."""
    if not path:
        return None
    for manifest_name in MANIFEST_NAMES:
        candidate = opj(path, manifest_name)
        if os.path.isfile(candidate):
            if manifest_name == '__orj__.py':
                warnings.warn(
                    "__orj__.py manifests are deprecated since 17.0, "
                    f"rename {candidate!r} to __manifest__.py "
                    "(valid since 10.0)",
                    category=DeprecationWarning
                )
            return candidate

def get_module_root(path):
    """
    Get closest module's root beginning from path

        # Given:
        # /foo/bar/module_dir/static/src/...

        get_module_root('/foo/bar/module_dir/static/')
        # returns '/foo/bar/module_dir'

        get_module_root('/foo/bar/module_dir/')
        # returns '/foo/bar/module_dir'

        get_module_root('/foo/bar')
        # returns None

    @param path: Path from which the lookup should start

    @return:  Module root path or None if not found
    """
    while not module_manifest(path):
        new_path = os.path.abspath(opj(path, os.pardir))
        if path == new_path:
            return None
        path = new_path
    return path

def load_manifest(module, mod_path=None):
    """ Load the module manifest from the file system. """

    if not mod_path:
        mod_path = get_module_path(module, downloaded=True)
    manifest_file = module_manifest(mod_path)

    if not manifest_file:
        _logger.debug('module %s: no manifest file found %s', module, MANIFEST_NAMES)
        return {}

    manifest = copy.deepcopy(_DEFAULT_MANIFEST)

    manifest['icon'] = get_module_icon(module)

    with tools.file_open(manifest_file, mode='r') as f:
        manifest.update(ast.literal_eval(f.read()))

    if not manifest['description']:
        readme_path = [opj(mod_path, x) for x in README
                       if os.path.isfile(opj(mod_path, x))]
        if readme_path:
            with tools.file_open(readme_path[0]) as fd:
                manifest['description'] = fd.read()

    if not manifest.get('license'):
        manifest['license'] = 'LGPL-3'
        _logger.warning("Missing `license` key in manifest for %r, defaulting to LGPL-3", module)

    # auto_install is either `False` (by default) in which case the module
    # is opt-in, either a list of dependencies in which case the module is
    # automatically installed if all dependencies are (special case: [] to
    # always install the module), either `True` to auto-install the module
    # in case all dependencies declared in `depends` are installed.
    if isinstance(manifest['auto_install'], collections.abc.Iterable):
        manifest['auto_install'] = set(manifest['auto_install'])
        non_dependencies = manifest['auto_install'].difference(manifest['depends'])
        assert not non_dependencies,\
            "auto_install triggers must be dependencies, found " \
            "non-dependencies [%s] for module %s" % (
                ', '.join(non_dependencies), module
            )
    elif manifest['auto_install']:
        manifest['auto_install'] = set(manifest['depends'])

    try:
        manifest['version'] = adapt_version(manifest['version'])
    except ValueError as e:
        if manifest.get("installable", True):
            raise ValueError(f"Module {module}: invalid manifest") from e
    manifest['addons_path'] = normpath(opj(mod_path, os.pardir))

    return manifest

def get_manifest(module, mod_path=None):
    """
    Get the module manifest.

    :param str module: The name of the module (sale, purchase, ...).
    :param Optional[str] mod_path: The optional path to the module on
        the file-system. If not set, it is determined by scanning the
        addons-paths.
    :returns: The module manifest as a dict or an empty dict
        when the manifest was not found.
    :rtype: dict
    """
    return copy.deepcopy(_get_manifest_cached(module, mod_path))

@functools.lru_cache(maxsize=None)
def _get_manifest_cached(module, mod_path=None):
    return load_manifest(module, mod_path)


def load_orj_module(module_name):
    """ Load an Orj module, if not already loaded.

    This loads the module and register all of its models, thanks to either
    the MetaModel metaclass, or the explicit instantiation of the model.
    This is also used to load server-wide module (i.e. it is also used
    when there is no model to register).
    """

    qualname = f'orj.addons.{module_name}'
    if qualname in sys.modules:
        return

    try:
        __import__(qualname)

        # Call the module's post-load hook. This can done before any model or
        # data has been initialized. This is ok as the post-load hook is for
        # server-wide (instead of registry-specific) functionalities.
        info = get_manifest(module_name)
        if info['post_load']:
            getattr(sys.modules[qualname], info['post_load'])()

    except AttributeError as err:
        _logger.critical("Couldn't load module %s", module_name)
        trace = traceback.format_exc()
        match = TYPED_FIELD_DEFINITION_RE.search(trace)
        if match and "most likely due to a circular import" in trace:
            field_name = match['field_name']
            field_class = match['field_class']
            field_type = match['field_type'] or match['type_param']
            if "." not in field_type:
                field_type = f"{module_name}.{field_type}"
            raise AttributeError(
                f"{err}\n"
                "To avoid circular import for the the comodel use the annotation syntax:\n"
                f"    {field_name}: {field_type} = fields.{field_class}(...)\n"
                "and add at the beggining of the file:\n"
                "    from __future__ import annotations"
            ).with_traceback(err.__traceback__) from None
        raise
    except Exception:
        _logger.critical("Couldn't load module %s", module_name)
        raise

def get_modules():
    """Returns the list of module names
    """
    def listdir(dir):
        def clean(name):
            name = os.path.basename(name)
            if name[-4:] == '.zip':
                name = name[:-4]
            return name

        def is_really_module(name):
            for mname in MANIFEST_NAMES:
                if os.path.isfile(opj(dir, name, mname)):
                    return True
        return [
            clean(it)
            for it in os.listdir(dir)
            if is_really_module(it)
        ]

    plist = []
    for ad in orj.addons.__path__:
        if not os.path.exists(ad):
            _logger.warning("addons path does not exist: %s", ad)
            continue
        plist.extend(listdir(ad))
    return sorted(set(plist))

def get_modules_with_version():
    modules = get_modules()
    res = dict.fromkeys(modules, adapt_version('1.0'))
    for module in modules:
        try:
            info = get_manifest(module)
            res[module] = info['version']
        except Exception:
            continue
    return res

def adapt_version(version):
    serie = release.major_version
    if version == serie or not version.startswith(serie + '.'):
        base_version = version
        version = '%s.%s' % (serie, version)
    else:
        base_version = version[len(serie) + 1:]

    if not re.match(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$", base_version):
        raise ValueError(f"Invalid version {base_version!r}. Modules should have a version in format `x.y`, `x.y.z`,"
                         f" `{serie}.x.y` or `{serie}.x.y.z`.")

    return version


current_test = False


def check_python_external_dependency(pydep):
    try:
        requirement = Requirement(pydep)
    except InvalidRequirement as e:
        msg = f"{pydep} is an invalid external dependency specification: {e}"
        raise Exception(msg) from e
    if requirement.marker and not requirement.marker.evaluate():
        _logger.debug(
            "Ignored external dependency %s because environment markers do not match",
            pydep
        )
        return
    try:
        version = importlib.metadata.version(requirement.name)
    except importlib.metadata.PackageNotFoundError as e:
        try:
            # keep compatibility with module name but log a warning instead of info
            importlib.import_module(pydep)
            _logger.warning("python external dependency on '%s' does not appear o be a valid PyPI package. Using a PyPI package name is recommended.", pydep)
            return
        except ImportError:
            pass
        msg = f"External dependency {pydep} not installed: {e}"
        raise Exception(msg) from e
    if requirement.specifier and not requirement.specifier.contains(version):
        msg = f"External dependency version mismatch: {pydep} (installed: {version})"
        raise Exception(msg)


def check_manifest_dependencies(manifest):
    depends = manifest.get('external_dependencies')
    if not depends:
        return
    for pydep in depends.get('python', []):
        check_python_external_dependency(pydep)

    for binary in depends.get('bin', []):
        try:
            tools.find_in_path(binary)
        except IOError:
            raise Exception('Unable to find %r in path' % (binary,))
