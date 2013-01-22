##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A recipe based on zc.recipe.testrunner
"""

import os
import os.path
import pkg_resources
import sys
import zc.buildout.easy_install

import z3c.recipe.scripts.scripts

class TestRunner:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        # We do this early so the "extends" functionality works before we get
        # to the other options below.
        self._delegated = z3c.recipe.scripts.scripts.Base(
            buildout, name, options)

        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name,
                'working-directory')

    def install(self):
        options = self.options
        generated = []
        eggs, ws = self._delegated.working_set(('collective.xmltestreport', ))

        test_paths = [ws.find(pkg_resources.Requirement.parse(spec)).location
                      for spec in eggs]

        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = '(%s) + ' % defaults

        if not os.path.exists(options['parts-directory']):
            os.mkdir(options['parts-directory'])
            generated.append(options['parts-directory'])
        site_py_dest = os.path.join(options['parts-directory'],
                                    'site-packages')
        if not os.path.exists(site_py_dest):
            os.mkdir(site_py_dest)
            generated.append(site_py_dest)
        wd = options.get('working-directory', '')
        if not wd:
            wd = options['location']
            if os.path.exists(wd):
                assert os.path.isdir(wd)
            else:
                os.mkdir(wd) # makedirs
                generated.append(wd)
        wd = os.path.abspath(wd)

        if self._delegated._relative_paths:
            wd = _relativize(self._delegated._relative_paths, wd)
            test_paths = [_relativize(self._delegated._relative_paths, p)
                          for p in test_paths]
        else:
            wd = repr(wd)
            test_paths = map(repr, test_paths)

        initialization = initialization_template % wd

        env_section = options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        initialization_section = options.get('initialization', '').strip()
        if initialization_section:
            initialization += initialization_section

        generated.extend(zc.buildout.easy_install.sitepackage_safe_scripts(
            self.buildout['buildout']['bin-directory'], ws,
            options['executable'], site_py_dest,
            reqs=[(options['script'], 'collective.xmltestreport.runner', 'run')],
            extra_paths=self._delegated.extra_paths,
            include_site_packages=self._delegated.include_site_packages,
            exec_sitecustomize=self._delegated.exec_sitecustomize,
            relative_paths=self._delegated._relative_paths,
            script_arguments=defaults + (
                    '[\n'+
                    ''.join(("        '--test-path', %s,\n" % p)
                            for p in test_paths)
                    +'        ]'),
            script_initialization=initialization,
            initialization=initialization,
            ))

        return generated

    update = install

arg_template = """[
  '--test-path', %(TESTPATH)s,
  ]"""

initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
os.chdir(%s)
"""

env_template = """os.environ['%s'] = %r
"""

def _relativize(base, path):
    base += os.path.sep
    if sys.platform == 'win32':
        #windoze paths are case insensitive, but startswith is not
        base = base.lower()
        path = path.lower()

    if path.startswith(base):
        path = 'join(base, %r)' % path[len(base):]
    else:
        path = repr(path)
    return path

