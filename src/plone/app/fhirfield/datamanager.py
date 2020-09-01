# _*_ coding: utf-8 _*_
from plone.dexterity.interfaces import IDexterityContent
from z3c.form.datamanager import AttributeField
from zope.component import adapter

from .interfaces import IFhirResource


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


@adapter(IDexterityContent, IFhirResource)
class FhirAttributeField(AttributeField):
    """ """

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        return self.field.get(self.adapted_context)

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        self.field.set(self.adapted_context, value)
