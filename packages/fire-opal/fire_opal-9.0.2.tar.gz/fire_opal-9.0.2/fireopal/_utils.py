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

"""
Module to host some utility functions, which are exposed at the top-level.
"""
import logging
from typing import (
    Any,
    Optional,
)

from qctrlworkflowclient.utils import package_versions_table

__all__ = ["print_package_versions"]

# Note: Remove `qiskit-ibm-provider` from package list
# once support for Primitives V1 is dropped.
PACKAGE_NAMES = [
    # External packages.
    "matplotlib",
    "networkx",
    "numpy",
    "qiskit",
    "qiskit_ibm_provider",
    "qiskit_ibm_runtime",
    "sympy",
    # Q-CTRL packages.
    "fireopal",
    "qctrlvisualizer",
    "qctrlworkflowclient",
]


def print_package_versions() -> None:
    """
    Print a Markdown-formatted table showing the Python version being used,
    as well as the versions of some loaded packages that are relevant to Fire Opal.
    """

    print(package_versions_table(PACKAGE_NAMES))


def log_activity(function_called: Optional[str] = None, **kwargs: Any) -> None:
    """
    Log the function called along with its parameters and types.

    Parameters
    ----------
    function_called : str or None, optional
        The name of the function to be associated with the parameter logging.
        Defaults to None.
    kwargs : Any
        The keyword arguments can be anything but typical use will be the arguments
        of the function being logged.
    """
    if function_called is not None:
        logging.info("QCTRL: The function %s was called.", function_called)
    for key, value in kwargs.items():
        logging.info("QCTRL: %s = %s of type %s", key, value, type(value))
