from typing import ClassVar, overload

Binary: DataBase
CLOUD_DEBUG: LogLevel
CLOUD_ERROR: LogLevel
CLOUD_INFO: LogLevel
CLOUD_WARNING: LogLevel
CONSOLE: LogOutput
FILE: LogOutput
Hex: DataBase

class ChipBackend:
    barrier_gate_timing: int
    basic_gates: list[str]
    chip_topology_edges: list[list[int]]
    compensate_angle_map: dict[tuple[int, int], tuple[float, float]]
    double_gate_timing: int
    echo_gate_timing: int
    patterns: dict[tuple[int, int], int]
    single_gate_timing: int
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: qcloud.ChipBackend) -> None


                    @brief Default constructor.

        2. __init__(self: qcloud.ChipBackend, _chip_topology_edges: list[list[int]], _basic_gates: list[str], _compensate_angle_map: dict[tuple[int, int], tuple[float, float]], _echo_gate_timing: int, _barrier_gate_timing: int, _single_gate_timing: int, _double_gate_timing: int, _patterns: dict[tuple[int, int], int]) -> None


                     @brief Parameterized constructor for ChipBackend.
                     @param[in] _chip_topology_edges Topology edges of the chip.
                     @param[in] _basic_gates List of supported basic gate names.
                     @param[in] _compensate_angle_map Map of qubit-pair to compensate angle.
                     @param[in] _echo_gate_timing Timing for echo gate.
                     @param[in] _barrier_gate_timing Timing for barrier gate.
                     @param[in] _single_gate_timing Timing for single-qubit gate.
                     @param[in] _double_gate_timing Timing for double-qubit gate.
                     @param[in] _patterns CZ patterns.
        """
    @overload
    def __init__(self, _chip_topology_edges: list[list[int]], _basic_gates: list[str], _compensate_angle_map: dict[tuple[int, int], tuple[float, float]], _echo_gate_timing: int, _barrier_gate_timing: int, _single_gate_timing: int, _double_gate_timing: int, _patterns: dict[tuple[int, int], int]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: qcloud.ChipBackend) -> None


                    @brief Default constructor.

        2. __init__(self: qcloud.ChipBackend, _chip_topology_edges: list[list[int]], _basic_gates: list[str], _compensate_angle_map: dict[tuple[int, int], tuple[float, float]], _echo_gate_timing: int, _barrier_gate_timing: int, _single_gate_timing: int, _double_gate_timing: int, _patterns: dict[tuple[int, int], int]) -> None


                     @brief Parameterized constructor for ChipBackend.
                     @param[in] _chip_topology_edges Topology edges of the chip.
                     @param[in] _basic_gates List of supported basic gate names.
                     @param[in] _compensate_angle_map Map of qubit-pair to compensate angle.
                     @param[in] _echo_gate_timing Timing for echo gate.
                     @param[in] _barrier_gate_timing Timing for barrier gate.
                     @param[in] _single_gate_timing Timing for single-qubit gate.
                     @param[in] _double_gate_timing Timing for double-qubit gate.
                     @param[in] _patterns CZ patterns.
        """

