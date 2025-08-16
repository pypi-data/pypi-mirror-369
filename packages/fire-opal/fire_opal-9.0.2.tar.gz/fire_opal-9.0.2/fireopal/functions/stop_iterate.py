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

from fireopal._utils import log_activity
from fireopal.credentials import Credentials

from .base import fire_opal_workflow


@fire_opal_workflow("stop_iterate_workflow")
def stop_iterate(
    credentials: Credentials,
    backend_name: str,
) -> dict:
    """
    Stop a hardware provider session previously opened by a call to `fireopal.iterate`.

    Parameters
    ----------
    credentials : Credentials
        The credentials for running circuits. See the `credentials` module for functions
        to generate credentials for your desired provider.
    backend_name : str
        The backend device name that should be used to run circuits.
    """
    log_activity(
        function_called="stop_iterate",
        credentials=credentials,
        backend_name=backend_name,
    )

    return {"credentials": credentials, "backend_name": backend_name}
