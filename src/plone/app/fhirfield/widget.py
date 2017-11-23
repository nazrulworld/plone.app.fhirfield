# _*_ coding: utf-8 _*_
from plone.app.fhirfield.helpers import parse_json_str
from plone.app.fhirfield.helpers import resource_type_str_to_fhir_model
from plone.app.fhirfield.interfaces import IFhirResource
from plone.app.fhirfield.interfaces import IFhirResourceValue
from plone.app.fhirfield.value import FhirResourceValue
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextAreaWidget
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


@adapter(IFhirResource, IFormLayer)
@implementer(IFieldWidget)
def FhirResourceFieldWidget(field, request):
    """IFieldWidget factory for FhirResourceWidget."""
    return FieldWidget(field, FhirResourceWidget(request))


class FhirResourceConverter(BaseDataConverter):
    """Data converter for the FhirResourceWidget
    """
    def fhir_resource_from_dict(self, dict_value):
        """ """
        try:
            model = resource_type_str_to_fhir_model(dict_value['resourceType'])
        except KeyError:
            raise ValueError('Invalid Fhir JSON String is provided! Resource type is missing')
        else:
            return FhirResourceValue(
                raw=model(dict_value),
                encoding='utf-8',
            )

    def toWidgetValue(self, value):
        if IFhirResourceValue.providedBy(value):
            return value
        elif isinstance(value, six.string_types):
            json_dict = parse_json_str(value)
            return self.fhir_resource_from_dict(json_dict)
        elif value is None:
            return None
        raise ValueError(
            'Can not convert {0:s} to an IFhirResourceValue'.format(repr(value))
        )

    def toFieldValue(self, value):
        """ """
        if IFhirResourceValue.providedBy(value):
            return value
        elif isinstance(value, six.string_types):
            return self.field.fromUnicode(value)
        raise ValueError(
            'Can not convert {0:s} to an IFhirResourceValue'.format(repr(value))
        )


class FhirResourceAreaConverter(BaseDataConverter):
    """Data converter for the original z3cform TextWidget

    This converter ignores the fact allowed_mime_types might be set,
    because the widget has no way to select it.
    It always assumes the default_mime_type was used.
    """
    def fhir_resource_from_dict(self, dict_value):
        """ """
        try:
            model = resource_type_str_to_fhir_model(dict_value['resourceType'])
        except KeyError:
            raise ValueError('Invalid Fhir JSON String is provided! Resource type is missing')
        else:
            return FhirResourceValue(
                raw=model(dict_value),
                encoding='utf-8',
            )

    def toWidgetValue(self, value):
        """ """
        if IFhirResourceValue.providedBy(value):
            if value:
                if self.widget.mode in ('input', 'hidden'):
                    return value.stringfy()
                elif self.widget.mode == 'display':
                    return value.stringfy()
            else:
                return None

        if isinstance(value, six.string_types):
            return value

        elif value is None:
            return None

        raise ValueError(
            'Can not convert {0:s} to unicode'.format(repr(value))
        )

    def toFieldValue(self, value):
        """ """
        if not value:
            return None
        elif isinstance(value, six.string_types):
            json_dict = parse_json_str(value)

            return self.fhir_resource_from_dict(json_dict)

        raise ValueError(
            'Can not convert {0:s} to an FhirResourceValue'.format(repr(value))
        )
