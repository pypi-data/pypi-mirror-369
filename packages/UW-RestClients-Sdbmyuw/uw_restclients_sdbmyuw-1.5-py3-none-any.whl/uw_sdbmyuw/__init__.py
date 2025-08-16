# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the Sdbmyuw service.

"""
import re
from urllib.parse import urlencode
import restclients_core
from uw_sdbmyuw.dao import Sdbmyuw_DAO
from restclients_core.exceptions import DataFailureException
from uw_sdbmyuw.models import ApplicationStatus, parse_statuses
from uw_sdbmyuw.exceptions import InvalidSystemKey


DAO = Sdbmyuw_DAO()


def get_app_status(system_key):
    """
    Get Undergraduate application status
    @return ApplicationStatus object
    @InvalidSystemKey if system_key is not valid
    """
    if invalid_system_key(system_key):
        raise InvalidSystemKey(
            "Invalid system key in get_app_status({})".format(system_key))

    url = get_appstatus_url(system_key)
    response = DAO.getURL(url, {})
    response_data = str(response.data)
    if response.status != 200:
        raise DataFailureException(url, response.status, response_data)
    if len(response.data) == 0:
        raise DataFailureException(url, 543, "status 200 but missing data")
    return parse_statuses(response_data)


def get_appstatus_url(system_key):
    return "/sdb_MyUW/appstatus.asp?{}".format(urlencode({"s": system_key}))


SYSTEM_KEY_PATTERN = re.compile(r'^\d{9}$')
ALLZERO_PATTERN = re.compile(r'^[0]+$')


def invalid_system_key(system_key_str):
    return (system_key_str is None or
            ALLZERO_PATTERN.match(system_key_str) or
            SYSTEM_KEY_PATTERN.match(system_key_str) is None)
