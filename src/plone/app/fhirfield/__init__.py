# -*- coding: utf-8 -*-
from plone.app.fhirfield import patch


patch.monkey_patch_fhir_base_model()

__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


# IMPORTS as API

from .field import FhirResource  # noqa: I001,F401
from .widget import FhirResourceWidget  # noqa: I001,F401
# DONE
