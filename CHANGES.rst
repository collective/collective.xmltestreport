Changelog
=========

2.0.1 (unreleased)
------------------

Bug fixes:

- Fix ``environment`` option. The ``key`` was used as the ``value``.


2.0.0 (2018-10-31)
------------------

Breaking changes:

- Add compatibility with Python 2 and Python 3.
  [gforcada]

- Switch from optparse to argparse to work with zope.testrunner >= 4.9.0
  [pbauer]
- Drop python 2.6 dependency.
  [gforcada]

Bug fixes:

- Clean up the code.
  [gforcada]

1.3.4 (2017-02-02)
------------------

Fixes:

- Fixed UnicodeDecodeError when error message contains non-ascii.
  Fixes https://github.com/collective/collective.xmltestreport/issues/16
  [maurits]


1.3.3 (2015-09-09)
------------------

- Dependency to z3c.recipe.scripts declared but it was nowhere used.
  Removed dependency. This makes it work with newer zc.buildout again.
  Fixes #10
  [jensens]


1.3.2 (2015-04-25)
------------------

- Fix error on utf-8 error string.
  [bloodbare]

- Fix encoding problem in python 3.
  [cedricmessiant]


1.3.1 (2013-10-03)
------------------

- Make sure errors in layer teardown don't prevent the test report from
  getting written.
  [davisagli]


1.3.0 (2013-04-29)
------------------

- Revert "Exclude system site-packages from tests' sys.path". This commit
  changed the API/output of collective.xmltestreport in a minor version without
  mentioning. This essentially broke all Jenkins jobs out there including all
  Plone coredev jobs and all the packages/code that relies on that output.
  [timo]


1.2.8 (2012-08-19)
------------------

- Add missing dependency to z3c.recipe.scripts
  [ggozad]


1.2.7 (2012-08-19)
------------------

- Exclude system site-packages from tests' sys.path'
  [Andrey Lebedev]


1.2.6 (2012-06-06)
------------------

- Fix import errors problem (TypeError) introduced in 1.2.5.
  [jone]


1.2.5 (2012-06-06)
------------------

- Handle startup failures (import errors) and expose them in the testresults.
  [jone]


1.2.4 (2011-12-04)
------------------

- Fix brown-bag release 1.2.3 that was missing CHANGES.txt etc.


1.2.3 (2011-12-02)
------------------

- Only depend on `elementtree` for Python < 2.5.


1.2.2 (2011-05-30)
------------------

- Fixed ``OSError`` in formatter which could occur when a test case modifies
  the current working directory to a directory that gets removed during the
  test. In such cases we fall back to the working directory as it was in the
  beginning of the tests.
  [dokai]


1.2.1 (2011-02-03)
------------------

- Fixed ``IndexError`` in formatter which could occur when the path of the
  current working directory was part of the path + file name of the doctest
  file but shorter.


1.2 (2011-01-27)
----------------

- Added support for Manuel_ tests. It gets activated when the package under
  test has tests using `manuel` and this way depends on `manuel`.
  [icemac]

.. _Manuel: http://pypi.python.org/pypi/manuel


1.1 (2011-01-20)
----------------

- Require `zope.testrunner` and remove support for zope.testing 3.7.
  [hannosch]

- Added support for `zope.testrunner` while retaining support for the older
  `zope.testing.testrunner`.
  [hannosch]

- No longer use the deprecated `zope.testing.doctest`.
  [hannosch]

- Distribution metadata cleanup.
  [hannosch]

- Use built-in `xml.etree` in favor of `elementree` in Python 2.5+ and added
  missing dependency on `zc.recipe.egg`.
  [multani]

1.0b3 (2010-06-07)
------------------

* Rename the ``-x`` option ``--xml``. This is necessary by zope.testing now
  uses the ``-x`` option for something else. :-(

1.0b2 (2009-11-08)
------------------

* Maintain compatibility with zope.testing 3.7.

1.0b1 (2009-11-07)
------------------

* Initial release
