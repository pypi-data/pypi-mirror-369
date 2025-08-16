# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Module in the ansys-turbogrid-api package that is internally used by modules in the pyturbogrid package for interactions with a running Ansys TurboGrid application.
"""

from enum import Enum

class PyTurboGrid:
    """
    This class enables you to launch, interact with, and quit, a session of TurboGrid.
    Refer to the :py:mod:`launcher` module to see how to create an instance of this class.
    """

    class TurboGridLocationType(Enum):
        TURBOGRID_INSTALL = 1
        TURBOGRID_RUNNING_CONTAINER = 2

    class TurboGridLogLevel(Enum):
        CRITICAL = 50
        ERROR = 40
        WARNING = 30
        INFO = 20
        NETWORK_DEBUG = 15
        DEBUG = 10
        NOTSET = 0

    def __init__(
        self,
        socket_port: int | None,
        turbogrid_location_type: TurboGridLocationType,
        cfxtg_location: str,
        additional_args_str: str | None,
        additional_kw_args: dict | None,
        log_level=TurboGridLogLevel.INFO,
    ): ...
    def read_inf(self, filename: str) -> None:
        """Read a blade model from a BladeGen \*.inf file.

        :param filename: Name or path for the Bladegen \*.inf file.
        :type filename: str
        """
        ...

    def read_ndf(
        self, ndffilename: str, cadfilename: str, flowpath: str, bladerow: str, bladename: str
    ) -> None:
        """Read a blade model from an NDF (\*.ndf) file.
        TurboGrid uses the details in the NDF file to generate and import a CAD file containing the blade geometry.

        :param ndffilename: Name or path for the NDF (\*.ndf) file.
        :type ndffilename: str
        :param cadfilename: Name of the CAD \*.x_b file to be generated.
        :type cadfilename: str
        :param flowpath: Name of the flowpath to use.
        :type flowpath: str
        :param bladerow: Name of the blade row to select.
        :type bladerow: str
        :param bladename: Name of the blade to load.
        :type bladename: str
        """
        ...

    def read_session(self, filename: str) -> None:
        """
        Read a session file to repeat a previous session.

        :param filename: Name of the session file.
        :type filename: str
        """
        ...

    def read_state(self, filename: str) -> None:
        """
        Restore a previous state from a saved state file.

        :param filename: Name of the state file.
        :type filename: str
        """
        ...

    def save_mesh(self, filename: str, onefile: str, onedomain: str) -> None:
        """
        Save generated mesh to a file.

        :param filename: Name of the mesh file to save.
        :type filename: str
        :param onefile: If enabled (true), write all of the available meshes to a single mesh file. The default is ``true``.
        :type onefile: str
        :param onedomain: If enabled (true), combine any inlet and outlet domain meshes with the passage domain,
            to form a single assembly. The default is ``true``.
        :type onedomain: str
        """
        ...

    def save_state(self, filename: str) -> None:
        """Save TurboGrid state into a file.

        :param filename: Name of the file to save.
        :type filename: str
        """
        ...

    def set_global_size_factor(self, global_size_factor: str) -> None:
        """
        Set global size factor.

        :param global_size_factor: Value to use as size factor in string format.
        :type global_size_factor: str
        """
        ...

    def set_inlet_hub_position(self, parametric_hub_location: str) -> None:
        """
        Set the parametric position of the inlet line on the hub.

        :param parametric_hub_location: Value to be used as parametric location in string format.
        :type parametric_hub_location: str
        """
        ...

    def set_inlet_shroud_position(self, parametric_shroud_location: str) -> None:
        """
        Set the parametric position of the inlet line on the shroud.

        :param parametric_shroud_location: Value to be used as parametric location in string format.
        :type parametric_shroud_location: str
        """
        ...

    def set_obj_param(self, object: str, param_val_pairs: str) -> None:
        """
        Update the value for a CCL object parameter.

        :param object: Name with full path for the CCL object.
        :type object: str
        :param param_val_pairs: Name and value pair for the parameter to set.
        :type param_val_pairs: str
        """
        ...

    def set_outlet_hub_position(self, parametric_hub_location: str) -> None:
        """
        Set the parametric position of the outlet line on the hub.

        :param parametric_hub_location: Value to be used as parametric location in string format.
        :type parametric_hub_location: str
        """
        ...

    def set_outlet_shroud_position(self, parametric_shroud_location: str) -> None:
        """
        Set the parametric position of the outlet line on the shroud.

        :param parametric_shroud_location: Value to be used as parametric location in string format.
        :type parametric_shroud_location: str
        """
        ...

    def set_topology_choice(self, atm_topology_choice: str) -> None:
        """
        Set the topology method to be used for the topology set generation process.

        :param atm_topology_choice: Name of the topology method to be used.
        :type atm_topology_choice: str

        Example

        >>> turbogrid.set_topology_choice("Single Round Round Refined")

        """
        ...

    def set_topology_list(self, atm_topology_list: str) -> None:
        """
        Set the list of topology pieces to be used for topology generation.

        :param atm_topology_list: The topology piece names concatenated using underscores.
        :type atm_topology_list: str

        Example

        >>> turbogrid.set_topology_list("LECircleHigh_TECircleLow")

        """
        ...

    def start_session(self, filename: str) -> None:
        """
        Start recording a new TurboGrid session.

        :param filename: Name of the session file.
        :type filename: str
        """
        ...

    def unsuspend(self, object: str) -> None:
        """
        Unsuspend a TurboGrid object.

        :param object: String specifying the name and type of the object to be unsuspended.
        :type object: str

        Example

        >>> turbogrid.unsuspend(object="/TOPOLOGY SET")

        """
        ...

    def query_mesh_statistics(self, domain: str) -> dict:
        """
        Returns mesh quality measures from TurboGrid for the current session and specified domain.
        **Note**: It is suggested to use the :py:mod:`mesh_statistics` module instead of directly calling this.

        :param domain: Name of the domain from which to obtain the measurements.
        :type domain: str
        :return: A dictionary form of the quality measurements.
        :rtype: dict

        """
        ...

    def query_mesh_statistics_histogram_data(
        self,
        variable: str,
        domain: str,
        number_of_bins: int,
        upper_bound: float,
        lower_bound: float,
        bin_units: str,
        scale: str,
        use_absolute_values: bool,
        bin_divisions: list,
    ) -> dict:
        """
        Returns data that can be used to plot mesh statistics histograms.

        :param variable: Name of the quality measurement to query from the statistics.
        :type variable: str
        :param domain: Name of the domain from which to obtain the measuments.
        :type domain: str
        :param number_of_bins: Number of histogram columns to use.
        :type number_of_bins: int
        :param upper_bound: The maximum limit for the horizontal axis.
        :type upper_bound: float
        :param lower_bound: The minimum limit for the horizontal axis.
        :type lower_bound: float
        :param bin_units: The unit to use for the horizontal ax1s.
        :type bin_units: str
        :param scale: Scaling type for the horizontal axis: 'linear' or 'logarithmic'.
        :type scale: str
        :param use_absolute_values: Choice of whether to use absolute or percentage values on the vertical axis.
        :type use_absolute_values: bool
        :param bin_divisions: User-provided bin divisions.
        :type bin_divisions: list
        :return: A dictionary form of the statistics for the requested quality measurement.
        :rtype: dict
        """
        ...

    def query_valid_topology_choices(self) -> list:
        """
        Returns the permitted topology methods for the blade geometry in the current session.

        :return: List of topology method names.
        :rtype: list
        """
        ...

    def quit(self) -> None:
        """Quit the PyTurboGrid instance."""
        ...

    def end_session(self) -> None:
        """Stop recording a TurboGrid session file."""
        ...
