# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import Layer
from plone.testing import z2
from zope.configuration import xmlconfig

import docker
import os
import sys
import time


__author__ = 'Md Nazrul Islam<email2nazrul@zitelab.dk>'

TEST_ZCML = """\
<configure
    xmlns="http://namespaces.zope.org/zope">
    <include package="plone.app.fhirfield.tests.fhir_rest_service" />
</configure>
"""
IS_TRAVIS = 'TRAVIS' in os.environ


class BaseDockerImage(object):
    """Docker based Service image base class"""
    docker_api_version = '1.37'
    name = None
    image = None
    port = None
    host = ''
    base_image_options = dict(
        cap_add=['IPC_LOCK'],
        mem_limit='1g',
        environment={},
        privileged=True,
        detach=True,
        publish_all_ports=True)

    def get_image_options(self):
        image_options = self.base_image_options.copy()
        return image_options

    def get_port(self):
        if api.env.test_mode():
            return self.port
        for port in self.container_obj.attrs['NetworkSettings']['Ports'].keys():
            if port == '6543/tcp':
                continue
            return self.container_obj.attrs['NetworkSettings']['Ports'][port][0]['HostPort']

    def get_host(self):
        if not self.host:
            return self.container_obj.attrs['NetworkSettings']['IPAddress']

        return self.host

    def check(self):
        return True

    def run(self):
        docker_client = docker.from_env(version=self.docker_api_version)
        # Create a new one
        container = docker_client.containers.run(
            image=self.image,
            **self.get_image_options()   # noqa: C815
        )
        ident = container.id
        count = 1

        self.container_obj = docker_client.containers.get(ident)

        opened = False
        sys.stdout.write('\n****** Starting {0}\n'.format(self.name))
        progress = '...'
        sys.stdout.write(progress + '\n')
        while count < 30 and not opened:
            if count > 0:
                time.sleep(1)
            count += 1
            try:
                self.container_obj = docker_client.containers.get(ident)
            except docker.errors.NotFound:
                sys.stdout.write('Container not found for {0}'.format(self.name))
                continue
            if self.container_obj.status == 'exited':
                logs = self.container_obj.logs()
                self.stop()
                raise Exception('Container failed to start {0}'.format(logs))

            if self.container_obj.attrs['NetworkSettings']['IPAddress'] != '':
                self.host = '127.0.0.1'

            if self.host != '':
                opened = self.check()
            progress += '...'
            sys.stdout.write(progress + '\n')

        if not opened:
            logs = self.container_obj.logs()
            self.stop()
            raise Exception('Could not start {0}: {1}'.format(self.name, logs))
        sys.stdout.write('{0} has been started ******\n'.format(self.name))
        return self.host, self.get_port()

    def stop(self):
        if self.container_obj is not None:
            try:
                self.container_obj.kill()
            except docker.errors.APIError:
                pass
            try:
                self.container_obj.remove(v=True, force=True)
            except docker.errors.APIError:
                pass


class Elasticsearch(BaseDockerImage):
    name = 'elasticsearch_ff'
    image = 'elasticsearch:2.4.6'
    port = 9200

    def get_image_options(self):
        image_options = super(Elasticsearch, self).get_image_options()
        image_options.update(dict(
            environment={},
            ports={
                '{0}/tcp'.format(self.port): ('127.0.0.1', self.port),
            },
        ))
        return image_options

    def check(self):
        import requests
        try:
            res = requests.get('http://{0}:{1}'.format(self.get_host(), self.get_port()), timeout=1)
            return res.status_code == 200
        except requests.RequestException:
            return False


ELASTICSEARCH_SERVER = Elasticsearch()


class ElasticsearchLayer(Layer):
    """Eleastic search server layer """
    def setUp(self):
        """Run the docker Elasticsearch Image"""
        ELASTICSEARCH_SERVER.run()

    def tearDown(self):
        """Let's clean up docker container """
        ELASTICSEARCH_SERVER.stop()


ELASTICSEARCH_SERVER_FIXTURE = ElasticsearchLayer()


class PloneAppFhirfieldLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configuration_context):  # noqa: N802
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)

        import z3c.form
        self.loadZCML(package=z3c.form)

        import plone.app.z3cform
        self.loadZCML(package=plone.app.z3cform)

        import collective.elasticsearch
        self.loadZCML(package=collective.elasticsearch)

        import plone.app.fhirfield
        self.loadZCML(package=plone.app.fhirfield)
        # initialize method not calling automatically
        z2.installProduct(app, 'plone.app.fhirfield')
        # Load Custom
        xmlconfig.string(TEST_ZCML, context=configuration_context)

    def setUpPloneSite(self, portal):  # noqa: N802

        setRoles(portal, TEST_USER_ID, ['Manager'])

        applyProfile(portal, 'plone.restapi:default')

        applyProfile(portal, 'collective.elasticsearch:default')

        applyProfile(portal, 'plone.app.fhirfield:default')

        # Apply Test profile
        applyProfile(portal, 'plone.app.fhirfield:testing')


PLONE_APP_FHIRFIELD_FIXTURE = PloneAppFhirfieldLayer()


PLONE_APP_FHIRFIELD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE,),
    name='PloneAppFhirfieldLayer:IntegrationTesting',
)

bases_ = ()
if not IS_TRAVIS:
    bases_ = (ELASTICSEARCH_SERVER_FIXTURE, )

PLONE_APP_FHIRFIELD_WITH_ES_INTEGRATION_TESTING = IntegrationTesting(
    bases=bases_ + (PLONE_APP_FHIRFIELD_FIXTURE, ),
    name='PloneAppFhirfieldLayer:WithElasticsearchIntegrationTesting',
)


PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneAppFhirfieldLayer:FunctionalTesting',
)

PLONE_APP_FHIRFIELD_WITH_ES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=bases_ + (PLONE_APP_FHIRFIELD_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneAppFhirfieldLayer:WithElasticsearchFunctionalTesting',
)

PLONE_APP_FHIRFIELD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_APP_FHIRFIELD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='PloneAppFhirfieldLayer:AcceptanceTesting',
)
