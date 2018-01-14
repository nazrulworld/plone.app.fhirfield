# _*_ coding: utf-8 _*_
from plone.app.fhirfield.interfaces import IFhirResourceModel

import os


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


BASE_TEST_PATH = os.path.dirname(os.path.abspath(__file__))
FHIR_FIXTURE_PATH = os.path.join(BASE_TEST_PATH, 'fixture', 'FHIR')


class IWrongInterface(IFhirResourceModel):
    """ """
    def meta():
        """ """


class NoneInterfaceClass(object):
    """docstring for ClassName"""
