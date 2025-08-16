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
from __future__ import annotations

import os
from dataclasses import (
    asdict,
    dataclass,
)
from functools import cached_property
from typing import (
    Any,
    Optional,
)

from qctrlworkflowclient import ApiRouter
from qctrlworkflowclient.utils import get_package_versions
from segment.analytics import Client as SegmentClient

from fireopal import __version__
from fireopal._utils import PACKAGE_NAMES
from fireopal.config import get_config

# Note: The Segment analytics write key is not private
# and thus can live within the Fire Opal Client. Please
# see: https://github.com/segmentio/Analytics-CSharp/issues/69
_SEGMENT_ANALYTICS_WRITE_KEY = os.getenv(
    "FIRE_OPAL_CLIENT_DEV_ANALYTICS_WRITE_KEY", "gPMCMpFYrKuDXOFQgPn99ZzeGZUgf8Jw"
)
_SEND_TO_SEGMENT = (
    not os.getenv("FIRE_OPAL_CLIENT_DISABLE_TRACKING", "False").lower() == "true"
)
_SEGMENT_DEBUG_LOGGER = (
    os.getenv("FIRE_OPAL_CLIENT_ANALYTICS_DEBUG", "False").lower() == "true"
)


def _get_user_payload(router: Optional[ApiRouter] = None) -> dict[str, Any]:
    """
    Grabs the user's information associated with the
    authenticated account.

    Parameters
    ----------
    router : ApiRouter, optional
        The ApiRouter instance connected to the user. Defaults to None.

    Returns
    -------
    str
        The user's email for identification and tracking.
    """
    if router is None:
        router = get_config().get_router()
    assert isinstance(router, ApiRouter)
    # pylint: disable=protected-access
    return router._client._auth._get_payload(router._client.get_access_token())


class UserTraits:
    """
    Collection of user information.

    Parameters
    ----------
    user_payload : Dict[str, Any]
        Payload of user information.
    """

    def __init__(self, user_payload: dict[str, Any]):
        self._user_payload = user_payload

    @property
    def email(self) -> str:
        """
        The user email associated with the authentication.
        Returns
        -------
        str
            The user's email.
        """
        return self._user_payload["email"]

    @property
    def first_name(self) -> str:
        """
        User's first name.

        Returns
        -------
        str
            The user's first name.
        """
        return self._user_payload["given_name"]

    @property
    def last_name(self) -> str:
        """
        User's last name.

        Returns
        -------
        str
            The user's last name.
        """
        return self._user_payload["family_name"]

    def to_dict(self) -> dict[str, str]:
        """
        Collects properties into a dictionary.

        Returns
        -------
        dict[str, str]
            The collection of user information.
        """
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }


@dataclass
class UserAnalyticsProperties:
    """
    Collection of properties used by the analytics client.
    """

    inputs: dict[str, Any]
    outputs: dict[str, Any]
    environment_information: dict[str, str]


@dataclass
class AnalyticsContext:
    """
    User's context for analytics purposes.

    Notes
    -----
    The Segment context has specific keywords. If this class
    needs to be expanded please look at the documentation:
    https://segment.com/docs/connections/spec/common/#context

    """

    app: dict[str, str]


def _check_for_remote_router() -> bool:
    """
    Check to see if it is a local or remote version
    of the Fire Opal client.

    Returns
    -------
    bool
        True if it is the remote Fire Opal client.
    """
    router = get_config().get_router()
    # pylint: disable=protected-access
    if isinstance(router, ApiRouter) and router._client._auth is not None:
        return True
    return False


class _BaseEventTracker:  # pylint:disable=too-few-public-methods
    """Base class for implementing event tracking."""

    def __init__(
        self, analytics_write_key: str, debug: bool = False, send: bool = True
    ):
        self._analytics_write_key = analytics_write_key
        self._analytics_options = {"debug": debug, "send": send}

    @cached_property
    def _client(self) -> SegmentClient:
        """Returns the configured Segment client."""
        return SegmentClient(self._analytics_write_key, **self._analytics_options)


