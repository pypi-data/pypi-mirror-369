import typing as ty
from .data import ProgramData, RoutineCallsData, RoutineData
import abc
from .strings import (
    _flat_profile_footer,
    _flat_profile_header,
    _call_graph_footer,
    _copyright,
    _call_graph_header,
    _index_header,
)



class BaseExporter(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def export(self, data: ProgramData) -> ty.Union[str, bytes]:
        """Export the given data.

        :param data: data of the program to export
        :return: a representation of the exported data
        """
        pass

class GprofExporter(BaseExporter):
    def __init__(self, default_time: ty.Optional[float] = 10):
        """Initialise the GprofExporter.

        :param default_time: arbitrary time value that will be used as the reference.
            If None, no scaling will be performed. If a float is given,
            the subroutines execution times will be scaled such that the longest
            subroutine execution time will be `default_time`.
        """
        super().__init__()
        self.default_time = default_time

    def export(self, data: ProgramData) -> str:
        seconds_scale: float = GprofExporter.get_second_scale(data, self.default_time)
        return "\n\n".join(
            [
                GprofExporter.generate_flat_profile(data, seconds_scale),
                GprofExporter.generate_call_graph(data, seconds_scale),
                GprofExporter.generate_index_by_function_names(data),
            ]
        )

    @staticmethod
    def get_second_scale(data: ProgramData, default_time: ty.Optional[float]) -> float:
        """Compute the scaling on seconds needed in order to have meaningful results.

        The gprof output format has a low precision of 0.01 seconds, i.e. 10
        milli-seconds. If the quantum routines of the program all take less than 10
        ms then the precision of the output format is not sufficient and the output
        will have no value. In order to circumvent this, the time taken by all the
        routines is scaled up.

        For the moment, the timings are scaled such that the longest subroutine will
        take `default_time` seconds.

        :param data: quantum program call data.
        :param default_time: arbitrary time value that will be used as the reference.
            If None, no scaling will be performed.
        :return: the floating point value that should scale all the timings.
        """
        if default_time is None:
            return 1.0

        routines_self_times_nano_seconds = [
            rout_data.self_call.self_nano_seconds
            for rout_data in data.routines_data.values()
        ]
        maximum_self_time_nano_seconds = max(routines_self_times_nano_seconds)
        return default_time / (maximum_self_time_nano_seconds / 10 ** 9)

    @staticmethod
    def generate_flat_profile(data: ProgramData, seconds_scale: float = 1.0) -> str:
        format_string = (
            "{0:>6.2f} {1:>9.2f} {2:>8.2f} {3:>8} {4:>8.2f} {5:>8.2f}  {6:<}"
        )

        routines_data = [
            {
                "% time": (
                    100
                    * rout_data.self_call.self_nano_seconds
                    / data.total_time_nanoseconds
                ),
                "cumulative seconds": 0.0,  # Computed later
                "self seconds": (
                    seconds_scale * rout_data.self_call.self_nano_seconds / 10 ** 9
                ),
                "calls": rout_data.self_call.number,
                "self ms/call": (
                    seconds_scale
                    * rout_data.self_call.self_nano_seconds
                    / 10 ** 6
                    / rout_data.self_call.number
                ),
                "total ms/call": seconds_scale
                * (
                    rout_data.self_call.self_nano_seconds
                    + rout_data.self_call.subroutines_nano_seconds
                )
                / 10 ** 6
                / rout_data.self_call.number,
                "name": rout_name,
            }
            for rout_name, rout_data in data.routines_data.items()
            if rout_name != data.entry_point
        ]
        # First sort by name
        routines_data.sort(key=lambda e: e["name"])
        # Then sort by decreasing number of calls
        routines_data.sort(key=lambda e: e["calls"], reverse=True)
        # Finally sort by decreasing runtime
        routines_data.sort(key=lambda e: e["self seconds"], reverse=True)
        # Compute the cumulative seconds field
        routines_data[0]["cumulative seconds"] = routines_data[0]["self seconds"]
        for i in range(1, len(routines_data)):
            routines_data[i]["cumulative seconds"] = (
                routines_data[i - 1]["cumulative seconds"]
                + routines_data[i]["self seconds"]
            )

        data_str = "\n".join(
            format_string.format(*data.values()) for data in routines_data
        )

        return _flat_profile_header + data_str + _flat_profile_footer + _copyright

    @staticmethod
    def _compute_call_data(routine_name: str, seconds_scale: float):
        pass

    @staticmethod
    def _routine_string_index(routine_name: str, data: ProgramData) -> str:
        return (
            # Note: gprof indices start at 1
            "{} [{}]".format(routine_name, data.indices[routine_name] + 1)
            if routine_name in data.indices
            else routine_name
        )

    @staticmethod
    def _routine_index_string(routine_name: str, data: ProgramData) -> str:
        return (
            # Note: gprof indices start at 1
            "[{}] {}".format(data.indices[routine_name] + 1, routine_name)
            if routine_name in data.indices
            else routine_name
        )

    @staticmethod
    def generate_call_graph(data: ProgramData, seconds_scale: float = 1.0) -> str:
        main_routine_format_string = (
            "{0:<5}  {1:>5.1f} {2:>7.2f} {3:^10.2f} {4:^10}   {5:<}"
        )
        call_data_format_string = (
            " " * len("index % time ") + "{0:>7.2f} {1:^10.2f} {2:^10}       {3:<}"
        )
        routines_strings = []
        for rout_name in sorted(
            data.indices.keys(),
            key=lambda kv: data.indices[kv],
        ):
            rout_data: RoutineData = data.routines_data[rout_name]
            called_by_data: ty.Dict[str, RoutineCallsData] = rout_data.called_by
            calls_data: ty.Dict[str, RoutineCallsData] = rout_data.subroutine_calls
            # Generate the lines about routines that called the current routine.
            called_by_str = "\n".join(
                [
                    call_data_format_string.format(
                        # self
                        # This is the amount of time that was propagated directly
                        # from the function into this parent.
                        seconds_scale * caller_data.self_nano_seconds / 10 ** 9,
                        # children
                        # This is the amount of time that was propagated from the
                        # function's children into this parent.
                        seconds_scale * caller_data.subroutines_nano_seconds / 10 ** 9,
                        # called
                        # This is the number of times this parent called the function
                        # `/' the total number of times the function was called.
                        # Recursive calls to the function are not included in the
                        # number after the `/'.
                        "{}/{}".format(
                            # Number of calls of `rout_name` from `caller_name`
                            caller_data.number,
                            # Total number of calls of `rout_name`
                            rout_data.self_call.number,
                        ),
                        # name
                        # This is the name of the parent. The parent's index number
                        # is printed after it. If the parent is a member of a cycle,
                        # the cycle number is printed between the name and the index
                        # number.
                        GprofExporter._routine_string_index(caller_name, data),
                    )
                    if caller_name != data.entry_point
                    else (" " * 49 + data.entry_point)
                    for caller_name, caller_data in called_by_data.items()
                ]
            )
            # Generate the line for the current routine
            primary_line_str = main_routine_format_string.format(
                # Function index
                # Note: gprof indices start at 1
                "[{}]".format(data.indices[rout_name] + 1),
                # Percent of total spent in this function and its children
                100
                * (
                    rout_data.self_call.self_nano_seconds
                    + rout_data.self_call.subroutines_nano_seconds
                )
                / data.total_time_nanoseconds,
                # self time
                seconds_scale * rout_data.self_call.self_nano_seconds / 10 ** 9,
                # children time
                seconds_scale * rout_data.self_call.subroutines_nano_seconds / 10 ** 9,
                # number of calls
                rout_data.self_call.number,
                # name of the routine + index
                GprofExporter._routine_string_index(rout_name, data),
            )
            calls_str = "\n".join(
                [
                    call_data_format_string.format(
                        # self
                        # This is the amount of time that was propagated directly
                        # from the child into the function.
                        seconds_scale * called_data.self_nano_seconds / 10 ** 9,
                        # children
                        # This is the amount of time that was propagated from the
                        # child's children to the function.
                        seconds_scale * called_data.subroutines_nano_seconds / 10 ** 9,
                        # called
                        # This is the number of times the function called this child
                        # `/' the total number of times the child was called.
                        # Recursive calls by the child are not listed in the number
                        # after the `/'.
                        "{}/{}".format(
                            # Number of calls of `called_name` from `rout_name`
                            called_data.number,
                            # Total number of calls of `called_name`
                            data.routines_data[called_name].self_call.number,
                        ),
                        # name
                        # This is the name of the child. The child's index number is
                        # printed after it. If the child is a member of a cycle,
                        # the cycle number is printed between the name and the index
                        # number.
                        GprofExporter._routine_string_index(called_name, data),
                    )
                    for called_name, called_data in calls_data.items()
                ]
            )
            routines_strings.append(
                "\n".join([called_by_str, primary_line_str, calls_str])
            )

        return (
            _call_graph_header
            + "\n-----------------------------------------------\n".join(
                routines_strings
            )
            + "\n-----------------------------------------------\n"
            + _call_graph_footer
            + _copyright
        )

    @staticmethod
    def generate_index_by_function_names(data) -> str:
        routines_names = sorted(
            data.indices.keys(), key=lambda rout_name: data.indices[rout_name]
        )
        left_column_strs = [
            GprofExporter._routine_index_string(rout_name, data)
            for rout_name in routines_names[::2]
        ]
        right_column_strs = [
            GprofExporter._routine_index_string(rout_name, data)
            for rout_name in routines_names[1::2]
        ]
        max_len_left = max(map(len, left_column_strs))
        format_left_str = "{:<" + str(max_len_left + 1) + "}"
        if len(right_column_strs) != len(left_column_strs):
            right_column_strs.append("")

        return (
            _index_header
            + "\n"
            + "\n".join(
                [
                    format_left_str.format(l) + r
                    for l, r in zip(left_column_strs, right_column_strs)
                ]
            )
        )
