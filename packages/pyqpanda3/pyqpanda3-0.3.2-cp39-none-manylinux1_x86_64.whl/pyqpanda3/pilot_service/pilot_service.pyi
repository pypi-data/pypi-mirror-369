from typing import ClassVar, overload

BACKEND_CALC_ERROR: ErrorCode
CLUSTER_BASE: ErrorCode
CLUSTER_SIMULATE_CALC_ERR: ErrorCode
DATABASE_ERROR: ErrorCode
ERR_BACKEND_CHIP_TASK_SOCKET_WRONG: ErrorCode
ERR_CHIP_OFFLINE: ErrorCode
ERR_EMPTY_PROG: ErrorCode
ERR_FIDELITY_MATRIX: ErrorCode
ERR_INVALID_URL: ErrorCode
ERR_MATE_GATE_CONFIG: ErrorCode
ERR_NOT_FOUND_APP_ID: ErrorCode
ERR_NOT_FOUND_TASK_ID: ErrorCode
ERR_OPERATOR_DB: ErrorCode
ERR_PARAMETER: ErrorCode
ERR_PARSER_SUB_TASK_RESULT: ErrorCode
ERR_PRE_ESTIMATE: ErrorCode
ERR_QCOMPILER_FAILED: ErrorCode
ERR_QPROG_LENGTH: ErrorCode
ERR_QST_PROG: ErrorCode
ERR_QUANTUM_CHIP_PROG: ErrorCode
ERR_QUBIT_SIZE: ErrorCode
ERR_QUBIT_TOPO: ErrorCode
ERR_QVM_INIT_FAILED: ErrorCode
ERR_REPEAT_MEASURE: ErrorCode
ERR_SCHEDULE_CHIP_TOPOLOGY_SUPPORTED: ErrorCode
ERR_SUB_GRAPH_OUT_OF_RANGE: ErrorCode
ERR_SYS_CALL_TIME_OUT: ErrorCode
ERR_TASK_BUF_OVERFLOW: ErrorCode
ERR_TASK_CONFIG: ErrorCode
ERR_TASK_STATUS_BUF_OVERFLOW: ErrorCode
ERR_TASK_TERMINATED: ErrorCode
ERR_TCP_INIT_FATLT: ErrorCode
ERR_TCP_SERVER_HALT: ErrorCode
ERR_UNKNOW_TASK_TYPE: ErrorCode
ERR_UNSUPPORT_BACKEND_TYPE: ErrorCode
EXCEED_MAX_CLOCK: ErrorCode
EXCEED_MAX_QUBIT: ErrorCode
JSON_FIELD_ERROR: ErrorCode
NO_ERROR_FOUND: ErrorCode
ORIGINIR_ERROR: ErrorCode
UNDEFINED_ERROR: ErrorCode

class ErrorCode:
    __members__: ClassVar[dict] = ...  # read-only
    BACKEND_CALC_ERROR: ClassVar[ErrorCode] = ...
    CLUSTER_BASE: ClassVar[ErrorCode] = ...
    CLUSTER_SIMULATE_CALC_ERR: ClassVar[ErrorCode] = ...
    DATABASE_ERROR: ClassVar[ErrorCode] = ...
    ERR_BACKEND_CHIP_TASK_SOCKET_WRONG: ClassVar[ErrorCode] = ...
    ERR_CHIP_OFFLINE: ClassVar[ErrorCode] = ...
    ERR_EMPTY_PROG: ClassVar[ErrorCode] = ...
    ERR_FIDELITY_MATRIX: ClassVar[ErrorCode] = ...
    ERR_INVALID_URL: ClassVar[ErrorCode] = ...
    ERR_MATE_GATE_CONFIG: ClassVar[ErrorCode] = ...
    ERR_NOT_FOUND_APP_ID: ClassVar[ErrorCode] = ...
    ERR_NOT_FOUND_TASK_ID: ClassVar[ErrorCode] = ...
    ERR_OPERATOR_DB: ClassVar[ErrorCode] = ...
    ERR_PARAMETER: ClassVar[ErrorCode] = ...
    ERR_PARSER_SUB_TASK_RESULT: ClassVar[ErrorCode] = ...
    ERR_PRE_ESTIMATE: ClassVar[ErrorCode] = ...
    ERR_QCOMPILER_FAILED: ClassVar[ErrorCode] = ...
    ERR_QPROG_LENGTH: ClassVar[ErrorCode] = ...
    ERR_QST_PROG: ClassVar[ErrorCode] = ...
    ERR_QUANTUM_CHIP_PROG: ClassVar[ErrorCode] = ...
    ERR_QUBIT_SIZE: ClassVar[ErrorCode] = ...
    ERR_QUBIT_TOPO: ClassVar[ErrorCode] = ...
    ERR_QVM_INIT_FAILED: ClassVar[ErrorCode] = ...
    ERR_REPEAT_MEASURE: ClassVar[ErrorCode] = ...
    ERR_SCHEDULE_CHIP_TOPOLOGY_SUPPORTED: ClassVar[ErrorCode] = ...
    ERR_SUB_GRAPH_OUT_OF_RANGE: ClassVar[ErrorCode] = ...
    ERR_SYS_CALL_TIME_OUT: ClassVar[ErrorCode] = ...
    ERR_TASK_BUF_OVERFLOW: ClassVar[ErrorCode] = ...
    ERR_TASK_CONFIG: ClassVar[ErrorCode] = ...
    ERR_TASK_STATUS_BUF_OVERFLOW: ClassVar[ErrorCode] = ...
    ERR_TASK_TERMINATED: ClassVar[ErrorCode] = ...
    ERR_TCP_INIT_FATLT: ClassVar[ErrorCode] = ...
    ERR_TCP_SERVER_HALT: ClassVar[ErrorCode] = ...
    ERR_UNKNOW_TASK_TYPE: ClassVar[ErrorCode] = ...
    ERR_UNSUPPORT_BACKEND_TYPE: ClassVar[ErrorCode] = ...
    EXCEED_MAX_CLOCK: ClassVar[ErrorCode] = ...
    EXCEED_MAX_QUBIT: ClassVar[ErrorCode] = ...
    JSON_FIELD_ERROR: ClassVar[ErrorCode] = ...
    NO_ERROR_FOUND: ClassVar[ErrorCode] = ...
    ORIGINIR_ERROR: ClassVar[ErrorCode] = ...
    UNDEFINED_ERROR: ClassVar[ErrorCode] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: pilot_service.ErrorCode, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: pilot_service.ErrorCode) -> int"""
    def __int__(self) -> int:
        """__int__(self: pilot_service.ErrorCode) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class PilotNoiseParams:
    double_gate_param: float
    double_p2: float
    double_pgate: float
    noise_model: str
    single_gate_param: float
    single_p2: float
    single_pgate: float
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""

