from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='collective.xmltestreport',
      version=version,
      description="A test runner which can output an XML report compatible with JUnit and Hudson",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='hudson junit xml zope.testing',
      author='Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/collective.xmltestreport',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.testing',
          'elementtree',
      ],
      entry_points="""
      [zc.buildout]
      default = collective.xmltestreport.recipe:TestRunner
      """,
      )
