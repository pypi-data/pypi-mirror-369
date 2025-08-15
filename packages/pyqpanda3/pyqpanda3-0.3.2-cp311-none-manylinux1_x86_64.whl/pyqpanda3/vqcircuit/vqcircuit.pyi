import numpy
from typing import Any, ClassVar, overload

ADJOINT_DIFF: DiffMethod

class DiffMethod:
    __members__: ClassVar[dict] = ...  # read-only
    ADJOINT_DIFF: ClassVar[DiffMethod] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: vqcircuit.DiffMethod, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: vqcircuit.DiffMethod) -> int"""
    def __int__(self) -> int:
        """__int__(self: vqcircuit.DiffMethod) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class ParamExpression:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: vqcircuit.ParamExpression) -> None

        2. __init__(self: vqcircuit.ParamExpression, arg0: vqcircuit.ParamExpression) -> None
        """
    @overload
    def __init__(self, arg0: ParamExpression) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: vqcircuit.ParamExpression) -> None

        2. __init__(self: vqcircuit.ParamExpression, arg0: vqcircuit.ParamExpression) -> None
        """
    def calculate_expression_val(self) -> None:
        """calculate_expression_val(self: vqcircuit.ParamExpression) -> None


        @brief Calculate the value of the expression. Please obtain the result using Interface get_expression_val.
                
        """
    def calculate_gradient_val(self, arg0: float) -> None:
        """calculate_gradient_val(self: vqcircuit.ParamExpression, arg0: float) -> None


        @brief Calculate the gradient value of the expression on its placeholders.
                
        """
    def get_expression_val(self) -> float:
        """get_expression_val(self: vqcircuit.ParamExpression) -> float


        @brief Obtain the val of the expression. Before using the interface ,please using interface calculate_expression_val firstly.
                
        """
    @overload
    def __add__(self, arg0: ParamExpression) -> ParamExpression:
        """__add__(*args, **kwargs)
        Overloaded function.

        1. __add__(self: vqcircuit.ParamExpression, arg0: vqcircuit.ParamExpression) -> vqcircuit.ParamExpression

        2. __add__(self: vqcircuit.ParamExpression, arg0: float) -> vqcircuit.ParamExpression
        """
    @overload
    def __add__(self, arg0: float) -> ParamExpression:
        """__add__(*args, **kwargs)
        Overloaded function.

        1. __add__(self: vqcircuit.ParamExpression, arg0: vqcircuit.ParamExpression) -> vqcircuit.ParamExpression

        2. __add__(self: vqcircuit.ParamExpression, arg0: float) -> vqcircuit.ParamExpression
        """
    @overload
    def __mul__(self, arg0: ParamExpression) -> ParamExpression:
        """__mul__(*args, **kwargs)
        Overloaded function.

        1. __mul__(self: vqcircuit.ParamExpression, arg0: vqcircuit.ParamExpression) -> vqcircuit.ParamExpression

        2. __mul__(self: vqcircuit.ParamExpression, arg0: float) -> vqcircuit.ParamExpression
        """
    @overload
    def __mul__(self, arg0: float) -> ParamExpression:
        """__mul__(*args, **kwargs)
        Overloaded function.

        1. __mul__(self: vqcircuit.ParamExpression, arg0: vqcircuit.ParamExpression) -> vqcircuit.ParamExpression

        2. __mul__(self: vqcircuit.ParamExpression, arg0: float) -> vqcircuit.ParamExpression
        """
    def __radd__(self, arg0: float) -> ParamExpression:
        """__radd__(self: vqcircuit.ParamExpression, arg0: float) -> vqcircuit.ParamExpression"""
    def __rmul__(self, arg0: float) -> ParamExpression:
        """__rmul__(self: vqcircuit.ParamExpression, arg0: float) -> vqcircuit.ParamExpression"""

class Parameter:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def size(self) -> int:
        """size(self: vqcircuit.Parameter) -> int"""

