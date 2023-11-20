# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '2.0.3.dev0'

requires = [
    'setuptools',
    'six',
    'zope.testing',
    'zope.testrunner',
    'zc.recipe.egg',
]



setup(
    name='collective.xmltestreport',
    version=version,
    description='A test runner which can output an XML report compatible '
    'with JUnit and Jenkins',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='jenkins junit xml zope.testing',
    author='Martin Aspeli',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/collective.xmltestreport',
    license='ZPL 2.1',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points="""
      [zc.buildout]
      default = collective.xmltestreport.recipe:TestRunner
      [console_scripts]
      xmltestreport = collective.xmltestreport.runner:run
      """,
)
