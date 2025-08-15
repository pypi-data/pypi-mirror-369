from collections import Counter
import typing as ty
from .data import ProgramData
from .Wrapper import QPandaWrapper, Wrapper
from .GprofExporter import BaseExporter, GprofExporter
from .exceptions import UnknownGateFound


class RoutineTree:
    def __init__(self, main_routine, gate_times: dict, wrapper=QPandaWrapper, **param):
        self._factory = RoutineNodeFactory()
        self._root = self._factory.get(
            wrapper(main_routine), gate_times
        )
        # Create the data structure that will store the call data.
        self._program_data: ProgramData = ProgramData(
            self._root.self_time + self._root.subroutines_times,
            register_base_subroutine_calls=param.get('use_base_cell', True)
        )
        # Enter the recursive exploration.
        self._root.first_pass_routines_data(self._program_data)

    def export(self, exporter: BaseExporter) -> ty.Union[str, bytes]:
        return exporter.export(self._program_data)


# self._cache[routine_wrapper] = RoutineNode(routine_wrapper, self, gate_times)
class RoutineNode:
    def __init__(
            self,
            routine: Wrapper,
            factory: "RoutineNodeFactory",
            gate_times: dict,
            unknown_name: str = "Unknown",
    ):
        self.unknown_name = unknown_name
        self._routine = routine

        self.self_time = 0
        self.subroutines_times = 0
        self._subroutines: ty.List["RoutineNode"] = list()
        # Stop early when we are on a terminal node.
        if RoutineNode._should_stop_recursion(self, gate_times):
            self.self_time = RoutineNode._get_gate_time(self.name, gate_times)
            return
        # Else, recurse and initialise self.{_subroutines, self_time, subroutines_times}
        for subroutine in routine:
            try:
                child_node: RoutineNode = factory.get(subroutine, gate_times)
            except UnknownGateFound as e:
                e.add_called_by(self.name)
                raise
            self._subroutines.append(child_node)
            self.subroutines_times += child_node.total_time
        # Finally, count the subroutine calls.
        self._subroutines_counter: ty.Dict["RoutineNode", int] = Counter(
            self._subroutines
        )

    @staticmethod
    def _get_gate_time(gate_name: str, gate_times: ty.Dict[str, int]) -> int:
        upper_gate_name: str = gate_name.upper()
        if upper_gate_name not in gate_times:
            raise UnknownGateFound(
                f"The gate '{upper_gate_name}' is considered as a base gate but is not "
                f"present in the provided gate times. Provided gate times are: "
                f"{gate_times}. Please add the gate '{upper_gate_name}' in the "
                f"provided gate execution times.",
                upper_gate_name,
            )
        return gate_times[upper_gate_name]

    @staticmethod
    def _should_stop_recursion(
            node: "RoutineNode", gate_times: ty.Dict[str, int]
    ) -> bool:
        return node._routine.name.upper() in gate_times or node._routine.is_base

    @property
    def name(self):
        return self.unknown_name if not self._routine.name else self._routine.name

    @property
    def is_base(self):
        return len(self._subroutines) == 0

    @property
    def total_time(self):
        return self.self_time + self.subroutines_times

    def first_pass_routines_data(self, data: ProgramData):
        data.add_subroutine(self.name)
        data.add_entry_point_call(self.name, 1, self.self_time, self.subroutines_times)
        self._first_pass_routines_data_impl(data)

    def _first_pass_routines_data_impl(
            self, data: ProgramData, number_of_calls: int = 1
    ):
        # Explore subroutines
        for subroutine, count in self._subroutines_counter.items():
            # If the subroutine should be added, add it to the data.
            if subroutine.name not in data.indices and (
                    data.register_base_subroutine_calls or not subroutine.is_base
            ):
                data.add_subroutine(subroutine.name)

            number_of_subroutine_calls: int = count * number_of_calls

            if subroutine.is_base:
                add_subroutine_method = data.add_base_subroutine_call
            else:
                add_subroutine_method = data.add_subroutine_call
            add_subroutine_method(
                self.name,
                subroutine.name,
                number_of_subroutine_calls,
                number_of_subroutine_calls * subroutine.self_time,
                number_of_subroutine_calls * subroutine.subroutines_times,
            )

            # Recurse if not base
            if not subroutine.is_base:
                subroutine._first_pass_routines_data_impl(
                    data, number_of_subroutine_calls
                )


class RoutineNodeFactory:
    def __init__(self):
        self._cache: ty.Dict[Wrapper, "RoutineNode"] = dict()

    def get(
            self,
            routine_wrapper: Wrapper,
            gate_times: dict,
    ) -> "RoutineNode":
        if routine_wrapper not in self._cache:
            self._cache[routine_wrapper] = RoutineNode(
                routine_wrapper, self, gate_times
            )
        return self._cache[routine_wrapper]


def profile(
        routine,
        gate_times: dict,
        exporter_kwargs: ty.Optional[ty.Dict[str, ty.Any]] = None,
        include_native_gates: bool = True,
        **framework_kwargs,
) -> ty.Union[str, bytes]:
    """Profile the given routine.

    :param routine: The routine to profile.
    :param gate_times: A dictionary whose keys are routine names and values are
        the execution time of the associated routine name.
    :param exporter: The output format to use. Can be either an instance of a
        subclass of BaseExporter or a string. Possible string values can be found in
        the keys of qprof.exporters.default_exporters.
    :param exporter_kwargs: keyword arguments forwarded to the exporter. See the
        exporter documentation for details.
    :param include_native_gates: True to include native gates in the report, else False.
        If native gates are included, the self-time of all the non-native subroutines
        will be 0.
    :param framework_kwargs: keyword arguments forwarded to the framework-specific
        RoutineWrapper. See the RoutineWrapper documentation for details.
    :return: a string that is formatted like gprof's output.
    """
    if exporter_kwargs is None:
        exporter_kwargs = dict()
    wrapper = framework_kwargs.get('wrapper',QPandaWrapper)
    tree = RoutineTree(routine, gate_times,wrapper)
    exporter = GprofExporter(**exporter_kwargs)
    return tree.export(exporter)
