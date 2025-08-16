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

from qctrlclient import ApiKeyAuth
from qctrlclient.defaults import (
    get_default_api_url,
    get_default_cli_auth,
)
from qctrlclient.exceptions import GraphQLQueryError
from qctrlclient.globals import global_value
from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlworkflowclient import (
    ApiRouter,
    CoreClientSettings,
    LocalRouter,
    Product,
    get_authenticated_client_for_product,
)
from qctrlworkflowclient.defaults import CliAuth

from .constants import (
    API_KEY_NAME,
    PACKAGE_INFO,
)


def get_default_router() -> ApiRouter:
    """Returns the default router that the Fire Opal
    client uses.
    """
    api_key = os.getenv(API_KEY_NAME)
    if api_key:
        auth = get_default_api_key_auth(api_key)
    else:
        auth = get_default_cli_auth()
    client = get_authenticated_client_for_product(
        PACKAGE_INFO.install_name,
        get_default_api_url(),
        auth,
    )
    settings = get_config()
    return ApiRouter(client, settings)


def get_default_api_key_auth(api_key: str) -> ApiKeyAuth:
    """
    Returns a token-based authentication handler
    pointed to the default API URL.
    """
    auth = ApiKeyAuth(get_default_api_url(), api_key)
    _validate_api_key(api_key, auth)
    return auth


def _validate_api_key(api_key: str, api_key_auth: ApiKeyAuth) -> None:
    """
    Validate the API key.

    Parameters
    ----------
    api_key : str
        The user's API key.
    api_key_auth : ApiKeyAuth
        The authentication handler generated from the user's API key.

    Raises
    ------
    QctrlArgumentsValueError
        If the API key is invalid, or if the account associated
        with the API key does not have a Fire Opal subscription.
    """
    # We can thus infer that the API key is invalid if the access token cannot be fetched.
    try:
        api_key_auth.access_token
    except GraphQLQueryError as error:
        raise QctrlArgumentsValueError(
            description="Invalid API key. Please check your key "
            "or visit https://accounts.q-ctrl.com to generate a new key.",
            arguments={"api_key": api_key},
        ) from error


@global_value("FIRE_OPAL_CONFIG")
def get_config() -> CoreClientSettings:
    """Returns the global Fire Opal settings."""
    return CoreClientSettings(router=get_default_router, product=Product.FIRE_OPAL)


def configure(**kwargs) -> None:  # type: ignore
    """
    Updates the global Fire Opal settings. See `CoreClientSettings`
    for details on which fields can be updated.

    Parameters
    ----------
    **kwargs
        Arbitrary keyword arguments to update the configuration.
    """
    config = get_config()
    config.update(**kwargs)


def configure_api(api_url: str, oidc_url: str) -> None:
    """Convenience function to configure Fire Opal for API
    routing.

    Parameters
    ----------
    api_url : str
        URL of the GraphQL schema
    oidc_url : str
        Base URL of the OIDC provider, for example Keycloak.
    """
    client = get_authenticated_client_for_product(
        PACKAGE_INFO.install_name,
        api_url,
        CliAuth(oidc_url),
    )
    settings = get_config()

    configure(router=ApiRouter(client, settings))


def configure_local(resolver: "BaseResolver") -> None:  # type: ignore
    """Convenience function to configure Fire Opal for local
    routing.

    Parameters
    ----------
    resolver : BaseResolver
        A local implementation of a workflow resolver which uses
        a registry that implements all of the available Fire Opal
        workflows
    """
    configure(router=LocalRouter(resolver))


def configure_organization(organization_slug: str) -> None:
    """Convenience function to configure the organization.

    Parameters
    ----------
    organization_slug : str
        Unique slug for the organization.
    """
    configure(organization=organization_slug)