class QPilotServiceBase:
    @overload
    def __init__(self, url: str, log_cout: bool = ..., api_key: str = ...) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: pilot_service.QPilotServiceBase, url: str, log_cout: bool = False, api_key: str = None) -> None

        2. __init__(self: pilot_service.QPilotServiceBase, url: str, log_cout: bool = False, username: str = None, password: str = None) -> None
        """
    @overload
    def __init__(self, url: str, log_cout: bool = ..., username: str = ..., password: str = ...) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: pilot_service.QPilotServiceBase, url: str, log_cout: bool = False, api_key: str = None) -> None

        2. __init__(self: pilot_service.QPilotServiceBase, url: str, log_cout: bool = False, username: str = None, password: str = None) -> None
        """
    def async_em_compute(self, parameter_json: str) -> str:
        """async_em_compute(self: pilot_service.QPilotServiceBase, parameter_json: str) -> str"""
    def async_real_chip_expectation(self, prog, hamiltonian: str, qubits: list[int] = ..., shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ...) -> str:
        """async_real_chip_expectation(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, hamiltonian: str, qubits: list[int] = [], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '') -> str

        deprecated, use request instead.
        """
    def async_real_chip_qst(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_real_chip_qst(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> str"""
    def async_real_chip_qst_density(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_real_chip_qst_density(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> str"""
    def async_real_chip_qst_fidelity(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_real_chip_qst_fidelity(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> str"""
    @overload
    def async_run(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., is_prob_counts: bool = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    @overload
    def async_run(self, ir: str, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., is_prob_counts: bool = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    @overload
    def async_run(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., is_prob_counts: bool = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    @overload
    def async_run(self, ir: list[str], shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., is_prob_counts: bool = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    @overload
    def async_run(self, prog, config_str: str) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    @overload
    def async_run(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., is_prob_counts: bool = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    @overload
    def async_run(self, ir: list[str], shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., is_prob_counts: bool = ..., describe: str = ..., point_lable: int = ...) -> str:
        """async_run(*args, **kwargs)
        Overloaded function.

        1. async_run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        2. async_run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        3. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        4. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        5. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. async_run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str

        7. async_run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], is_prob_counts: bool = True, describe: str = '', point_lable: int = 0) -> str
        """
    def build_expectation_task_msg(self, prog, hamiltonian: str, qubits: list[int] = ..., shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., task_describe: str = ...) -> str:
        """build_expectation_task_msg(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, hamiltonian: str, qubits: list[int] = [], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], task_describe: str = '') -> str

        use C++ to build a expectation task body.
        """
    def build_init_msg(self, api_key: str) -> str:
        """build_init_msg(self: pilot_service.QPilotServiceBase, api_key: str) -> str"""
    def build_qst_task_msg(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., task_describe: str = ...) -> str:
        """build_qst_task_msg(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], task_describe: str = '') -> str

        use C++ to build ordinary qst task msg body
        """
    def build_query_msg(self, task_id: str) -> str:
        """build_query_msg(self: pilot_service.QPilotServiceBase, task_id: str) -> str"""
    def build_task_msg(self, prog, shot: int, chip_id: str, is_amend: bool, is_mapping: bool, is_optimization: bool, specified_block: list[int], task_describe: str, point_lable: int, priority: int) -> str:
        """build_task_msg(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int, chip_id: str, is_amend: bool, is_mapping: bool, is_optimization: bool, specified_block: list[int], task_describe: str, point_lable: int, priority: int) -> str

        use c++ to build real chip measure task msg body.
        """
    def build_task_proto_msg(self, shot: int, chip_id: str, is_amend: bool, is_mapping: bool, is_optimization: bool, specified_block: list[int], task_describe: str, point_lable: int, priority: int) -> str:
        """build_task_proto_msg(self: pilot_service.QPilotServiceBase, shot: int, chip_id: str, is_amend: bool, is_mapping: bool, is_optimization: bool, specified_block: list[int], task_describe: str, point_lable: int, priority: int) -> str

        use c++ to build real chip measure task msg body.
        """
    def em_compute(self, parameter_json: str) -> list[float]:
        """em_compute(self: pilot_service.QPilotServiceBase, parameter_json: str) -> list[float]"""
    def get_expectation_result(self, task_id: str) -> list:
        """get_expectation_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list"""
    @overload
    def get_measure_result(self, task_id: str) -> list:
        """get_measure_result(*args, **kwargs)
        Overloaded function.

        1. get_measure_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list

        2. get_measure_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list
        """
    @overload
    def get_measure_result(self, task_id: str) -> list:
        """get_measure_result(*args, **kwargs)
        Overloaded function.

        1. get_measure_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list

        2. get_measure_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list
        """
    def get_token(self, rep_json: str) -> ErrorCode:
        """get_token(self: pilot_service.QPilotServiceBase, rep_json: str) -> pilot_service.ErrorCode"""
    def init_config(self, url: str, log_cout: bool) -> None:
        """init_config(self: pilot_service.QPilotServiceBase, url: str, log_cout: bool) -> None"""
    def noise_learning(self, parameter_json: str = ...) -> str:
        """noise_learning(self: pilot_service.QPilotServiceBase, parameter_json: str = True) -> str"""
    def output_version(self) -> str:
        """output_version(self: pilot_service.QPilotServiceBase) -> str"""
    def parse_prob_counts_result(self, result_str: list[str]) -> list[dict[str, int]]:
        """parse_prob_counts_result(self: pilot_service.QPilotServiceBase, result_str: list[str]) -> list[dict[str, int]]

        Parse result str to map<string, double>
        Args:
            result_str: Taeget result string

        Returns:
            array: vector<map<string, double>>
        Raises:
            none

        """
    def parse_probability_result(self, result_str: list[str]) -> list[dict[str, float]]:
        """parse_probability_result(self: pilot_service.QPilotServiceBase, result_str: list[str]) -> list[dict[str, float]]

        Parse result str to map<string, double>
        Args:
            result_str: Taeget result string

        Returns:
            array: vector<map<string, double>>
        Raises:
            none

        """
    def parse_task_result(self, result_str: str) -> dict[str, float]:
        """parse_task_result(self: pilot_service.QPilotServiceBase, result_str: str) -> dict[str, float]

        Parse result str to map<string, double>
        Args:
            result_str: Taeget result string

        Returns:
            dict: map<string, double>
        Raises:
            none

        """
    def parser_expectation_result(self, json_str: str) -> list:
        """parser_expectation_result(self: pilot_service.QPilotServiceBase, json_str: str) -> list

        deprecated, use Python's json lib.
        """
    def parser_sync_result(self, json_str: str) -> list[dict[str, float]]:
        """parser_sync_result(self: pilot_service.QPilotServiceBase, json_str: str) -> list[dict[str, float]]"""
    def query_compile_prog(self, task_id: str, without_compensate: bool = ...) -> list:
        """query_compile_prog(self: pilot_service.QPilotServiceBase, task_id: str, without_compensate: bool = True) -> list

        Query Task compile prog by task_id
        Args:
            without_compensate: whether return the prog without angle compensate

        Returns:
            bool: whether find compile prog success
        Raises:
            none

        """
    @overload
    def query_result(self, task_id: str) -> list:
        """query_result(*args, **kwargs)
        Overloaded function.

        1. query_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list

        Query Task State by task_id
        Args:
            task_id: Taeget task id, got by async_run

        Returns:
            string: task state: 2: Running; 3: Finished; 4: Failed
            string: task result string
        Raises:
            none


        2. query_result(self: pilot_service.QPilotServiceBase, task_id: str, is_save: bool, file_path: str = '') -> list
        """
    @overload
    def query_result(self, task_id: str, is_save: bool, file_path: str = ...) -> list:
        """query_result(*args, **kwargs)
        Overloaded function.

        1. query_result(self: pilot_service.QPilotServiceBase, task_id: str) -> list

        Query Task State by task_id
        Args:
            task_id: Taeget task id, got by async_run

        Returns:
            string: task state: 2: Running; 3: Finished; 4: Failed
            string: task result string
        Raises:
            none


        2. query_result(self: pilot_service.QPilotServiceBase, task_id: str, is_save: bool, file_path: str = '') -> list
        """
    def query_task_state_vec(self, task_id: str) -> list:
        """query_task_state_vec(self: pilot_service.QPilotServiceBase, task_id: str) -> list

        Query Task State by task_id
        Args:
            task_id: Taeget task id, got by async_run

        Returns:
            string: task state: 2: Running; 3: Finished; 4: Failed
            array: task result array
        Raises:
            none

        """
    def real_chip_expectation(self, prog, hamiltonian: str, qubits: list[int] = ..., shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ...) -> float:
        """real_chip_expectation(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, hamiltonian: str, qubits: list[int] = [], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '') -> float

        deprecated, use request instead.
        """
    @overload
    def real_chip_measure_prob_count(self, ir: str, shot: int = ..., chip_id: str = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> dict[str, int]:
        """real_chip_measure_prob_count(*args, **kwargs)
        Overloaded function.

        1. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        2. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        3. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]

        4. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]
        """
    @overload
    def real_chip_measure_prob_count(self, prog, shot: int = ..., chip_id: str = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> dict[str, int]:
        """real_chip_measure_prob_count(*args, **kwargs)
        Overloaded function.

        1. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        2. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        3. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]

        4. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]
        """
    @overload
    def real_chip_measure_prob_count(self, ir: list[str], shot: int = ..., chip_id: str = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> list[dict[str, int]]:
        """real_chip_measure_prob_count(*args, **kwargs)
        Overloaded function.

        1. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        2. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        3. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]

        4. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]
        """
    @overload
    def real_chip_measure_prob_count(self, prog, shot: int = ..., chip_id: str = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> list[dict[str, int]]:
        """real_chip_measure_prob_count(*args, **kwargs)
        Overloaded function.

        1. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        2. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, int]

        3. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]

        4. real_chip_measure_prob_count(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, int]]
        """
    @overload
    def run(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> dict[str, float]:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run(self, ir: str, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> dict[str, float]:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> list[dict[str, float]]:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run(self, ir: list[str], shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> list[dict[str, float]]:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run(self, prog, config_str: str) -> str:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run(self, prog, shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> list[dict[str, float]]:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run(self, ir: list[str], shot: int = ..., chip_id: str = ..., is_amend: bool = ..., is_mapping: bool = ..., is_optimization: bool = ..., specified_block: list[int] = ..., describe: str = ..., point_lable: int = ...) -> list[dict[str, float]]:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        2. run(self: pilot_service.QPilotServiceBase, ir: str, shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> dict[str, float]

        3. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        4. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        5. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], config_str: str) -> str

        6. run(self: pilot_service.QPilotServiceBase, prog: list[QPanda3::QProg], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]

        7. run(self: pilot_service.QPilotServiceBase, ir: list[str], shot: int = 1000, chip_id: str = 'any_quantum_chip', is_amend: bool = True, is_mapping: bool = True, is_optimization: bool = True, specified_block: list[int] = [], describe: str = '', point_lable: int = 0) -> list[dict[str, float]]
        """
    @overload
    def run_simulator(self, prog, shot: int) -> dict[str, float]:
        """run_simulator(*args, **kwargs)
        Overloaded function.

        1. run_simulator(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int) -> dict[str, float]

        Run a quantum program with given number of shots and return measure result.

        2. run_simulator(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, qubit_vec: list[int]) -> dict[str, float]

        Run a quantum program measuring only specified qubits, return pmeasure result.
        """
    @overload
    def run_simulator(self, prog, qubit_vec: list[int]) -> dict[str, float]:
        """run_simulator(*args, **kwargs)
        Overloaded function.

        1. run_simulator(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, shot: int) -> dict[str, float]

        Run a quantum program with given number of shots and return measure result.

        2. run_simulator(self: pilot_service.QPilotServiceBase, prog: QPanda3::QProg, qubit_vec: list[int]) -> dict[str, float]

        Run a quantum program measuring only specified qubits, return pmeasure result.
        """
    def tcp_recv(self, ip: str, port: int, task_id: str) -> list:
        """tcp_recv(self: pilot_service.QPilotServiceBase, ip: str, port: int, task_id: str) -> list"""
