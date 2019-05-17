Migration
=========

1.0.0 to 2.0.0
--------------

1. Simply old indexes are not usable any more! as new ES server (6.x.x) is used.
2. Do backup of your existing Data.fs (important!).
3. From plone controlpanel, Go to elasticsearch settings page ``/@@elastic-controlpanel``.
4. Convert Catalog again, make sure in the ``Indexes for which all searches are done through ElasticSearch`` section
   your desired indexes are select.
5. If your site is behind the proxy, we suggest make `ssh tuneling to connect <https://www.ssh.com/ssh/tunneling/example>`_ your site.
   Because next takes much times, (depends on your data size)
6. Rebuild Catalog && wait for success, if you face any problem try again.


1.0.0rc3 to 1.0.0rc4
--------------------

1. Keep backup of existing Data.fs (nice to have)

2. Go to plone control panel's Addon settings

3. Uninstall and Install again `plone.app.fhirfield`

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
