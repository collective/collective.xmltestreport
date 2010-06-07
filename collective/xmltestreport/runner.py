##############################################################################
#
# Copyright (c) 2004-2006 Zope Corporation and Contributors.
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
"""Test runner based on zope.testing.testrunner
"""

import sys
import optparse

from zope.testing.testrunner.runner import Runner
from zope.testing.testrunner.options import parser

from collective.xmltestreport.formatter import XMLOutputFormattingWrapper

# Set up XML output parsing

xmlOptions = optparse.OptionGroup(parser, "Generate XML test reports", "Support for JUnit style XML output")
xmlOptions.add_option(
    '--xml', action="store_true", dest='xmlOutput',
    help="""\
If given, XML reports will be written to the current directory. If you created
the testrunner using the buildout recipe provided by this package, this will
be in the buildout `parts` directroy, e.g. `parts/test`.
""")
parser.add_option_group(xmlOptions)

# Test runner and execution methods

class XMLAwareRunner(Runner):
    """Add output formatter delegate to the test runner before execution
    """
    
    def configure(self):
        super(XMLAwareRunner, self).configure()
        self.options.output = XMLOutputFormattingWrapper(self.options.output)

def run(defaults=None, args=None, script_parts=None):
    """Main runner function which can be and is being used from main programs.

    Will execute the tests and exit the process according to the test result.

    """
    failed = run_internal(defaults, args, script_parts=script_parts)
    sys.exit(int(failed))

def run_internal(defaults=None, args=None, script_parts=None):
    """Execute tests.

    Returns whether errors or failures occured during testing.

    """
    
    try:
        runner = XMLAwareRunner(defaults, args, script_parts=script_parts)
    except TypeError: # zope.testing <= 3.7
        runner = XMLAwareRunner(defaults, args)
    
    runner.run()
    
    # Write XML file of results if -x option is given
    if runner.options.xmlOutput:
        runner.options.output.writeXMLReports()
    
    return runner.failed
