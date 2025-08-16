# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

import restclients_core
from restclients_core.exceptions import DataFailureException
from uw_sdbmyuw import get_app_status, get_appstatus_url, invalid_system_key, \
    Sdbmyuw_DAO
from uw_sdbmyuw.exceptions import InvalidSystemKey
from uw_sdbmyuw.util import fdao_sdbmyuw_override


@fdao_sdbmyuw_override
class AppStatusTest(TestCase):

    def test_get_appstatus_url(self):
        self.assertEqual(get_appstatus_url('000000000'),
                         '/sdb_MyUW/appstatus.asp?s=000000000')

    def test_invalid_system_key(self):
        self.assertRaises(InvalidSystemKey,
                          get_app_status,
                          '000000000')
        self.assertFalse(invalid_system_key('000000001'))
        self.assertTrue(invalid_system_key(None))

    def test_get_app_status(self):
        statuses = get_app_status('000000001')
        self.assertIsNotNone(statuses)
        self.assertEqual(len(statuses), 2)
        self.assertTrue(statuses[0].is_freshman)
        self.assertTrue(statuses[0].is_bothell)

        self.assertTrue(statuses[1].is_freshman)
        self.assertTrue(statuses[1].is_seattle)

        statuses = get_app_status('000000002')
        self.assertTrue(statuses[0].is_post_bac)
        self.assertTrue(statuses[0].is_international)
        self.assertTrue(statuses[0].is_bothell)

        self.assertTrue(statuses[1].is_post_bac)
        self.assertTrue(statuses[1].is_international)
        self.assertTrue(statuses[1].is_tacoma)

        statuses = get_app_status('000000003')
        self.assertTrue(statuses[0].is_returning)
        self.assertTrue(statuses[0].is_seattle)

        statuses = get_app_status('000000004')
        self.assertTrue(statuses[0].is_transfer)
        self.assertTrue(statuses[0].is_bothell)

        self.assertTrue(statuses[1].is_transfer)
        self.assertTrue(statuses[1].is_seattle)

        status = get_app_status('000000005')[0]
        self.assertTrue(status.is_ug_non_matriculated)
        self.assertTrue(status.is_bothell)
        self.assertEqual(status.quarter, "winter")
        self.assertEqual(status.year, 2018)

        status = get_app_status('000000006')[0]
        self.assertTrue(status.no_ug_app)

        statuses = get_app_status('000000007')
        status = statuses[0]
        self.assertTrue(status.is_bothell)
        self.assertTrue(status.is_freshman)
        self.assertEqual(status.quarter, "autumn")
        self.assertEqual(status.year, 2017)

        status = statuses[1]
        self.assertTrue(status.is_seattle)
        self.assertTrue(status.is_freshman)
        self.assertEqual(status.quarter, "autumn")
        self.assertEqual(status.year, 2017)

        status = statuses[2]
        self.assertTrue(status.is_tacoma)
        self.assertTrue(status.is_freshman)
        self.assertEqual(status.quarter, "autumn")
        self.assertEqual(status.year, 2017)

        # bothell freshman 2022 autumn
        statuses = get_app_status('000000008')
        self.assertEqual(len(statuses), 1)
        status = statuses[0]
        self.assertTrue(status.is_bothell)
        self.assertTrue(status.is_freshman)
        self.assertEqual(status.quarter, "autumn")

    def test_error_cases(self):
        self.assertRaises(
            DataFailureException, get_app_status, '100000001')
        self.assertRaises(
            DataFailureException, get_app_status, '000000009')
