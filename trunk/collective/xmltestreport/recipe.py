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
import zc.buildout.easy_install
import zc.recipe.egg

class TestRunner:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options
        dest = []
        eggs, ws = self.egg.working_set(('zope.testing', 'collective.xmltestreport', ))

        test_paths = [ws.find(pkg_resources.Requirement.parse(spec)).location
                      for spec in eggs]

        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = '(%s) + ' % defaults

        wd = options.get('working-directory', '')
        if not wd:
            wd = options['location']
            if os.path.exists(wd):
                assert os.path.isdir(wd)
            else:
                os.mkdir(wd)
            dest.append(wd)
        wd = os.path.abspath(wd)

        if self.egg._relative_paths:
            wd = _relativize(self.egg._relative_paths, wd)
            test_paths = [_relativize(self.egg._relative_paths, p)
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

        dest.extend(zc.buildout.easy_install.scripts(
            [(options['script'], 'collective.xmltestreport.runner', 'run')],
            ws, options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            arguments = defaults + (
                    '[\n'+
                    ''.join(("        '--test-path', %s,\n" % p)
                            for p in test_paths)
                    +'        ]'),
            initialization = initialization,
            relative_paths = self.egg._relative_paths,
            ))

        return dest

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
    if path.startswith(base):
        path = 'join(base, %r)' % path[len(base):]
    else:
        path = repr(path)
    return path