class ChipInfo:
    def __init__(self) -> None:
        """__init__(self: qcloud.ChipInfo) -> None"""
    def available_qubits(self) -> list[int]:
        """available_qubits(self: qcloud.ChipInfo) -> list[int]


                    @brief Retrieves the list of available qubits on the chip.
                    @return A vector of qubit indices that are available.
        """
    def chip_id(self) -> str:
        """chip_id(self: qcloud.ChipInfo) -> str


                    @brief Retrieves the chip ID.
                    @return The chip ID as a string.
        """
    def double_qubits_info(self) -> list[DoubleQubitsInfo]:
        """double_qubits_info(self: qcloud.ChipInfo) -> list[qcloud.DoubleQubitsInfo]


                    @brief Retrieves the list of double qubit information for the chip.
                    @return A vector of `DoubleQubitsInfo` objects representing the pairs of qubits.
        """
    def get_basic_gates(self) -> list[str]:
        """get_basic_gates(self: qcloud.ChipInfo) -> list[str]


                    @brief Retrieves the list of basic gates for the chip.
                    @return A vector of basic gates.
        """
    def get_chip_backend(self, *args, **kwargs):
        """get_chip_backend(self: qcloud.ChipInfo, qubits: list[int] = []) -> QPanda3::ChipBackend


                    @brief Get the backend of the chip.
                    @return  the backend
        """
    def get_chip_topology(self, qubits: list[int] = ...) -> list[list[int]]:
        """get_chip_topology(self: qcloud.ChipInfo, qubits: list[int] = []) -> list[list[int]]


                    @brief Get the topology structure of the chip.
                    @return  the edges of chip topologies
        """
    def get_compensate_angle_map(self) -> dict[tuple[int, int], tuple[float, float]]:
        """get_compensate_angle_map(self: qcloud.ChipInfo) -> dict[tuple[int, int], tuple[float, float]]


                    @brief Retrieves the compensate angle map on the chip.
                    @return compensate angle map.
        """
    def get_double_gate_timing(self) -> int:
        """get_double_gate_timing(self: qcloud.ChipInfo) -> int


                    @brief Retrieves the double gate timing on the chip.
                    @return double gate timing.
        """
    def get_single_gate_timing(self) -> int:
        """get_single_gate_timing(self: qcloud.ChipInfo) -> int


                    @brief Retrieves the single gate timing on the chip.
                    @return single gate timing.
        """
    def high_frequency_qubits(self) -> list[int]:
        """high_frequency_qubits(self: qcloud.ChipInfo) -> list[int]


                    @brief Retrieves the list of high-frequency qubits on the chip.
                    @return A vector of qubit indices that have high frequency.
        """
    def qubits_num(self) -> int:
        """qubits_num(self: qcloud.ChipInfo) -> int


                    @brief Retrieves the number of qubits on the chip.
                    @return The number of qubits as a size_t.
        """
    def single_qubit_info(self) -> list[SingleQubitInfo]:
        """single_qubit_info(self: qcloud.ChipInfo) -> list[qcloud.SingleQubitInfo]


                    @brief Retrieves the list of single qubit information for the chip.
                    @return A vector of `SingleQubitInfo` objects representing the qubits.
        """

class DataBase:
    __members__: ClassVar[dict] = ...  # read-only
    Binary: ClassVar[DataBase] = ...
    Hex: ClassVar[DataBase] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.DataBase, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.DataBase) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.DataBase) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class DataFormat:
    __members__: ClassVar[dict] = ...  # read-only
    BINARY: ClassVar[DataFormat] = ...
    DEFAULT: ClassVar[DataFormat] = ...
    INSTRUCTION_SET: ClassVar[DataFormat] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.DataFormat, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.DataFormat) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.DataFormat) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class DoubleQubitsInfo:
    def __init__(self, arg0: int, arg1: int, arg2: float) -> None:
        """__init__(self: qcloud.DoubleQubitsInfo, arg0: int, arg1: int, arg2: float) -> None"""
    def get_fidelity(self) -> float:
        """get_fidelity(self: qcloud.DoubleQubitsInfo) -> float


                    @brief Retrieves the fidelity of the double qubit gate.
                    @return The double qubit gate fidelity as a double.
        """
    def get_qubits(self) -> list[int]:
        """get_qubits(self: qcloud.DoubleQubitsInfo) -> list[int]


                    @brief Retrieves the pair of qubits involved in the double qubit gate.
                    @return A vector containing the two qubit indices.
        """

