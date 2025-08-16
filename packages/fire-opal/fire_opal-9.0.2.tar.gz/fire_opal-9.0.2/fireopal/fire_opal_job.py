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
"""Fire Opal Job class."""

from __future__ import annotations

from typing import Any

from qctrlworkflowclient.router.api import (
    Action,
    ActionStatus,
    ApiRouter,
)

from fireopal._event_tracker import (
    _EVENT_TRACKER,
    UserTraits,
    _check_for_remote_router,
    _get_user_payload,
)
from fireopal.config import get_config
from fireopal.functions.get_result import get_result

# Note: The statuses here, if changed, need to be updated in the
# `status` method of the `FireOpalJob` class below.
_FIRE_OPAL_JOB_STATUSES = {
    ActionStatus.SUCCESS.value: "Job has finished successfully.",
    ActionStatus.REVOKED.value: "Job has been cancelled.",
    ActionStatus.FAILURE.value: "Job has failed.",
    ActionStatus.PENDING.value: "Job has been submitted to Q-CTRL.",
    ActionStatus.RECEIVED.value: "Job has been submitted to Q-CTRL.",
    ActionStatus.RETRY.value: "Job has been submitted to Q-CTRL.",
    ActionStatus.STARTED.value: "Job has been submitted to Q-CTRL.",
}


class FireOpalJob:
    """
    Fire Opal Job class.
    """

    def __init__(self, action: Action) -> None:
        """
        Contains information regarding jobs submitted to Q-CTRL.

        Parameters
        ----------
        action : Action
            The unique identifier object for a job submitted
            to Q-CTRL.
        """
        self._action = action

    @property
    def action_id(self) -> str:
        """
        The identifier for a Q-CTRL job.

        Returns
        -------
        str
            The identifier for a Q-CTRL job.
        """
        return self._action.action_id

    def status(self) -> dict[str, str]:
        """
        The status of the Q-CTRL Fire Opal job, as explained in the following
        list:
            ``SUCCESS``:
                "Job has finished successfully."
            ``REVOKED``:
                "Job has been cancelled."
            ``FAILURE``:
                "Job has failed."
            ``PENDING``:
                "Job has been submitted to Q-CTRL."
            ``RECEIVED``:
                "Job has been submitted to Q-CTRL."
            ``RETRY``:
                "Job has been submitted to Q-CTRL."
            ``STARTED``:
                "Job has been submitted to Q-CTRL."

        Returns
        -------
        dict[str, str]
            The status of the Q-CTRL Fire Opal job.
        """
        router: ApiRouter = get_config().get_router()
        if _check_for_remote_router():
            user_traits = UserTraits(_get_user_payload(router))
            _EVENT_TRACKER.track_fire_opal_job_status(
                user_traits=user_traits, action_id=self.action_id
            )

        assert isinstance(router, ApiRouter)
        action = router.update_action_status(action=self._action)

        return {
            "status_message": _FIRE_OPAL_JOB_STATUSES[action.status],
            "action_status": action.status,
        }

    def result(self) -> dict[str, Any]:
        """
        The results of the Q-CTRL Fire Opal job.

        Returns
        -------
        dict[str, Any]
            The results of the Q-CTRL Fire Opal job.
        """
        if _check_for_remote_router():
            user_traits = UserTraits(_get_user_payload())
            _EVENT_TRACKER.track_fire_opal_job_result(
                user_traits=user_traits, action_id=self.action_id
            )
        return get_result(self._action.action_id)