class _FireOpalEventTracker(_BaseEventTracker):
    """
    Implements the Fire Opal client tracking events.
    """

    @cached_property
    def environment_information(self) -> dict[str, str]:
        """
        Collect the relevant package versions.

        Returns
        -------
        dict[str, str]
            The package and the version installed in the environment.
        """
        return dict(get_package_versions(package_names=PACKAGE_NAMES))

    @property
    def analytics_context(self) -> AnalyticsContext:
        """
        Grab information relating to the user's context
        as defined by Segment.

        Returns
        -------
        AnalyticsContext
            A dataclass containing all relevant information
            pertaining to the User's context.
        """
        return AnalyticsContext(app={"name": "fire-opal", "version": __version__})

    def track_get_result(self, user_traits: UserTraits, action_id: int | str) -> None:
        """
        Tracker for the get_result function.

        Parameters
        ----------
        user_traits : UserTraits
            The user traits associated with the authenticated account.
        action_id : int or str
            The action_id which uniquely identifies the result. It is an input to
            `get_result` function.
        """
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            {"action_id": action_id}, {}, self.environment_information
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_get_result",
            properties=asdict(analytics_properties),
        )

    def track_fire_opal_job_result(
        self, user_traits: UserTraits, action_id: int | str
    ) -> None:
        """
        Tracker for the Fire Opal Job result method.

        Parameters
        ----------
        user_traits : UserTraits
            The user traits associated with the authenticated account.
        action_id : int or str
            The action_id which uniquely identifies the result. It is an input to
            `get_result` function.
        """
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            {"action_id": action_id}, {}, self.environment_information
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_fire_opal_job_result",
            properties=asdict(analytics_properties),
        )

    def track_fire_opal_job_status(
        self, user_traits: UserTraits, action_id: int | str
    ) -> None:
        """
        Tracker for the Fire Opal Job status method.

        Parameters
        ----------
        user_traits : UserTraits
            The user traits associated with the authenticated account.
        action_id : int or str
            The action_id which uniquely identifies the result. It is an input to
            `update_action_status` function.
        """
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            {"action_id": action_id}, {}, self.environment_information
        )
        self._client.track(
            user_id=user_traits.email,
            event="requested_fire_opal_job_status",
            properties=asdict(analytics_properties),
        )

    def track_activity_monitor(
        self, user_traits: UserTraits, limit: int, offset: int, status: Optional[str]
    ) -> None:
        """
        Tracker for activity monitor.

        Parameters
        ----------
        user_traits : UserTraits
            The user traits associated with the authenticated account.
        limit : int
            The number of actions to fetch. Cannot exceed 50.
        offset : int
            The number of recent actions to ignore before starting to fetch.
        status : str or None, optional
            The filter for action status. If None, fetches actions of all
            statuses.
        """
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            inputs={"limit": limit, "offset": offset, "status": status},
            outputs={},
            environment_information=self.environment_information,
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_activity_monitor",
            properties=asdict(analytics_properties),
        )

    def track_get_action_metadata(
        self, user_traits: UserTraits, limit: int, offset: int, status: Optional[str]
    ) -> None:
        """
        Tracker the get_action_metadata function.

        Parameters
        ----------
        user_traits : UserTraits
            The user traits associated with the authenticated account.
        limit : int
            The number of actions to fetch. Cannot exceed 50.
        offset : int
            The number of recent actions to ignore before starting to fetch.
        status : str or None, optional
            The filter for action status. If None, fetches actions of all
            statuses.
        """
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            inputs={"limit": limit, "offset": offset, "status": status},
            outputs={},
            environment_information=self.environment_information,
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_get_action_metadata",
            properties=asdict(analytics_properties),
        )

    def track_configure_organization(
        self, user_traits: UserTraits, organization_slug: str
    ) -> None:
        """Tracks the configure_org monitor."""
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            inputs={"organization_slug": organization_slug},
            outputs={},
            environment_information=self.environment_information,
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_configure_org",
            properties=asdict(analytics_properties),
        )

    def track_make_credentials_for_ibm_cloud(self, user_traits: UserTraits) -> None:
        """Tracks the credential creation for IBM cloud."""
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )
        analytics_properties = UserAnalyticsProperties(
            inputs={}, outputs={}, environment_information=self.environment_information
        )
        self._client.track(
            user_id=user_traits.email,
            event="requested_make_ibm_cloud_credentials",
            properties=asdict(analytics_properties),
        )

    def track_estimate_expectation(
        self,
        user_traits: UserTraits,
        circuit_count: int,
        observable_count: int,
        parameter_count: int,
    ) -> None:
        """Tracks the `estimate_expectation` workflow."""
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )

        analytics_properties = UserAnalyticsProperties(
            {
                "total_circuits": circuit_count,
                "total_observables": observable_count,
                "parameterized_circuit_count": parameter_count,
            },
            {},
            self.environment_information,
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_estimate_expectation",
            properties=asdict(analytics_properties),
        )

    def track_iterate(
        self, user_traits: UserTraits, circuit_count: int, parameter_count: int
    ) -> None:
        """Tracks the iterate workflow."""
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )

        analytics_properties = UserAnalyticsProperties(
            {
                "total_circuits": circuit_count,
                "parameterized_circuit_count": parameter_count,
            },
            {},
            self.environment_information,
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_iterate",
            properties=asdict(analytics_properties),
        )

    def track_iterate_expectation(
        self,
        user_traits: UserTraits,
        circuit_count: int,
        observable_count: int,
        parameter_count: int,
    ) -> None:
        """Tracks the `iterate_expectation` workflow."""
        self._client.identify(
            user_id=user_traits.email,
            traits=user_traits.to_dict(),
            context=asdict(self.analytics_context),
        )

        analytics_properties = UserAnalyticsProperties(
            {
                "total_circuits": circuit_count,
                "total_observables": observable_count,
                "parameterized_circuit_count": parameter_count,
            },
            {},
            self.environment_information,
        )

        self._client.track(
            user_id=user_traits.email,
            event="requested_iterate_expectation",
            properties=asdict(analytics_properties),
        )


_EVENT_TRACKER = _FireOpalEventTracker(
    analytics_write_key=_SEGMENT_ANALYTICS_WRITE_KEY,
    debug=_SEGMENT_DEBUG_LOGGER,
    send=_SEND_TO_SEGMENT,
)
