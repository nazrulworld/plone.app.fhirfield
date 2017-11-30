# -*- coding: utf-8 -*-
from plone.app.fhirfield import patch

__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'

patch.monkey_patch_fhir_base_model()

# Imports as API
from .field import FhirResource
from .widget import FhirResourceWidget