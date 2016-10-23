import doctest
import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('coverage', test)


def test_suite():
    ret = doctest.DocFileSuite(
        'TESTDOC.txt',
        setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
        doctest.REPORT_UDIFF)
    return ret
