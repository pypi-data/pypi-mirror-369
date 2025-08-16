"""Logical Z measurement implementations for the Steane 7-qubit code.

This module provides logical Z measurement implementations for the Steane 7-qubit code, enabling measurements in the Z
basis while preserving error correction capabilities.
"""

# Copyright 2024 The PECOS Developers
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License.You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from pecos.qeclib import qubit
from pecos.slr import Block, Comment, CReg, QReg, Qubit


class NoFlagMeasureZ(Block):
    """Non-flagged logical Z measurement for Steane code.

    This class performs a logical Z measurement without using flag qubits
    for error detection during the measurement process.
    """

    def __init__(self, d: list[Qubit], a: QReg, out: CReg) -> None:
        """Initialize NoFlagMeasureZ block for non-flagged logical Z measurement.

        Args:
            d: List of data qubits for the logical measurement.
            a: Ancilla qubit register for the measurement.
            out: Classical register to store the measurement result.
        """
        super().__init__()

        self.extend(
            Comment("Measure logical Z with no flagging"),
            qubit.Prep(a[0]),
            qubit.H(a[0]),
            qubit.CZ(
                (d[0], a[0]),
                (d[1], a[0]),
                (d[2], a[0]),
            ),
            qubit.H(a[0]),
            qubit.Measure(a[0]) > out[0],
        )
