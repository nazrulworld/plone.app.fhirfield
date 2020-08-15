# -*- coding: utf-8 -*-

from z3c.form.error import ComputedErrorViewMessage
from z3c.form.error import ErrorViewDiscriminators
from z3c.form.error import ErrorViewSnippet
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema.interfaces import ValidationError

from .compat import json
from .field import FhirResource


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


def extract_error_message(computed_value):
    """ComputedValue"""
    return computed_value.error.args[0]


FhirFieldErrorMessage = ComputedErrorViewMessage(
    extract_error_message, error=ValidationError, field=FhirResource
)


class FhirFieldErrorViewSnippet(ErrorViewSnippet):
    """ """

    template = ViewPageTemplateFile("templates/error/error.pt")

    def jsonize(self, value, indent=2):
        """ """
        return json.dumps(value, indent=indent)

    def required_jsonization(self, value):
        """ """
        return isinstance(value, (list, tuple, dict))

    def render(self):
        """ """
        return self.template(self)


# We now need to assert the special discriminators specific to this view:
ErrorViewDiscriminators(
    FhirFieldErrorViewSnippet, error=ValidationError, field=FhirResource
)
