# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_sdbmyuw.dao import Sdbmyuw_DAO


fdao_sdbmyuw_override = use_mock(Sdbmyuw_DAO())