class JobStatus:
    __members__: ClassVar[dict] = ...  # read-only
    COMPUTING: ClassVar[JobStatus] = ...
    FAILED: ClassVar[JobStatus] = ...
    FINISHED: ClassVar[JobStatus] = ...
    QUEUING: ClassVar[JobStatus] = ...
    WAITING: ClassVar[JobStatus] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.JobStatus, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.JobStatus) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.JobStatus) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class LogLevel:
    __members__: ClassVar[dict] = ...  # read-only
    CLOUD_DEBUG: ClassVar[LogLevel] = ...
    CLOUD_ERROR: ClassVar[LogLevel] = ...
    CLOUD_INFO: ClassVar[LogLevel] = ...
    CLOUD_WARNING: ClassVar[LogLevel] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.LogLevel, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.LogLevel) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.LogLevel) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class LogOutput:
    __members__: ClassVar[dict] = ...  # read-only
    CONSOLE: ClassVar[LogOutput] = ...
    FILE: ClassVar[LogOutput] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.LogOutput, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.LogOutput) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.LogOutput) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class NOISE_MODEL:
    __members__: ClassVar[dict] = ...  # read-only
    BITFLIP_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    BIT_PHASE_FLIP_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DAMPING_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DECOHERENCE_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DEPHASING_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DEPOLARIZING_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    PHASE_DAMPING_OPERATOR: ClassVar[NOISE_MODEL] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.NOISE_MODEL, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.NOISE_MODEL) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.NOISE_MODEL) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class QCloudBackend:
    def __init__(self, arg0: str) -> None:
        """__init__(self: qcloud.QCloudBackend, arg0: str) -> None


                    @brief Initializes a QCloudBackend with a given backend name.
                    @param[in] backend_name The name of the quantum cloud backend.
        """
    def chip_backend(self, qubits: list[int] = ...) -> ChipBackend:
        """chip_backend(self: qcloud.QCloudBackend, qubits: list[int] = []) -> qcloud.ChipBackend"""
    def chip_info(self) -> ChipInfo:
        """chip_info(self: qcloud.QCloudBackend) -> qcloud.ChipInfo


                    @brief Retrieves the chip topology for a given chip name.
                    @param[in] chip_name The name of the chip.
                    @return The chip topology as a `ChipConfig` object.
        """
    @overload
    def expval_hamiltonian(self, prog, hamiltonian, shots: int = ..., noise_model: QCloudNoiseModel = ...) -> float:
        """expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda3::QProg, hamiltonian: QPanda3::Hamiltonian, shots: int = 1000, noise_model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef3ce4d8f0>) -> float


        @brief Calculate the expected value of a given Hamiltonian with respect to a quantum program on the QCloud backend.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
         of a specified Hamiltonian using a quantum program, specifically for execution on a cloud-based quantum backend.
         It supports simulation with an optional noise model tailored for the cloud environment.

        @param prog The quantum program to be executed.
        @param hamiltonian The Hamiltonian for which the expected value is to be calculated.
        @param shots The number of times the quantum program is sampled to estimate the expected value.
                      Defaults to 1000 if not specified.
        @param noise_model The noise model to be applied during the simulation on the QCloud backend.
                            Defaults to a default-constructed NoiseModel if not specified.

        @return The expected value of the Hamiltonian as a double.


            

        2. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda3::QProg, hamiltonian: QPanda3::Hamiltonian, options: qcloud.QCloudOptions) -> float


        @brief Calculate the expected value of a given Hamiltonian with respect to a quantum program on the QCloud backend using specified options.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
        of a specified Hamiltonian using a quantum program. It allows for customization of the execution
        through QCloudOptions, which can include settings for the cloud-based quantum backend.

        @param prog The quantum program to be executed.
        @param hamiltonian The Hamiltonian for which the expected value is to be calculated.
        @param options The QCloudOptions that specify the configuration for the execution on the QCloud backend.

        @return The expected value of the Hamiltonian as a double.


        """
    @overload
    def expval_hamiltonian(self, prog, hamiltonian, options: QCloudOptions) -> float:
        """expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda3::QProg, hamiltonian: QPanda3::Hamiltonian, shots: int = 1000, noise_model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef3ce4d8f0>) -> float


        @brief Calculate the expected value of a given Hamiltonian with respect to a quantum program on the QCloud backend.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
         of a specified Hamiltonian using a quantum program, specifically for execution on a cloud-based quantum backend.
         It supports simulation with an optional noise model tailored for the cloud environment.

        @param prog The quantum program to be executed.
        @param hamiltonian The Hamiltonian for which the expected value is to be calculated.
        @param shots The number of times the quantum program is sampled to estimate the expected value.
                      Defaults to 1000 if not specified.
        @param noise_model The noise model to be applied during the simulation on the QCloud backend.
                            Defaults to a default-constructed NoiseModel if not specified.

        @return The expected value of the Hamiltonian as a double.


            

        2. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda3::QProg, hamiltonian: QPanda3::Hamiltonian, options: qcloud.QCloudOptions) -> float


        @brief Calculate the expected value of a given Hamiltonian with respect to a quantum program on the QCloud backend using specified options.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
        of a specified Hamiltonian using a quantum program. It allows for customization of the execution
        through QCloudOptions, which can include settings for the cloud-based quantum backend.

        @param prog The quantum program to be executed.
        @param hamiltonian The Hamiltonian for which the expected value is to be calculated.
        @param options The QCloudOptions that specify the configuration for the execution on the QCloud backend.

        @return The expected value of the Hamiltonian as a double.


        """
    @overload
    def expval_pauli_operator(self, prog, pauli_operator, shots: int = ..., noise_model: QCloudNoiseModel = ...) -> float:
        """expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda3::QProg, pauli_operator: QPanda3::PauliOperator, shots: int = 1000, noise_model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6370>) -> float


        @brief Calculate the expected value of a given Pauli operator with respect to a quantum program on the QCloud backend.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
         of a specified Pauli operator using a quantum program, intended for execution on a cloud-based quantum backend.
         It allows for the inclusion of an optional noise model specific to the cloud environment.

        @param prog The quantum program to be executed.
        @param pauli_operator The Pauli operator for which the expected value is to be calculated.
        @param shots The number of times the quantum program is sampled to estimate the expected value.
                      Defaults to 1000 if not specified.
        @param noise_model The noise model to be applied during the simulation on the QCloud backend.
                            Defaults to a default-constructed NoiseModel if not specified.

        @return The expected value of the Pauli operator as a double.
            

        2. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda3::QProg, pauli_operator: QPanda3::PauliOperator, options: qcloud.QCloudOptions) -> float


        @brief Calculate the expected value of a given Pauli operator with respect to a quantum program on the QCloud backend using specified options.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
        of a specified Pauli operator using a quantum program. It provides flexibility in execution
        through QCloudOptions, which can include various settings tailored for the cloud-based quantum backend.

        @param prog The quantum program to be executed.
        @param pauli_operator The Pauli operator for which the expected value is to be calculated.
        @param options The QCloudOptions that specify the configuration for the execution on the QCloud backend.

        @return The expected value of the Pauli operator as a double.

        """
    @overload
    def expval_pauli_operator(self, prog, pauli_operator, options: QCloudOptions) -> float:
        """expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda3::QProg, pauli_operator: QPanda3::PauliOperator, shots: int = 1000, noise_model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6370>) -> float


        @brief Calculate the expected value of a given Pauli operator with respect to a quantum program on the QCloud backend.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
         of a specified Pauli operator using a quantum program, intended for execution on a cloud-based quantum backend.
         It allows for the inclusion of an optional noise model specific to the cloud environment.

        @param prog The quantum program to be executed.
        @param pauli_operator The Pauli operator for which the expected value is to be calculated.
        @param shots The number of times the quantum program is sampled to estimate the expected value.
                      Defaults to 1000 if not specified.
        @param noise_model The noise model to be applied during the simulation on the QCloud backend.
                            Defaults to a default-constructed NoiseModel if not specified.

        @return The expected value of the Pauli operator as a double.
            

        2. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda3::QProg, pauli_operator: QPanda3::PauliOperator, options: qcloud.QCloudOptions) -> float


        @brief Calculate the expected value of a given Pauli operator with respect to a quantum program on the QCloud backend using specified options.

        @details This member function of the QCloudBackend class computes the expected value (or expectation value)
        of a specified Pauli operator using a quantum program. It provides flexibility in execution
        through QCloudOptions, which can include various settings tailored for the cloud-based quantum backend.

        @param prog The quantum program to be executed.
        @param pauli_operator The Pauli operator for which the expected value is to be calculated.
        @param options The QCloudOptions that specify the configuration for the execution on the QCloud backend.

        @return The expected value of the Pauli operator as a double.

        """
    def name(self) -> str:
        """name(self: qcloud.QCloudBackend) -> str


                    @brief Retrieves the name of the quantum cloud backend.
                    @return The name of the backend.
        """
    @overload
    def run(self, prog, shots: int, model: QCloudNoiseModel = ...) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, qubits: list[int]) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, qubits) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, shots: int, options: QCloudOptions, enable_binary_encoding: bool = ...) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, progs, shots: int, options: QCloudOptions, enable_binary_encoding: bool = ...) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, amplitudes: list[str]) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, amplitude: str) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x7fef33aa6a70>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, qubits: std::initializer_list<unsigned long>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, progs: list[QPanda3::QProg], shots: int, options: qcloud.QCloudOptions, enable_binary_encoding: bool = False) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] progs The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @param[in] enable_binary_encoding The options for enable binary encoding.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda3::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run_instruction(self, instruction: str, shots: int, options: QCloudOptions) -> QCloudJob:
        """run_instruction(*args, **kwargs)
        Overloaded function.

        1. run_instruction(self: qcloud.QCloudBackend, instruction: str, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a single quantum instruction string on the backend.
                    @param[in] instruction A JSON string representing a quantum instruction list.
                    @param[in] shots Number of shots to execute.
                    @param[in] options Configuration options for the execution.
                    @return A `QCloudJob` object representing the submitted job.
            

        2. run_instruction(self: qcloud.QCloudBackend, instructions: list[str], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a list of quantum instruction strings on the backend.
                    @param[in] instructions A vector of JSON strings, each representing a quantum instruction list.
                    @param[in] shots Number of shots to execute for each instruction.
                    @param[in] options Configuration options for the execution.
                    @return A `QCloudJob` object representing the submitted job.
        """
    @overload
    def run_instruction(self, instructions: list[str], shots: int, options: QCloudOptions) -> QCloudJob:
        """run_instruction(*args, **kwargs)
        Overloaded function.

        1. run_instruction(self: qcloud.QCloudBackend, instruction: str, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a single quantum instruction string on the backend.
                    @param[in] instruction A JSON string representing a quantum instruction list.
                    @param[in] shots Number of shots to execute.
                    @param[in] options Configuration options for the execution.
                    @return A `QCloudJob` object representing the submitted job.
            

        2. run_instruction(self: qcloud.QCloudBackend, instructions: list[str], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a list of quantum instruction strings on the backend.
                    @param[in] instructions A vector of JSON strings, each representing a quantum instruction list.
                    @param[in] shots Number of shots to execute for each instruction.
                    @param[in] options Configuration options for the execution.
                    @return A `QCloudJob` object representing the submitted job.
        """
    def run_quantum_state_tomography(self, prog, shots: int, options: QCloudOptions = ...) -> QCloudJob:
        """run_quantum_state_tomography(self: qcloud.QCloudBackend, prog: QPanda3::QProg, shots: int, options: qcloud.QCloudOptions = False) -> qcloud.QCloudJob


                    @brief Runs quantum state tomography on the backend with specified options.
                    @param[in] prog The quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.
        """

