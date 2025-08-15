# This code is part of cqlib.
#
# Copyright (C) 2024 China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""parameters in the quantum circuit"""

from __future__ import annotations
from typing import Union
from sympy import Symbol, sympify, sstr, Add, Mul, Pow, Expr, exp as sym_exp


class Parameter:
    """
    Instruction Parameter Class.

    Represents a symbolic parameter within a quantum circuit. It supports arithmetic operations
    and symbolic manipulations using the sympy library.
    """

    __slots__ = ["_symbol", "_hash", '_str']

    def __init__(self, symbol: Union[str, Parameter, Expr]):
        """
        Initializes a Parameter object with a given symbol. The symbol can be a string,
        another Parameter, or a sympy expression.


        Args:
            symbol (str | Parameter | Expr): The symbolic representation or name of the parameter.
        """
        if isinstance(symbol, str):
            if not symbol.isidentifier():
                raise ValueError("Symbol must be a valid identifier.")
            symbol = Symbol(symbol)
        elif isinstance(symbol, Expr):
            symbol = sympify(symbol)
        elif isinstance(symbol, Parameter):
            symbol = symbol.symbol
        else:
            raise TypeError(f"Invalid type for symbol: {type(symbol).__name__}")
        self._symbol = symbol
        self._hash = None
        self._str = None

    @property
    def symbol(self) -> Symbol:
        """
        Returns the sympy symbol associated with this Parameter.

        Returns:
            Expr: The sympy expression of the symbol.
        """
        return self._symbol

    def value(self, params: dict) -> Expr:
        """
        Evaluate the parameter symbol with specific numerical values provided in a dictionary.

        This method substitutes the values from the `params` dictionary into the symbolic
        expression of the parameter. Only non-zero values are considered for substitution to
        prevent unintended simplifications or alterations of the expression.


        Args:
            params (dict): A dictionary mapping parameter objects or their string representations
                to numerical values.

        Returns:
            Expr: The result of the symbol after substitution.
        """
        values = {str(param): value for param, value in params.items() if value is not None}

        return self._symbol.subs(values)

    def __add__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, Add)

    def __radd__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, Add)

    def __sub__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, lambda a, b: a - b)

    def __rsub__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, lambda a, b: -a + b)

    def __mul__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, Mul)

    def __rmul__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, Mul)

    def __neg__(self) -> Parameter:
        return self._apply_operation(0, lambda a, b: b - a)

    def __truediv__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, lambda a, b: a / b)

    def __rtruediv__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, lambda a, b: b / a)

    def __pow__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, Pow)

    def __rpow__(self, other: Union[int, float, Parameter]) -> Parameter:
        return self._apply_operation(other, lambda a, b: Pow(b, a))

    def exp(self):
        """
        Calculate the exponent of this parameter (e^parameter).

        Returns:
            Parameter: A new Parameter instance representing the exponential
                of the original parameter.
        """
        return Parameter(sym_exp(self.symbol))

    def _apply_operation(self, other: Union[int, float, Parameter], operation) -> Parameter:
        if isinstance(other, Parameter):
            return Parameter(operation(self.symbol, other.symbol))
        if isinstance(other, (int, float, Expr)):
            return Parameter(operation(self.symbol, other))
        raise TypeError(f"Unsupported type {type(other).__name__} for operation with Parameter")

    def __hash__(self):
        if not hasattr(self, '_hash') or self._hash is None:
            self._hash = hash(str(self))
        return self._hash

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)})"

    def __str__(self):
        if not hasattr(self, '_str') or self._str is None:
            self._str = sstr(self.symbol, full_prec=False)
        return self._str

    def __eq__(self, other: Parameter) -> bool:
        """
        Check equality of two Parameter instances based on their string representation.

        Returns:
            bool: True if both parameters are equal, False otherwise.
        """
        if not isinstance(other, Parameter):
            return False
        return self._symbol == other._symbol

    def copy(self) -> Parameter:
        """
        copy the Parameter.
        """
        return Parameter(symbol=self._symbol)

    @property
    def base_params(self):
        """
        Returns the base parameters as a list of Parameter instances, extracting symbols
            if the parameter is a compound expression.

        Returns:
            List[Parameter]: A list of base parameters.
        """
        if isinstance(self._symbol, Symbol):
            return [self]

        return [Parameter(s) for s in self._symbol.atoms(Symbol)]