class ResGradients:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @overload
    def at(self, idx_s: list[int]) -> float:
        """at(*args, **kwargs)
        Overloaded function.

        1. at(self: vqcircuit.ResGradients, idx_s: list[int]) -> float


        @brief Get a gradient value

        @details If a mutable parameter is placeholder-ed using vqc.Param([idx_dim0, idx_dim1, ..., idx_dimn]), the corresponding gradient value can be obtained using at([idx_dim0, idx_dim1, ..., idx_dimn]).
        @param idx_s It should be input like [idx_dim0, idx_dim1, ..., idx_dimn]
        @return A gradient value
            

        2. at(self: vqcircuit.ResGradients, idx: int) -> float


        @brief Get a gradient value

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate a quantum circuit, the gradient value corresponding to the parameter value val_i can be obtained using at(i).
        @param idx_s It's i
        @return A gradient value
            
        """
    @overload
    def at(self, idx: int) -> float:
        """at(*args, **kwargs)
        Overloaded function.

        1. at(self: vqcircuit.ResGradients, idx_s: list[int]) -> float


        @brief Get a gradient value

        @details If a mutable parameter is placeholder-ed using vqc.Param([idx_dim0, idx_dim1, ..., idx_dimn]), the corresponding gradient value can be obtained using at([idx_dim0, idx_dim1, ..., idx_dimn]).
        @param idx_s It should be input like [idx_dim0, idx_dim1, ..., idx_dimn]
        @return A gradient value
            

        2. at(self: vqcircuit.ResGradients, idx: int) -> float


        @brief Get a gradient value

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate a quantum circuit, the gradient value corresponding to the parameter value val_i can be obtained using at(i).
        @param idx_s It's i
        @return A gradient value
            
        """
    @overload
    def at(self, i) -> Any:
        """at(*args, **kwargs)
        Overloaded function.

        1. at(self: vqcircuit.ResGradients, idx_s: list[int]) -> float


        @brief Get a gradient value

        @details If a mutable parameter is placeholder-ed using vqc.Param([idx_dim0, idx_dim1, ..., idx_dimn]), the corresponding gradient value can be obtained using at([idx_dim0, idx_dim1, ..., idx_dimn]).
        @param idx_s It should be input like [idx_dim0, idx_dim1, ..., idx_dimn]
        @return A gradient value
            

        2. at(self: vqcircuit.ResGradients, idx: int) -> float


        @brief Get a gradient value

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate a quantum circuit, the gradient value corresponding to the parameter value val_i can be obtained using at(i).
        @param idx_s It's i
        @return A gradient value
            
        """
    def gradients(self) -> list[float]:
        """gradients(self: vqcircuit.ResGradients) -> list[float]


        @brief Get all gradient values

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate the quantum circuit, the corresponding gradient values will be returned in the form [gradient_0, gradient_1, ..., gradient_n], where the gradient value gradient_i corresponds to the parameter value val_i.
        @return Returns a list where each element is a gradient value.
            
        """
    def __len__(self) -> int:
        """__len__(self: vqcircuit.ResGradients) -> int


        @brief If an array [val_0, val_1, ..., val_n] is passed in as parameter values to generate a quantum circuit, the size of this array will be returned, and this size is equal to the number of gradient values.
            
        """