class QCloudJob:
    def __init__(self, arg0: str) -> None:
        """__init__(self: qcloud.QCloudJob, arg0: str) -> None


                    @brief Initializes a QCloudJob with a job ID.
                    @param[in] job_id The ID of the quantum job.
        """
    def job_id(self) -> str:
        """job_id(self: qcloud.QCloudJob) -> str


                    @brief Retrieves the job ID.
                    @details If the job ID is empty, throws a runtime error.
                    @return The job ID.
        """
    def query(self, *args, **kwargs):
        """query(self: qcloud.QCloudJob) -> QPanda3::QCloudResult


                    @brief Queries the quantum job for information.
                    @return A `QCloudResult` object containing the job query result.
        """
    def result(self, *args, **kwargs):
        """result(self: qcloud.QCloudJob) -> QPanda3::QCloudResult


                    @brief Retrieves the result of the quantum job.
                    @return A `QCloudResult` object containing the job result.
        """
    def status(self) -> JobStatus:
        """status(self: qcloud.QCloudJob) -> qcloud.JobStatus


                    @brief Retrieves the current status of the quantum job.
                    @return The status of the job as a `JobStatus` enumeration value.
        """

class QCloudNoiseModel:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: qcloud.QCloudNoiseModel) -> None

        @brief Default constructor for QCloudNoiseModel.

        2. __init__(self: qcloud.QCloudNoiseModel, arg0: qcloud.NOISE_MODEL, arg1: list[float], arg2: list[float]) -> None


                    @brief Initializes a QCloudNoiseModel with a noise model and its parameters. 
                    @param[in] model The noise model. 
                    @param[in] single_p The single qubit noise parameters.
                    @param[in] double_p The double qubit noise parameters.
        """
    @overload
    def __init__(self, arg0: NOISE_MODEL, arg1: list[float], arg2: list[float]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: qcloud.QCloudNoiseModel) -> None

        @brief Default constructor for QCloudNoiseModel.

        2. __init__(self: qcloud.QCloudNoiseModel, arg0: qcloud.NOISE_MODEL, arg1: list[float], arg2: list[float]) -> None


                    @brief Initializes a QCloudNoiseModel with a noise model and its parameters. 
                    @param[in] model The noise model. 
                    @param[in] single_p The single qubit noise parameters.
                    @param[in] double_p The double qubit noise parameters.
        """
    def get_double_params(self) -> list[float]:
        """get_double_params(self: qcloud.QCloudNoiseModel) -> list[float]


                    @brief Returns the double qubit noise parameters.
        """
    def get_noise_model(self) -> str:
        """get_noise_model(self: qcloud.QCloudNoiseModel) -> str


                    @brief Returns the current noise model as a string.
        """
    def get_single_params(self) -> list[float]:
        """get_single_params(self: qcloud.QCloudNoiseModel) -> list[float]


                    @brief Returns the single qubit noise parameters.
        """
    def is_enabled(self) -> bool:
        """is_enabled(self: qcloud.QCloudNoiseModel) -> bool


                    @brief Checks if the noise model is enabled.
        """
    def print(self) -> None:
        """print(self: qcloud.QCloudNoiseModel) -> None


                    @brief Prints the noise model and its parameters to the standard output.
        """
    def set_double_params(self, arg0: list[float]) -> None:
        """set_double_params(self: qcloud.QCloudNoiseModel, arg0: list[float]) -> None


                    @brief Sets the double qubit noise parameters. 
                    @param[in] double_p The double qubit noise parameters.
        """
    def set_single_params(self, arg0: list[float]) -> None:
        """set_single_params(self: qcloud.QCloudNoiseModel, arg0: list[float]) -> None


                    @brief Sets the single qubit noise parameters. 
                    @param[in] single The single qubit noise parameters.
        """
    def __eq__(self, arg0: QCloudNoiseModel) -> bool:
        """__eq__(self: qcloud.QCloudNoiseModel, arg0: qcloud.QCloudNoiseModel) -> bool


                    @brief Compares two QCloudNoiseModel objects for equality.
        """
    def __ne__(self, arg0: QCloudNoiseModel) -> bool:
        """__ne__(self: qcloud.QCloudNoiseModel, arg0: qcloud.QCloudNoiseModel) -> bool


                    @brief Compares two QCloudNoiseModel objects for inequality.
        """

