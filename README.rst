Introduction
============

This recipe is a merge of ``collective.xmltestreport`` and 
``tranchitella.recipe.testrunner``. It provides XML output for test and 
coverage report.

This package provides an extension to the test runner to the one that ships
with ``zope.testrunner``, as well as a buildout recipe based on
``zc.recipe.testrunner`` to install a test script for this test runner.

The test runner is identical to the one in ``zope.testrunner``, but it is
capable of writing test reports in the XML format output by JUnit/Ant. This
allows the test results to be analysed by tools such as the Jenkins continuous
integration server.

It also replaces the builtin coverage module from ``zope.testing`` with Ned 
Batchelder's. With this replacement it is also possible to write XML, HTML 
output.

Code repository
===============

https://github.com/collective/collective.xmltestreport

.. |travisci| image::  https://travis-ci.org/lugensa/collective.xmltestreport.png
.. _travisci: https://travis-ci.org/lugensa/collective.xmltestreport

|travisci|_

Usage
=====

In your buildout, add a part like this::

    [buildout]
    parts =
        ...
        test

    ...

    [test]
    recipe = collective.xmltestreport
    eggs =
        my.package
    defaults = ['--auto-color', '--auto-progress', '--coverage-xml', '--coverage-branch']

The recipe accepts the same options as zc.recipe.testrunner, so look at its
documentation for details.

When buildout is run, you should have a script in ``bin/test`` and a directory
``parts/test``.

To run the tests, use the ``bin/test`` script. If you pass the ``--xml``
option, test reports will be written to ``parts/test/testreports`` directory::

    $ bin/test --xml -s my.package --coverage-module my.package

Use ``bin/test --help`` for a full list of options.

If you are using Jenkins, you can now configure the build to publish JUnit
test reports for ``<buildoutdir>/parts/test/testreports/*.xml`` and ``<buildoutdir>/parts/test/testreports/coverage.xml``.
