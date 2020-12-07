# -*- coding: utf-8 -*-
"""Installer for the plone.app.fhirfield package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("MIGRATION.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)

install_requires = ["setuptools", "jsonpatch", "fhirpath>=0.7.1"]
test_requires = [
    "plone.restapi",
    "plone.schemaeditor",
    "plone.supermodel",
    "plone.app.testing",
    "plone.testing>=7.0.1",
    "plone.app.contenttypes",
    "plone.app.robotframework[debug]",
    "collective.MockMailHost",
    "Products.contentmigration",
    "requests",
    "flake8-bugbear"
]

setup(
    name="plone.app.fhirfield",
    version="4.2.0",
    description="FHIR field for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Programming Language :: Python :: 3.9",
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
    python_requires=">=3.6",
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        "test": test_requires
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
