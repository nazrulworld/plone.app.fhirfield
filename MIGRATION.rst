Migration
=========

1.0.0b6 to 1.0.0rc3
-------------------

1. Keep backup of existing Data.fs (important)

2. Just `Clear and Rebuild` existing catalogs. Go to site management -> portal_catalog -> Advanced Tab and click the `Clear and Rebuild` button. Caution: this activity could take longer time.


1.0.0bx to 1.0.0b6
------------------

1. You will need to remove all the indexes who are based on `Fhir*******Index`. Go to ZMI to portal catalog tool. `{site url}/portal_catalog/manage_catalogIndexes`.

2. Update the `plone.app.fhirfield` version and run the buildout.

3. List out any products those defined (profile/catalog.xml) indexes based on `Fhir*******Index` as meta type. Reninstall them all.

4. From ZMI, portal_catalog tool, `{site url}/portal_catalog/manage_catalogAdvanced` ``Clear and Rebuild``