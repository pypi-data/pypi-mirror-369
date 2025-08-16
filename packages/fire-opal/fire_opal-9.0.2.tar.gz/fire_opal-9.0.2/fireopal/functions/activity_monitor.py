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
from dataclasses import (
    astuple,
    dataclass,
)
from datetime import datetime
from typing import (
    Any,
    Optional,
)

from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlworkflowclient import ApiRouter
from qctrlworkflowclient.router.api import ActionStatus

from fireopal._event_tracker import (
    _EVENT_TRACKER,
    UserTraits,
    _check_for_remote_router,
    _get_user_payload,
)
from fireopal._utils import log_activity
from fireopal.config import get_config


def activity_monitor(
    limit: int = 1, offset: int = 0, status: Optional[str] = None
) -> None:
    """
    Print metadata from previously submitted actions.

    Parameters
    ----------
    limit : int, optional
        The number of actions to print. Cannot exceed 50. Defaults to 1.
    offset : int, optional
        The number of recent actions to ignore before starting to print.
        Defaults to 0.
    status : str or None, optional
        The filter for action status. If None, fetches actions of all
        statuses. Defaults to None.
    """
    log_activity(
        function_called="activity_monitor", limit=limit, offset=offset, status=status
    )

    if _check_for_remote_router():
        user_traits = UserTraits(_get_user_payload())
        _EVENT_TRACKER.track_activity_monitor(
            user_traits=user_traits, limit=limit, offset=offset, status=status
        )
    # Row items.
    filtered_action_metadata = get_action_metadata(limit, offset, status)
    if len(filtered_action_metadata) == 0:
        print("No jobs found for the specified filter(s).")
        return

    rows = [astuple(metadatum) for metadatum in filtered_action_metadata]

    # Column headers.
    headers = (
        "Function",
        "Status",
        "Created at (UTC)",
        "Updated at (UTC)",
        "Action ID",
    )

    # Column widths.
    column_widths = (
        max(max(len(row[column]) for row in rows), len(headers[column]))
        for column in range(5)
    )

    name_width, status_width, created_width, updated_width, id_width = column_widths

    # Add headers and dash separators at top of table.
    table_items = [
        headers,
        (
            "-" * name_width,
            "-" * status_width,
            "-" * created_width,
            "-" * updated_width,
            "-" * id_width,
        ),
    ] + rows

    # Build table.
    print(
        "\n".join(
            [
                f"| {name:{name_width}s} | {status:{status_width}s} | "
                f"{created_at:{created_width}s} | {updated_at:{updated_width}s} | "
                f"{action_id:{id_width}s} |"
                for (name, status, created_at, updated_at, action_id) in table_items
            ]
        )
    )


def get_action_metadata(
    limit: int = 1, offset: int = 0, status: Optional[str] = None
) -> list[ActionMetadata]:
    """
    Fetch metadata from previously submitted actions.

    Parameters
    ----------
    limit : int, optional
        The number of actions to fetch. Cannot exceed 50. Defaults to 1.
    offset : int, optional
        The number of recent actions to ignore before starting to fetch.
        Defaults to 0.
    status : str or None, optional
        The filter for action status. If None, fetches actions of all
        statuses. Defaults to None.

    Returns
    -------
    list[ActionMetadata]
        Action metadata.
    """
    if limit > 50:
        logging.error("QCTRL - The limit cannot exceed 50.")
        raise QctrlArgumentsValueError(
            "The limit cannot exceed 50.", arguments={"limit": limit}
        )
    if status is None:
        print(
            "Getting jobs for all statuses. To filter jobs by status, ",
            "use the status keyword argument. Valid status values are: "
            f"{', '.join([status.value for status in ActionStatus])}.\n",
        )
    router: ApiRouter = get_config().get_router()
    if _check_for_remote_router():
        user_traits = UserTraits(_get_user_payload(router=router))
        _EVENT_TRACKER.track_get_action_metadata(
            user_traits=user_traits, limit=limit, offset=offset, status=status
        )

    action_metadata: list[dict[str, Any]] = router.activity_monitor(
        limit, offset, status
    )

    # Filter to relevant fields.
    desired_fields = ("name", "status", "createdAt", "updatedAt", "modelId")
    filtered_action_metadata: list[dict[str, Any]] = [
        {k: v for k, v in metadatum.items() if k in desired_fields}
        for metadatum in action_metadata
    ]

    # Format data.
    workflow_to_public_function = {
        "compile_and_run_workflow": "execute",
        "estimate_expectation_workflow": "estimate_expectation",
        "show_supported_devices_workflow": "show_supported_devices",
        "validate_input_circuits_workflow": "validate",
        "solve_qaoa_workflow": "solve_qaoa",
        "iterate_workflow": "iterate",
        "iterate_expectation_workflow": "iterate_expectation",
        "stop_iterate_workflow": "stop_iterate",
    }
    result: list[ActionMetadata] = []
    for metadatum in filtered_action_metadata:
        created_at = datetime.fromisoformat(metadatum["createdAt"])
        updated_at = datetime.fromisoformat(metadatum["updatedAt"])
        metadatum["createdAt"] = created_at.strftime("%Y-%m-%d %H:%M:%S")
        metadatum["updatedAt"] = updated_at.strftime("%Y-%m-%d %H:%M:%S")
        metadatum["name"] = workflow_to_public_function.get(metadatum["name"], None)
        if metadatum["name"] is not None:
            result.append(
                ActionMetadata(
                    metadatum["name"],
                    metadatum["status"],
                    metadatum["createdAt"],
                    metadatum["updatedAt"],
                    metadatum["modelId"],
                )
            )
    return result


@dataclass
class ActionMetadata:
    """
    Model for formatted action metadata.

    Parameters
    ----------
    name : str
        The name of the client function that submitted this action.
    status : str
        The action's status.
    created_at : str
        The creation date of the action in UTC.
    updated_at : str
        The last updated date of the action in UTC.
    model_id : str
        The unique identifier for this action.
    """

    name: str
    status: str
    created_at: str
    updated_at: str
    model_id: str
