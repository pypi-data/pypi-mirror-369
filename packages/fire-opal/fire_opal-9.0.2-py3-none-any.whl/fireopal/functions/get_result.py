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

import logging
from typing import Any

from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlworkflowclient import print_warnings
from qctrlworkflowclient.router.api import (
    Action,
    ApiRouter,
)

from fireopal._event_tracker import (
    _EVENT_TRACKER,
    UserTraits,
    _check_for_remote_router,
    _get_user_payload,
)
from fireopal.config import get_config


def get_result(action_id: int | str) -> dict[str, Any]:
    """
    Retrieve the result of a previously submitted action, blocking
    for completion if the action is still in progress.

    Parameters
    ----------
    action_id : int or str
        The unique identifier associated with the action.
        You can retrieve this value from the activity monitor.

    Returns
    -------
    dict[str, Any]
        The action result. The shape of this dictionary
        will be the same as that of the result returned
        from the function that was previously called
        to create this action.
    """
    if not str(action_id).isnumeric():
        logging.error("QCTRL - The action ID must be an integer.")
        raise QctrlArgumentsValueError(
            "The action ID must be an integer.", arguments={"action_id": action_id}
        )
    router: ApiRouter = get_config().get_router()

    action = Action(action_id=str(action_id))
    decoded_result = router.get_result(action, revoke_on_interrupt=False).decoded
    assert isinstance(decoded_result, dict)

    if _check_for_remote_router():
        user_traits = UserTraits(_get_user_payload(router))
        _EVENT_TRACKER.track_get_result(user_traits=user_traits, action_id=action_id)
    return print_warnings(decoded_result)
