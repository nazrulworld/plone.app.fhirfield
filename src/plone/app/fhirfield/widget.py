# _*_ coding: utf-8 _*_
from plone.app.fhirfield.interfaces import IFhirResource
from plone.app.fhirfield.interfaces import IFhirResourceValue
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only

import six


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class IFhirResourceWidget(ITextAreaWidget):
    """ """


@implementer_only(IFhirResourceWidget)
class FhirResourceWidget(TextAreaWidget):

    klass = u'fhirResourceWidget'
    value = None

    def update(self):
        super(FhirResourceWidget, self).update()
        addFieldClass(self)

    def extract(self, default=NOVALUE):
        raw = self.request.get(self.name, default)
        return raw


@adapter(IFhirResource, IFormLayer)
@implementer(IFieldWidget)
def FhirResourceFieldWidget(field, request):
    """IFieldWidget factory for FhirResourceWidget."""
    return FieldWidget(field, FhirResourceWidget(request))


class FhirResourceConverter(BaseDataConverter):
    """Data converter for the FhirResourceWidget
    """

    def toWidgetValue(self, value):
        if IFhirResourceValue.providedBy(value):
            return value

        elif value in (NOVALUE, None, ''):
            return IFhirResource(self.field).from_none()

        elif isinstance(value, six.string_types):
            return IFhirResource(self.field).fromUnicode(value)

        raise ValueError(
            'Can not convert {0!s} to an IFhirResourceValue'.format(value),
        )

    def toFieldValue(self, value):
        """ """
        if IFhirResourceValue.providedBy(value):
            return value

        elif isinstance(value, six.string_types):
            return IFhirResource(self.field).fromUnicode(value)

        elif value in (NOVALUE, None, ''):
            return IFhirResource(self.field).from_none()

        raise ValueError(
            'Can not convert {0!s} to an IFhirResourceValue'.format(value),
        )


class FhirResourceAreaConverter(BaseDataConverter):
    """Data converter for the original z3cform TextWidget"""

    def toWidgetValue(self, value):
        """ """
        if value in (None, '', NOVALUE):
            return ''

        if IFhirResourceValue.providedBy(value):
            if self.widget.mode in ('input', 'hidden'):
                return value.stringify()
            elif self.widget.mode == 'display':
                return value.stringify()

        if isinstance(value, six.string_types):
            return value

        raise ValueError(
            'Can not convert {0:s} to unicode'.format(repr(value)),
        )

    def toFieldValue(self, value):
        """ """
        if IFhirResourceValue.providedBy(value):
            return value

        elif isinstance(value, six.string_types):
            return IFhirResource(self.field).fromUnicode(value)

        elif value in (NOVALUE, None, ''):
            return IFhirResource(self.field).from_none()

        raise ValueError(
            'Can not convert {0!r} to an IFhirResourceValue'.format(value),
        )
