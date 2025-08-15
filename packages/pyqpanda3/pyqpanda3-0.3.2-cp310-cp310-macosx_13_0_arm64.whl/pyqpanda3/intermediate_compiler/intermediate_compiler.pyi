def convert_originir_file_to_qprog(*args, **kwargs):
    """convert_originir_file_to_qprog(ir_filepath: str) -> QPanda3::QProg


    @brief This interface converts a file containing instruction set string in OriginIR format into the quantum program QProg.

    @param[in] ir_filepath File path to be converted containing OriginIR instruction set string.
    @return The Converted quantum program QProg.
          
    """
def convert_originir_string_to_qprog(*args, **kwargs):
    """convert_originir_string_to_qprog(string: str) -> QPanda3::QProg


    @brief This interface converts instruction set string in OriginIR format into the quantum program QProg.

    @param[in] ir_str OriginIR instruction set string to be converted.
    @return The Converted quantum program QProg.
      
    """
def convert_qasm_file_to_qprog(*args, **kwargs):
    """convert_qasm_file_to_qprog(qasm_filepath: str) -> QPanda3::QProg


    @brief This interface converts a file containing instruction set string in QASM format into the quantum program QProg.

    @param[in] qasm_filepath File path to be converted containing QASM instruction set string.
    @return The Converted quantum program QProg.
          
    """
def convert_qasm_string_to_qprog(*args, **kwargs):
    """convert_qasm_string_to_qprog(qasm_str: str) -> QPanda3::QProg


    @brief This interface converts instruction set string in QASM format into the quantum program QProg.

    @param[in] qasm_str QASM instruction set string to be converted.
    @return The Converted quantum program QProg.
          
    """
def convert_qprog_to_originir(prog, precision: int = ...) -> str:
    """convert_qprog_to_originir(prog: QPanda3::QProg, precision: int = 8) -> str


    @brief This interface converts the quantum program QProg to an instruction set string in OriginIR format.

    @param[in] prog The quantum program to be converted.
    @param[in] precision The number of decimal places in a floating-point number.precision should be a non-negative integer.
    @return The Converted OriginIR instruction set string.
          
    """
def convert_qprog_to_qasm(prog, precision: int = ...) -> str:
    """convert_qprog_to_qasm(prog: QPanda3::QProg, precision: int = 8) -> str


    @brief This interface converts the quantum program QProg to an instruction set string in OpenQASM 2.0 format.

    @param[in] prog The quantum program to be converted.
    @param[in] precision The number of decimal places in a floating-point number.precision should be a non-negative integer.
    @return The Converted OriginIR instruction set string.
          
    """
