#!/usr/bin/env python

# Copyright (c) 2017 Ericsson and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""
OpenStack deployment checker

Verifies that:
 - Credentials file is given and contains the right information
 - OpenStack endpoints are reachable
"""

import logging
import logging.config
import os
import pkg_resources
import socket
from urlparse import urlparse

from snaps.openstack.utils import glance_utils
from snaps.openstack.utils import keystone_utils
from snaps.openstack.utils import neutron_utils
from snaps.openstack.utils import nova_utils
from snaps.openstack.tests import openstack_tests

__author__ = "Jose Lausuch <jose.lausuch@ericsson.com>"

LOGGER = logging.getLogger(__name__)


def verify_connectivity(adress, port):
    """ Returns true if an ip/port is reachable"""
    connection = socket.socket()
    connection.settimeout(10)
    try:
        connection.connect((adress, port))
        LOGGER.debug('%s:%s is reachable!', adress, port)
        return True
    except socket.error:
        LOGGER.error('%s:%s is not reachable.', adress, port)
    return False


class CheckDeployment(object):
    """ Check deployment class."""

    def __init__(self, rc_file='/home/opnfv/functest/conf/openstack.creds'):
        self.rc_file = rc_file
        self.services = ('compute', 'network', 'image')
        self.os_creds = None

    def check_rc(self):
        """ Check if RC file exists and contains OS_AUTH_URL """
        if not os.path.isfile(self.rc_file):
            raise IOError('RC file {} does not exist!'.format(self.rc_file))
        if 'OS_AUTH_URL' not in open(self.rc_file).read():
            raise SyntaxError('OS_AUTH_URL not defined in {}.'.
                              format(self.rc_file))

    def check_auth_endpoint(self):
        """ Verifies connectivity to the OS_AUTH_URL given in the RC file """
        rc_endpoint = self.os_creds.auth_url
        if not (verify_connectivity(urlparse(rc_endpoint).hostname,
                                    urlparse(rc_endpoint).port)):
            raise Exception("OS_AUTH_URL {} is not reachable.".
                            format(rc_endpoint))
        LOGGER.info("Connectivity to OS_AUTH_URL %s ...OK", rc_endpoint)

    def check_public_endpoint(self):
        """ Gets the public endpoint and verifies connectivity to it """
        public_endpoint = keystone_utils.get_endpoint(self.os_creds,
                                                      'identity',
                                                      interface='public')
        if not (verify_connectivity(urlparse(public_endpoint).hostname,
                                    urlparse(public_endpoint).port)):
            raise Exception("Public endpoint {} is not reachable.".
                            format(public_endpoint))
        LOGGER.info("Connectivity to the public endpoint %s ...OK",
                    public_endpoint)

    def check_service_endpoint(self, service):
        """ Verifies connectivity to a given openstack service """
        endpoint = keystone_utils.get_endpoint(self.os_creds,
                                               service,
                                               interface='public')
        if not (verify_connectivity(urlparse(endpoint).hostname,
                                    urlparse(endpoint).port)):
            raise Exception("{} endpoint {} is not reachable.".
                            format(service, endpoint))
        LOGGER.info("Connectivity to endpoint '%s' %s ...OK",
                    service, endpoint)

    def check_nova(self):
        """ checks that a simple nova operation works """
        try:
            client = nova_utils.nova_client(self.os_creds)
            client.servers.list()
            LOGGER.info("Nova service ...OK")
        except Exception as error:
            LOGGER.error("Nova service ...FAILED")
            raise error

    def check_neutron(self):
        """ checks that a simple neutron operation works """
        try:
            client = neutron_utils.neutron_client(self.os_creds)
            client.list_networks()
            LOGGER.info("Neutron service ...OK")
        except Exception as error:
            LOGGER.error("Neutron service ...FAILED")
            raise error

    def check_glance(self):
        """ checks that a simple glance operation works """
        try:
            client = glance_utils.glance_client(self.os_creds)
            client.images.list()
            LOGGER.info("Glance service ...OK")
        except Exception as error:
            LOGGER.error("Glance service ...FAILED")
            raise error

    def check_all(self):
        """
        Calls all the class functions and returns 0 if all of them succeed.
        This is the method called by prepare_env or CLI
        """
        self.check_rc()
        try:
            self.os_creds = openstack_tests.get_credentials(
                os_env_file=self.rc_file,
                proxy_settings_str=None,
                ssh_proxy_cmd=None)
        except:
            raise Exception("Problem while getting credentials object.")
        if self.os_creds is None:
            raise Exception("Credentials is None.")
        self.check_auth_endpoint()
        self.check_public_endpoint()
        for service in self.services:
            self.check_service_endpoint(service)
        self.check_nova()
        self.check_neutron()
        self.check_glance()
        return 0


def main():
    """Entry point"""
    logging.config.fileConfig(pkg_resources.resource_filename(
        'functest', 'ci/logging.ini'))
    logging.captureWarnings(True)
    deployment = CheckDeployment()
    return deployment.check_all()