class ResGradientsAndExpectation:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @overload
    def at(self, idx_s: list[int]) -> float:
        """at(*args, **kwargs)
        Overloaded function.

        1. at(self: vqcircuit.ResGradientsAndExpectation, idx_s: list[int]) -> float


        @brief Get a gradient value

        @details If a mutable parameter is placeholder-ed using vqc.Param([idx_dim0, idx_dim1, ..., idx_dimn]), the corresponding gradient value can be obtained using at([idx_dim0, idx_dim1, ..., idx_dimn]).
        @param idx_s It should be input like [idx_dim0, idx_dim1, ..., idx_dimn]
        @return A gradient value
            

        2. at(self: vqcircuit.ResGradientsAndExpectation, idx: int) -> float


        @brief Get a gradient value

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate a quantum circuit, the gradient value corresponding to the parameter value val_i can be obtained using at(i).
        @param idx_s It's i
        @return A gradient value
            
        """
    @overload
    def at(self, idx: int) -> float:
        """at(*args, **kwargs)
        Overloaded function.

        1. at(self: vqcircuit.ResGradientsAndExpectation, idx_s: list[int]) -> float


        @brief Get a gradient value

        @details If a mutable parameter is placeholder-ed using vqc.Param([idx_dim0, idx_dim1, ..., idx_dimn]), the corresponding gradient value can be obtained using at([idx_dim0, idx_dim1, ..., idx_dimn]).
        @param idx_s It should be input like [idx_dim0, idx_dim1, ..., idx_dimn]
        @return A gradient value
            

        2. at(self: vqcircuit.ResGradientsAndExpectation, idx: int) -> float


        @brief Get a gradient value

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate a quantum circuit, the gradient value corresponding to the parameter value val_i can be obtained using at(i).
        @param idx_s It's i
        @return A gradient value
            
        """
    @overload
    def at(self, i) -> Any:
        """at(*args, **kwargs)
        Overloaded function.

        1. at(self: vqcircuit.ResGradientsAndExpectation, idx_s: list[int]) -> float


        @brief Get a gradient value

        @details If a mutable parameter is placeholder-ed using vqc.Param([idx_dim0, idx_dim1, ..., idx_dimn]), the corresponding gradient value can be obtained using at([idx_dim0, idx_dim1, ..., idx_dimn]).
        @param idx_s It should be input like [idx_dim0, idx_dim1, ..., idx_dimn]
        @return A gradient value
            

        2. at(self: vqcircuit.ResGradientsAndExpectation, idx: int) -> float


        @brief Get a gradient value

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate a quantum circuit, the gradient value corresponding to the parameter value val_i can be obtained using at(i).
        @param idx_s It's i
        @return A gradient value
            
        """
    def data(self) -> tuple[float, list[float]]:
        """data(self: vqcircuit.ResGradientsAndExpectation) -> tuple[float, list[float]]


        @brief Get internal data
        @details All gradient values and the expectation value are returned as a combination of fundamental data types. The first element of the tuple corresponds to the expectation value, and the second element is a list containing all the gradient values.
            
        """
    def expectation_val(self) -> float:
        """expectation_val(self: vqcircuit.ResGradientsAndExpectation) -> float


        @brief expectation value
        @return Returns a expectation value.
            
        """
    def gradients(self) -> list[float]:
        """gradients(self: vqcircuit.ResGradientsAndExpectation) -> list[float]


        @brief Get all gradient values

        @details If an array [val_0, val_1, ..., val_n] is passed as the parameter values to generate the quantum circuit, the corresponding gradient values will be returned in the form [gradient_0, gradient_1, ..., gradient_n], where the gradient value gradient_i corresponds to the parameter value val_i.
        @return Returns a list where each element is a gradient value.
            
        """

class ResNGradients:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @overload
    def at(self, idx: int) -> ResGradients:
        """at(self: vqcircuit.ResNGradients, idx: int) -> vqcircuit.ResGradients


        @brief Pass in N sets of parameters to generate N quantum circuits and their corresponding N sets of gradient values. The at(idx) method is used to retrieve all gradient values corresponding to the idx-th set of parameters, with the result returned as a ResGradients object.
            
        """
    @overload
    def at(self, idx) -> Any:
        """at(self: vqcircuit.ResNGradients, idx: int) -> vqcircuit.ResGradients


        @brief Pass in N sets of parameters to generate N quantum circuits and their corresponding N sets of gradient values. The at(idx) method is used to retrieve all gradient values corresponding to the idx-th set of parameters, with the result returned as a ResGradients object.
            
        """
    def data(self) -> list[list[float]]:
        """data(self: vqcircuit.ResNGradients) -> list[list[float]]


        @brief The internal data storing gradient values is returned as a combination of built-in types. It returns a list where each element is a list that stores a set of gradients. This set of gradients corresponds to a specific set of parameters.
            
        """
    def __len__(self) -> int:
        """__len__(self: vqcircuit.ResNGradients) -> int


        @brief return the total of gradient groups, which equal N
            
        """

class ResNResGradientsAndExpectation:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @overload
    def at(self, idx: int) -> ResGradientsAndExpectation:
        """at(self: vqcircuit.ResNResGradientsAndExpectation, idx: int) -> vqcircuit.ResGradientsAndExpectation


        @brief Pass in N sets of parameters to generate N quantum circuits and their corresponding N sets of gradient values. The at(idx) method is used to retrieve all gradient values corresponding to the idx-th set of parameters, with the result returned as a ResGradientsAndExpectation object.
             
        """
    @overload
    def at(self, idx) -> Any:
        """at(self: vqcircuit.ResNResGradientsAndExpectation, idx: int) -> vqcircuit.ResGradientsAndExpectation


        @brief Pass in N sets of parameters to generate N quantum circuits and their corresponding N sets of gradient values. The at(idx) method is used to retrieve all gradient values corresponding to the idx-th set of parameters, with the result returned as a ResGradientsAndExpectation object.
             
        """
    def data(self) -> list[tuple[float, list[float]]]:
        """data(self: vqcircuit.ResNResGradientsAndExpectation) -> list[tuple[float, list[float]]]


        @brief The internal data storing gradient values is returned as a combination of built-in types. A list is returned, where each element of the list is a tuple. The first element of the tuple corresponds to a gradient value, and the second element is a list that stores a set of gradients. This tuple corresponds to a set of parameters.
            
        """
    def __len__(self) -> int:
        """__len__(self: vqcircuit.ResNResGradientsAndExpectation) -> int


        @brief return the total of gradient and expectation groups, which equal N
            
        """

