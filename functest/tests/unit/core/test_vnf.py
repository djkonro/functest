#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
import unittest

import mock

from functest.core import vnf
from functest.core import testcase
from functest.utils import constants

from snaps.openstack.os_credentials import OSCreds


class VnfBaseTesting(unittest.TestCase):
    """The class testing VNF."""
    # pylint: disable=missing-docstring,too-many-public-methods

    tenant_name = 'test_tenant_name'
    tenant_description = 'description'

    def setUp(self):
        constants.CONST.__setattr__("vnf_foo_tenant_name", self.tenant_name)
        constants.CONST.__setattr__(
            "vnf_foo_tenant_description", self.tenant_description)
        self.test = vnf.VnfOnBoarding(project='functest', case_name='foo')

    def test_run_deploy_vnf_exc(self):
        with mock.patch.object(self.test, 'prepare'),\
            mock.patch.object(self.test, 'deploy_orchestrator',
                              return_value=None), \
            mock.patch.object(self.test, 'deploy_vnf',
                              side_effect=Exception):
            self.assertEqual(self.test.run(),
                             testcase.TestCase.EX_TESTCASE_FAILED)

    def test_run_test_vnf_exc(self):
        with mock.patch.object(self.test, 'prepare'),\
            mock.patch.object(self.test, 'deploy_orchestrator',
                              return_value=None), \
            mock.patch.object(self.test, 'deploy_vnf'), \
            mock.patch.object(self.test, 'test_vnf',
                              side_effect=Exception):
            self.assertEqual(self.test.run(),
                             testcase.TestCase.EX_TESTCASE_FAILED)

    def test_run_deploy_orch_ko(self):
        with mock.patch.object(self.test, 'prepare'),\
                mock.patch.object(self.test, 'deploy_orchestrator',
                                  return_value=False), \
                mock.patch.object(self.test, 'deploy_vnf',
                                  return_value=True), \
                mock.patch.object(self.test, 'test_vnf',
                                  return_value=True):
            self.assertEqual(self.test.run(),
                             testcase.TestCase.EX_TESTCASE_FAILED)

    def test_run_vnf_deploy_ko(self):
        with mock.patch.object(self.test, 'prepare'),\
                mock.patch.object(self.test, 'deploy_orchestrator',
                                  return_value=True), \
                mock.patch.object(self.test, 'deploy_vnf',
                                  return_value=False), \
                mock.patch.object(self.test, 'test_vnf',
                                  return_value=True):
            self.assertEqual(self.test.run(),
                             testcase.TestCase.EX_TESTCASE_FAILED)

    def test_run_vnf_test_ko(self):
        with mock.patch.object(self.test, 'prepare'),\
                mock.patch.object(self.test, 'deploy_orchestrator',
                                  return_value=True), \
                mock.patch.object(self.test, 'deploy_vnf',
                                  return_value=True), \
                mock.patch.object(self.test, 'test_vnf',
                                  return_value=False):
            self.assertEqual(self.test.run(),
                             testcase.TestCase.EX_TESTCASE_FAILED)

    def test_run_default(self):
        with mock.patch.object(self.test, 'prepare'),\
                mock.patch.object(self.test, 'deploy_orchestrator',
                                  return_value=True), \
                mock.patch.object(self.test, 'deploy_vnf',
                                  return_value=True), \
                mock.patch.object(self.test, 'test_vnf',
                                  return_value=True):
            self.assertEqual(self.test.run(), testcase.TestCase.EX_OK)

    def test_deploy_vnf_unimplemented(self):
        with self.assertRaises(vnf.VnfDeploymentException):
            self.test.deploy_vnf()

    def test_test_vnf_unimplemented(self):
        with self.assertRaises(vnf.VnfTestException):
            self.test.test_vnf()

    def test_deploy_orch_unimplemented(self):
        self.assertTrue(self.test.deploy_orchestrator())

#    @mock.patch('snaps.openstack.tests.openstack_tests.get_credentials',
#                return_value='test')
#    @mock.patch('snaps.openstack.create_project.OpenStackProject',
#                return_value=True)
#    @mock.patch('snaps.openstack.create_user.OpenStackUser',
#                return_value=True)
#    def test_prepare(self, *args):
#        self.assertEqual(self.test.prepare(),
#                         testcase.TestCase.EX_OK)
#        args[0].assert_called_once_with()
#        args[1].assert_called_once_with('test', self.tenant_name)
#        args[2].assert_called_once_with(
#            'test', self.tenant_name, self.tenant_description)
#        args[3].assert_called_once_with()

    @mock.patch('snaps.openstack.tests.openstack_tests.get_credentials',
                return_value=OSCreds(
                    username='user', password='pass',
                    auth_url='http://foo.com:5000/v3', project_name='bar'),
                side_effect=Exception)
    def test_prepare_keystone_client_ko(self, *args):
        with self.assertRaises(vnf.VnfPreparationException):
            self.test.prepare()
        args[0].assert_called_once()

#    @mock.patch('snaps.openstack.tests.openstack_tests.get_credentials',
#                return_value=OS_CREDS)
#    @mock.patch('snaps.openstack.create_project.OpenStackProject')
#    @mock.patch('snaps.openstack.create_project.OpenStackProject.create',
#                side_effect=Exception)
#    def test_prepare_tenant_creation_ko(self, *args):
#        with self.assertRaises(vnf.VnfPreparationException):
#            self.test.prepare()
#        args[2].assert_called_once()
#        args[1].assert_called_once_with(OS_CREDS,
#                                        ProjectSettings(
#                                           name=self.tenant_name,
#                                           description=self.tenant_description,
#                                        ))
#        args[0].assert_called_once()

#    @mock.patch('snaps.openstack.tests.openstack_tests.get_credentials')
#    @mock.patch('snaps.openstack.create_project.OpenStackProject',
#                return_value=0)
#    @mock.patch('snaps.openstack.create_user.OpenStackUser',
#                side_effect=Exception)
#    def test_prepare_user_creation_ko(self, *args):
#        with self.assertRaises(vnf.VnfPreparationException):
#            self.test.prepare()
#        args[0].assert_called_once_with(mock.ANY, self.tenant_name)
#        args[1].assert_called_once_with(
#            mock.ANY, self.tenant_name, self.tenant_description)
#        args[2].assert_called_once_with()


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
