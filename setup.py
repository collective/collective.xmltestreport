from setuptools import setup, find_packages
import sys

version = '1.3.5.dev0'

requires = [
    'setuptools',
    'zope.testing',
    'zope.testrunner',
    'zc.recipe.egg',
]

if sys.version_info < (2, 5):
    # Starting from Python 2.5, the stdlib ships the `elementtree` package as
    # `xml.etree`.
    # So we need this dependency only if we have a too old (before 2.5) version
    # of Python.
    requires.append('elementtree')


setup(name='collective.xmltestreport',
      version=version,
      description="A test runner which can output an XML report compatible "
                  "with JUnit and Jenkins",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          ],
      keywords='jenkins junit xml zope.testing',
      author='Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.org/project/collective.xmltestreport',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      [zc.buildout]
      default = collective.xmltestreport.recipe:TestRunner
      """,
      )
