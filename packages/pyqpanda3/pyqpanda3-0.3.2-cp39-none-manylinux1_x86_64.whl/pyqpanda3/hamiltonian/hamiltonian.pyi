import numpy
from typing import overload

class Hamiltonian:
    @overload
    def __init__(self) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, other: Hamiltonian) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, pauli_operator: PauliOperator) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, pauli: str) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, pauli_with_coef_s: dict[str, complex]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, paulis: list[str], coefs: list[complex]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = ...) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, mat: numpy.ndarray[numpy.float64[m, n]]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.Hamiltonian) -> None


        @brief Constructs a Hamiltonian object.
 
        @details Initializes a new instance of the Hamiltonian class. This constructor may set up
        default values or perform any necessary initialization steps required for the
        object to be in a valid state.
            

        2. __init__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> None


        @brief Copy constructor for Hamiltonian.
 
        @details Creates a new Hamiltonian object as a copy of an existing one. This constructor deep-copies
        the state of the `other` Hamiltonian object, ensuring that the new object is an independent
        instance with the same state.
 
        @param other The Hamiltonian object to copy from.
            

        3. __init__(self: hamiltonian.Hamiltonian, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Constructs a Hamiltonian from a PauliOperator.
 
        @details Initializes a new Hamiltonian object using the given PauliOperator as a basis. This
        constructor may perform any necessary transformations or calculations to convert the
        PauliOperator into a valid Hamiltonian representation.
 
        @param other The PauliOperator object to use for constructing the Hamiltonian.
            

        4. __init__(self: hamiltonian.Hamiltonian, pauli: str) -> None


        @brief Constructs a Hamiltonian from a string representation of Pauli operators.

        @details Initializes a new Hamiltonian object using a string that represents one or more Pauli
        operators. This constructor parses the input string and constructs the corresponding
        Hamiltonian based on the specified operators.
        input must be \'X\' or \'Y\' or \'Z\' or \'I\',this will construct a pauli(X/Y/Z/I) to qbit0

        @param a_pauli The string containing the Pauli operator representation.
            

        5. __init__(self: hamiltonian.Hamiltonian, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a Hamiltonian from a map of operators and their coefficients.
 
        @details Initializes a new Hamiltonian object using a map that associates strings representing
        quantum operators with their corresponding complex coefficients. This constructor
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient.
 
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}
 
        @param ops A map where the keys are strings representing quantum operators and the values
        are complex numbers representing the coefficients of those operators.
            

        6. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a Hamiltonian from a vector of operators and their coefficients.

        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. This constructor assumes that the vectors `ops` and
        `coef_s` have the same length and constructs the Hamiltonian by summing the
        contributions of each operator weighted by its coefficient.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]

        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
            

        7. __init__(self: hamiltonian.Hamiltonian, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool = True) -> None


        @brief Constructs a Hamiltonian from a vector of operators, their coefficients, and a flag.
 
        @details Initializes a new Hamiltonian object using two vectors: one containing strings that
        represent quantum operators, and another containing the corresponding complex
        coefficients for those operators. Additionally, this constructor takes a boolean flag
        `AB_is_A1_B0` that specifies a particular configuration or interpretation of the
        operators.
        This constructor assumes that the vectors `ops` and `coef_s` have the same length and
        constructs the Hamiltonian by summing the contributions of each operator weighted by
        its coefficient. The `AB_is_A1_B0` flag may affect how the operators are interpreted or
        combined in the final Hamiltonian.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops A vector of strings representing quantum operators.
        @param coef_s A vector of complex numbers representing the coefficients of the operators.
        @param AB_is_A1_B0 A boolean flag that specifies a particular configuration or
        interpretation of the operators.
            

        8. __init__(self: hamiltonian.Hamiltonian, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a Hamiltonian from a vector of tuples containing operators, indices, and coefficients.
 
        @details Initializes a new Hamiltonian object using a vector of tuples. Each tuple contains a
        string representing a quantum operator, a vector of size_t representing the indices of
        the operator (e.g., for tensor products or multi-site operators), and a complex number
        representing the coefficient of the operator.
        This constructor constructs the Hamiltonian by summing the contributions of each
        operator-index-coefficient tuple.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]
 
        @param ops A vector of tuples, where each tuple contains a string (operator), a vector
        of size_t (indices), and a complex number (coefficient).
            

        9. __init__(self: hamiltonian.Hamiltonian, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a Hamiltonian object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    def matrix(self) -> numpy.ndarray[numpy.complex128[m, n]]:
        """matrix(self: hamiltonian.Hamiltonian) -> numpy.ndarray[numpy.complex128[m, n]]


        @brief Converts a Hamiltonian object to its corresponding matrix representation.
 
        @details This function takes a Hamiltonian object as input and returns its matrix representation.
 
        @param opt The Hamiltonian object to be converted.
        @return A matrix representing the Hamiltonian object.
        
        """
    def pauli_operator(self) -> PauliOperator:
        """pauli_operator(self: hamiltonian.Hamiltonian) -> hamiltonian.PauliOperator"""
    def str_no_I(self) -> str:
        '''str_no_I(self: hamiltonian.Hamiltonian) -> str


        @brief Converts the Pauli operators to a string representation without the identity operator \'I\'.
        *
        This method represents the Pauli operators (X, Y, Z) acting on qubits as a string
        composed of characters \'X\', \'Y\', \'Z\', and numbers. For example, "X1 Y4" represents
        the Pauli operator X acting on the qubit with index 1 and the Pauli operator Y
        acting on the qubit with index 4. The parameter `AB_is_A1_B0` determines the order
        of the character substrings representing the Pauli operators acting on the qubits.
        If `AB_is_A1_B0` is true, the substring corresponding to the qubit with the larger
        index appears first in the resulting string; otherwise, it appears later.
        *
        @param AB_is_A1_B0 A boolean value indicating the order of the substrings in the result.
        @return A string representation of the Pauli operators without the identity operator \'I\'.
            
        '''
    def str_with_I(self, AB_is_A1_B0: bool = ...) -> str:
        """str_with_I(self: hamiltonian.Hamiltonian, AB_is_A1_B0: bool = True) -> str


        @brief Converts the Hamiltonian to a string representation with Pauli matrices.
        *
        This method converts the current `Hamiltonian` object to a string representation
        where the Pauli matrices are represented by the characters 'X', 'Y', 'Z', and 'I'.
        The parameter `AB_is_A1_B0` indicates the relationship between the order of the
        characters in the string and the qubit indices. If `AB_is_A1_B0` is true, then the
        characters with smaller indices in the string correspond to larger qubit indices.
        Otherwise, the characters with smaller indices in the string correspond to smaller
        qubit indices.
        *
        @param AB_is_A1_B0 A boolean value that specifies the character order in relation
        to qubit indices.
        @return A string representation of the `Hamiltonian` object with Pauli matrices
        represented by 'X', 'Y', 'Z', and 'I'.
            
        """
    def str_withou_I(self) -> str:
        '''str_withou_I(self: hamiltonian.Hamiltonian) -> str


        @brief Converts the Pauli operators to a string representation without the identity operator \'I\'.
        *
        This method represents the Pauli operators (X, Y, Z) acting on qubits as a string
        composed of characters \'X\', \'Y\', \'Z\', and numbers. For example, "X1 Y4" represents
        the Pauli operator X acting on the qubit with index 1 and the Pauli operator Y
        acting on the qubit with index 4. The parameter `AB_is_A1_B0` determines the order
        of the character substrings representing the Pauli operators acting on the qubits.
        If `AB_is_A1_B0` is true, the substring corresponding to the qubit with the larger
        index appears first in the resulting string; otherwise, it appears later.
        *
        @param AB_is_A1_B0 A boolean value indicating the order of the substrings in the result.
        @return A string representation of the Pauli operators without the identity operator \'I\'.
            
        '''
    @overload
    def tensor(self, other: Hamiltonian) -> Hamiltonian:
        """tensor(*args, **kwargs)
        Overloaded function.

        1. tensor(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the tensor product operator between two Hamiltonians.
 
        @details This method computes the tensor product of two `Hamiltonian` objects. In the
        resulting tensor product:
        1. The qubit indices in the current object (`self`) remain unchanged.
        2. The qubit indices in the other object (`other`) are incremented by the number
        of qubits in the current object.
        The result is a new `Hamiltonian` object that represents the tensor product of the
        two input objects.
 
        @param other The `Hamiltonian` object to compute the tensor product with the
        current object.
        @return A new `Hamiltonian` object that is the tensor product of the current
        object and `other`.
            

        2. tensor(self: hamiltonian.Hamiltonian, n: int) -> hamiltonian.Hamiltonian


        @brief Overload for the exponentiation operator to perform tensor product.
        *
        This method allows for raising the `Hamiltonian` object to a power `n` by
        performing a tensor product with itself `n-1` times. The tensor product is
        performed such that the qubit indices in the self object remain unchanged, while
        the indices in the other objects involved in the tensor product (implicit in the
        definition of the tensor product for Hamiltonians) are shifted to avoid overlap.
        *
        @param n The power to which the `Hamiltonian` object is raised, corresponding to
         the number of tensor product operations performed.
        @return A new `Hamiltonian` object that is the result of performing the tensor
        product with the initial object `n-1` times.
            
        """
    @overload
    def tensor(self, n: int) -> Hamiltonian:
        """tensor(*args, **kwargs)
        Overloaded function.

        1. tensor(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the tensor product operator between two Hamiltonians.
 
        @details This method computes the tensor product of two `Hamiltonian` objects. In the
        resulting tensor product:
        1. The qubit indices in the current object (`self`) remain unchanged.
        2. The qubit indices in the other object (`other`) are incremented by the number
        of qubits in the current object.
        The result is a new `Hamiltonian` object that represents the tensor product of the
        two input objects.
 
        @param other The `Hamiltonian` object to compute the tensor product with the
        current object.
        @return A new `Hamiltonian` object that is the tensor product of the current
        object and `other`.
            

        2. tensor(self: hamiltonian.Hamiltonian, n: int) -> hamiltonian.Hamiltonian


        @brief Overload for the exponentiation operator to perform tensor product.
        *
        This method allows for raising the `Hamiltonian` object to a power `n` by
        performing a tensor product with itself `n-1` times. The tensor product is
        performed such that the qubit indices in the self object remain unchanged, while
        the indices in the other objects involved in the tensor product (implicit in the
        definition of the tensor product for Hamiltonians) are shifted to avoid overlap.
        *
        @param n The power to which the `Hamiltonian` object is raised, corresponding to
         the number of tensor product operations performed.
        @return A new `Hamiltonian` object that is the result of performing the tensor
        product with the initial object `n-1` times.
            
        """
    def to_hamiltonian_pq2(self) -> list[tuple[dict[int, str], complex]]:
        """to_hamiltonian_pq2(self: hamiltonian.Hamiltonian) -> list[tuple[dict[int, str], complex]]"""
    @overload
    def update_by_tensor(self, other: Hamiltonian) -> Hamiltonian:
        """update_by_tensor(*args, **kwargs)
        Overloaded function.

        1. update_by_tensor(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the tensor product assignment operator.
        This method computes the tensor product (Kronecker product) of the current
        `Hamiltonian` object with another `Hamiltonian` object `other` and assigns the
        result back to the current object.

        @param other The `Hamiltonian` object to compute the tensor product with.
        @return A reference to the current `Hamiltonian` object after the tensor product operation.
        @note This operation is typically used in quantum mechanics and linear algebra contexts.
            

        2. update_by_tensor(self: hamiltonian.Hamiltonian, n: int) -> hamiltonian.Hamiltonian


        @brief Overload for the tensor product assignment operator to compute the n-th power of the tensor product.

        @details This method computes the n-th power of the tensor product of the current `Hamiltonian`
        object with itself and assigns the result back to the current object.
        Note that this operation is equivalent to repeatedly applying the tensor product `n` times.

        @param n The power of the tensor product to compute.
        @return A reference to the current `Hamiltonian` object after the tensor product power operation.
        @see Hamiltonian operator^(size_t n) for the non-assignment version of this operation.
            
        """
    @overload
    def update_by_tensor(self, n: int) -> Hamiltonian:
        """update_by_tensor(*args, **kwargs)
        Overloaded function.

        1. update_by_tensor(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the tensor product assignment operator.
        This method computes the tensor product (Kronecker product) of the current
        `Hamiltonian` object with another `Hamiltonian` object `other` and assigns the
        result back to the current object.

        @param other The `Hamiltonian` object to compute the tensor product with.
        @return A reference to the current `Hamiltonian` object after the tensor product operation.
        @note This operation is typically used in quantum mechanics and linear algebra contexts.
            

        2. update_by_tensor(self: hamiltonian.Hamiltonian, n: int) -> hamiltonian.Hamiltonian


        @brief Overload for the tensor product assignment operator to compute the n-th power of the tensor product.

        @details This method computes the n-th power of the tensor product of the current `Hamiltonian`
        object with itself and assigns the result back to the current object.
        Note that this operation is equivalent to repeatedly applying the tensor product `n` times.

        @param n The power of the tensor product to compute.
        @return A reference to the current `Hamiltonian` object after the tensor product power operation.
        @see Hamiltonian operator^(size_t n) for the non-assignment version of this operation.
            
        """
    def __add__(self, other: Hamiltonian) -> Hamiltonian:
        """__add__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the addition operator.
 
        @details This method allows for the addition of two `Hamiltonian` objects. It returns a new
        `Hamiltonian` object that is the sum of the current object and the one passed as a
        parameter.
        (1)If two terms are identical except for their coefficients, a new term is generated with a
        coefficient that is the sum of the original coefficients, and the part of the new term other 
        than the coefficient is the same as the original two terms.
        (2)If two terms are different (excluding coefficients), then two new terms are generated, which are
        identical to the original two terms respectively.
 
        @param other The `Hamiltonian` object to add to the current object.
        @return A new `Hamiltonian` object that is the sum of the current object and `H`.
            
        """
    def __eq__(self, other: Hamiltonian) -> bool:
        """__eq__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> bool


        @brief Checks if the current Hamiltonian is equal to another Hamiltonian.
        *
        This method compares the current `Hamiltonian` object with another `Hamiltonian`
        object `other` to determine if they are equal.
        *
        @param other The `Hamiltonian` object to compare with the current object.
        @return True if the current and other `Hamiltonian` objects are equal, false otherwise.
            
        """
    def __iadd__(self, other: Hamiltonian) -> Hamiltonian:
        """__iadd__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the addition assignment operator to add another Hamiltonian.

        This method adds the given `Hamiltonian` object `other` to the current `Hamiltonian`
        object and assigns the result back to the current object.

        @param other The `Hamiltonian` object to add to the current object.
        @return A reference to the current `Hamiltonian` object after the addition.
            
        """
    def __imul__(self, other: Hamiltonian) -> Hamiltonian:
        """__imul__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication assignment operator to multiply by another Hamiltonian.
        *
        This method multiplies the current `Hamiltonian` object by another `Hamiltonian`
        object `other` and assigns the result back to the current object.
        *
        @param other The `Hamiltonian` object to multiply with the current object.
        @return A reference to the current `Hamiltonian` object after the multiplication.
            
        """
    def __isub__(self, other: Hamiltonian) -> Hamiltonian:
        """__isub__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the subtraction assignment operator to subtract another Hamiltonian.
        *
        This method subtracts the given `Hamiltonian` object `other` from the current `Hamiltonian`
        object and assigns the result back to the current object.
        *
        @param other The `Hamiltonian` object to subtract from the current object.
        @return A reference to the current `Hamiltonian` object after the subtraction.
            
        """
    def __matmul__(self, other: Hamiltonian) -> Hamiltonian:
        """__matmul__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication operator between two Hamiltonians.
 
        @details This method allows for the multiplication of two `Hamiltonian` objects. The
        multiplication follows the distributive property, with the smallest unit of
        operation being the multiplication of coefficients and individual Pauli matrices.
        Parenthetical expressions are handled appropriately. The result is a new
        `Hamiltonian` object that represents the product of the two input objects.
 
        @param other The `Hamiltonian` object to multiply with the current object.
        @return A new `Hamiltonian` object that is the product of the current object and
        `other`.
            
        """
    @overload
    def __mul__(self, other: Hamiltonian) -> Hamiltonian:
        """__mul__(*args, **kwargs)
        Overloaded function.

        1. __mul__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication operator between two Hamiltonians.
 
        @details This method allows for the multiplication of two `Hamiltonian` objects. The
        multiplication follows the distributive property, with the smallest unit of
        operation being the multiplication of coefficients and individual Pauli matrices.
        Parenthetical expressions are handled appropriately. The result is a new
        `Hamiltonian` object that represents the product of the two input objects.
 
        @param other The `Hamiltonian` object to multiply with the current object.
        @return A new `Hamiltonian` object that is the product of the current object and
        `other`.
            

        2. __mul__(self: hamiltonian.Hamiltonian, scalar: complex) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication operator with a complex scalar.

        @details This method allows for the multiplication of a `Hamiltonian` object by a complex
        scalar. It returns a new `Hamiltonian` object that is the product of the current
        object and the scalar.

        @param scalar The complex scalar to multiply the `Hamiltonian` by.
        @return A new `Hamiltonian` object that is the product of the current object and
         `scalar`.
            
        """
    @overload
    def __mul__(self, scalar: complex) -> Hamiltonian:
        """__mul__(*args, **kwargs)
        Overloaded function.

        1. __mul__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication operator between two Hamiltonians.
 
        @details This method allows for the multiplication of two `Hamiltonian` objects. The
        multiplication follows the distributive property, with the smallest unit of
        operation being the multiplication of coefficients and individual Pauli matrices.
        Parenthetical expressions are handled appropriately. The result is a new
        `Hamiltonian` object that represents the product of the two input objects.
 
        @param other The `Hamiltonian` object to multiply with the current object.
        @return A new `Hamiltonian` object that is the product of the current object and
        `other`.
            

        2. __mul__(self: hamiltonian.Hamiltonian, scalar: complex) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication operator with a complex scalar.

        @details This method allows for the multiplication of a `Hamiltonian` object by a complex
        scalar. It returns a new `Hamiltonian` object that is the product of the current
        object and the scalar.

        @param scalar The complex scalar to multiply the `Hamiltonian` by.
        @return A new `Hamiltonian` object that is the product of the current object and
         `scalar`.
            
        """
    def __rmul__(self, scalar: complex) -> Hamiltonian:
        """__rmul__(self: hamiltonian.Hamiltonian, scalar: complex) -> hamiltonian.Hamiltonian


        @brief Overload for the multiplication operator with a complex scalar.

        @details This method allows for the multiplication of a `Hamiltonian` object by a complex
        scalar. It returns a new `Hamiltonian` object that is the product of the current
        object and the scalar.

        @param scalar The complex scalar to multiply the `Hamiltonian` by.
        @return A new `Hamiltonian` object that is the product of the current object and
         `scalar`.
            
        """
    def __sub__(self, other: Hamiltonian) -> Hamiltonian:
        """__sub__(self: hamiltonian.Hamiltonian, other: hamiltonian.Hamiltonian) -> hamiltonian.Hamiltonian


        @brief Overload for the subtraction assignment operator to subtract another Hamiltonian.
 
        @details This method subtracts the given `Hamiltonian` object `other` from the current `Hamiltonian`
        object and assigns the result back to the current object.
        (1)If two terms are identical except for their coefficients, then a new term is generated 
        with a coefficient that is the difference between the original coefficients (left operand minus 
        right operand), and the part of the new term other than the coefficient is the same as the original 
        two terms.
        (2)If two terms are different (excluding coefficients), then two new terms are generated. One of the
        new terms corresponds to the left operand and is exactly the same as the left operand. The other new
        term corresponds to the right operand and is the result of multiplying the coefficient of the right 
        operand by -1.
 
        @param other The `Hamiltonian` object to subtract from the current object.
        @return A reference to the current `Hamiltonian` object after the subtraction.
            
        """

class PauliOperator:
    @overload
    def __init__(self) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, pauli_operator: PauliOperator) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, pauli: str) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, pauli_with_coef_s: dict[str, complex]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, paulis: list[str], coefs: list[complex]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    @overload
    def __init__(self, mat: numpy.ndarray[numpy.float64[m, n]]) -> None:
        '''__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: hamiltonian.PauliOperator) -> None


        @brief Constructs a default PauliOperator object.

        @details This constructor initializes a new PauliOperator object with default values.
        The default behavior may include setting the operator to an identity or null state,
        depending on the implementation details.
            

        2. __init__(self: hamiltonian.PauliOperator, pauli_operator: hamiltonian.PauliOperator) -> None


        @brief Copy constructor for PauliOperator.
 
        @details This constructor creates a new PauliOperator object that is a copy of an existing
        PauliOperator object. It initializes the new object with the same state and values
        as the provided `other` object.
 
        @param other The PauliOperator object to copy from.
            

        3. __init__(self: hamiltonian.PauliOperator, pauli: str) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.

        @param a_pauli The string representation of the Pauli operator.
            

        4. __init__(self: hamiltonian.PauliOperator, pauli_with_coef_s: dict[str, complex]) -> None


        @brief Constructs a PauliOperator from a string representation.

        @details This constructor initializes a new PauliOperator object based on a given string
        `a_pauli` that represents a Pauli operator. The specific format and interpretation
        of the string are defined by the implementation.
        input like: {\\"X0 Z1\\":1.1,\\"Y2 I1\\":2.1+0.j}

        @param a_pauli The string representation of the Pauli operator.
            

        5. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex]) -> None


        @brief Constructs a PauliOperator from vectors of operations and coefficients.

        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. The length of both
        vectors should be the same, and each pair of elements (one from `ops` and one from
        `coef_s`) represents a term in the Pauli operator.
        input like: [\\"X0 Z1\\",\\"Y2 I1\\"],[1.1+0.j,2.1+0.j]
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.

        @param a_pauli The string representation of the Pauli operator.
            

        6. __init__(self: hamiltonian.PauliOperator, paulis: list[str], coefs: list[complex], AB_is_A1_B0: bool) -> None


        @brief Constructs a PauliOperator from vectors of operations, coefficients, and an additional boolean flag.
 
        @details This constructor initializes a new PauliOperator object based on two given vectors:
        `ops` containing string representations of Pauli operator symbols, and `coef_s`
        containing the corresponding std::complex<double> coefficients. Additionally, it
        takes a boolean flag `A` which may affect the initialization process or the behavior
        of the constructed PauliOperator object. The length of both vectors `ops` and `coef_s`
        should be the same, and each pair of elements (one from `ops` and one from `coef_s`)
        represents a term in the Pauli operator.
        input like: [\\"XZI\\",\\"IZX\\"],[1.1+0.j,2.1+0.j],true
 
        @param ops The vector of Pauli operator symbols.
        @param coef_s The vector of corresponding coefficients.
        @param A     The boolean flag that may affect the initialization or behavior.
            

        7. __init__(self: hamiltonian.PauliOperator, paulis_qbits_coef__s: list[tuple[str, list[int], complex]]) -> None


        @brief Constructs a PauliOperator from a vector of tuples.

        @details This constructor initializes a new PauliOperator object based on a given vector of
        tuples `ops`. Each tuple contains three elements: a string representing a Pauli
        operator symbol, a vector of size_t indices, and a std::complex<double> coefficient.
        The vector of tuples represents a collection of terms in the Pauli operator, where
        each term is specified by its operator symbol, indices (if applicable), and coefficient.
        input like: [(\\"XZ\\",[0,4],1.1+0.j),(\\"YX\\",[1,2],2.1+0.j)]

        @param ops The vector of tuples containing Pauli operator symbols, indices, and coefficients.
            

        8. __init__(self: hamiltonian.PauliOperator, mat: numpy.ndarray[numpy.float64[m, n]]) -> None


        @brief Constructs a PauliOperator object from a given real number matrix.

        @param mat A const reference to an real number Matrix with dynamic size.
        The matrix is expected to have double precision elements.
            
        '''
    def group_commuting(self, qubit_wise: bool = ...) -> list[PauliOperator]:
        """group_commuting(self: hamiltonian.PauliOperator, qubit_wise: bool = False) -> list[hamiltonian.PauliOperator]


        @brief Groups a set of Pauli operators into commuting subsets.

        @details This function takes a PauliOperator as input and groups it into commuting subsets.
        If qubit_wise is true, the grouping is done based on qubit-wise commutation,
        where two Pauli operators commute if they act on different qubits or have commuting Pauli matrices on the same qubits.
        If qubit_wise is false, the grouping is done based on full commutation,
        where two Pauli operators commute if their commutator is zero.

        @param qubit_wise A boolean indicating whether to use qubit-wise commutation (true) or full commutation (false).
        @return A vector of vectors of PauliOperator, where each inner vector contains commuting Pauli operators.
        
        """
    def matrix(self) -> numpy.ndarray[numpy.complex128[m, n]]:
        """matrix(self: hamiltonian.PauliOperator) -> numpy.ndarray[numpy.complex128[m, n]]


        @brief Converts a PauliOperator object to its corresponding matrix representation.
 
        @details This function takes a PauliOperator as input and returns its matrix representation.
        The PauliOperator is expected to be a tensor product of Pauli matrices (X, Y, Z, I)
        acting on a specific number of qubits.
 
        @param opt The PauliOperator object to be converted.
        @return A matrix representing the PauliOperator.
            
        """
    def str_no_I(self) -> str:
        '''str_no_I(self: hamiltonian.PauliOperator) -> str


        @brief Converts the PauliOperator to a string representation without the \'I\' (identity) term.
 
        @details This method generates a string that represents the PauliOperator, excluding the \'I\' term.
        The string consists of characters \'X\', \'Y\', \'Z\', and digits, where "X#", "Y#", and "Z#" represent
        Pauli operators X, Y, and Z acting on qubits with index #, respectively.
        The `AB_is_A1_B0` parameter specifies the order of the character substrings representing the Pauli
        operators on different qubits in the resulting string. If `AB_is_A1_B0` is true, the substring
        corresponding to the qubit with the larger index appears first in the string. If false, the substring
        with the smaller index appears first.
        @param AB_is_A1_B0 If true, the substring for the qubit with the larger index appears first in the string.
        If false, the substring for the qubit with the smaller index appears first.
        @return A string that represents the PauliOperator without the \'I\' term, with the specified order of substrings.
            
        '''
    def str_with_I(self, AB_is_A1_B0: bool = ...) -> str:
        """str_with_I(self: hamiltonian.PauliOperator, AB_is_A1_B0: bool = True) -> str


        @brief Converts the PauliOperator to a string representation with Pauli matrices.
 
        @details This method converts the current `PauliOperator` object to a string representation
        where the Pauli matrices are represented by the characters 'X', 'Y', 'Z', and 'I'.
        The parameter `AB_is_A1_B0` indicates the relationship between the order of the
        characters in the string and the qubit indices. If `AB_is_A1_B0` is true, then the
        characters with smaller indices in the string correspond to larger qubit indices.
        Otherwise, the characters with smaller indices in the string correspond to smaller
        qubit indices.
 
        @param AB_is_A1_B0 A boolean value that specifies the character order in relation
        to qubit indices.
        @return A string representation of the `PauliOperator` object with Pauli matrices
        represented by 'X', 'Y', 'Z', and 'I'.
            
        """
    def str_withou_I(self) -> str:
        '''str_withou_I(self: hamiltonian.PauliOperator) -> str


        @brief Converts the PauliOperator to a string representation without the \'I\' (identity) term.
 
        @details This method generates a string that represents the PauliOperator, excluding the \'I\' term.
        The string consists of characters \'X\', \'Y\', \'Z\', and digits, where "X#", "Y#", and "Z#" represent
        Pauli operators X, Y, and Z acting on qubits with index #, respectively.
        The `AB_is_A1_B0` parameter specifies the order of the character substrings representing the Pauli
        operators on different qubits in the resulting string. If `AB_is_A1_B0` is true, the substring
        corresponding to the qubit with the larger index appears first in the string. If false, the substring
        with the smaller index appears first.
        @param AB_is_A1_B0 If true, the substring for the qubit with the larger index appears first in the string.
        If false, the substring for the qubit with the smaller index appears first.
        @return A string that represents the PauliOperator without the \'I\' term, with the specified order of substrings.
            
        '''
    @overload
    def tensor(self, other: PauliOperator) -> PauliOperator:
        """tensor(*args, **kwargs)
        Overloaded function.

        1. tensor(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `^` operator for performing the tensor product of two PauliOperators.
 
        @details This method computes the tensor product (Kronecker product) of the current PauliOperator
        with another PauliOperator, resulting in a new PauliOperator that represents the combined
        system of the two input PauliOperators.
 
        @param other The PauliOperator to compute the tensor product with.
        @return A new PauliOperator that is the tensor product of the two input PauliOperators.
            

        2. tensor(self: hamiltonian.PauliOperator, n: int) -> hamiltonian.PauliOperator


        @brief Overload of the `^` operator for performing the tensor product operation n-1 times.
 
        @details This method allows for the computation of the tensor product of the current PauliOperator
        with itself `n-1` times, resulting in a new PauliOperator that represents this repeated
        tensor product.
 
        @param n The number of times to perform the tensor product operation (i.e., `n-1` tensor products).
        @return A new PauliOperator that is the result of performing the tensor product operation `n-1` times.
            
        """
    @overload
    def tensor(self, n: int) -> PauliOperator:
        """tensor(*args, **kwargs)
        Overloaded function.

        1. tensor(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `^` operator for performing the tensor product of two PauliOperators.
 
        @details This method computes the tensor product (Kronecker product) of the current PauliOperator
        with another PauliOperator, resulting in a new PauliOperator that represents the combined
        system of the two input PauliOperators.
 
        @param other The PauliOperator to compute the tensor product with.
        @return A new PauliOperator that is the tensor product of the two input PauliOperators.
            

        2. tensor(self: hamiltonian.PauliOperator, n: int) -> hamiltonian.PauliOperator


        @brief Overload of the `^` operator for performing the tensor product operation n-1 times.
 
        @details This method allows for the computation of the tensor product of the current PauliOperator
        with itself `n-1` times, resulting in a new PauliOperator that represents this repeated
        tensor product.
 
        @param n The number of times to perform the tensor product operation (i.e., `n-1` tensor products).
        @return A new PauliOperator that is the result of performing the tensor product operation `n-1` times.
            
        """
    def terms(self, *args, **kwargs):
        """terms(self: hamiltonian.PauliOperator) -> list[QPanda3::HamiltonianPauli::PauliTerm]"""
    def to_hamiltonian_pq2(self) -> list[tuple[dict[int, str], complex]]:
        """to_hamiltonian_pq2(self: hamiltonian.PauliOperator) -> list[tuple[dict[int, str], complex]]"""
    def to_qcircuits(self, *args, **kwargs):
        """to_qcircuits(self: hamiltonian.PauliOperator) -> list[tuple[QPanda3::QCircuit, complex]]"""
    def __add__(self, other: PauliOperator) -> PauliOperator:
        """__add__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `+` operator for adding two PauliOperators.
 
        @details This method allows for the addition of two PauliOperators, resulting in a new
        PauliOperator that represents the sum of the two input PauliOperators.
 
        @param pauli_op The PauliOperator to add to the current PauliOperator.
        @return A new PauliOperator that is the sum of the two input PauliOperators.
            
        """
    def __eq__(self, other: PauliOperator) -> bool:
        """__eq__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> bool


        @brief Checks if the current PauliOperator is equal to another PauliOperator.
 
        @details This method compares the current PauliOperator with another PauliOperator to determine if they are equal.
        Two PauliOperators are considered equal if they have the same terms and coefficients.
 
        @param other The PauliOperator to compare with the current PauliOperator.
        @return True if the current PauliOperator is equal to the input PauliOperator, false otherwise.
            
        """
    def __iadd__(self, other: PauliOperator) -> PauliOperator:
        """__iadd__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `+=` operator for adding two PauliOperators.

        @details This method allows for the addition of two PauliOperators. The current PauliOperator is updated to be the sum
        of the current PauliOperator and the input PauliOperator.

        @param other The PauliOperator to add to the current PauliOperator.
        @return A reference to the updated current PauliOperator.
            
        """
    def __imul__(self, other: PauliOperator) -> PauliOperator:
        """__imul__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `=` operator for multiplying two PauliOperators.
 
        @details This method allows for the multiplication of two PauliOperators. The current PauliOperator is updated to be the product
        of the current PauliOperator and the input PauliOperator.
        Note: The multiplication of PauliOperators typically follows the rules of tensor products and may result in a new
        PauliOperator with combined terms and coefficients.
 
        @param other The PauliOperator to multiply with the current PauliOperator.
        @return A reference to the updated current PauliOperator.
            
        """
    def __isub__(self, other: PauliOperator) -> PauliOperator:
        """__isub__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `-=` operator for subtracting two PauliOperators.
 
        @details This method allows for the subtraction of two PauliOperators. The current PauliOperator is updated to be the difference
        of the current PauliOperator and the input PauliOperator.
 
        @param other The PauliOperator to subtract from the current PauliOperator.
        @return A reference to the updated current PauliOperator.
            
        """
    def __matmul__(self, other: PauliOperator) -> PauliOperator:
        """__matmul__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `` operator for multiplying two PauliOperators.
 
        @details This method allows for the multiplication of two PauliOperators, resulting in a new
        PauliOperator that represents the product of the two input PauliOperators.
        (1)If two terms are identical except for their coefficients, then a new term is generated 
        with a coefficient that is the difference between the original coefficients (left operand minus 
        right operand), and the part of the new term other than the coefficient is the same as the original 
        two terms.
        (2)If two terms are different (excluding coefficients), then two new terms are generated. One of the
        new terms corresponds to the left operand and is exactly the same as the left operand. The other new
        term corresponds to the right operand and is the result of multiplying the coefficient of the right 
        operand by -1.
 
        @param other The PauliOperator to multiply with the current PauliOperator.
        @return A new PauliOperator that is the product of the two input PauliOperators. 
            
        """
    @overload
    def __mul__(self, other: PauliOperator) -> PauliOperator:
        """__mul__(*args, **kwargs)
        Overloaded function.

        1. __mul__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `` operator for multiplying two PauliOperators.
 
        @details This method allows for the multiplication of two PauliOperators, resulting in a new
        PauliOperator that represents the product of the two input PauliOperators.
        (1)If two terms are identical except for their coefficients, then a new term is generated 
        with a coefficient that is the difference between the original coefficients (left operand minus 
        right operand), and the part of the new term other than the coefficient is the same as the original 
        two terms.
        (2)If two terms are different (excluding coefficients), then two new terms are generated. One of the
        new terms corresponds to the left operand and is exactly the same as the left operand. The other new
        term corresponds to the right operand and is the result of multiplying the coefficient of the right 
        operand by -1.
 
        @param other The PauliOperator to multiply with the current PauliOperator.
        @return A new PauliOperator that is the product of the two input PauliOperators. 
            

        2. __mul__(self: hamiltonian.PauliOperator, scalar: complex) -> hamiltonian.PauliOperator


        @brief Overload of the `` operator for multiplying a PauliOperator by a scalar.
 
        @details This method allows for the multiplication of a PauliOperator by a scalar value,
        resulting in a new PauliOperator that represents the scaled version of the original
        PauliOperator.

        @param scalar The scalar value to multiply the PauliOperator by.
        @return A new PauliOperator that is the scaled version of the original PauliOperator.
            
        """
    @overload
    def __mul__(self, scalar: complex) -> PauliOperator:
        """__mul__(*args, **kwargs)
        Overloaded function.

        1. __mul__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `` operator for multiplying two PauliOperators.
 
        @details This method allows for the multiplication of two PauliOperators, resulting in a new
        PauliOperator that represents the product of the two input PauliOperators.
        (1)If two terms are identical except for their coefficients, then a new term is generated 
        with a coefficient that is the difference between the original coefficients (left operand minus 
        right operand), and the part of the new term other than the coefficient is the same as the original 
        two terms.
        (2)If two terms are different (excluding coefficients), then two new terms are generated. One of the
        new terms corresponds to the left operand and is exactly the same as the left operand. The other new
        term corresponds to the right operand and is the result of multiplying the coefficient of the right 
        operand by -1.
 
        @param other The PauliOperator to multiply with the current PauliOperator.
        @return A new PauliOperator that is the product of the two input PauliOperators. 
            

        2. __mul__(self: hamiltonian.PauliOperator, scalar: complex) -> hamiltonian.PauliOperator


        @brief Overload of the `` operator for multiplying a PauliOperator by a scalar.
 
        @details This method allows for the multiplication of a PauliOperator by a scalar value,
        resulting in a new PauliOperator that represents the scaled version of the original
        PauliOperator.

        @param scalar The scalar value to multiply the PauliOperator by.
        @return A new PauliOperator that is the scaled version of the original PauliOperator.
            
        """
    def __rmul__(self, scalar: complex) -> PauliOperator:
        """__rmul__(self: hamiltonian.PauliOperator, scalar: complex) -> hamiltonian.PauliOperator


        @brief Overload of the `` operator for multiplying a PauliOperator by a scalar.
 
        @details This method allows for the multiplication of a PauliOperator by a scalar value,
        resulting in a new PauliOperator that represents the scaled version of the original
        PauliOperator.

        @param scalar The scalar value to multiply the PauliOperator by.
        @return A new PauliOperator that is the scaled version of the original PauliOperator.
            
        """
    def __sub__(self, other: PauliOperator) -> PauliOperator:
        """__sub__(self: hamiltonian.PauliOperator, other: hamiltonian.PauliOperator) -> hamiltonian.PauliOperator


        @brief Overload of the `-` operator for subtracting two PauliOperators.
 
        @details This method allows for the subtraction of one PauliOperator from another, resulting in a new
        PauliOperator that represents the difference between the two input PauliOperators.
        (1)If two terms are identical except for their coefficients, a new term is generated with a
        coefficient that is the sum of the original coefficients, and the part of the new term other 
        than the coefficient is the same as the original two terms.
        (2)If two terms are different (excluding coefficients), then two new terms are generated, which are
        identical to the original two terms respectively.
 
        @param pauli_op The PauliOperator to subtract from the current PauliOperator.
        @return A new PauliOperator that is the result of subtracting the input PauliOperator from the current one.
            
        """

