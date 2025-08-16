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
from typing import Optional

import networkx as nx
from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.run_options import RunOptions
from sympy import Expr

from fireopal._utils import log_activity
from fireopal.credentials import Credentials

from ..fire_opal_job import FireOpalJob
from .base import async_fire_opal_workflow


@async_fire_opal_workflow("solve_qaoa_workflow")
def solve_qaoa(
    problem: Expr | nx.Graph,
    credentials: Credentials,
    problem_type: Optional[str] = None,
    backend_name: Optional[str] = None,
    run_options: Optional[RunOptions] = None,
) -> FireOpalJob:
    """
    Solve a QAOA problem.

    Parameters
    ----------
    problem : Expr or nx.Graph
        The QAOA problem definition, represented as either an
        `nx.Graph` or `sympy.Expr`.
    credentials : Credentials
        The credentials for running circuits on an IBM backend.
        Use the `make_credentials_for_ibm_cloud` function from the `credentials` module
        to generate properly formatted credentials.
    problem_type : str, optional
        The class of QAOA problem to solve. Required for graph problem definitions,
        which currently only includes support for "maxcut".
    backend_name : str, optional
        The backend device that should be used to run circuits. Defaults to None.
    run_options : RunOptions or None, optional
        Additional options for circuit execution. See the `run_options` module
        for classes to store run options for your desired provider.
        Defaults to None.

    Returns
    -------
    FireOpalJob
        A job object containing results and warnings from the execution. The
        results have the following keys:

        ``solution_bitstring (str)``
            The solution bitstring with the best cost found, across all iterations.
        ``solution_bitstring_cost (float)``
            The cost of the solution bitstring.
        ``final_bitstring_distribution (dict[str, int])``
            The bitstring counts dictionary associated with the minimum cost
            across all iterations.
        ``iteration_count (int)``
            The total number of QAOA iterations performed by the optimizer.
        ``variables_to_bitstring_index_map (dict[str, int])``
            The mapping from the variables to the equivalent bit in the bitstring.
        ``best_parameters (list[float])``
            The optimized beta and gamma parameters across all iterations.
        ``warnings (list[str])``
            The warnings produced while compiling or running QAOA.
    """
    log_activity(
        function_called="solve_qaoa",
        problem=problem,
        problem_type=problem_type,
        backend_name=backend_name,
    )
    if isinstance(problem, nx.Graph):
        if len(list(problem.nodes)) < 2:
            logging.error("QCTRL - Graph has less than 2 nodes.")
            raise QctrlArgumentsValueError(
                "Please create a graph with at least 2 nodes and one edge.",
                arguments={"problem": problem},
            )
        if not isinstance(problem_type, str):
            logging.error(
                "QCTRL - problem_type is required when a Graph problem is provided."
            )
            raise QctrlArgumentsValueError(
                "problem_type is required when a Graph problem is provided",
                arguments={
                    "type(problem)": type(problem),
                    "type(problem_type)": type(problem_type),
                },
            )
    else:
        # Note: Forcing `problem_type` to `""` to avoid passing None down QAOA stack.
        problem_type = ""

    print(
        "This function performs multiple consecutive runs. "
        "Wait time may vary depending on hardware queues.\n"
    )
    return {
        "problem": problem,
        "problem_type": problem_type,
        "credentials": credentials,
        "backend_name": backend_name,
        "run_options": run_options,
    }  # type: ignore[return-value]
