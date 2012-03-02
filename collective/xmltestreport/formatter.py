import datetime
import doctest
import os
import os.path
import socket
import sys
import traceback

from zope.testrunner.find import StartUpFailure

try:
    # Python >= 2.5
    from xml.etree import ElementTree
except ImportError:
    # Python < 2.5
    from elementtree import ElementTree

from collective.xmltestreport.utils import prettyXML

try:
    import manuel.testing
    HAVE_MANUEL = True
except ImportError:
    HAVE_MANUEL = False


class TestSuiteInfo(object):

    def __init__(self):
        self.testCases = []
        self.errors = 0
        self.failures = 0
        self.time = 0.0

    @property
    def tests(self):
        return len(self.testCases)

    @property
    def successes(self):
        return self.tests - (self.errors + self.failures)


class TestCaseInfo(object):

    def __init__(self, test, time, testClassName, testName, failure=None,
                 error=None):
        self.test = test
        self.time = time
        self.testClassName = testClassName
        self.testName = testName
        self.failure = failure
        self.error = error

def get_test_class_name(test):
    """Compute the test class name from the test object."""
    return "%s.%s" % (test.__module__, test.__class__.__name__, )


def filename_to_suite_name_parts(filename):
    #the module is loaded so we try to get name from sys.modules
    filepath = os.path.realpath(filename)
    filedir = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    mod = [module for name, module in sys.modules.items() if "%s/__init__" % filedir in str(module)]
    if len(mod) > 0:
        suiteName = mod[0].__name__
	return [suiteName]

    # XXX is this code still needed!?
    # lop off whatever portion of the path we have in common
    # with the current working directory; crude, but about as
    # much as we can do :(

    filenameParts = filename.split(os.path.sep)
    cwdParts = os.getcwd().split(os.path.sep)
    longest = min(len(filenameParts), len(cwdParts))
    for i in range(longest):
        if filenameParts[i] != cwdParts[i]:
            break

    if i < len(filenameParts) - 1:

        # The real package name couldn't have a '.' in it. This
        # makes sense for the common egg naming patterns, and
        # will still work in other cases

        suiteNameParts = []
        for part in reversed(filenameParts[i:-1]):
            if '.' in part:
                break
            suiteNameParts.insert(0, part)

        # don't lose the filename, which would have a . in it
        suiteNameParts.append(filenameParts[-1])
        return suiteNameParts
    # ok too hard we cant find anything but at least we return something
    return ['unknown']


def parse_doc_file_case(test):
    if not isinstance(test, doctest.DocFileCase):
        return None, None, None

    filename = test._dt_test.filename
    suiteNameParts = filename_to_suite_name_parts(filename)
    testSuite = 'doctest-' + '-'.join(suiteNameParts)
    testName = test._dt_test.name
    testClassName = '.'.join(suiteNameParts[:-1])
    return testSuite, testName, testClassName


def parse_doc_test_case(test):
    if not isinstance(test, doctest.DocTestCase):
        return None, None, None

    testDottedNameParts = test._dt_test.name.split('.')
    testClassName = get_test_class_name(test)
    testSuite = testClassName = '.'.join(testDottedNameParts[:-1])
    testName = testDottedNameParts[-1]
    return testSuite, testName, testClassName


def parse_manuel(test):
    if not (HAVE_MANUEL and isinstance(test, manuel.testing.TestCase)):
        return None, None, None
    filename = test.regions.location
    suiteNameParts = filename_to_suite_name_parts(filename)
    testSuite = 'manuel-' + '-'.join(suiteNameParts)
    testName = suiteNameParts[-1]
    testClassName = '.'.join(suiteNameParts[:-1])
    return testSuite, testName, testClassName


def parse_startup_failure(test):
    if not isinstance(test, StartUpFailure):
        return None, None, None
    testModuleName = test.module
    return testModuleName, 'Startup', testModuleName


def parse_unittest(test):
    testId = test.id()
    if testId is None:
        return None, None, None
    testClassName = get_test_class_name(test)
    testSuite = testClassName
    testName = testId[len(testClassName)+1:]
    return testSuite, testName, testClassName