class PauliTerm:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def coef(self) -> complex:
        """coef(self: hamiltonian.PauliTerm) -> complex"""
    def paulis(self, *args, **kwargs):
        """paulis(self: hamiltonian.PauliTerm) -> list[QPanda3::HamiltonianPauli::PauliWithQbit]"""
    def to_qcircuit(self, *args, **kwargs):
        """to_qcircuit(self: hamiltonian.PauliTerm) -> QPanda3::QCircuit"""

class PauliWithQbit:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def is_I(self) -> bool:
        """is_I(self: hamiltonian.PauliWithQbit) -> bool"""
    def is_X(self) -> bool:
        """is_X(self: hamiltonian.PauliWithQbit) -> bool"""
    def is_Y(self) -> bool:
        """is_Y(self: hamiltonian.PauliWithQbit) -> bool"""
    def is_Z(self) -> bool:
        """is_Z(self: hamiltonian.PauliWithQbit) -> bool"""
    def pauli_char(self) -> str:
        """pauli_char(self: hamiltonian.PauliWithQbit) -> str"""
    def qbit(self) -> int:
        """qbit(self: hamiltonian.PauliWithQbit) -> int"""
    def to_qgate(self, *args, **kwargs):
        """to_qgate(self: hamiltonian.PauliWithQbit) -> QPanda3::QGate"""