class QCloudOptions:
    def __init__(self) -> None:
        """__init__(self: qcloud.QCloudOptions) -> None


                    @brief Default constructor for QCloudOptions.
                    @details Initializes all options to their default values.
        """
    @overload
    def get_custom_option(self, arg0: str) -> int:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    @overload
    def get_custom_option(self, arg0: str) -> float:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    @overload
    def get_custom_option(self, arg0: str) -> str:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    @overload
    def get_custom_option(self, arg0: str) -> bool:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    def get_custom_options(self) -> dict[str, int | float | str | bool]:
        """get_custom_options(self: qcloud.QCloudOptions) -> dict[str, Union[int, float, str, bool]]


                    @brief Retrieves all custom options.
                    @return A dictionary of all custom options, where keys are option names and values are the option values.
        """
    def has_custom_option(self, arg0: str) -> bool:
        """has_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Checks if a custom option with the given key exists.
                    @param[in] key The key of the custom option.
                    @return True if the custom option exists, false otherwise.
        """
    def is_amend(self) -> bool:
        """is_amend(self: qcloud.QCloudOptions) -> bool


                    @brief Checks whether amendment is enabled.
                    @return A boolean indicating whether amendment is enabled.
        """
    def is_mapping(self) -> bool:
        """is_mapping(self: qcloud.QCloudOptions) -> bool


                    @brief Checks whether mapping is enabled.
                    @return A boolean indicating whether mapping is enabled.
        """
    def is_optimization(self) -> bool:
        """is_optimization(self: qcloud.QCloudOptions) -> bool


                    @brief Checks whether optimization is enabled.
                    @return A boolean indicating whether optimization is enabled.
        """
    def is_prob_counts(self) -> bool:
        """is_prob_counts(self: qcloud.QCloudOptions) -> bool


                    @brief Checks is_prob_counts value.
                    @return is_prob_counts value.
        """
    def point_label(self) -> int:
        """point_label(self: qcloud.QCloudOptions) -> int


                    @brief Checks point label value.
                    @return A int number represent point label value.
        """
    def print(self) -> None:
        """print(self: qcloud.QCloudOptions) -> None


                    @brief Prints the current settings of the options.
        """
    def set_amend(self, arg0: bool) -> None:
        """set_amend(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief Set whether amendment is enabled.
                    @param[in] is_amend A boolean indicating whether amendment is enabled.
        """
    def set_custom_option(self, arg0: str, arg1: int | float | str | bool) -> None:
        """set_custom_option(self: qcloud.QCloudOptions, arg0: str, arg1: Union[int, float, str, bool]) -> None


                    @brief Sets a custom option with a given key and value.
                    @param[in] key The key for the custom option.
                    @param[in] value The value for the custom option, which can be int, double, string, or bool.
        """
    def set_is_prob_counts(self, arg0: bool) -> None:
        """set_is_prob_counts(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief set_is_prob_counts for real chip task.
                    @param[in] is_prob_counts.
        """
    def set_mapping(self, arg0: bool) -> None:
        """set_mapping(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief Set whether mapping is enabled.
                    @param[in] is_mapping A boolean indicating whether mapping is enabled.
        """
    def set_optimization(self, arg0: bool) -> None:
        """set_optimization(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief Set whether optimization is enabled.
                    @param[in] is_optimization A boolean indicating whether optimization is enabled.
        """
    def set_point_label(self, arg0: int) -> None:
        """set_point_label(self: qcloud.QCloudOptions, arg0: int) -> None


                    @brief Set point label for real chip task.
                    @param[in] point label a int level number.
        """
    def set_specified_block(self, arg0: list[int]) -> None:
        """set_specified_block(self: qcloud.QCloudOptions, arg0: list[int]) -> None


                    @brief set_specified_block for real chip task.
                    @param[in] specified_block.
        """
    def specified_block(self) -> list[int]:
        """specified_block(self: qcloud.QCloudOptions) -> list[int]


                    @brief Checks specified_block value.
                    @return specified_block value.
        """

