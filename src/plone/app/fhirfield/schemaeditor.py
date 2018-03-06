# _*_ coding: utf-8 _*_
from plone import api
from plone.app.fhirfield import field
from plone.app.fhirfield import interfaces
from plone.app.fhirfield.compat import _
from plone.schemaeditor.fields import FieldFactory

import logging


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'

logger = logging.getLogger('plone.app.fhirfield')

# Patch: for plone 5.x
if api.env.plone_version().startswith('5'):
    import plone.app.dexterity.browser.types as padbt
    padbt.ALLOWED_FIELDS.append(u'plone.app.fhirfield.field.FhirResource')
    logger.info(
                'schemaeditor: patch done! `plone.app.fhirfield.field.FhirResource` is added in whitelist\n'
                'Location: plone.app.dexterity.browser.types.ALLOWED_FIELDS',
            )


class IFhirResource(interfaces.IFhirResource):
    """ """


FhirResourceFieldFactory = FieldFactory(field.FhirResource, _(u'FHIR Resource Field'))
