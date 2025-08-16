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
from typing import (
    Any,
    Optional,
)

from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.run_options import RunOptions

from fireopal.credentials import Credentials


def handle_single_item(item: Any) -> list[Any]:
    """
    Convert a single item to a list holding containing it, if applicable.

    Parameters
    ----------
    item : Any
        One or more items.

    Returns
    -------
    list[Any]
        The input if originally provided as a list. Otherwise, the input in
        a list.
    """
    if not isinstance(item, list):
        return [item]
    return item


def check_single_circuit_validity(
    circuit: str, circuit_index: Optional[int] = None
) -> None:
    """
    Validate that circuits are of type string as well as nonempty.

    Parameters
    ----------
    circuit : str
        The input circuit.
    circuit_index : int, optional
        The index of the circuit if the input is a list. Defaults to None.
    """

    extras = {"circuit_index": circuit_index} if circuit_index is not None else None
    if not isinstance(circuit, str):
        logging.error(
            "QCTRL - Invalid type received for circuits input. The circuit must be a string."
        )
        raise QctrlArgumentsValueError(
            "Invalid type received for circuits input. The circuit must be a string.",
            arguments={"circuits": circuit},
            extras=extras,
        )
    if not circuit:
        logging.error("QCTRL - The circuit string provided must be non-empty.")
        raise QctrlArgumentsValueError(
            "The circuit string provided must be non-empty.",
            arguments={"circuits": circuit},
            extras=extras,
        )


def check_single_parameter_dict_validity(
    parameters: dict[str, float], parameter_dict_index: Optional[int] = None
) -> None:
    """
    Validate that the parameter dictionary and its entries have valid
    types.

    Parameters
    ----------
    parameters : dict[str, float]
        The parameter dictionary.
    parameter_dict_index : int, optional
        The index of the parameter dictionary if the parameters input
        is a list. Defaults to None.
    """

    extras = (
        {"parameter_dict_index": parameter_dict_index}
        if parameter_dict_index is not None
        else None
    )
    if not isinstance(parameters, dict):
        logging.error(
            "QCTRL - Invalid type received for parameters input. "
            "The parameters must consist of dictionaries."
        )
        raise QctrlArgumentsValueError(
            "Invalid type received for parameters input. "
            "The parameters must consist of dictionaries.",
            arguments={"parameters": parameters},
            extras=extras,
        )
    for key, value in parameters.items():
        if not isinstance(key, str):
            logging.error(
                "QCTRL - Invalid type received for parameters' key. "
                "The keys in parameters must be strings."
            )
            raise QctrlArgumentsValueError(
                "Invalid type received for parameters' key. "
                "The keys in parameters must be strings.",
                arguments={"parameters": parameters},
                extras=extras,
            )
        if not isinstance(value, float):
            logging.error(
                "QCTRL - Invalid type received for parameters' values. "
                "The values in parameters must be floats."
            )
            raise QctrlArgumentsValueError(
                "Invalid type received for parameters' values. "
                "The values in parameters must be floats.",
                arguments={"parameters": parameters},
                extras=extras,
            )


def check_circuit_submission_validity(
    circuits: str | list[str],
    shot_count: int,
    credentials: Credentials,
    backend_name: str,
    parameters: Optional[dict[str, float] | list[dict[str, float]]] = None,
    run_options: Optional[RunOptions] = None,
) -> None:
    """
    Check if the inputs are valid for submission of circuits to a hardware provider.

    Parameters
    ----------
    circuits : str or list[str]
        Quantum circuit(s) in the form of QASM string(s). You can use Qiskit to
        generate these strings. This list or string must be non-empty.
    shot_count : int
        Number of bitstrings that are sampled from the final quantum state.
    credentials : Credentials
        The credentials for running circuits. See the `credentials` module for functions
        to generate credentials for your desired provider.
    backend_name : str
        The backend device name that should be used to run circuits.
    parameters : dict[str, float] or list[dict[str, float]] or None, optional
        The list of parameters for the circuit(s), if they're parametric.
        Defaults to None.
    run_options : RunOptions or None, optional
        Additional options for circuit execution. Defaults to None.
    """

    if isinstance(circuits, list):
        if not all(isinstance(circuit, str) for circuit in circuits):
            logging.error(
                "Q-CTRL: Invalid type received for circuits input. All circuits must be strings."
            )
            raise QctrlArgumentsValueError(
                "Invalid type received for circuits input. All circuits must be strings.",
                arguments={"circuits": circuits},
            )
        if len(circuits) == 0:
            logging.error("Q-CTRL: The list of circuits must be non-empty.")
            raise QctrlArgumentsValueError(
                "The list of circuits must be non-empty.",
                arguments={"circuits": circuits},
            )
        for index, circuit in enumerate(circuits):
            check_single_circuit_validity(circuit=circuit, circuit_index=index)
    else:
        check_single_circuit_validity(circuit=circuits)
    if not isinstance(shot_count, int):
        logging.error(
            "Q-CTRL: Invalid type received for shot_count input. The shot_count must be an integer."
        )
        raise QctrlArgumentsValueError(
            "Invalid type received for shot_count input. The shot_count must be an integer.",
            arguments={"shot_count": shot_count},
        )
    if not isinstance(credentials, dict):
        logging.error(
            "Q-CTRL: Invalid type received for credentials input. "
            "The credentials must be a dictionary."
        )
        raise QctrlArgumentsValueError(
            "Invalid type received for credentials input. The credentials must be a dictionary.",
            arguments={
                "credentials": credentials,
                "credentials type": type(credentials),
            },
        )
    if not isinstance(backend_name, str):
        logging.error(
            "Q-CTRL: Invalid type received for backend_name input. "
            "The backend_name must be a string."
        )
        raise QctrlArgumentsValueError(
            "Invalid type received for backend_name input. The backend_name must be a string.",
            arguments={"backend_name": backend_name},
        )
    if parameters is not None:
        if not isinstance(parameters, (list, dict)):
            logging.error(
                "Q-CTRL: Invalid type received for parameters input. "
                "The parameters must be a list or dict."
            )
            raise QctrlArgumentsValueError(
                "Invalid type received for parameters input. "
                "The parameters must be a list or dict.",
                arguments={"parameters": parameters},
            )

        if isinstance(parameters, list):
            for index, parameter_dict in enumerate(parameters):
                check_single_parameter_dict_validity(
                    parameters=parameter_dict, parameter_dict_index=index
                )
        else:
            check_single_parameter_dict_validity(parameters=parameters)
    if run_options is not None:
        if not isinstance(run_options, RunOptions):
            logging.error(
                "Q-CTRL: Invalid type received for run_options input. "
                "The run_options must be an instance of RunOptions."
            )
            raise QctrlArgumentsValueError(
                "Invalid type received for run_options input. "
                "The run_options must be an instance of RunOptions.",
                arguments={"run_options": run_options},
            )
