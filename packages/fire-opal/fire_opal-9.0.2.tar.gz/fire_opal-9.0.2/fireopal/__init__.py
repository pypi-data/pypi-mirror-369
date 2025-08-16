# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

__version__ = "9.0.2"


from qctrlworkflowclient.utils import check_package_version as _check_package_version

from . import (
    credentials,
    run_options,
    types,
)
from ._utils import print_package_versions
from .config import configure_organization
from .constants import PACKAGE_INFO as _package_info
from .functions import (
    activity_monitor,
    authenticate_qctrl_account,
    estimate_expectation,
    execute,
    get_action_metadata,
    get_result,
    iterate,
    iterate_expectation,
    show_supported_devices,
    solve_qaoa,
    stop_iterate,
    validate,
)

_check_package_version(_package_info)

# Note: Need to include the late import below for
# docs to be generated, while avoiding a circular
# import issue.
# pylint: disable=wrong-import-position
from .fire_opal_job import FireOpalJob

__all__ = [
    "activity_monitor",
    "authenticate_qctrl_account",
    "credentials",
    "configure_organization",
    "execute",
    "estimate_expectation",
    "get_action_metadata",
    "get_result",
    "iterate",
    "iterate_expectation",
    "run_options",
    "show_supported_devices",
    "solve_qaoa",
    "stop_iterate",
    "validate",
    "print_package_versions",
    "FireOpalJob",
    "types",
]