class VQCResult:
    def __init__(self) -> None:
        """__init__(self: vqcircuit.VQCResult) -> None


        @brief Default constructor for the VQCircuitResult class.
        @details This constructor initializes a new instance of the VQCircuitResult class. The VQCircuitResult class is used to store and manage a collection of QCircuit objects generated by a VQCircuit.
            
        """
    def at(self, *args, **kwargs):
        """at(self: vqcircuit.VQCResult, idxs: list[int]) -> QPanda3::QCircuit


        @brief Accesses a QCircuit object at a specified index.
        @details This method retrieves a reference to the QCircuit object at the specified index, which is determined by the provided vector of qubit indices. The vector should contain the indices of the qubits that correspond to the desired QCircuit.
        @param idxs the specified index
        @return a reference to the QCircuit object at the specified index
            
        """
    def expval_at(self, idxs: list[int]) -> float:
        """expval_at(self: vqcircuit.VQCResult, idxs: list[int]) -> float


        @brief Calculates the expectation value of a QCircuit object at a specified index.
        @param idxs the specified index
        @return the expectation value of a QCircuit object at a specified index.
            
        """
    @overload
    def expval_hamiltonian(self, hamiltonian, shots: int, model, used_threads: int = ..., backend: str = ...) -> list[float]:
        '''expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        2. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        3. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            

        4. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            
        '''
    @overload
    def expval_hamiltonian(self, hamiltonian, used_threads: int = ..., backend: str = ...) -> list[float]:
        '''expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        2. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        3. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            

        4. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            
        '''
    @overload
    def expval_hamiltonian(self, hamiltonian, idx_s: list[int], shots: int, model, used_threads: int = ..., backend: str = ...) -> float:
        '''expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        2. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        3. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            

        4. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            
        '''
    @overload
    def expval_hamiltonian(self, hamiltonian, idx_s: list[int], used_threads: int = ..., backend: str = ...) -> float:
        '''expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        2. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Hamiltonian.

        @details This function evaluates the expectation value of a Hamiltonian on a quantum state.
        The expectation value is computed based on the specified number of shots and can
        optionally incorporate a noise model to simulate real-world conditions.

        @param Ham The Hamiltonian for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values
        of the Hamiltonian terms.
            

        3. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            

        4. expval_hamiltonian(self: vqcircuit.VQCResult, hamiltonian: QPanda3::Hamiltonian, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Hamiltonian.

        @details This function computes the expectation value for a subset of terms in a given Hamiltonian,
        as specified by the indices provided. The computation can optionally include a noise model
        and is performed based on the number of shots specified.

        @param Ham The Hamiltonian containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Hamiltonian to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default,but you can select "GPU").

        @return A double representing the combined expectation value of the specified Hamiltonian terms.
            
        '''
    @overload
    def expval_pauli_operator(self, pauli_operator, shots: int, model, used_threads: int = ..., backend: str = ...) -> list[float]:
        '''expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        2. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        3. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            

        4. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            
        '''
    @overload
    def expval_pauli_operator(self, pauli_operator, used_threads: int = ..., backend: str = ...) -> list[float]:
        '''expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        2. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        3. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            

        4. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            
        '''
    @overload
    def expval_pauli_operator(self, pauli_operator, idx_s: list[int], shots: int, model, used_threads: int = ..., backend: str = ...) -> float:
        '''expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        2. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        3. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            

        4. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            
        '''
    @overload
    def expval_pauli_operator(self, pauli_operator, idx_s: list[int], used_threads: int = ..., backend: str = ...) -> float:
        '''expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param shots The number of measurements to perform. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        2. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, used_threads: int = 4, backend: str = \'CPU\') -> list[float]


        @brief Calculates the expectation value of a given Pauli operator.

        @details This function evaluates the expectation value of a Pauli operator on a quantum state.
        The result is returned as a vector of doubles, where each element corresponds to the
        expectation value for a specific measurement basis or configuration.

        @param pauli_operator The Pauli operator for which the expectation value is to be computed.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A reference to a vector of doubles containing the expectation values.
            

        3. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], shots: int, model: QPanda3::NoiseModel, used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param shots The number of measurements to perform for each term. Default is 1.
        @param model The noise model to apply during the simulation. Default is an empty (ideal) NoiseModel.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            

        4. expval_pauli_operator(self: vqcircuit.VQCResult, pauli_operator: QPanda3::PauliOperator, idx_s: list[int], used_threads: int = 4, backend: str = \'CPU\') -> float


        @brief Calculates the expectation value of specific terms in a Pauli operator.

        @details This function evaluates the expectation value for a subset of terms in a given Pauli operator,
        as specified by the indices provided. The computation can optionally include a noise model
        and is based on the number of shots specified.

        @param pauli_operator The Pauli operator containing the terms of interest.
        @param idx_s A vector of indices specifying which terms of the Pauli operator to evaluate.
        @param used_threads The number of threads to use for parallel computation. Default is 4.
        @param backend Specifies the backend for computation ("CPU" by default, but you can select "GPU").

        @return A double representing the combined expectation value of the specified Pauli operator terms.
            
        '''

