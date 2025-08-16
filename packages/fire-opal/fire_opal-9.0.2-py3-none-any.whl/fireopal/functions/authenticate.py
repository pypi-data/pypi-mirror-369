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

import os
from typing import Optional

from qctrlclient.defaults import get_default_api_url
from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlworkflowclient.defaults import get_authenticated_client_for_product
from qctrlworkflowclient.router import ApiRouter

from fireopal.config import (
    configure,
    get_config,
    get_default_api_key_auth,
)
from fireopal.constants import (
    API_KEY_NAME,
    PACKAGE_INFO,
)


def authenticate_qctrl_account(api_key: Optional[str] = None) -> None:
    """
    Authenticate a Fire Opal session.

    Parameters
    ----------
    api_key : str or None, optional
        The value of your API key. If not provided,
        the key should be saved in an environment variable
        called QCTRL_API_KEY. Defaults to None.
    """
    if api_key is None:
        try:
            api_key = os.environ[API_KEY_NAME]
        except KeyError as error:
            raise QctrlArgumentsValueError(
                description="No API key provided in environment or function call. "
                "To call this function without arguments, "
                f"save your API key's value in the {API_KEY_NAME} environment variable.",
                arguments={"api_key": api_key},
            ) from error
    api_key_auth = get_default_api_key_auth(api_key)

    # Grab the global Fire Opal settings, which specify a default router
    # whose internal GQL client uses browser-based authentication.
    settings = get_config()

    # Create a router that uses the global settings and an internal
    # client with token-based authentication.
    client = get_authenticated_client_for_product(
        package_name=PACKAGE_INFO.install_name,
        api_url=get_default_api_url(),
        auth=api_key_auth,
    )
    router = ApiRouter(client, settings)

    # Configure the global settings to use the router with token-based
    # authentication.
    configure(router=router)

    print("Q-CTRL authentication successful!")
