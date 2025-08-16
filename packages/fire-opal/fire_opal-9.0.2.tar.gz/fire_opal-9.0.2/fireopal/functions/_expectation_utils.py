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
import warnings

from qctrlcommons.exceptions import QctrlArgumentsValueError

from fireopal.types import (
    ObservableType,
    PauliOperator,
)

INVALID_OBSERVABLES_ERROR_MESSAGE = (
    "Invalid type received for observables input. "
    "Please refer to the Fire Opal Estimator documentation for valid input types."
)


def validate_and_convert_observables(
    observables: ObservableType,
) -> list[PauliOperator]:
    """
    Validate the observable input for the `estimate_expectation` and `iterate_expectation`
    functions and convert them to a list of `PauliOperator` objects.

    Parameters
    ----------
    observables : ObservableType
        The observable or observables to be validated.

    Returns
    -------
    list[PauliOperator]
        The validated observable(s) as a list of PauliOperator objects.

    Raises
    ------
    QctrlArgumentsValueError
        If the input is not a valid observable or list of observables.

    Notes
    -----
    list[tuple[str, float]] observable type is deprecated and will be
    removed in future versions.
    """

    validated_observables: list[PauliOperator] = []
    if isinstance(observables, PauliOperator):
        validated_observables = [observables]
    elif isinstance(observables, list):
        if all(isinstance(obs, PauliOperator) for obs in observables):
            validated_observables = observables
        elif all(isinstance(obs, (str, tuple)) for obs in observables):
            if all(isinstance(obs, str) for obs in observables):
                validated_observables = [PauliOperator(observables)]
            elif all(
                isinstance(obs, tuple)
                and isinstance(obs[0], str)
                and isinstance(obs[1], (int, float, complex))
                for obs in observables
            ):
                warnings.warn(
                    "Passing a list of tuples of strings and floats as observables is deprecated "
                    "and will be removed in future versions. Consider using a `dict[str, float]` "
                    "or a list of `PauliOperator` objects instead.",
                    DeprecationWarning,
                )
                validated_observables = [PauliOperator.from_list(observables)]
    elif isinstance(observables, str):
        validated_observables = [PauliOperator(observables)]
    elif isinstance(observables, dict):
        if all(
            isinstance(key, str) and isinstance(value, (int, float, complex))
            for key, value in observables.items()
        ):
            validated_observables = [PauliOperator.from_dict(observables)]

    if not validated_observables:
        logging.error("Q-CTRL: %s", INVALID_OBSERVABLES_ERROR_MESSAGE)
        raise QctrlArgumentsValueError(
            INVALID_OBSERVABLES_ERROR_MESSAGE,
            arguments={"observables": observables},
        )

    return validated_observables
