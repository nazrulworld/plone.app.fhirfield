# -*- coding: utf-8 -*-
"""Installer for the plone.app.fhirfield package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("MIGRATION.rst").read(),
        open("SEARCH.rst").read(),
        open("RESTAPI.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)

install_requires = ["setuptools", "jsonpatch"]
elasticsearch_requires = ["collective.elasticsearch>=3.0.4"]
fhirpath_requires = ["collective.fhirpath"]
test_requires = [
    "plone.restapi",
    "plone.schemaeditor",
    "plone.supermodel",
    "plone.app.testing",
    "plone.testing>=5.0.0",
    "plone.app.contenttypes",
    "plone.app.robotframework[debug]",
    "collective.MockMailHost",
    "Products.contentmigration",
    "requests",
]

setup(
    name="plone.app.fhirfield",
    version="3.0.0b1",
    description="FHIR field for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 5.3",
        "Framework :: Plone :: Addon",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone Zope FHIR Field",
    author="Md Nazrul Islam",
    author_email="email2nazrul@gmail.com",
    url="https://pypi.org/project/plone.app.fhirfield/",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["plone", "plone.app"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        "test": test_requires + elasticsearch_requires,
        "elasticsearch": elasticsearch_requires,
        "fhirpath": fhirpath_requires
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
