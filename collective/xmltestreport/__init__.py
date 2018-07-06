##############################################################################
#
# Copyright (c) 2004-2013 Zope Foundation and Contributors.
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
"""Test runner
    """

import os
import sys


def run(defaults=None, args=None, script_parts=None, cwd=None, warnings=None):
    """Main runner function which can be and is being used from main programs.
        
        Will execute the tests and exit the process according to the test result.
        
        """
    failed = run_internal(defaults, args, script_parts=script_parts, cwd=cwd, warnings=warnings)
    sys.exit(int(failed))


def run_internal(defaults=None, args=None, script_parts=None, cwd=None, warnings=None):
    """Execute tests.
        
        Returns whether errors or failures occured during testing.
        
        
        """
    if script_parts is None:
        script_parts = _script_parts(args)
    if cwd is None:
        cwd = os.getcwd()
    # XXX Bah. Lazy import to avoid circular/early import problems
    from collective.xmltestreport import runner
    runner.run(defaults, args, script_parts=script_parts, cwd=cwd, warnings=warnings)
    return runner.failed


def _script_parts(args=None):
    script_parts = (args or sys.argv)[0:1]
    # If we are running via setup.py, then we'll have to run the
    # sub-process differently.
    if script_parts[0] == 'setup.py':
        script_parts = ['-c', 'from zope.testrunner import run; run()']
    else:
        # make sure we remember the absolute path early -- the tests might
        # do an os.chdir()
        script_parts[0] = os.path.abspath(script_parts[0])
    return script_parts


if __name__ == '__main__':
    run()
