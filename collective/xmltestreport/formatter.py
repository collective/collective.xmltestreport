import os
import sys
import socket
import datetime
import traceback

from elementtree import ElementTree

from collective.xmltestreport.utils import prettyXML

from zope.testing.doctest import DocTestCase

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
    
    def __init__(self, test, time, testClassName, testName, failure=None, error=None):
        self.test = test
        self.time = time
        self.testClassName = testClassName
        self.testName = testName
        self.failure = failure
        self.error = error

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
    
    def _record(self, test, seconds, failure=None, error=None):
        testClassName = "%s.%s" % (test.__module__, test.__class__.__name__,)
        testId = test.id()
        
        # Is this a doctest?
        if isinstance(test, DocTestCase):
            # Attempt to calculate a suite name and pseudo class name based on the filename
            filepath = os.path.realpath(test._dt_test.filename)
            filedir = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            suiteName = filename
            mod = [module for name, module in sys.modules.items() if "%s/__init__" % filedir in str(module)]
            if len(mod) > 0:
               suiteName = mod[0].__name__
            testSuite = '%s-doctest' % suiteName
            testName = test._dt_test.name
            testClassName = suiteName
               
        else:
            testSuite = testClassName
            testName = testId[len(testClassName)+1:]

        suite = self._testSuites.setdefault(testSuite, TestSuiteInfo())
        suite.testCases.append(TestCaseInfo(test, seconds, testClassName, testName, failure, error))
        
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
            outputFile.write(prettyXML(testSuiteNode))
            outputFile.close()