class QCloudResult:
    def __init__(self, arg0: str) -> None:
        """__init__(self: qcloud.QCloudResult, arg0: str) -> None


                    @brief Initializes a QCloudResult from a result string.
                    @param[in] result_string A string containing the job result data.
        """
    def get_amplitudes(self) -> dict[str, complex]:
        """get_amplitudes(self: qcloud.QCloudResult) -> dict[str, complex]


                    @brief Retrieves the amplitudes for particular quantum state.
                    @return A complex number representing the amplitude.
        """
    def get_counts(self, base: DataBase = ...) -> dict[str, int]:
        """get_counts(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> dict[str, int]


                    @brief Retrieves the counts for each state.
                    @return A map where the keys are the state strings and the values are the corresponding counts.
        """
    def get_counts_list(self, base: DataBase = ...) -> list[dict[str, int]]:
        """get_counts_list(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> list[dict[str, int]]


                    @brief Retrieves the list of counts for each state across different measurements.
                    @return A list of maps, each containing state strings as keys and corresponding counts as values.
        """
    def get_probs(self, base: DataBase = ...) -> dict[str, float]:
        """get_probs(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> dict[str, float]


                    @brief Retrieves the probabilities for each state.
                    @return A map where the keys are the state strings and the values are the corresponding probabilities.
        """
    def get_probs_list(self, base: DataBase = ...) -> list[dict[str, float]]:
        """get_probs_list(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> list[dict[str, float]]


                    @brief Retrieves the list of probabilities for each state across different measurements.
                    @return A list of maps, each containing state strings as keys and corresponding probabilities as values.
        """
    def get_state_fidelity(self) -> float:
        """get_state_fidelity(self: qcloud.QCloudResult) -> float


                    @brief Retrieves the state fidelity for particular quantum state.
                    @return A double number representing the state fidelity.
        """
    def get_state_tomography_density(self) -> list[list[complex]]:
        """get_state_tomography_density(self: qcloud.QCloudResult) -> list[list[complex]]


                    @brief Retrieves the state tomography density for particular quantum state.
                    @return state tomography density matrix representing the state fidelity.
        """
    def job_status(self) -> JobStatus:
        """job_status(self: qcloud.QCloudResult) -> qcloud.JobStatus


                    @brief Retrieves the status of the quantum job.
                    @return A `JobStatus` enum representing the job status.
        """
    def origin_data(self) -> str:
        """origin_data(self: qcloud.QCloudResult) -> str


                    @brief Retrieves the origin data for QCloudResult.
                    @return origin_data with json format.
        """

