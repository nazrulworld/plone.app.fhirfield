# -*- coding: utf-8 -*-
""" """
from plone.app.fhirfield import patch  # noqa: I001

from .field import FhirResource  # noqa: I001,F401
from .widget import FhirResourceWidget  # noqa: I001,F401


patch.monkey_patch_fhir_base_model()  # noqa: I003


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"
