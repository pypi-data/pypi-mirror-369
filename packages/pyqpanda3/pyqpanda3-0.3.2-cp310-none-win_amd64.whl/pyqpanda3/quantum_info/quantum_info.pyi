import numpy
from typing import Any, Callable, ClassVar, overload

class Chi:
    @overload
    def __init__(self, other: Chi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Chi, other: quantum_info.Chi) -> None


        @brief Generate Chi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        2. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Choi) -> None


        @brief Generate Chi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Chi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Chi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Chi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Chi, other: quantum_info.Chi) -> None


        @brief Generate Chi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        2. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Choi) -> None


        @brief Generate Chi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Chi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Chi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Chi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Chi, other: quantum_info.Chi) -> None


        @brief Generate Chi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        2. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Choi) -> None


        @brief Generate Chi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Chi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Chi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Chi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Chi, other: quantum_info.Chi) -> None


        @brief Generate Chi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        2. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Choi) -> None


        @brief Generate Chi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Chi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Chi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Chi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Chi, other: quantum_info.Chi) -> None


        @brief Generate Chi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        2. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Choi) -> None


        @brief Generate Chi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Chi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Chi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.Chi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Chi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    def evolve(self, *args, **kwargs):
        """evolve(*args, **kwargs)
        Overloaded function.

        1. evolve(self: quantum_info.Chi, state: QPanda3::QuantumInformation::DensityMatrix) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (density matrix) and return the result as a DensityMatrix object.
        @param state a DensityMatrix object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            

        2. evolve(self: quantum_info.Chi, state: QPanda3::QuantumInformation::StateVector) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (state vector).
        @param state a StateVector object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            
        """
    def get_input_dim(self) -> int:
        """get_input_dim(self: quantum_info.Chi) -> int


        @brief Get the input dimension of the QuantumChannel

        @return size_t the input dimension of the QuantumChannel
            
        """
    def get_output_dim(self) -> int:
        """get_output_dim(self: quantum_info.Chi) -> int


        @brief Get the output dimension of the QuantumChannel

        @return size_t the output dimension of the QuantumChannel

        """
    def ndarray(self) -> numpy.ndarray[numpy.complex128]:
        """ndarray(self: quantum_info.Chi) -> numpy.ndarray[numpy.complex128]


        @brief Return internal data as a numpy.ndarray.
        @return numpy.ndarray The internal data.
            
        """
    def __eq__(self, other: Chi) -> bool:
        """__eq__(self: quantum_info.Chi, other: quantum_info.Chi) -> bool


        @brief Equality check. Determine if the internal data of two Chi objects are equal.
        @param other another Chi object

        @return Bool if they are same, return true.
            
        """

