import abc
import typing as ty
from enum import Enum
from typing import Union, Iterable
import pyqpanda3.core as pq


class Wrapper(abc.ABC):

    @abc.abstractmethod
    def __init__(self, routine):
        """Initialise the wrapper with the given routine

        :param routine: a framework-specific routine that will be wrapped.
        """
        pass

    @abc.abstractmethod
    def __iter__(self) -> ty.Iterable["Wrapper"]:
        """Magic Python method to make the RoutineWrapper object iterable.

        :return: an iterable over all the subroutines called by the wrapped routine.
            The subroutines should be wrapped by the RoutineWrapper.
        """
        pass

    @property
    def ops(self):
        return list(self)

    @property
    @abc.abstractmethod
    def is_base(self) -> bool:
        """Check if the wrapped routine is a "base" routine.

        Base routines are routines that are considered as primitive, i.e. that do not
        call any subroutine.
        The concept of base routine is essential for qprof as only base routines should
        have an entry in the "gate_times" dictionary provided to the "profile" method
        and base routines are used to stop the recursion into the call-tree.

        :return: True if the wrapped routine is considered as a "base" routine,
            else False.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the name of the wrapped subroutine."""
        pass

    @abc.abstractmethod
    def __hash__(self) -> int:
        """Computes the hash of the wrapped routine.

        __hash__ and __eq__ methods are used by qprof to cache routines and re-use
        already computed data. This optimisation gives impressive results on some
        circuits and is expected to improve the runtime of qprof on nearly all
        quantum circuits, because routines are most of the time re-used.

        :return: int representing a hash of the wrapper routine.
        """
        pass

    @abc.abstractmethod
    def __eq__(self, other: "Wrapper") -> bool:
        """Equality testing for wrapped routines.

        __hash__ and __eq__ methods are used by qprof to cache routines and re-use
        already computed data. This optimisation gives impressive results on some
        circuits and is expected to improve the runtime of qprof on nearly all
        quantum circuits, because routines are most of the time re-used.

        Two routines should be considered equal if and only if they generate exactly
        the same circuit.

        Comparing the generated circuits might be a costly task, but other methods
        can be used. For example, routines with the same name and the same parameters
        might be considered as equal (may be framework-dependent).

        :param other: instance of RoutineWrapper to test for equality with self.
        :return: True if self and other are equal (i.e. generate the exact same
            quantum circuit) else False.
        """
        pass


class QPandaWrapper(Wrapper):
    class QPandaType(Enum):
        QCircuit = 'QCircuit'
        QGate = 'QGate'

    def __init__(self, qcirc: Union[pq.QCircuit, pq.QGate]):
        # super().__init__()
        if isinstance(qcirc, pq.QCircuit):
            self.type = QPandaWrapper.QPandaType.QCircuit
        else:
            self.type = QPandaWrapper.QPandaType.QGate

        self._main_operation = qcirc
        self._name = qcirc.name()

    def __iter__(self) -> Iterable["QPandaWrapper"]:
        for op in self._main_operation.operations():
            yield QPandaWrapper(op)

    @property
    def ops(self):
        return list(self)

    @property
    def is_base(self):
        return self.type == QPandaWrapper.QPandaType.QGate

    @property
    def name(self):
        return self._name

    def __hash__(self):
        """Get the hash of the wrapped instruction

        :return: hash of the wrapped instruction
        """

        if self.type == QPandaWrapper.QPandaType.QGate:
            instr = self._main_operation
            return hash((self.name, tuple(instr.parameters())))
        else:
            return hash((self.name,))

    def __eq__(self, other: "QPandaWrapper"):
        """Equality testing.

        :param other: right-hand side of the equality operator
        :return: True if self and other are equal, else False
        """
        if self.type == QPandaWrapper.QPandaType.QCircuit:
            return self.name == other.name
        else:
            sinstr: Instruction = self._main_operation
            oinstr: Instruction = other._main_operation
            return (
                    sinstr.name() == oinstr.name()
                    and len(sinstr.parameters()) == len(oinstr.parameters())
                    and all(sp == op for sp, op in zip(sinstr.parameters(), oinstr.parameters()))
            )