class QCloudService:
    def __init__(self, api_key: str, url: str = ...) -> None:
        """__init__(self: qcloud.QCloudService, api_key: str, url: str = 'http://pyqanda-admin.qpanda.cn') -> None


                    @brief Initializes a QCloudService.
                    @param[in] API key for accessing the cloud service.
                    @param[in] URL of the cloud service (defaults to DEFAULT_URL).
        """
    def backend(self, *args, **kwargs):
        """backend(self: qcloud.QCloudService, arg0: str) -> QPanda3::QCloudBackend


                    @brief Retrieves a backend by its name.
                    @param[in] backend_name The name of the backend.
                    @return A QCloudBackend object corresponding to the specified backend name.
        """
    def backends(self) -> dict[str, bool]:
        """backends(self: qcloud.QCloudService) -> dict[str, bool]


                    @brief Returns a list of available backend names.
                    @return A list of backend names as strings.
        """
    def setup_logging(self, output: LogOutput = ..., file_path: str = ...) -> None:
        """setup_logging(self: qcloud.QCloudService, output: qcloud.LogOutput = <LogOutput.CONSOLE: 0>, file_path: str = '') -> None


                    @brief Sets up the logging configuration.
                    @param[in] output The log output type (default is LogOutput::CONSOLE).
                    @param[in] file_path The file path for saving logs, optional.
        """