class VQCircuit:
    def __init__(self, pre_split: bool = ...) -> None:
        """__init__(self: vqcircuit.VQCircuit, pre_split: bool = True) -> None


        @brief Constructs a new instance of the VariationalQuantumCircuit class.

        @details This constructor initializes a new empty instance of the VariationalQuantumCircuit class, ready for further configuration and use.
            
        """
    def Param(self, *args, **kwargs):
        """Param(*args, **kwargs)
        Overloaded function.

        1. Param(self: vqcircuit.VQCircuit, idxs: list[int], emement_label: str) -> QPanda3::VQCParamSystem::ParamExpression


        @brief Retrieves the multi-dimensional array indices and associates a label with the corresponding parameter.
        @details This method takes a vector of indices (`idxs`) specifying a position in a multi-dimensional array, along with a label string (`element_label`) to identify the parameter at that position.It returns the provided indices and internally associates the label with the corresponding parameter.
        @param idxs a vector of indices specifying a position in a multi-dimensional array
        @param emement_label a label string to identify the parameter 
        @return th position in the multi-dimensional array
            

        2. Param(self: vqcircuit.VQCircuit, idxs: list[int]) -> QPanda3::VQCParamSystem::ParamExpression


        @brief Retrieves the multi-dimensional array indices and associates a label with the corresponding parameter.
        @details This method takes a vector of indices (`idxs`) specifying a position in a multi-dimensional array, along with a label string (`element_label`) to identify the parameter at that position.It returns the provided indices and internally associates the label with the corresponding parameter.
        @param idxs a vector of indices specifying a position in a multi-dimensional array
        @return th position in the multi-dimensional array
            

        3. Param(self: vqcircuit.VQCircuit, emement_label: str) -> QPanda3::VQCParamSystem::ParamExpression


        @brief Retrieves the multidimensional array index for a variable parameter with a specified label.
        @details This method takes a label string for a variable parameter and returns the corresponding multidimensional array index.
        @param emement_label a label string to identify the parameter 
        @return th position in the multi-dimensional array
            
        """
    def append(self, sub_vqc: VQCircuit, placeholder_map) -> VQCircuit:
        """append(self: vqcircuit.VQCircuit, sub_vqc: vqcircuit.VQCircuit, placeholder_map: list[tuple[QPanda3::VQCParamSystem::ParamExpression, QPanda3::VQCParamSystem::ParamExpression]]) -> vqcircuit.VQCircuit


        @brief Appends a sub-VQCircuit to the current VQCircuit with a placeholder map.

        @details This method appends the given sub_vqc to the current VQCircuit instance. The placeholder_map
        is used to map parameters in the sub_vqc to the parameters in the current VQCircuit.

        Add all quantum gates in a VQCircuit object subvqc to a VQCircuit object self. The addition process only re-maps and sets the placeholder.
        If the variable parameter of a quantum gate is in the form of an expression, during the addition process, it still retains its expression form, but the placeholder that constitutes the expression changes from a placeholder of subvqc to a placeholder of self. When self updates the value of the placeholder, subvqc is not affected.

        @param self The current VQCircuit instance.
        @param sub_vqc The sub-VQCircuit to be appended.
        @param placeholder_map A list of tuples where each tuple contains two ParamExpression objects.
                            The first element is the parameter from the sub_vqc, and the second
                            element is the corresponding parameter in the current VQCircuit.
        @return The current VQCircuit instance with the sub_vqc appended.
            
        """
    def display_ansatz(self) -> str:
        """display_ansatz(self: vqcircuit.VQCircuit) -> str


        @brief Displays the structure of the ansatz (variational quantum circuit).
        @details This method prints or otherwise displays the structure and components of the variational quantum circuit (ansatz) to the user.
            
        """
    def get_Param_dims(self) -> list[int]:
        """get_Param_dims(self: vqcircuit.VQCircuit) -> list[int]


        @brief Retrieves the dimension information of the `Param` object.
        @return returns a vector of size_t values representing the dimension sizes associated with the `Param` object.
            
        """
    @overload
    def get_gradients(self, params: numpy.ndarray[numpy.float64], observable, diff_method: DiffMethod) -> ResGradients:
        """get_gradients(*args, **kwargs)
        Overloaded function.

        1. get_gradients(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResGradients


        @brief Retrieve the gradients of the expectation value with respect to the parameters.

        @details This function computes the gradients of the expectation value of a given Hamiltonian
        with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value gradients are computed.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResGradients object containing the computed gradients.
            

        2. get_gradients(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, param_group_total: int, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResNGradients


        @brief Retrieve the gradients of the expectation value with respect to the parameters.

        @details This function computes the gradients of the expectation value of a given Hamiltonian
        with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value gradients are computed.
        @param param_group_total The total number of parameter groups.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResNGradients object containing the computed gradients.
            
        """
    @overload
    def get_gradients(self, params: numpy.ndarray[numpy.float64], observable, param_group_total: int, diff_method: DiffMethod) -> ResNGradients:
        """get_gradients(*args, **kwargs)
        Overloaded function.

        1. get_gradients(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResGradients


        @brief Retrieve the gradients of the expectation value with respect to the parameters.

        @details This function computes the gradients of the expectation value of a given Hamiltonian
        with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value gradients are computed.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResGradients object containing the computed gradients.
            

        2. get_gradients(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, param_group_total: int, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResNGradients


        @brief Retrieve the gradients of the expectation value with respect to the parameters.

        @details This function computes the gradients of the expectation value of a given Hamiltonian
        with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value gradients are computed.
        @param param_group_total The total number of parameter groups.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResNGradients object containing the computed gradients.
            
        """
    @overload
    def get_gradients_and_expectation(self, params: numpy.ndarray[numpy.float64], observable, diff_method: DiffMethod) -> ResGradientsAndExpectation:
        """get_gradients_and_expectation(*args, **kwargs)
        Overloaded function.

        1. get_gradients_and_expectation(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResGradientsAndExpectation


        @brief Retrieve the gradients of the expectation value and the expectation value itself with respect to the parameters.

        @details this function computes both the gradients of the expectation value and the expectation value
        of a given Hamiltonian with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value and its gradients are computed.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResGradientsAndExpectation object containing the computed gradients and expectation value.
            

        2. get_gradients_and_expectation(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, param_group_total: int, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResNResGradientsAndExpectation


        @brief Retrieve the gradients of the expectation value and the expectation value itself with respect to the parameters.

        @details This function computes both the gradients of the expectation value and the expectation value
        of a given Hamiltonian with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value and its gradients are computed.
        @param param_group_total The total number of parameter groups.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResNResGradientsAndExpectation object containing the computed gradients and expectation value.
            
        """
    @overload
    def get_gradients_and_expectation(self, params: numpy.ndarray[numpy.float64], observable, param_group_total: int, diff_method: DiffMethod) -> ResNResGradientsAndExpectation:
        """get_gradients_and_expectation(*args, **kwargs)
        Overloaded function.

        1. get_gradients_and_expectation(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResGradientsAndExpectation


        @brief Retrieve the gradients of the expectation value and the expectation value itself with respect to the parameters.

        @details this function computes both the gradients of the expectation value and the expectation value
        of a given Hamiltonian with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value and its gradients are computed.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResGradientsAndExpectation object containing the computed gradients and expectation value.
            

        2. get_gradients_and_expectation(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64], observable: QPanda3::Hamiltonian, param_group_total: int, diff_method: vqcircuit.DiffMethod) -> vqcircuit.ResNResGradientsAndExpectation


        @brief Retrieve the gradients of the expectation value and the expectation value itself with respect to the parameters.

        @details This function computes both the gradients of the expectation value and the expectation value
        of a given Hamiltonian with respect to the specified parameters using the specified differentiation method.

        @param params An array of parameter values.
        @param observable The Hamiltonian for which the expectation value and its gradients are computed.
        @param param_group_total The total number of parameter groups.
        @param diff_method The differentiation method to use for computing gradients.
        @return A ResNResGradientsAndExpectation object containing the computed gradients and expectation value.
            
        """
    def mutable_parameter_total(self) -> int:
        """mutable_parameter_total(self: vqcircuit.VQCircuit) -> int


        @brief Get the total number of mutable parameters.
        @details This function returns the total number of parameters used.
        @return The total number of mutable parameters.
            
        """
    @overload
    def set_Param(self, dim_size_s: list[int], dim_label_s: list[str]) -> None:
        """set_Param(*args, **kwargs)
        Overloaded function.

        1. set_Param(self: vqcircuit.VQCircuit, dim_size_s: list[int], dim_label_s: list[str]) -> None


        @brief Sets the dimension sizes and labels for the `Param` object.
        @details This method allows the user to specify both the dimension sizes and corresponding labels for the `Param` object.
        @param dim_size_s a vector with dim's sizes
        @param dim_label_s a vector with dim's labels
            

        2. set_Param(self: vqcircuit.VQCircuit, dim_size_s: list[int]) -> None


        @brief Sets the dimension sizes for the `Param` object.
        @details This method allows the user to specify the dimension sizes for the `Param` object using a vector of size_t values.
        @param dim_size_s a vector with dim's sizes
            
        """
    @overload
    def set_Param(self, dim_size_s: list[int]) -> None:
        """set_Param(*args, **kwargs)
        Overloaded function.

        1. set_Param(self: vqcircuit.VQCircuit, dim_size_s: list[int], dim_label_s: list[str]) -> None


        @brief Sets the dimension sizes and labels for the `Param` object.
        @details This method allows the user to specify both the dimension sizes and corresponding labels for the `Param` object.
        @param dim_size_s a vector with dim's sizes
        @param dim_label_s a vector with dim's labels
            

        2. set_Param(self: vqcircuit.VQCircuit, dim_size_s: list[int]) -> None


        @brief Sets the dimension sizes for the `Param` object.
        @details This method allows the user to specify the dimension sizes for the `Param` object using a vector of size_t values.
        @param dim_size_s a vector with dim's sizes
            
        """
    def __call__(self, *args, **kwargs):
        """__call__(self: vqcircuit.VQCircuit, params: numpy.ndarray[numpy.float64]) -> QPanda3::VQCircuitResultOld


        @brief Applies parameter values to the variational quantum circuit and evaluates it.
        @details This method applies the provided parameter values (`data`) to the variational quantum circuit, considering the specified dimension sizes (`dim_size_s`). operator (`<<`). The variational quantum gate to be inserted is specified as the parameter `vqgate`.It then evaluates the circuit and returns the result as a `VQCircuitResult` object.
        @param params a numpy.ndarray object with all params to generate QCircuit objects
            
        """
    @overload
    def __lshift__(self, qgate) -> VQCircuit:
        """__lshift__(*args, **kwargs)
        Overloaded function.

        1. __lshift__(self: vqcircuit.VQCircuit, qgate: QPanda3::QGate) -> vqcircuit.VQCircuit


        @brief Inserts a quantum gate into the variational quantum circuit.
        @details This operator overload allows for the insertion of quantum gates into the variational quantum circuit using the stream insertion operator (`<<`). The quantum 
        @param qgate the quantum gate will be inserted to the variational quantum circuit,the qgate is with fixed params or without pparams gate to be inserted is specified as the parameter `qgate`.
            

        2. __lshift__(self: vqcircuit.VQCircuit, qcircuit: QPanda3::QCircuit) -> vqcircuit.VQCircuit


        @brief Inserts a quantum circuit into the variational quantum circuit.
        @details This operator overload allows for the insertion of a complete quantum circuit into the variational quantum circuit using the stream insertion operator (`<<`). The quantum circuit to be inserted is specified as the parameter `qcircuit`
        @param qcircuit the quantum qcircuit will be inserted to the variational quantum circuit,its gates are with fixed params or without params gate to be inserted.
            

        3. __lshift__(self: vqcircuit.VQCircuit, vqgate: QPanda3::VariationalQuantumGate) -> vqcircuit.VQCircuit


        @brief Inserts a variational quantum gate into the variational quantum circuit.
        @details This operator overload allows for the insertion of a variational quantum gate into the variational quantum circuit using the stream insertion operator (`<<`). The variational quantum gate to be inserted is specified as the parameter `vqgate`.
        @param vqgate a variational quantum gate object
            
        """
    @overload
    def __lshift__(self, qcircuit) -> VQCircuit:
        """__lshift__(*args, **kwargs)
        Overloaded function.

        1. __lshift__(self: vqcircuit.VQCircuit, qgate: QPanda3::QGate) -> vqcircuit.VQCircuit


        @brief Inserts a quantum gate into the variational quantum circuit.
        @details This operator overload allows for the insertion of quantum gates into the variational quantum circuit using the stream insertion operator (`<<`). The quantum 
        @param qgate the quantum gate will be inserted to the variational quantum circuit,the qgate is with fixed params or without pparams gate to be inserted is specified as the parameter `qgate`.
            

        2. __lshift__(self: vqcircuit.VQCircuit, qcircuit: QPanda3::QCircuit) -> vqcircuit.VQCircuit


        @brief Inserts a quantum circuit into the variational quantum circuit.
        @details This operator overload allows for the insertion of a complete quantum circuit into the variational quantum circuit using the stream insertion operator (`<<`). The quantum circuit to be inserted is specified as the parameter `qcircuit`
        @param qcircuit the quantum qcircuit will be inserted to the variational quantum circuit,its gates are with fixed params or without params gate to be inserted.
            

        3. __lshift__(self: vqcircuit.VQCircuit, vqgate: QPanda3::VariationalQuantumGate) -> vqcircuit.VQCircuit


        @brief Inserts a variational quantum gate into the variational quantum circuit.
        @details This operator overload allows for the insertion of a variational quantum gate into the variational quantum circuit using the stream insertion operator (`<<`). The variational quantum gate to be inserted is specified as the parameter `vqgate`.
        @param vqgate a variational quantum gate object
            
        """
    @overload
    def __lshift__(self, vqgate) -> VQCircuit:
        """__lshift__(*args, **kwargs)
        Overloaded function.

        1. __lshift__(self: vqcircuit.VQCircuit, qgate: QPanda3::QGate) -> vqcircuit.VQCircuit


        @brief Inserts a quantum gate into the variational quantum circuit.
        @details This operator overload allows for the insertion of quantum gates into the variational quantum circuit using the stream insertion operator (`<<`). The quantum 
        @param qgate the quantum gate will be inserted to the variational quantum circuit,the qgate is with fixed params or without pparams gate to be inserted is specified as the parameter `qgate`.
            

        2. __lshift__(self: vqcircuit.VQCircuit, qcircuit: QPanda3::QCircuit) -> vqcircuit.VQCircuit


        @brief Inserts a quantum circuit into the variational quantum circuit.
        @details This operator overload allows for the insertion of a complete quantum circuit into the variational quantum circuit using the stream insertion operator (`<<`). The quantum circuit to be inserted is specified as the parameter `qcircuit`
        @param qcircuit the quantum qcircuit will be inserted to the variational quantum circuit,its gates are with fixed params or without params gate to be inserted.
            

        3. __lshift__(self: vqcircuit.VQCircuit, vqgate: QPanda3::VariationalQuantumGate) -> vqcircuit.VQCircuit


        @brief Inserts a variational quantum gate into the variational quantum circuit.
        @details This operator overload allows for the insertion of a variational quantum gate into the variational quantum circuit using the stream insertion operator (`<<`). The variational quantum gate to be inserted is specified as the parameter `vqgate`.
        @param vqgate a variational quantum gate object
            
        """