class Choi:
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Choi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            

        2. __init__(self: quantum_info.Choi, other: quantum_info.Choi) -> None


        @brief Generate Choi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Choi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Choi, other: quantum_info.Chi) -> None


        @brief Generate Choi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        5. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Choi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            
        """
    @overload
    def __init__(self, other: Choi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Choi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            

        2. __init__(self: quantum_info.Choi, other: quantum_info.Choi) -> None


        @brief Generate Choi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Choi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Choi, other: quantum_info.Chi) -> None


        @brief Generate Choi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        5. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Choi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Choi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            

        2. __init__(self: quantum_info.Choi, other: quantum_info.Choi) -> None


        @brief Generate Choi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Choi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Choi, other: quantum_info.Chi) -> None


        @brief Generate Choi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        5. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Choi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            
        """
    @overload
    def __init__(self, other: Chi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Choi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            

        2. __init__(self: quantum_info.Choi, other: quantum_info.Choi) -> None


        @brief Generate Choi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Choi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Choi, other: quantum_info.Chi) -> None


        @brief Generate Choi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        5. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Choi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate Choi object based on a Kraus object
        @param other a quantum channel as a Kraus object
            

        2. __init__(self: quantum_info.Choi, other: quantum_info.Choi) -> None


        @brief Generate Choi object based on a Choi object
        @param other a quantum channel as a Choi object
            

        3. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate Choi object based on a PTM object
        @param other a quantum channel as a PTM object
            

        4. __init__(self: quantum_info.Choi, other: quantum_info.Chi) -> None


        @brief Generate Choi object based on a Chi object
        @param other a quantum channel as a Chi object
            

        5. __init__(self: quantum_info.Choi, other: QPanda3::QuantumInformation::SuperOp) -> None


        @brief Generate Choi object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            
        """
    def evolve(self, *args, **kwargs):
        """evolve(*args, **kwargs)
        Overloaded function.

        1. evolve(self: quantum_info.Choi, state: QPanda3::QuantumInformation::DensityMatrix) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (density matrix) and return the result as a DensityMatrix object.
        @param state a DensityMatrix object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            

        2. evolve(self: quantum_info.Choi, state: QPanda3::QuantumInformation::StateVector) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (state vector).
        @param state a StateVector object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            
        """
    def get_input_dim(self) -> int:
        """get_input_dim(self: quantum_info.Choi) -> int


        @brief Get the input dimension of the QuantumChannel

        @return size_t the input dimension of the QuantumChannel
            
        """
    def get_output_dim(self) -> int:
        """get_output_dim(self: quantum_info.Choi) -> int


        @brief Get the output dimension of the QuantumChannel

        @return size_t the output dimension of the QuantumChannel
            
        """
    def __eq__(self, other: Choi) -> bool:
        """__eq__(self: quantum_info.Choi, other: quantum_info.Choi) -> bool


        @brief Equality check. Determine if the internal data of two Choi objects are equal.
        @param other another Choi object

        @return Bool if they are same, return true.
            
        """

class DensityMatrix:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.DensityMatrix) -> None


        @brief Default constructor, which by default constructs a density matrix for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> None


        @brief Generate a DensityMatrix object from another DensityMatrix
        @param other another DensityMatrix
            

        3. __init__(self: quantum_info.DensityMatrix, data: list[list[complex]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        4. __init__(self: quantum_info.DensityMatrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        5. __init__(self: quantum_info.DensityMatrix, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a density matrix where the state of each qubit is currently 0.
        @param qbit_total the total number of qubits in the quantum system
            

        6. __init__(self: quantum_info.DensityMatrix, other: QPanda3::QuantumInformation::StateVector) -> None


        @brief Construct a new DensityMatrix object based on an existing StateVector object.
        @param other an existing StateVector object.
            
        """
    @overload
    def __init__(self, other: DensityMatrix) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.DensityMatrix) -> None


        @brief Default constructor, which by default constructs a density matrix for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> None


        @brief Generate a DensityMatrix object from another DensityMatrix
        @param other another DensityMatrix
            

        3. __init__(self: quantum_info.DensityMatrix, data: list[list[complex]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        4. __init__(self: quantum_info.DensityMatrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        5. __init__(self: quantum_info.DensityMatrix, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a density matrix where the state of each qubit is currently 0.
        @param qbit_total the total number of qubits in the quantum system
            

        6. __init__(self: quantum_info.DensityMatrix, other: QPanda3::QuantumInformation::StateVector) -> None


        @brief Construct a new DensityMatrix object based on an existing StateVector object.
        @param other an existing StateVector object.
            
        """
    @overload
    def __init__(self, data: list[list[complex]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.DensityMatrix) -> None


        @brief Default constructor, which by default constructs a density matrix for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> None


        @brief Generate a DensityMatrix object from another DensityMatrix
        @param other another DensityMatrix
            

        3. __init__(self: quantum_info.DensityMatrix, data: list[list[complex]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        4. __init__(self: quantum_info.DensityMatrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        5. __init__(self: quantum_info.DensityMatrix, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a density matrix where the state of each qubit is currently 0.
        @param qbit_total the total number of qubits in the quantum system
            

        6. __init__(self: quantum_info.DensityMatrix, other: QPanda3::QuantumInformation::StateVector) -> None


        @brief Construct a new DensityMatrix object based on an existing StateVector object.
        @param other an existing StateVector object.
            
        """
    @overload
    def __init__(self, data: numpy.ndarray[numpy.complex128[m, n]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.DensityMatrix) -> None


        @brief Default constructor, which by default constructs a density matrix for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> None


        @brief Generate a DensityMatrix object from another DensityMatrix
        @param other another DensityMatrix
            

        3. __init__(self: quantum_info.DensityMatrix, data: list[list[complex]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        4. __init__(self: quantum_info.DensityMatrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        5. __init__(self: quantum_info.DensityMatrix, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a density matrix where the state of each qubit is currently 0.
        @param qbit_total the total number of qubits in the quantum system
            

        6. __init__(self: quantum_info.DensityMatrix, other: QPanda3::QuantumInformation::StateVector) -> None


        @brief Construct a new DensityMatrix object based on an existing StateVector object.
        @param other an existing StateVector object.
            
        """
    @overload
    def __init__(self, qbit_total: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.DensityMatrix) -> None


        @brief Default constructor, which by default constructs a density matrix for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> None


        @brief Generate a DensityMatrix object from another DensityMatrix
        @param other another DensityMatrix
            

        3. __init__(self: quantum_info.DensityMatrix, data: list[list[complex]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        4. __init__(self: quantum_info.DensityMatrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        5. __init__(self: quantum_info.DensityMatrix, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a density matrix where the state of each qubit is currently 0.
        @param qbit_total the total number of qubits in the quantum system
            

        6. __init__(self: quantum_info.DensityMatrix, other: QPanda3::QuantumInformation::StateVector) -> None


        @brief Construct a new DensityMatrix object based on an existing StateVector object.
        @param other an existing StateVector object.
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.DensityMatrix) -> None


        @brief Default constructor, which by default constructs a density matrix for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> None


        @brief Generate a DensityMatrix object from another DensityMatrix
        @param other another DensityMatrix
            

        3. __init__(self: quantum_info.DensityMatrix, data: list[list[complex]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        4. __init__(self: quantum_info.DensityMatrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a density matrix based on the input 2D complex number array.
        @param data a 2D complex number array
            

        5. __init__(self: quantum_info.DensityMatrix, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a density matrix where the state of each qubit is currently 0.
        @param qbit_total the total number of qubits in the quantum system
            

        6. __init__(self: quantum_info.DensityMatrix, other: QPanda3::QuantumInformation::StateVector) -> None


        @brief Construct a new DensityMatrix object based on an existing StateVector object.
        @param other an existing StateVector object.
            
        """
    def at(self, row_idx: int, col_idx: int) -> complex:
        """at(self: quantum_info.DensityMatrix, row_idx: int, col_idx: int) -> complex


        @brief Retrieve a specific element of the internal data using matrix row and column indices
        @param row_idx row indices
        @param col_idx col indices

        @return a specific element of the internal data
            
        """
    def dim(self) -> int:
        """dim(self: quantum_info.DensityMatrix) -> int


        @brief Retrieve the number of ground states corresponding to the density matrix

        @return the number of ground states corresponding to the density matrix.
            
        """
    def evolve(self, circuit) -> DensityMatrix:
        """evolve(self: quantum_info.DensityMatrix, circuit: QPanda3::QCircuit) -> quantum_info.DensityMatrix


        @brief Evolve the density matrix using the quantum circuit QCircuit without updating the internal data of the original DensityMatrix object; the evolution result is returned as a new DensityMatrix object
        @param circuit a quantum circuit QCircuit

        @return a new DensityMatrix object
            
        """
    def is_valid(self) -> bool:
        """is_valid(self: quantum_info.DensityMatrix) -> bool


        @brief Validate the internal data of the density matrix.

        @return if is valid, return true
            
        """
    def ndarray(self) -> numpy.ndarray[numpy.complex128]:
        """ndarray(self: quantum_info.DensityMatrix) -> numpy.ndarray[numpy.complex128]


        @brief Generate a numpy.ndarray object using data in self

        @return  a numpy.ndarray object
            
        """
    def purity(self) -> complex:
        """purity(self: quantum_info.DensityMatrix) -> complex


        @brief Retrieve the purity of the density matrix.

        @return the purity of the density matrix
            
        """
    def to_statevector(self) -> list[complex]:
        """to_statevector(self: quantum_info.DensityMatrix) -> list[complex]


        @brief Retrieve the corresponding state vector..

        @return the corresponding state vector
            
        """
    def update_by_evolve(self, circuit) -> DensityMatrix:
        """update_by_evolve(self: quantum_info.DensityMatrix, circuit: QPanda3::QCircuit) -> quantum_info.DensityMatrix


        @brief Evolve the density matrix using the quantum circuit QCircuit and update the internal data of the original DensityMatrix object
        @param circuit a quantum circuit QCircuit

        @return a new DensityMatrix object
            
        """
    def __eq__(self, other: DensityMatrix) -> bool:
        """__eq__(self: quantum_info.DensityMatrix, other: quantum_info.DensityMatrix) -> bool


        @brief Equality check. Determine if the internal data of two DensityMatrix objects are equal.
        @param DensityMatrix another DensityMatrix object

        @return Bool if they are same, return true.
            
        """

class Kraus:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, left: list[Matrix]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, left: list[Matrix], right: list[Matrix]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, matrix: Matrix) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: Choi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: Chi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: SuperOp) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: PTM) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: Kraus) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Kraus) -> None


        @brief Default constructor, generates a Kraus object with no elements
            

        2. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param left a kraus operator list
            

        3. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on a list of operators (an array of 2D matrices)..
        @detail The left operator list of the generated Kraus object is constructed from the input array of matrices, while the right operator list is empty
        @param right a kraus operator list
            

        4. __init__(self: quantum_info.Kraus, left: list[quantum_info.Matrix], right: list[quantum_info.Matrix]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        5. __init__(self: quantum_info.Kraus, left: list[numpy.ndarray[numpy.complex128[m, n]]], right: list[numpy.ndarray[numpy.complex128[m, n]]]) -> None


        @brief Construct a Kraus object based on two lists of operators (arrays of 2D matrices).
        @detail The left operator list of the generated Kraus object is constructed from the first input array, and the right operator list is constructed from the second input array.
        @param left a kraus operator list for left operator list of the generated Kraus object
        @param right a kraus operator list for right operator list of the generated Kraus object
            

        6. __init__(self: quantum_info.Kraus, matrix: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        7. __init__(self: quantum_info.Kraus, matrix: quantum_info.Matrix) -> None


        @brief Construct a Kraus object based on a single operator (a 2D matrix).
        @detail The left operator list of the generated Kraus object is constructed from the input. The right operator list of the generated Kraus object is empty.
        @param matrix a single operator (a 2D matrix)
            

        8. __init__(self: quantum_info.Kraus, other: quantum_info.Choi) -> None


        @brief Generate Kraus object based on a Choi object
        @param other a quantum channel as a Choi object
            

        9. __init__(self: quantum_info.Kraus, other: quantum_info.Chi) -> None


        @brief Generate Kraus object based on a Chi object
        @param other a quantum channel as a Chi object
            

        10. __init__(self: quantum_info.Kraus, other: quantum_info.SuperOp) -> None


        @brief Generate Kraus object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        11. __init__(self: quantum_info.Kraus, other: quantum_info.PTM) -> None


        @brief Generate Kraus object based on a PTM object
        @param other a quantum channel as a PTM object
            

        12. __init__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> None


        @brief Generate Kraus object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    def append(self, other: Kraus) -> bool:
        """append(self: quantum_info.Kraus, other: quantum_info.Kraus) -> bool


        @brief Append the internal data of another Kraus object to the end of the current Kraus object's internal data
        @param other another Kraus object
            
        """
    def clear(self) -> None:
        """clear(self: quantum_info.Kraus) -> None


        @brief Clear the data in Kraus object
            
        """
    def evolve(self, *args, **kwargs):
        """evolve(*args, **kwargs)
        Overloaded function.

        1. evolve(self: quantum_info.Kraus, state: QPanda3::QuantumInformation::DensityMatrix) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (density matrix) and return the result as a DensityMatrix object.
        @param state a DensityMatrix object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            

        2. evolve(self: quantum_info.Kraus, state: QPanda3::QuantumInformation::StateVector) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (state vector).
        @param state a StateVector object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            
        """
    def get_input_dim(self) -> int:
        """get_input_dim(self: quantum_info.Kraus) -> int


        @brief Get the input dimension of the QuantumChannel

        @return size_t the input dimension of the QuantumChannel
            
        """
    def get_output_dim(self) -> int:
        """get_output_dim(self: quantum_info.Kraus) -> int


        @brief Get the output dimension of the QuantumChannel

        @return size_t the output dimension of the QuantumChannel
            
        """
    def left(self) -> list[Matrix]:
        """left(self: quantum_info.Kraus) -> list[quantum_info.Matrix]


        @brief Retrieve the list of left operators inside a Kraus object

        @return the list of left operators inside a Kraus object
            
        """
    @overload
    def left_push_back(self, val: Matrix) -> None:
        """left_push_back(*args, **kwargs)
        Overloaded function.

        1. left_push_back(self: quantum_info.Kraus, val: quantum_info.Matrix) -> None


        @brief Add the data from a Matrix object to the end of the left operator list inside a Kraus object
        @param val a Matrix object
            

        2. left_push_back(self: quantum_info.Kraus, val: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Add the data from a Matrix object to the end of the left operator list inside a Kraus object
        @param val a Matrix object
            
        """
    @overload
    def left_push_back(self, val: numpy.ndarray[numpy.complex128[m, n]]) -> None:
        """left_push_back(*args, **kwargs)
        Overloaded function.

        1. left_push_back(self: quantum_info.Kraus, val: quantum_info.Matrix) -> None


        @brief Add the data from a Matrix object to the end of the left operator list inside a Kraus object
        @param val a Matrix object
            

        2. left_push_back(self: quantum_info.Kraus, val: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Add the data from a Matrix object to the end of the left operator list inside a Kraus object
        @param val a Matrix object
            
        """
    def right(self) -> list[Matrix]:
        """right(self: quantum_info.Kraus) -> list[quantum_info.Matrix]


        @brief Retrieve the list of right operators inside a Kraus object

        @return the list of right operators inside a Kraus object
            
        """
    @overload
    def right_push_back(self, val: Matrix) -> None:
        """right_push_back(*args, **kwargs)
        Overloaded function.

        1. right_push_back(self: quantum_info.Kraus, val: quantum_info.Matrix) -> None


        @brief Add the data from a Matrix object to the end of the right operator list inside a Kraus object
        @param val a Matrix object
            

        2. right_push_back(self: quantum_info.Kraus, val: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Add the data from a Matrix object to the end of the right operator list inside a Kraus object
        @param val a Matrix object
            
        """
    @overload
    def right_push_back(self, val: numpy.ndarray[numpy.complex128[m, n]]) -> None:
        """right_push_back(*args, **kwargs)
        Overloaded function.

        1. right_push_back(self: quantum_info.Kraus, val: quantum_info.Matrix) -> None


        @brief Add the data from a Matrix object to the end of the right operator list inside a Kraus object
        @param val a Matrix object
            

        2. right_push_back(self: quantum_info.Kraus, val: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Add the data from a Matrix object to the end of the right operator list inside a Kraus object
        @param val a Matrix object
            
        """
    def __eq__(self, other: Kraus) -> bool:
        """__eq__(self: quantum_info.Kraus, other: quantum_info.Kraus) -> bool


        @brief Equality check. Determine if the internal data of two Kraus objects are equal.
        @param Kraus another Kraus object

        @return Bool if they are same, return true.
            
        """

class Matrix:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Matrix) -> None


        @brief Construct Matrix using data.
            

        2. __init__(self: quantum_info.Matrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct Matrix using data.
            
        """
    @overload
    def __init__(self, data: numpy.ndarray[numpy.complex128[m, n]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.Matrix) -> None


        @brief Construct Matrix using data.
            

        2. __init__(self: quantum_info.Matrix, data: numpy.ndarray[numpy.complex128[m, n]]) -> None


        @brief Construct Matrix using data.
            
        """
    def L2(self) -> complex:
        """L2(self: quantum_info.Matrix) -> complex


        @brief Return the L2 norm value of the matrix.
        @return Matrix the L2 norm value of the matrix.
            
        """
    def T(self) -> Matrix:
        """T(self: quantum_info.Matrix) -> quantum_info.Matrix


        @brief Return the corresponding transpose matrix.
        @return Matrix the corresponding transpose matrix.
            
        """
    def adjoint(self) -> Matrix:
        """adjoint(self: quantum_info.Matrix) -> quantum_info.Matrix


        @brief Return the corresponding adjoint matrix (conjugate transpose).
        @return Matrix the corresponding adjoint matrix (conjugate transpose).
            
        """
    @overload
    def at(self, rowIdx: int, colIdx: int) -> complex:
        """at(self: quantum_info.Matrix, rowIdx: int, colIdx: int) -> complex


        @brief Get element at (rowIdx,colIdx).
        @rowIdx size_t row idx
        @colIdx size_t col idx

        @return complex the val of the element.
            
        """
    @overload
    def at(self, rowIdx, colIdx) -> Any:
        """at(self: quantum_info.Matrix, rowIdx: int, colIdx: int) -> complex


        @brief Get element at (rowIdx,colIdx).
        @rowIdx size_t row idx
        @colIdx size_t col idx

        @return complex the val of the element.
            
        """
    def col_total(self) -> int:
        """col_total(self: quantum_info.Matrix) -> int


        @brief Return the total cols' total of the matrix.
        @return size_t The total cols' total of the matrix.
            
        """
    def hermitian_conjugate(self) -> Matrix:
        """hermitian_conjugate(self: quantum_info.Matrix) -> quantum_info.Matrix


        @brief Return the corresponding adjoint matrix (conjugate transpose).
        @return Matrix the corresponding adjoint matrix (conjugate transpose).
            
        """
    def is_hermitian(self) -> bool:
        """is_hermitian(self: quantum_info.Matrix) -> bool


        @brief Determine if the matrix is Hermitian.
        @return bool if the matrix is Hermitian,return true.
            
        """
    def ndarray(self) -> numpy.ndarray[numpy.complex128]:
        """ndarray(self: quantum_info.Matrix) -> numpy.ndarray[numpy.complex128]


        @brief Return internal data as a numpy.ndarray.
        @return numpy.ndarray The internal data.
            
        """
    def row_total(self) -> int:
        """row_total(self: quantum_info.Matrix) -> int


        @brief Return the total rows' total of the matrix.
        @return size_t The total rows' total of the matrix.
            
        """
    def transpose(self) -> Matrix:
        """transpose(self: quantum_info.Matrix) -> quantum_info.Matrix


        @brief Return the corresponding transpose matrix.
        @return Matrix the corresponding transpose matrix.
            
        """
    def __eq__(self, other: Matrix) -> bool:
        """__eq__(self: quantum_info.Matrix, other: quantum_info.Matrix) -> bool


        @brief Equality check. Determine if the internal data of two Matrix objects are equal.
        @param other another Matrix object

        @return bool if they are same, return true.
            
        """

class PTM:
    @overload
    def __init__(self, other: Choi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.PTM, other: quantum_info.Choi) -> None


        @brief Generate PTM object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.PTM, other: quantum_info.PTM) -> None


        @brief Generate PTM object based on a PTM object
        @param other a quantum channel as a PTM object
            

        3. __init__(self: quantum_info.PTM, other: quantum_info.Chi) -> None


        @brief Generate PTM object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.PTM, other: quantum_info.SuperOp) -> None


        @brief Generate PTM object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.PTM, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate PTM object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: PTM) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.PTM, other: quantum_info.Choi) -> None


        @brief Generate PTM object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.PTM, other: quantum_info.PTM) -> None


        @brief Generate PTM object based on a PTM object
        @param other a quantum channel as a PTM object
            

        3. __init__(self: quantum_info.PTM, other: quantum_info.Chi) -> None


        @brief Generate PTM object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.PTM, other: quantum_info.SuperOp) -> None


        @brief Generate PTM object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.PTM, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate PTM object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: Chi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.PTM, other: quantum_info.Choi) -> None


        @brief Generate PTM object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.PTM, other: quantum_info.PTM) -> None


        @brief Generate PTM object based on a PTM object
        @param other a quantum channel as a PTM object
            

        3. __init__(self: quantum_info.PTM, other: quantum_info.Chi) -> None


        @brief Generate PTM object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.PTM, other: quantum_info.SuperOp) -> None


        @brief Generate PTM object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.PTM, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate PTM object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: SuperOp) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.PTM, other: quantum_info.Choi) -> None


        @brief Generate PTM object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.PTM, other: quantum_info.PTM) -> None


        @brief Generate PTM object based on a PTM object
        @param other a quantum channel as a PTM object
            

        3. __init__(self: quantum_info.PTM, other: quantum_info.Chi) -> None


        @brief Generate PTM object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.PTM, other: quantum_info.SuperOp) -> None


        @brief Generate PTM object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.PTM, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate PTM object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.PTM, other: quantum_info.Choi) -> None


        @brief Generate PTM object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.PTM, other: quantum_info.PTM) -> None


        @brief Generate PTM object based on a PTM object
        @param other a quantum channel as a PTM object
            

        3. __init__(self: quantum_info.PTM, other: quantum_info.Chi) -> None


        @brief Generate PTM object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.PTM, other: quantum_info.SuperOp) -> None


        @brief Generate PTM object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        5. __init__(self: quantum_info.PTM, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate PTM object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    def evolve(self, *args, **kwargs):
        """evolve(*args, **kwargs)
        Overloaded function.

        1. evolve(self: quantum_info.PTM, state: QPanda3::QuantumInformation::DensityMatrix) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (density matrix) and return the result as a DensityMatrix object.
        @param state a DensityMatrix object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            

        2. evolve(self: quantum_info.PTM, state: QPanda3::QuantumInformation::StateVector) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (state vector).
        @param state a StateVector object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            
        """
    def get_input_dim(self) -> int:
        """get_input_dim(self: quantum_info.PTM) -> int


        @brief Get the input dimension of the QuantumChannel

        @return size_t the input dimension of the QuantumChannel
            
        """
    def get_output_dim(self) -> int:
        """get_output_dim(self: quantum_info.PTM) -> int


        @brief Get the output dimension of the QuantumChannel

        @return size_t the output dimension of the QuantumChannel
            
        """
    def __eq__(self, state: PTM) -> bool:
        """__eq__(self: quantum_info.PTM, state: quantum_info.PTM) -> bool


        @brief Equality check. Determine if the internal data of two PTM objects are equal.
        @param other another PTM object

        @return Bool if they are same, return true.
            
        """

class QuantumChannel:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""

class StateSystemType:
    __members__: ClassVar[dict] = ...  # read-only
    Q2Q1Q0: ClassVar[StateSystemType] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: quantum_info.StateSystemType, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: quantum_info.StateSystemType) -> int"""
    def __int__(self) -> int:
        """__int__(self: quantum_info.StateSystemType) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class StateVector:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.StateVector) -> None


        @brief Default constructor, which by default constructs a state vector for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> None


        @brief Generate a StateVector object from another StateVector object
        @param other another StateVector object
            

        3. __init__(self: quantum_info.StateVector, data: dict[int, complex]) -> None


        @brief Construct a state vector based on the input dictionary
        @param data a dictionary
            

        4. __init__(self: quantum_info.StateVector, data: list[complex]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        5. __init__(self: quantum_info.StateVector, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        6. __init__(self: quantum_info.StateVector, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a state vector where the state of each qubit is currently 0
        @param qbit_total the total number of qubits in the quantum system
            
        """
    @overload
    def __init__(self, other: StateVector) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.StateVector) -> None


        @brief Default constructor, which by default constructs a state vector for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> None


        @brief Generate a StateVector object from another StateVector object
        @param other another StateVector object
            

        3. __init__(self: quantum_info.StateVector, data: dict[int, complex]) -> None


        @brief Construct a state vector based on the input dictionary
        @param data a dictionary
            

        4. __init__(self: quantum_info.StateVector, data: list[complex]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        5. __init__(self: quantum_info.StateVector, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        6. __init__(self: quantum_info.StateVector, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a state vector where the state of each qubit is currently 0
        @param qbit_total the total number of qubits in the quantum system
            
        """
    @overload
    def __init__(self, data: dict[int, complex]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.StateVector) -> None


        @brief Default constructor, which by default constructs a state vector for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> None


        @brief Generate a StateVector object from another StateVector object
        @param other another StateVector object
            

        3. __init__(self: quantum_info.StateVector, data: dict[int, complex]) -> None


        @brief Construct a state vector based on the input dictionary
        @param data a dictionary
            

        4. __init__(self: quantum_info.StateVector, data: list[complex]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        5. __init__(self: quantum_info.StateVector, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        6. __init__(self: quantum_info.StateVector, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a state vector where the state of each qubit is currently 0
        @param qbit_total the total number of qubits in the quantum system
            
        """
    @overload
    def __init__(self, data: list[complex]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.StateVector) -> None


        @brief Default constructor, which by default constructs a state vector for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> None


        @brief Generate a StateVector object from another StateVector object
        @param other another StateVector object
            

        3. __init__(self: quantum_info.StateVector, data: dict[int, complex]) -> None


        @brief Construct a state vector based on the input dictionary
        @param data a dictionary
            

        4. __init__(self: quantum_info.StateVector, data: list[complex]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        5. __init__(self: quantum_info.StateVector, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        6. __init__(self: quantum_info.StateVector, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a state vector where the state of each qubit is currently 0
        @param qbit_total the total number of qubits in the quantum system
            
        """
    @overload
    def __init__(self, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.StateVector) -> None


        @brief Default constructor, which by default constructs a state vector for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> None


        @brief Generate a StateVector object from another StateVector object
        @param other another StateVector object
            

        3. __init__(self: quantum_info.StateVector, data: dict[int, complex]) -> None


        @brief Construct a state vector based on the input dictionary
        @param data a dictionary
            

        4. __init__(self: quantum_info.StateVector, data: list[complex]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        5. __init__(self: quantum_info.StateVector, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        6. __init__(self: quantum_info.StateVector, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a state vector where the state of each qubit is currently 0
        @param qbit_total the total number of qubits in the quantum system
            
        """
    @overload
    def __init__(self, qbit_total: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.StateVector) -> None


        @brief Default constructor, which by default constructs a state vector for a quantum system with only one qubit and its current state being all zeros.
            

        2. __init__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> None


        @brief Generate a StateVector object from another StateVector object
        @param other another StateVector object
            

        3. __init__(self: quantum_info.StateVector, data: dict[int, complex]) -> None


        @brief Construct a state vector based on the input dictionary
        @param data a dictionary
            

        4. __init__(self: quantum_info.StateVector, data: list[complex]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        5. __init__(self: quantum_info.StateVector, data: numpy.ndarray[numpy.complex128[m, 1]]) -> None


        @brief Construct a state vector based on a given complex number array
        @param data a complex number array
            

        6. __init__(self: quantum_info.StateVector, qbit_total: int) -> None


        @brief Specify the total number of qubits in the quantum system and generate a state vector where the state of each qubit is currently 0
        @param qbit_total the total number of qubits in the quantum system
            
        """
    def at(self, idx: int) -> complex:
        """at(self: quantum_info.StateVector, idx: int) -> complex


        @brief Retrieve the element with index
        @param idx, the index of the element

        @return the element with index
            
        """
    def dim(self) -> int:
        """dim(self: quantum_info.StateVector) -> int


        @brief Retrieve the number of ground states corresponding to the state vector

        @return the number of ground states corresponding to the state vector.
            
        """
    def evolve(self, circuit) -> StateVector:
        """evolve(self: quantum_info.StateVector, circuit: QPanda3::QCircuit) -> quantum_info.StateVector


        @brief Evolve the quantum state using the quantum circuit QCircuit without updating the internal data of the original StateVector object, and return the result as a new StateVector object
        @param circuit a quantum circuit QCircuit

        @return a new StateVector object
            
        """
    def get_density_matrix(self) -> Matrix:
        """get_density_matrix(self: quantum_info.StateVector) -> quantum_info.Matrix


        @brief Retrieve the density matrix corresponding to the state vector.

        @return the density matrix corresponding to the state vector.
            
        """
    def is_valid(self) -> bool:
        """is_valid(self: quantum_info.StateVector) -> bool


        @brief Check if the internal data of the state vector is valid.

        @return return true if is valid
            
        """
    def ndarray(self) -> numpy.ndarray[numpy.complex128]:
        """ndarray(self: quantum_info.StateVector) -> numpy.ndarray[numpy.complex128]


        @brief Generate a numpy.ndarray object using data in self

        @return  a numpy.ndarray object
            
        """
    def purity(self) -> complex:
        """purity(self: quantum_info.StateVector) -> complex


        @brief Retrieve the purity of the state vector.

        @return the purity of the state vector
            
        """
    def update_by_evolve(self, circuit) -> StateVector:
        """update_by_evolve(self: quantum_info.StateVector, circuit: QPanda3::QCircuit) -> quantum_info.StateVector


        @brief Evolve the quantum state using the quantum circuit QCircuit and update the internal data of the original StateVector object
        @param circuit a quantum circuit QCircuit

        @return a new StateVector object
            
        """
    def __eq__(self, other: StateVector) -> bool:
        """__eq__(self: quantum_info.StateVector, other: quantum_info.StateVector) -> bool


        @brief Equality check. Determine if the internal data of two StateVector objects are equal.
        @param StateVector another StateVector object

        @return Bool if they are same, return true.
            
        """

class SuperOp:
    @overload
    def __init__(self, other: Choi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.SuperOp, other: quantum_info.Choi) -> None


        @brief Generate SuperOp object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.SuperOp, other: quantum_info.SuperOp) -> None


        @brief Generate SuperOp object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        3. __init__(self: quantum_info.SuperOp, other: quantum_info.Chi) -> None


        @brief Generate SuperOp object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate SuperOp object based on a PTM object
        @param other a quantum channel as a PTM object
            

        5. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate SuperOp object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: SuperOp) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.SuperOp, other: quantum_info.Choi) -> None


        @brief Generate SuperOp object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.SuperOp, other: quantum_info.SuperOp) -> None


        @brief Generate SuperOp object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        3. __init__(self: quantum_info.SuperOp, other: quantum_info.Chi) -> None


        @brief Generate SuperOp object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate SuperOp object based on a PTM object
        @param other a quantum channel as a PTM object
            

        5. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate SuperOp object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other: Chi) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.SuperOp, other: quantum_info.Choi) -> None


        @brief Generate SuperOp object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.SuperOp, other: quantum_info.SuperOp) -> None


        @brief Generate SuperOp object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        3. __init__(self: quantum_info.SuperOp, other: quantum_info.Chi) -> None


        @brief Generate SuperOp object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate SuperOp object based on a PTM object
        @param other a quantum channel as a PTM object
            

        5. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate SuperOp object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.SuperOp, other: quantum_info.Choi) -> None


        @brief Generate SuperOp object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.SuperOp, other: quantum_info.SuperOp) -> None


        @brief Generate SuperOp object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        3. __init__(self: quantum_info.SuperOp, other: quantum_info.Chi) -> None


        @brief Generate SuperOp object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate SuperOp object based on a PTM object
        @param other a quantum channel as a PTM object
            

        5. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate SuperOp object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    @overload
    def __init__(self, other) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: quantum_info.SuperOp, other: quantum_info.Choi) -> None


        @brief Generate SuperOp object based on a Choi object
        @param other a quantum channel as a Choi object
            

        2. __init__(self: quantum_info.SuperOp, other: quantum_info.SuperOp) -> None


        @brief Generate SuperOp object based on a SuperOp object
        @param other a quantum channel as a SuperOp object
            

        3. __init__(self: quantum_info.SuperOp, other: quantum_info.Chi) -> None


        @brief Generate SuperOp object based on a Chi object
        @param other a quantum channel as a Chi object
            

        4. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::PTM) -> None


        @brief Generate SuperOp object based on a PTM object
        @param other a quantum channel as a PTM object
            

        5. __init__(self: quantum_info.SuperOp, other: QPanda3::QuantumInformation::Kraus) -> None


        @brief Generate SuperOp object based on a Kraus object
        @param other a quantum channel as a Kraus object
            
        """
    def evolve(self, *args, **kwargs):
        """evolve(*args, **kwargs)
        Overloaded function.

        1. evolve(self: quantum_info.SuperOp, state: QPanda3::QuantumInformation::DensityMatrix) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (density matrix) and return the result as a DensityMatrix object.
        @param state a DensityMatrix object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            

        2. evolve(self: quantum_info.SuperOp, state: QPanda3::QuantumInformation::StateVector) -> QPanda3::QuantumInformation::DensityMatrix


        @brief Evolve a quantum state (state vector).
        @param state a StateVector object as a quantum state

        @return DensityMatrix a DensityMatrix object as result of evolving.
            
        """
    def get_input_dim(self) -> int:
        """get_input_dim(self: quantum_info.SuperOp) -> int


        @brief Get the input dimension of the QuantumChannel

        @return size_t the input dimension of the QuantumChannel
            
        """
    def get_output_dim(self) -> int:
        """get_output_dim(self: quantum_info.SuperOp) -> int


        @brief Get the output dimension of the QuantumChannel

        @return size_t the output dimension of the QuantumChannel
            
        """
    def __eq__(self, other: SuperOp) -> bool:
        """__eq__(self: quantum_info.SuperOp, other: quantum_info.SuperOp) -> bool


        @brief Equality check. Determine if the internal data of two SuperOp objects are equal.
        @param other another SuperOp object

        @return Bool if they are same, return true.
            
        """

class Unitary:
    def __init__(self, qcircuit, system_type: StateSystemType = ...) -> None:
        """__init__(self: quantum_info.Unitary, qcircuit: QPanda3::QCircuit, system_type: quantum_info.StateSystemType = <StateSystemType.Q2Q1Q0: 1>) -> None


        @brief Constructs a Unitary operation from a quantum circuit and a system type.

        This constructor initializes a Unitary object based on the given quantum circuit and the specified system type.
 
        @param qcircuit The quantum circuit that defines the unitary operation.
        @param system_type The type of the system that the unitary operation acts on, with a default value of `SystemType::Q2Q1Q0`.
            
        """
    def ndarray(self) -> numpy.ndarray[numpy.complex128]:
        """ndarray(self: quantum_info.Unitary) -> numpy.ndarray[numpy.complex128]


        @brief Generate a numpy.ndarray object using data in self

        @return  a numpy.ndarray object
            
        """
    def __eq__(self, other: Unitary) -> bool:
        """__eq__(self: quantum_info.Unitary, other: quantum_info.Unitary) -> bool


        @brief Equality check. Determine if the internal data of two Unitary objects are equal.
        @param Unitary another Unitary object

        @return Bool if they are same, return true.
            
        """

@overload
def KL_divergence(p: list[float], q: list[float]) -> float:
    """KL_divergence(*args, **kwargs)
    Overloaded function.

    1. KL_divergence(p: list[float], q: list[float]) -> float


    @brief Calculates the Kullback-Leibler (KL) divergence between two discrete probability distributions.

    The KL divergence is defined as:
    \\[
    \\mathrm{KL}(\\mathrm{p} \\| \\mathrm{q})=\\sum \\mathrm{p}(\\mathrm{x}) \\log \\frac{\\mathrm{p}(\\mathrm{x})}{\\mathrm{q}(\\mathrm{x})}
    \\]

    @note The KL divergence is not commutative, i.e., \\(\\mathrm{KL}(\\mathrm{p} \\| \\mathrm{q}) \\neq \\mathrm{KL}(\\mathrm{q} \\| \\mathrm{p})\\).

    @param p A constant reference to the first probability distribution.
    @param q A constant reference to the second probability distribution.
    @return double The KL divergence between the two distributions.
        

    2. KL_divergence(p_pdf: Callable[[float], float], q_pdf: Callable[[float], float], x_start: float, x_end: float, dx: float = 0.0001) -> float


    @brief Calculates the KL divergence for continuous probability distributions using function pointers.

    The KL divergence is given by the formula:
    \\f[
    \\mathrm{KL}(\\mathrm{p} \\| \\mathrm{q})=\\int \\mathrm{p}(\\mathrm{x}) \\log \\frac{\\mathrm{p}(\\mathrm{x})}{\\mathrm{q}(\\mathrm{x})} \\mathrm{dx}
    \\f]

    @param p_pdf A pointer to a function representing the probability distribution p(x).
    @param q_pdf A pointer to a function representing the probability distribution q(x).
    @param x_start The starting point of the integration.
    @param x_end The end point of the integration.
    @param dx The step size for the numerical integration (default is 1e-4).
    @return double The calculated KL divergence.

    @note The KL divergence is not commutative.
        
    """
@overload
def KL_divergence(p_pdf: Callable[[float], float], q_pdf: Callable[[float], float], x_start: float, x_end: float, dx: float = ...) -> float:
    """KL_divergence(*args, **kwargs)
    Overloaded function.

    1. KL_divergence(p: list[float], q: list[float]) -> float


    @brief Calculates the Kullback-Leibler (KL) divergence between two discrete probability distributions.

    The KL divergence is defined as:
    \\[
    \\mathrm{KL}(\\mathrm{p} \\| \\mathrm{q})=\\sum \\mathrm{p}(\\mathrm{x}) \\log \\frac{\\mathrm{p}(\\mathrm{x})}{\\mathrm{q}(\\mathrm{x})}
    \\]

    @note The KL divergence is not commutative, i.e., \\(\\mathrm{KL}(\\mathrm{p} \\| \\mathrm{q}) \\neq \\mathrm{KL}(\\mathrm{q} \\| \\mathrm{p})\\).

    @param p A constant reference to the first probability distribution.
    @param q A constant reference to the second probability distribution.
    @return double The KL divergence between the two distributions.
        

    2. KL_divergence(p_pdf: Callable[[float], float], q_pdf: Callable[[float], float], x_start: float, x_end: float, dx: float = 0.0001) -> float


    @brief Calculates the KL divergence for continuous probability distributions using function pointers.

    The KL divergence is given by the formula:
    \\f[
    \\mathrm{KL}(\\mathrm{p} \\| \\mathrm{q})=\\int \\mathrm{p}(\\mathrm{x}) \\log \\frac{\\mathrm{p}(\\mathrm{x})}{\\mathrm{q}(\\mathrm{x})} \\mathrm{dx}
    \\f]

    @param p_pdf A pointer to a function representing the probability distribution p(x).
    @param q_pdf A pointer to a function representing the probability distribution q(x).
    @param x_start The starting point of the integration.
    @param x_end The end point of the integration.
    @param dx The step size for the numerical integration (default is 1e-4).
    @return double The calculated KL divergence.

    @note The KL divergence is not commutative.
        
    """
@overload
def hellinger_distance(p: dict[int, float], q: dict[int, float]) -> float:
    """hellinger_distance(*args, **kwargs)
    Overloaded function.

    1. hellinger_distance(p: dict[int, float], q: dict[int, float]) -> float


    @brief Template function to calculate the Hellinger distance between two probability distributions.

    @param dist_p A reference to the first probability distribution, represented as an unordered map with keys of type long long and values of type double.
    @param dist_q A reference to the second probability distribution, represented as an unordered map with keys of type long long and values of type double.
    @return double The Hellinger distance between the two distributions.
        

    2. hellinger_distance(p: dict[str, float], q: dict[str, float]) -> float


    @brief Template function to calculate the Hellinger distance between two probability distributions.

    @param dist_p A reference to the first probability distribution, represented as an unordered map with keys of type string and values of type double.
    @param dist_q A reference to the second probability distribution, represented as an unordered map with keys of type string and values of type double.
    @return double The Hellinger distance between the two distributions.
        
    """
@overload
def hellinger_distance(p: dict[str, float], q: dict[str, float]) -> float:
    """hellinger_distance(*args, **kwargs)
    Overloaded function.

    1. hellinger_distance(p: dict[int, float], q: dict[int, float]) -> float


    @brief Template function to calculate the Hellinger distance between two probability distributions.

    @param dist_p A reference to the first probability distribution, represented as an unordered map with keys of type long long and values of type double.
    @param dist_q A reference to the second probability distribution, represented as an unordered map with keys of type long long and values of type double.
    @return double The Hellinger distance between the two distributions.
        

    2. hellinger_distance(p: dict[str, float], q: dict[str, float]) -> float


    @brief Template function to calculate the Hellinger distance between two probability distributions.

    @param dist_p A reference to the first probability distribution, represented as an unordered map with keys of type string and values of type double.
    @param dist_q A reference to the second probability distribution, represented as an unordered map with keys of type string and values of type double.
    @return double The Hellinger distance between the two distributions.
        
    """
@overload
def hellinger_fidelity(p: dict[int, float], q: dict[int, float]) -> float:
    """hellinger_fidelity(*args, **kwargs)
    Overloaded function.

    1. hellinger_fidelity(p: dict[int, float], q: dict[int, float]) -> float


    @brief Calculates the Hellinger fidelity between two probability distributions represented as unordered maps.

    @param dist_p A constant reference to the first probability distribution.
    @param dist_q A constant reference to the second probability distribution.
    @return double The Hellinger fidelity between the two distributions.
        

    2. hellinger_fidelity(p: dict[str, float], q: dict[str, float]) -> float


    @brief Calculates the Hellinger fidelity between two probability distributions represented as unordered maps.

    @param dist_p A constant reference to the first probability distribution.
    @param dist_q A constant reference to the second probability distribution.
    @return double The Hellinger fidelity between the two distributions.
        
    """
@overload
def hellinger_fidelity(p: dict[str, float], q: dict[str, float]) -> float:
    """hellinger_fidelity(*args, **kwargs)
    Overloaded function.

    1. hellinger_fidelity(p: dict[int, float], q: dict[int, float]) -> float


    @brief Calculates the Hellinger fidelity between two probability distributions represented as unordered maps.

    @param dist_p A constant reference to the first probability distribution.
    @param dist_q A constant reference to the second probability distribution.
    @return double The Hellinger fidelity between the two distributions.
        

    2. hellinger_fidelity(p: dict[str, float], q: dict[str, float]) -> float


    @brief Calculates the Hellinger fidelity between two probability distributions represented as unordered maps.

    @param dist_p A constant reference to the first probability distribution.
    @param dist_q A constant reference to the second probability distribution.
    @return double The Hellinger fidelity between the two distributions.
        
    """
