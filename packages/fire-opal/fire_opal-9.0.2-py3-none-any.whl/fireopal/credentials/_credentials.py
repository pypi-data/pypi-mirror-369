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

from typing import Dict

from qctrlcommons.exceptions import QctrlArgumentsValueError

from fireopal._event_tracker import (
    _EVENT_TRACKER,
    UserTraits,
    _check_for_remote_router,
    _get_user_payload,
)
from fireopal.config import get_config

Credentials = Dict[str, str]


def make_credentials_for_ibm_cloud(token: str, instance: str) -> Credentials:
    """
    The Credentials builder for IBM cloud devices.

    Parameters
    ----------
    token : str
        The IBM API account token.
    instance : str,
        The IBM cloud instance, the user's CRN.

    Returns
    -------
    Credentials
        A dictionary usable for the `credentials`
        argument of any Fire Opal function using IBM Cloud.
    """
    if _check_for_remote_router():
        user_traits = UserTraits(_get_user_payload())
        _EVENT_TRACKER.track_make_credentials_for_ibm_cloud(user_traits=user_traits)
    _check_all_strings(token=token, instance=instance)
    return {"token": token, "instance": instance, "provider": "ibm_cloud"}


def make_credentials_for_braket(arn: str) -> Credentials:
    """
    Make a Credentials dictionary for Braket.

    Parameters
    ----------
    arn : str
        The Amazon resource number for an IAM role
        that has Braket permissions and trusts Q-CTRL's
        AWS account.

    Returns
    -------
    Credentials
        A dictionary usable for the `credentials`
        argument of any Fire Opal web API function.

    Notes
    -----
    This function performs only basic type checking of
    the credentials it receives. It does not check whether
    the credentials are valid for hardware access.
    """
    _check_all_strings(arn=arn)
    config = get_config()
    organizations = (
        config.get_router()._organizations  # pylint: disable=protected-access
    )
    user_organization = next(
        organization
        for organization in organizations
        if organization.slug == config.organization
    )
    user_organization_id = user_organization.organization_id

    return {"arn": arn, "organization_id": user_organization_id, "provider": "braket"}


def _check_all_strings(**kwargs: str) -> None:
    """
    Check whether all arguments are strings.

    Raises
    ------
    QctrlArgumentsValueError
        If there are non-string arguments.
    """
    if not all((isinstance(arg, str) for arg in kwargs.values())):
        raise QctrlArgumentsValueError(
            description="All arguments should be strings.",
            arguments={f"{key} type": type(value) for key, value in kwargs.items()},
        )
