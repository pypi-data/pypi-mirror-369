# ======================================================================================
#
# Copyright: CERFACS, LIRMM, Total S.A. - the quantum computing team (March 2021)
# Contributor: Adrien Suau (adrien.suau@cerfacs.fr)
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your discretion) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.
#
# See the GNU Lesser General Public License for more details. You should have received
# a copy of the GNU Lesser General Public License along with this program. If not, see
# https://www.gnu.org/licenses/lgpl-3.0.txt
#
# ======================================================================================


class QprofException(BaseException):
    def __init__(self, message: str):
        super(QprofException, self).__init__(message)


class UnknownGateFound(QprofException):
    def __init__(self, message: str, unknown_gate_name: str):
        super(UnknownGateFound, self).__init__(message)
        self.stack_trace = [unknown_gate_name]

    def add_called_by(self, caller: str):
        self.stack_trace.append(caller)

    def __str__(self):
        return "\n".join(
            [
                super(UnknownGateFound, self).__str__(),
                "Stack trace: " + " -> ".join(reversed(self.stack_trace)),
            ]
        )


class UnsupportedPluginAPI(QprofException):
    def __init__(self, plugin_module_name: str):
        super(UnsupportedPluginAPI, self).__init__(plugin_module_name)
