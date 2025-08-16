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

from enum import Enum
from functools import partial
from typing import (
    Any,
    Callable,
    Optional,
)

from qctrlworkflowclient import (
    core_workflow,
    print_warnings,
)
from qctrlworkflowclient.functions import async_core_workflow
from qctrlworkflowclient.router.api import (
    Action,
    DecodedResult,
)

from fireopal.config import get_config
from fireopal.fire_opal_job import FireOpalJob

BRAKET_IONQ_DEVICES = ["Aria-1", "Aria-2", "Forte-1", "braket_sv"]


def _formatter(input_: DecodedResult) -> Any:
    result = input_.decoded
    if isinstance(result, dict):
        return print_warnings(result)
    return result


def _async_formatter(input_: dict[str, Action]) -> FireOpalJob:
    assert isinstance(input_, dict) and input_.get("async_result") is not None
    return FireOpalJob(action=input_["async_result"])


class RegistryName(str, Enum):
    """Enum of registry names for backend mapping."""

    FIRE_OPAL = "FIRE_OPAL"
    FIRE_OPAL_CORE_BRAKET_IONQ = "FIRE_OPAL_CORE_BRAKET_IONQ"


BACKEND_REGISTRY_MAP = {}

BACKEND_REGISTRY_MAP.update(
    {device: RegistryName.FIRE_OPAL_CORE_BRAKET_IONQ for device in BRAKET_IONQ_DEVICES}
)


def backend_registry_selector(data: dict[str, Any]) -> Optional[str]:
    """
    Selects the registry to use based on the provider and backend in the data.
    """

    provider = data["credentials"]["provider"]
    if provider == "ibm_cloud":
        return RegistryName.FIRE_OPAL.value
    if provider == "braket":
        check_for_parameters_braket(data)
        backend_name = data["backend_name"]
        if backend_name not in BACKEND_REGISTRY_MAP:
            raise ValueError(f"Unsupported backend name: {backend_name}.")
        return BACKEND_REGISTRY_MAP[backend_name].value
    raise ValueError(f"Unsupported provider: {provider}.")


def provider_registry_selector(data: dict[str, Any]) -> Optional[str]:
    """
    Selects the registry to use based on the provider in the data.
    """

    provider = data["credentials"]["provider"]
    if provider == "ibm_cloud":
        return RegistryName.FIRE_OPAL.value
    if provider == "braket":
        # Note: Ideally we should have a separate registry for Braket itself.
        return RegistryName.FIRE_OPAL_CORE_BRAKET_IONQ.value
    raise ValueError(f"Unsupported provider: {provider}.")


def check_for_parameters_braket(data: dict[str, Any]) -> None:
    """
    Check if the data contains parameters for Braket.

    Raises
    ------
    ValueError
        If parameters are found in the data since we don't support them for Braket.
    """
    assert data["credentials"]["provider"] == "braket"
    if data.get("parameters") is not None:
        raise ValueError("Parameters are not currently supported for Braket.")


fire_opal_workflow: Callable = partial(core_workflow, get_config, formatter=_formatter)
async_fire_opal_workflow: Callable = partial(
    async_core_workflow, get_config, formatter=_async_formatter
)