class XMLOutputFormattingWrapper(object):
    """Output formatter which delegates to another formatter for all
    operations, but also prepares an element tree of test output.
    """

    def __init__(self, options):
        self.delegate = options.output
        self._testSuites = {} # test class -> list of test names
        self.testresult_dir = os.getcwd()
        if options.testresult_dir:
            self.testresult_dir = options.testresult_dir 

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def test_failure(self, test, seconds, exc_info):
        self._record(test, seconds, failure=exc_info)
        return self.delegate.test_failure(test, seconds, exc_info)

    def test_error(self, test, seconds, exc_info):
        self._record(test, seconds, error=exc_info)
        return self.delegate.test_error(test, seconds, exc_info)

    def test_success(self, test, seconds):
        self._record(test, seconds)
        return self.delegate.test_success(test, seconds)

    def import_errors(self, import_errors):
        if import_errors:
            for test in import_errors:
                self._record(test, 0, error=test.exc_info)
        return self.delegate.import_errors(import_errors)

    def _record(self, test, seconds, failure=None, error=None):
        try:
            os.getcwd()
        except OSError:
            # In case the current directory is no longer available fallback to
            # the default working directory.
            os.chdir(self.testresult_dir)

        for parser in [parse_doc_file_case,
                       parse_doc_test_case,
                       parse_manuel,
                       parse_startup_failure,
                       parse_unittest]:
            testSuite, testName, testClassName = parser(test)
            if (testSuite, testName, testClassName) != (None, None, None):
                break

        if (testSuite, testName, testClassName) == (None, None, None):
            raise TypeError(
                "Unknown test type: Could not compute testSuite, testName, "
                "testClassName: %r" % test)

        suite = self._testSuites.setdefault(testSuite, TestSuiteInfo())
        suite.testCases.append(TestCaseInfo(
            test, seconds, testClassName, testName, failure, error))

        if failure is not None:
            suite.failures += 1

        if error is not None:
            suite.errors += 1

        if seconds:
            suite.time += seconds

    def writeXMLReports(self, properties={}):

        timestamp = datetime.datetime.now().isoformat()
        hostname = socket.gethostname()

        workingDir = self.testresult_dir
        reportsDir = os.path.join(workingDir, 'testreports')
        if not os.path.exists(reportsDir):
            os.mkdir(reportsDir)

        for name, suite in self._testSuites.items():
            filename = os.path.join(reportsDir, name + '.xml')

            testSuiteNode = ElementTree.Element('testsuite')

            testSuiteNode.set('tests', str(suite.tests))
            testSuiteNode.set('errors', str(suite.errors))
            testSuiteNode.set('failures', str(suite.failures))
            testSuiteNode.set('hostname', hostname)
            testSuiteNode.set('name', name)
            testSuiteNode.set('time', str(suite.time))
            testSuiteNode.set('timestamp', timestamp)

            propertiesNode = ElementTree.Element('properties')
            testSuiteNode.append(propertiesNode)

            for k, v in properties.items():
                propertyNode = ElementTree.Element('property')
                propertiesNode.append(propertyNode)

                propertyNode.set('name', k)
                propertyNode.set('value', v)

            for testCase in suite.testCases:
                testCaseNode = ElementTree.Element('testcase')
                testSuiteNode.append(testCaseNode)

                testCaseNode.set('classname', testCase.testClassName)
                testCaseNode.set('name', testCase.testName)
                testCaseNode.set('time', str(testCase.time))

                if testCase.error:
                    errorNode = ElementTree.Element('error')
                    testCaseNode.append(errorNode)

                    try:
                        excType, excInstance, tb = testCase.error
                        errorMessage = str(excInstance)
                        stackTrace = ''.join(traceback.format_tb(tb))
                    finally: # Avoids a memory leak
                        del tb

                    errorNode.set('message', errorMessage.split('\n')[0])
                    errorNode.set('type', str(excType))
                    errorNode.text = errorMessage + '\n\n' + stackTrace

                if testCase.failure:

                    failureNode = ElementTree.Element('failure')
                    testCaseNode.append(failureNode)

                    try:
                        excType, excInstance, tb = testCase.failure
                        errorMessage = str(excInstance)
                        stackTrace = ''.join(traceback.format_tb(tb))
                    except UnicodeEncodeError:
                        errorMessage = 'Could not extract error str for unicode error'
                        stackTrace = ''.join(traceback.format_tb(tb))
                    finally: # Avoids a memory leak
                        del tb

                    failureNode.set('message', errorMessage.split('\n')[0])
                    failureNode.set('type', str(excType))
                    failureNode.text = errorMessage + '\n\n' + stackTrace

            # XXX: We don't have a good way to capture these yet
            systemOutNode = ElementTree.Element('system-out')
            testSuiteNode.append(systemOutNode)
            systemErrNode = ElementTree.Element('system-err')
            testSuiteNode.append(systemErrNode)

            # Write file
            outputFile = open(filename, 'w')
            outputFile.write(prettyXML(testSuiteNode).decode('utf-8'))
            outputFile.close()