class SingleQubitInfo:
    def __init__(self) -> None:
        """__init__(self: qcloud.SingleQubitInfo) -> None"""
    def get_frequency(self) -> float:
        """get_frequency(self: qcloud.SingleQubitInfo) -> float


                    @brief Retrieves the frequency of the qubit.
                    @return The qubit frequency as a double.
        """
    def get_qubit_id(self) -> str:
        """get_qubit_id(self: qcloud.SingleQubitInfo) -> str


                    @brief Retrieves the ID of the qubit.
                    @return The qubit ID as a string.
        """
    def get_readout_fidelity(self) -> float:
        """get_readout_fidelity(self: qcloud.SingleQubitInfo) -> float


                    @brief Retrieves the readout fidelity of the qubit.
                    @return The readout fidelity as a double.
        """
    def get_single_gate_fidelity(self) -> float:
        """get_single_gate_fidelity(self: qcloud.SingleQubitInfo) -> float


                    @brief Retrieves the fidelity of the single gate for this qubit.
                    @return The single gate fidelity as a double.
        """
    def get_t1(self) -> float:
        """get_t1(self: qcloud.SingleQubitInfo) -> float


                    @brief Retrieves the T1 relaxation time of the qubit.
                    @return The T1 relaxation time as a double.
        """
    def get_t2(self) -> float:
        """get_t2(self: qcloud.SingleQubitInfo) -> float


                    @brief Retrieves the T2 coherence time of the qubit.
                    @return The T2 coherence time as a double.
        """
