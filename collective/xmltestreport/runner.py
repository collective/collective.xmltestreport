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
# Addendum: This recipe merges collective.xmltestreport and 
# tranchitella.recipe.testrunner 
#
##############################################################################
"""Test runner based on zope.testing.testrunner
"""

import sys
import optparse

from zope.testing.testrunner.runner import Runner
from zope.testing.testrunner.options import parser

from collective.xmltestreport.formatter import XMLOutputFormattingWrapper
from coverage import coverage
import zope.testing.testrunner.options

# add the --coverage-annotate option
zope.testing.testrunner.options.analysis.add_option(
     '--coverage-annotate', action="store", metavar='PATH',
    dest='coverage_annotate',
    help="""Store coverage annotation in the specified directorz.""")
# add the --coverage-branch option
zope.testing.testrunner.options.analysis.add_option(
     '--coverage-branch', action="store_true",
    dest='coverage_branch', help="""Enable branch coverage.""")
# add the --coverage-module option
zope.testing.testrunner.options.analysis.add_option(
     '--coverage-module', action="append", type='string',
    dest='coverage_modules', metavar="MODULE",
    help="Perform code-coverage analysis for the given module using "
        "the coverage library.")
# add the --coverage-xml option
zope.testing.testrunner.options.analysis.add_option(
     '--coverage-xml', action="store_true",
    dest='coverage_xml', help="""Enable XML coverage report.""")

# Set up XML output parsing
xmlOptions = optparse.OptionGroup(parser, "Generate XML test reports", "Support for JUnit style XML output")
xmlOptions.add_option(
    '--testresult-dir', action="store", metavar='PATH', dest='testresult_dir', help="Testresult directory")
xmlOptions.add_option(
    '-x', action="store_true", dest='xmlOutput',
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
        self.options.output = XMLOutputFormattingWrapper(self.options)

def run(defaults=None, args=None, script_parts=None):
    """Main runner function which can be and is being used from main programs.

    Will execute the tests and exit the process according to the test result.

    """
    import os
    options = zope.testing.testrunner.options.get_options(args, defaults)
    testresult_dir = os.getcwd()

    if options.testresult_dir:
        testresult_dir = options.testresult_dir 
    if not os.path.exists(testresult_dir):
        os.mkdir(testresult_dir)
    # coverage support
    if options.coverage_modules:
        cover = coverage(branch=options.coverage_branch)
        cover.exclude('#pragma[: ]+[nN][oO] [cC][oO][vV][eE][rR]')
        cover.start()
    # test runner
    failed = run_internal(defaults, args, script_parts)

    # coverage report
    if options.coverage_modules:
        cover.stop()
        cover.save()
        modules = [module for name, module in sys.modules.items()
            if with_coverage(name, module, options.coverage_modules)]
        print "\nCoverage report\n===============\n"
        
        cover.report(modules)
        if options.coverage_xml:
            #thanks to nosexcover for this part
            morfs = [ m.__file__ for m in modules if hasattr(m, '__file__') ]
            cover.xml_report(morfs, outfile=os.path.join(testresult_dir, 'testreports', 'coverage.xml'))
        if options.coverage_annotate:
            cover.annotate(morfs=modules,
                directory=options.coverage_annotate)
    # return code
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

def with_coverage(name, module, modules):
    if hasattr(module, '__file__'):
        for m in modules:
            if name.startswith(m):
                return True
    return False
