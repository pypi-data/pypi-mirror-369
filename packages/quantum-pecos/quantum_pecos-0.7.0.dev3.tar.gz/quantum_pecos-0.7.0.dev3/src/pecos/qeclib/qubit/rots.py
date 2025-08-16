"""Rotation gate implementations for qubits.

This module provides implementations of rotation gates around different
axes of the Bloch sphere, including parameterized rotations used in
quantum error correction and quantum algorithms.
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

from pecos.qeclib.qubit.qgate_base import QGate, TQGate


class RXGate(QGate):
    """X-axis rotation gate.

    This gate performs a rotation around the X-axis of the Bloch sphere.
    """

    has_parameters = True


RX = RXGate()


class RYGate(QGate):
    """Y-axis rotation gate.

    This gate performs a rotation around the Y-axis of the Bloch sphere.
    """

    has_parameters = True


RY = RYGate()


class RZGate(QGate):
    """Z-axis rotation gate.

    This gate performs a rotation around the Z-axis of the Bloch sphere.
    """

    has_parameters = True


RZ = RZGate()


class RZZGate(TQGate):
    """Two-qubit ZZ rotation gate.

    This gate performs a rotation around the ZZ-axis for two qubits.
    """

    has_parameters = True


RZZ = RZZGate()
