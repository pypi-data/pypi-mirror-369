# Copyright 2022 The PECOS Developers
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License.You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""WebAssembly integration for the classical virtual machine.

This module provides WebAssembly support for the PECOS classical virtual machine,
enabling execution of compiled classical functions in quantum-classical algorithms.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from pecos.engines.cvm.binarray import BinArray
from pecos.engines.cvm.sim_func import sim_exec
from pecos.engines.cvm.wasm_vms.wasmer import read_wasmer
from pecos.engines.cvm.wasm_vms.wasmtime import read_wasmtime
from pecos.errors import MissingCCOPError

if TYPE_CHECKING:
    from typing import Any

    from pecos.circuits import QuantumCircuit


class CCOPObject(Protocol):
    """Protocol for CCOP objects."""

    def exec(self, func_name: str, args: list) -> int:
        """Execute a function."""
        ...


class EngineRunner(Protocol):
    """Protocol for engine runner objects."""

    debug: bool
    ccop: CCOPObject | None
    circuit: QuantumCircuit


def read_pickle(picklefile: str | bytes) -> CCOPObject:
    """Read in either a file path or byte object meant to be a pickled class used to define the ccop.

    Warning: This function loads pickled data which can be a security risk if the data
    comes from untrusted sources. Only use with trusted circuit metadata.
    """
    if isinstance(picklefile, str):  # filename
        with Path.open(picklefile, "rb") as f:
            return pickle.load(f)  # noqa: S301 - Loading trusted circuit metadata
    else:
        return pickle.loads(picklefile)  # noqa: S301 - Loading trusted circuit metadata


def get_ccop(circuit: QuantumCircuit) -> CCOPObject | None:
    """Get classical coprocessor object from circuit metadata.

    Extracts and initializes the classical coprocessor (CCOP) object from
    the circuit metadata, supporting various CCOP types including Python,
    WebAssembly, and object-based implementations.

    Args:
        circuit: Quantum circuit containing CCOP metadata.

    Returns:
        Initialized CCOP object, or None if no CCOP is specified.

    Raises:
        Exception: If CCOP type is unknown or unsupported.
    """
    if circuit.metadata.get("ccop"):
        ccop = circuit.metadata["ccop"]
        ccop_type = circuit.metadata["ccop_type"]

        if ccop_type is None:
            ccop_type = "wasmtime"

        # Set self.ccop
        # ------------------------------------------------
        if ccop_type in {"py", "python"}:
            ccop = read_pickle(ccop)

        elif ccop_type == "wasmtime":
            ccop = read_wasmtime(ccop)

        elif ccop_type in {"wasmer", "wasmer_cl"}:
            ccop = read_wasmer(ccop, compiler="wasmer_cl")

        elif ccop_type == "wasmer_llvm":
            ccop = read_wasmer(ccop, compiler=ccop_type)

        elif ccop_type in {"obj", "object"}:
            pass

        else:
            msg = f'Got ccop object but ccop_type "{ccop_type}" is unknown or not supported!'
            raise Exception(msg)

        # Call the CCOP object initialization method.
        ccop.exec("init", [])

    else:
        ccop = None

    return ccop


def eval_cfunc(
    runner: EngineRunner,
    params: dict[str, Any],
    output: dict[str, BinArray],
) -> None:
    """Evaluate a classical function using the coprocessor.

    Executes a classical function through the CCOP interface, handling
    argument preparation, function dispatch, and result assignment to
    output variables.

    Args:
        runner: Engine runner containing CCOP and execution context.
        params: Function parameters including function name, arguments, and assignments.
        output: Dictionary for storing function results.

    Raises:
        MissingCCOPError: If CCOP is not available or function is not found.
        NotImplementedError: If return value types are unsupported.
    """
    func = params["func"]
    assign_vars = params["assign_vars"]
    args = params["args"]

    valargs = [(sym, output[sym]) for sym in args]

    try:
        if runner.debug and func.startswith("sim_"):
            vals = sim_exec(func, runner, valargs)

        else:
            vals = runner.ccop.exec(func, valargs, debug=runner.debug)

    except AttributeError:
        ccop = runner.circuit.metadata["ccop"]
        ccop_type = runner.circuit.metadata["ccop_type"]

        if ccop is None:
            msg = f"Wasm ({ccop_type}) function not found: {func} with args: {args}"
            raise MissingCCOPError(msg) from AttributeError

        msg = f"Classical coprocessor object not assigned or missing exec method. Wasm-type = {ccop_type}"
        raise MissingCCOPError(msg) from AttributeError

    if assign_vars:
        if len(assign_vars) == 1:
            a_obj = output[assign_vars[0]]
            if runner.debug and func.startswith("sim_"):
                output[assign_vars[0]] = vals
            else:
                b = BinArray(a_obj.size, int(vals))
                a_obj.set(b)

        else:
            for asym, b in zip(assign_vars, vals, strict=False):
                a_obj = output[asym]

                if runner.debug and func.startswith("sim_"):
                    output[asym] = b
                elif isinstance(b, int):
                    bin_array = BinArray(
                        a_obj.size,
                        int(b),
                    )
                    a_obj.set(bin_array)
                else:
                    msg = "Only int return values are supported currently"
                    raise NotImplementedError(msg)
