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

"""
OpenQASM 2.0 Parser for cqlib

This module provides a parser that reads OpenQASM 2.0 files and converts
them into cqlib Circuit objects.


Note:
- Classical bits are not supported.
- File imports are limited to `qelib1.inc` only.
- Conditional operations (if Statements) are implemented.
- Reset operation (reset) are implemented.
- Opaque gate definitions (opaque) are implemented.
- Measurement result mapping to classical bits is not supported.
"""

import math
import operator

import numpy as np
import sympy as sp
from antlr4 import FileStream, CommonTokenStream, InputStream

from cqlib.exceptions import QASMParserError
from cqlib.circuits.circuit import Circuit

from ._antlr4.OpenQASM2Lexer import OpenQASM2Lexer
from ._antlr4.OpenQASM2Parser import OpenQASM2Parser
from ._antlr4.OpenQASM2Visitor import OpenQASM2Visitor

# openqasm2.0 id gate wait time
I_DURATION = 60

BASE_GATES = {
    'U': [3, 1],
    'CX': [0, 2],
}

QELIB1_GATES = {
    'u3': [3, 1],
    'u2': [2, 1],
    'u1': [1, 1],
    'u': [3, 1],
    'cx': [0, 2],
    'id': [0, 1],
    'x': [0, 1],
    'y': [0, 1],
    'z': [0, 1],
    'h': [0, 1],
    'p': [1, 1],
    's': [0, 1],
    'sdg': [0, 1],
    'sx': [0, 1],
    'sxdg': [0, 1],
    't': [0, 1],
    'tdg': [0, 1],
    'rx': [1, 1],
    'ry': [1, 1],
    'rz': [1, 1],
    'cz': [0, 2],
    'cy': [0, 2],
    'ch': [0, 2],
    'swap': [0, 2],
    'cswap': [0, 3],
    'ccx': [0, 3],
    'crx': [1, 2],
    'cry': [1, 2],
    'crz': [1, 2],
    'csx': [0, 2],
}

FUNCTIONS = {
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'exp': sp.exp,
    'ln': sp.log,
    'sqrt': sp.sqrt,
    'acos': sp.acos,
    'atan': sp.atan,
    'asin': sp.asin,
}

OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '^': operator.pow,
}


# pylint: disable=too-few-public-methods
class CustomGateItem:
    """
    Represents an operation within a custom gate definition.
    """

    def __init__(self, gate: str, params: list[str | float], qubits: list[int]):
        """
        init  CustomGateItem

        Args:
            gate (str): The name of the gate operation.
            params (list): A list of parameters for the gate operation.
            qubits (list): A list of qubit identifiers the gate acts on.
        """
        self.gate = gate
        self.params = params
        self.qubits = qubits


class CustomGate:
    """
    Represents a custom quantum gate defined in OpenQASM.
    """

    def __init__(
            self,
            name: str,
            params: list,
            qubits: list,
            converter: 'OpenQASM2Converter'
    ):
        """

        Args:
            name (str): The name of the custom gate.
            params (list): Parameter names for the custom gate.
            qubits (list): Qubit argument names for the custom gate.
            converter (OpenQASM2Converter): Reference to the main converter for context.
        """
        self.name = name
        self.params = params
        if len(qubits) < 1:
            raise QASMParserError("At least one quantum argument is mandatory for gates to act on")
        self.qubits = qubits
        self.op_list: list[CustomGateItem] = []
        self.converter = converter

    def visit_goplist(self, ctx: OpenQASM2Parser.GoplistContext):
        """
        Parses the gate operation list within a custom gate definition.

        Args:
            ctx (OpenQASM2Parser.GoplistContext): The context for the gate operation list.
        """
        operations = []
        if not ctx.children:
            return

        for child in ctx.children:
            if isinstance(child, OpenQASM2Parser.UopContext):
                operations.append(self.visit_uop(child))
            elif child.getText() == 'barrier':
                # Process a barrier operation
                barrier_index = ctx.children.index(child)
                idlist_ctx = ctx.children[barrier_index + 1]
                ids = [id_tok.getText() for id_tok in idlist_ctx.ID()]
                operations.append(CustomGateItem('barrier', params=[], qubits=ids))
        self.op_list = operations

    def visit_uop(self, ctx: OpenQASM2Parser.UopContext) -> CustomGateItem:
        """
        Parses a single gate operation within a custom gate definition.

        Args:
            ctx (OpenQASM2Parser.UopContext): The context for the gate operation.
        """
        gate = ctx.getChild(0).getText()
        if gate == self.name:
            raise QASMParserError(f"Quantum gates cannot be called in a loop.\n "
                                  f"gate {gate} line {ctx.start.line} {ctx.getText()}")

        parameters = []
        if gate == 'U':
            parameters = self.converter.visitExplist(ctx.explist())
            qubits = self.converter.visitArgument(ctx.argument(0))
        elif gate == 'CX':
            ctl_qubit = self.converter.visitArgument(ctx.argument(0))
            target_qubit = self.converter.visitArgument(ctx.argument(1))
            qubits = [ctl_qubit, target_qubit]
        else:
            if exp_list := ctx.explist():
                parameters = self.converter.visitExplist(exp_list)
            qubits = self.converter.visitAnylist(ctx.anylist())

        return CustomGateItem(gate, params=parameters, qubits=qubits)

    def execute(self, gate: str, exp_list: list[str], qubit_list: list[int]):
        """
        Executes the custom gate by applying its operations to the circuit.

        Args:
            gate (str): The name of the custom gate.
            exp_list (list): List of parameter values for the gate.
            qubit_list (list): List of qubit indices the gate acts on.
        """
        if len(self.params) != len(exp_list) or len(self.qubits) != len(qubit_list):
            raise QASMParserError(f"gate args error: {gate}")
        ps = dict(zip(self.params, exp_list))
        qs = dict(zip(self.qubits, qubit_list))

        for op in self.op_list:
            if op.gate in self.converter.custom_gates:
                self.converter.custom_gates[op.gate].execute(op.gate, op.params, op.qubits)
                continue
            params = []
            for p in op.params:
                if isinstance(p, sp.Basic):
                    value = p.subs(ps)
                    params.append(round(float(value), self.converter.precision))
                elif isinstance(p, str):
                    params.append(ps[str(p)])
                else:
                    params.append(p)
            # params = [ps[p] if isinstance(p, str) else p for p in op.params]
            qubits = [qs[q] for q in op.qubits]
            match op.gate:
                case 'U':
                    self.converter.circuit.u(qubits[0], *params)
                case 'CX':
                    self.converter.circuit.cx(*qubits, *params)
                case 'barrier':
                    self.converter.circuit.barrier(*qubits, *params)
                case _:
                    self.converter.execute_op(self.converter.circuit, op.gate, qubits, params)


# pylint: disable=too-many-instance-attributes
class OpenQASM2Converter(OpenQASM2Visitor):
    """
    Converts OpenQASM 2.0 code into a cqlib Circuit object.
    """

    def __init__(self, precision: int = 10):
        """
        init Converter.

        Args:
            precision (int, optional): The number of decimal places to round parameters to.
        """
        super().__init__()
        self.circuit = Circuit(0)
        self.gates = BASE_GATES
        self.functions = FUNCTIONS
        self.operators = OPERATORS
        self.include_qelib1 = False
        self.qubits = {}
        self.clbits = {}
        self.custom_gates: dict[str, CustomGate] = {}
        self.current_custom_gate = None
        self.measure_ops = {}
        self.precision = precision

    def visitMainprogram(self, ctx: OpenQASM2Parser.MainprogramContext):
        """
        Parses the main program structure of the OpenQASM file.

        Args:
            ctx (OpenQASM2Parser.MainprogramContext): The context of the main program.

        ```antlr4
        mainprogram : 'OPENQASM' real ';' program EOF;
        ```
        """
        child_count = ctx.getChildCount()
        if child_count < 2:
            raise QASMParserError(f"format error: {ctx.getText()}")
        if ctx.getChild(0).getText() != 'OPENQASM':
            raise QASMParserError(f" {ctx.getText()}")
        if float(ctx.getChild(1).getText()) != 2.0:
            raise QASMParserError(f" {ctx.getText()}")
        return self.visitChildren(ctx)

    def visitIncludeStatement(self, ctx: OpenQASM2Parser.IncludeStatementContext):
        """
        Handles include statements in the OpenQASM code.

        Args:
            ctx (OpenQASM2Parser.IncludeStatementContext): The context of the include statement.

        ```antlr4
        includeStatement
            : 'include' STRING ';'
            ;
        ```
        """
        filename = ctx.STRING().getText()
        if filename[1:-1] != 'qelib1.inc':
            raise QASMParserError(f"Unsupported file included: {filename}. "
                                  f"Only 'qelib1.inc' is supported.")
        self.gates.update(QELIB1_GATES)
        self.include_qelib1 = True
        return self.visitChildren(ctx)

    def visitStatement(self, ctx: OpenQASM2Parser.StatementContext):
        """
        Parses individual statements in the OpenQASM code.

        Args:
            ctx (OpenQASM2Parser.StatementContext): The context of the statement.

        ```antlr4
        statement
            : includeStatement            // 新增文件包含语句
            | decl                        // 量子或经典寄存器声明
            | gatedecl                    // 空门定义
            | 'opaque' ID idlist ';'      // 不透明门
            | 'opaque' ID '(' idlist ')' idlist ';'
            | qop                         // 量子操作
            | 'if' '(' ID '==' nninteger ')' qop
            | 'barrier' anylist ';'
            ;
        ```
        """
        if statement := ctx.includeStatement():
            return self.visitIncludeStatement(statement)
        if decl := ctx.decl():
            return self.visitDecl(decl)
        if gate_decl := ctx.gatedecl():
            return self.visitGatedecl(gate_decl)
        if qop := ctx.qop():
            return self.visitQop(qop)
        gate = ctx.getChild(0).getText()
        if gate == 'opaque':
            raise QASMParserError(f"Unsupported gate: opaque. {ctx.getText()}")
        if gate == 'if':
            raise QASMParserError(f"Unsupported gate: if. {ctx.getText()}")
        if gate == 'barrier':
            qs = []
            for a in self.visitAnylist(ctx.anylist()):
                qs.extend(self.get_qubits(a))
            self.circuit.barrier(*qs)
            return
        raise QASMParserError(f"Unknown gate: {gate}")

    def visitDecl(self, ctx: OpenQASM2Parser.DeclContext):
        """
        Handles quantum and classical register declarations.

        Args:
            ctx (OpenQASM2Parser.DeclContext): The context of the declaration.

        ```antlr4
        decl
            : 'qreg' ID '[' nninteger ']' ';'
            | 'creg' ID '[' nninteger ']' ';'
            ;
        ```
        """
        tag = ctx.getChild(0).getText()
        name = ctx.ID().getText()
        size = int(ctx.nninteger().getText())

        if tag == 'qreg':
            qubits_len = len(self.qubits)
            for i in range(size):
                self.circuit.add_qubit(i + qubits_len)
                k = f'{name}_{i}'
                if k in self.qubits:
                    raise QASMParserError(f"Duplicate qreg definitions: {ctx.getText()}")
                self.qubits[k] = i + qubits_len
        elif tag == 'creg':
            cl_len = len(self.clbits)
            for i in range(size):
                k = f'{name}_{i}'
                if k in self.clbits:
                    raise QASMParserError(f"Duplicate creg definitions: {ctx.getText()}")
                self.clbits[k] = cl_len + i
        else:
            raise QASMParserError(f"Unknown definitions: {ctx.getText()}")

    def visitGatedecl(self, ctx: OpenQASM2Parser.GatedeclContext):
        """
        Parses custom gate definitions.

        Args:
            ctx (OpenQASM2Parser.GatedeclContext): The context of the gate definition.

        ```antlr4
        gatedecl
            : 'gate' ID idlist '{' goplist '}'               // 无参数的 gate
            | 'gate' ID '(' ')' idlist '{' goplist '}'       // 空参数列表的 gate
            | 'gate' ID '(' idlist ')' idlist '{' goplist '}' // 带参数的 gate
            ;
        ```
        """
        gate_name = ctx.ID().getText()

        def get_id(id_list):
            ids = []
            for t in id_list.ID():
                ids.append(t.getText())
            return ids

        if len(ctx.idlist()) == 1:
            parameters = []
            qubit_args = get_id(ctx.idlist(0))
        else:
            parameters = get_id(ctx.idlist(0))
            qubit_args = get_id(ctx.idlist(1))
        if gate_name in self.custom_gates:
            raise QASMParserError(f"Duplicate gate definitions: {gate_name} \n"
                                  f"line {ctx.start.line}, {ctx.getText()}")

        gate = CustomGate(gate_name, params=parameters, qubits=qubit_args, converter=self)
        gate.visit_goplist(ctx.goplist())
        self.custom_gates[gate_name] = gate

    def visitQop(self, ctx: OpenQASM2Parser.QopContext):
        """
        Parses quantum operations (gates, measurements, resets).

        Args:
            ctx (OpenQASM2Parser.QopContext): The context of the quantum operation.

        ```antlr4
        qop
            : uop
            | 'measure' argument '->' argument ';'
            | 'reset' argument ';'
            ;
        ```
        """
        child_count = ctx.getChildCount()
        if ctx.uop() and child_count == 1:
            return self.visitUop(ctx.uop())
        if ctx.getChild(0).getText() == 'measure' and child_count == 5:
            qubit = self.visitArgument(ctx.argument(0))
            qubit = self.get_qubits(qubit)
            for q in qubit:
                self.circuit.measure(q)
        elif ctx.getChild(0) == 'reset':
            raise QASMParserError("Unsupported quantum gates: reset")
        return None

    def visitUop(self, ctx: OpenQASM2Parser.UopContext):
        """
        Parses quantum gate operations.

        Args:
            ctx (OpenQASM2Parser.UopContext): The context of the gate operation.

        ```antlr4
        uop
            : 'U' '(' explist ')' argument ';'
            | 'CX' argument ',' argument ';'
            | ID anylist ';'
            | ID '(' explist ')' anylist ';'
            ;
        ```
        """
        gate = ctx.getChild(0).getText()
        if not gate:
            return
        if gate not in self.gates and gate not in self.custom_gates:
            tip = f'Unknown gate "{gate}"'
            if not self.include_qelib1:
                tip += ', did you forget to include qelib1.inc?'
            raise QASMParserError(tip)

        if gate in self.custom_gates:
            if exp_list := ctx.explist():
                exp_list = self.visitExplist(exp_list)
            else:
                exp_list = []
            any_list = self.visitAnylist(ctx.anylist())
            for group in self.parse_qubit_group(any_list):
                self.custom_gates[gate].execute(gate, exp_list, group)
            return

        if gate == 'U':
            parameters = self.visitExplist(ctx.explist())
            arguments = self.visitArgument(ctx.argument(0))
            for a in self.parse_qubit_group(arguments):
                self.circuit.u(*a, *parameters)
        elif gate == 'CX':
            ctl_qubit = self.visitArgument(ctx.argument(0))
            # cs = self.get_qubits(ctl_qubit)
            target_qubit = self.visitArgument(ctx.argument(1))
            for group in self.parse_qubit_group([ctl_qubit, target_qubit]):
                self.circuit.cx(*group)
        else:
            self.handle_custom_operation(ctx)

    def handle_custom_operation(self, ctx):
        """
        Handles built-in and custom gate operations.

        Args:
            ctx (OpenQASM2Parser.UopContext): The context of the gate operation.
        """
        gate = ctx.ID().getText()
        if ctx.explist():
            parameters = self.visitExplist(ctx.explist())
        else:
            parameters = []
        arguments = self.visitAnylist(ctx.anylist())
        gp = self.gates[gate]
        if gp[0] != len(parameters) or gp[1] != len(arguments):
            raise QASMParserError(f"parameter abnormality: line {ctx.start.line} "
                                  f"{gate}\n{ctx.getText()}")
        qubit_count = len(arguments)
        if qubit_count == 1:
            qubits = self.get_qubits(arguments)
            for q in qubits:
                self.execute_op(self.circuit, gate, [q], parameters)
        elif qubit_count == 2:
            for qubits in self.parse_qubit_group(arguments):
                self.execute_op(self.circuit, gate, qubits, parameters)
        elif qubit_count == 3:
            qubits_0 = self.get_qubits(arguments[0])
            qubits_1 = self.get_qubits(arguments[1])
            qubits_2 = self.get_qubits(arguments[2])
            if len(qubits_0) != len(qubits_1) != len(qubits_2):
                raise QASMParserError(f'The number of qubit 0/1/2 must be the same.'
                                      f'\n{ctx.getText()}')
            for i, q0 in enumerate(qubits_0):
                self.execute_op(self.circuit, gate, [q0, qubits_1[i], qubits_2[i]], parameters)
        else:
            raise QASMParserError(f"Unknown gate: {ctx.getText()}")

    def visitExplist(self, ctx: OpenQASM2Parser.ExplistContext):
        """
        Parses a list of expressions.

        Args:
            ctx (OpenQASM2Parser.ExplistContext): The context of the expression list.

        ```antlr4
        explist
            : exp (',' exp)*
            ;
        ```
        """
        expressions = [self.visitExp(exp_ctx) for exp_ctx in ctx.exp()]
        return expressions

    def visitAnylist(self, ctx: OpenQASM2Parser.AnylistContext):
        """
        Parses a list of identifiers or mixed lists.

        Args:
            ctx (OpenQASM2Parser.AnylistContext): The context of the anylist.

        ```antlr4
            anylist
                : idlist
                | mixedlist
                ;
        ```
        """
        if ctx.idlist():
            return self.visitIdlist(ctx.idlist())
        if ctx.mixedlist():
            return self.visitMixedlist(ctx.mixedlist())
        raise QASMParserError(f"Unknown op: {ctx.getText()}")

    def visitIdlist(self, ctx: OpenQASM2Parser.IdlistContext):
        """
        Parses a list of identifiers.

        Args:
            ctx (OpenQASM2Parser.IdlistContext): The context of the identifier list.

        ```antlr4
        idlist
            : ID (',' ID)*
            ;
        ```
        """
        ids = [id_tok.getText() for id_tok in ctx.ID()]
        return ids

    # pylint: disable=too-many-return-statements
    # def visitExp(self, ctx: OpenQASM2Parser.ExpContext):
    #     """
    #     Parses expressions, including numerical values and mathematical operations.
    #
    #     Args:
    #         ctx (OpenQASM2Parser.ExpContext): The context of the expression.
    #
    #     ```antlr4
    #     exp
    #         : real
    #         | nninteger
    #         | 'pi'
    #         | ID
    #         | exp '+' exp
    #         | exp '-' exp
    #         | exp '*' exp
    #         | exp '/' exp
    #         | '-' exp
    #         | exp '^' exp
    #         | '(' exp ')'
    #         | unaryop '(' exp ')'
    #         ;
    #     ```
    #     """
    #     child_count = ctx.getChildCount()
    #     if ctx.real():
    #         return round(float(ctx.real().getText()), self.precision)
    #     if ctx.nninteger():
    #         return int(ctx.nninteger().getText())
    #     if child_count == 1 and ctx.getText() == 'pi':
    #         return round(np.pi, self.precision)
    #     if ctx.ID():
    #         return ctx.ID().getText()
    #     if child_count == 3:
    #         if ctx.getChild(0).getText() == '(' and ctx.getChild(2).getText() == ')':
    #             return self.visitExp(ctx.exp(0))
    #         left = self.visitExp(ctx.exp(0))
    #         op = ctx.getChild(1).getText()
    #         right = self.visitExp(ctx.exp(1))
    #         if op not in self.operators:
    #             raise QASMParserError(f'Unknown op: {op}\n{ctx.getText()}')
    #         # exp = f'{left} {op} {right}'
    #         return round(self.operators[op](left, right), self.precision)
    #         # return exp
    #     if child_count == 2 and ctx.getChild(0).getText() == '-':
    #         # Unary minus
    #         exp = self.visitExp(ctx.exp(0))
    #         return exp * -1
    #     if unaryop := ctx.unaryop():
    #         func = unaryop.getText()
    #         exp = self.visitExp(ctx.exp(0))
    #         if func not in self.functions:
    #             raise QASMParserError(f'Unknown op function: {func}\n{ctx.getText()}')
    #         return round(self.functions[func](exp), self.precision)
    #     raise QASMParserError(f'Unknown op: {ctx.getText()}')

    def visitExp(self, ctx: OpenQASM2Parser.ExpContext):
        exp = self.visitAdditiveExp(ctx.additiveExp())
        if isinstance(exp, sp.Basic):
            exp = sp.simplify(exp)
            if exp.is_real:
                return round(float(exp.evalf()), self.precision)
        return exp

    def visitAdditiveExp(self, ctx: OpenQASM2Parser.AdditiveExpContext):
        exp = self.visitMultiplicativeExp(ctx.multiplicativeExp())
        if additive_exp := ctx.additiveExp():
            additive_exp = self.visitAdditiveExp(additive_exp)
            op = ctx.getChild(1).getText()
            if op == '+':
                exp = additive_exp + exp
            elif op == '-':
                exp = additive_exp - exp
        return exp

    def visitMultiplicativeExp(self, ctx: OpenQASM2Parser.MultiplicativeExpContext):
        exp = self.visitExponentialExp(ctx.exponentialExp())
        if multiplicative_exp := ctx.multiplicativeExp():
            multiplicative_exp = self.visitMultiplicativeExp(multiplicative_exp)
            op = ctx.getChild(1).getText()
            if op == '*':
                exp = multiplicative_exp * exp
            elif op == '/':
                exp = multiplicative_exp / exp
        return exp

    def visitExponentialExp(self, ctx: OpenQASM2Parser.ExponentialExpContext):
        exp = self.visitUnaryExp(ctx.unaryExp())
        if exponential_exp := ctx.exponentialExp():
            exp = exp ** self.visitExponentialExp(exponential_exp)
        return exp

    def visitUnaryExp(self, ctx: OpenQASM2Parser.UnaryExpContext):
        if exp := ctx.primaryExp():
            return self.visitPrimaryExp(exp)
        if exp := ctx.unaryExp():
            return 0 - self.visitUnaryExp(exp)

    def visitPrimaryExp(self, ctx: OpenQASM2Parser.PrimaryExpContext):
        token = ctx.getText()
        if real := ctx.real():
            return sp.Float(real.getText(), self.precision)
        if nninteger := ctx.nninteger():
            return sp.Integer(nninteger.getText())
        if token == 'pi':
            return sp.pi
        if unaryop := ctx.unaryop():
            func = unaryop.getText()
            if func not in self.functions:
                raise QASMParserError(f'Unknown op function: {func}\n{ctx.getText()}')
            exp = self.visitExp(ctx.exp())
            return self.functions[func](exp)
        if exp := ctx.exp():
            return self.visitExp(exp)
        if id_ := ctx.ID():
            return sp.symbols(id_.getText())

    def visitMixedlist(self, ctx: OpenQASM2Parser.MixedlistContext):
        """
        Parses mixed lists of identifiers with optional indices.

        Args:
            ctx (OpenQASM2Parser.MixedlistContext): The context of the mixed list.

        ```antlr4
        mixedlist
            : ID ('[' nninteger ']')? (',' ID ('[' nninteger ']')?)*
            ;
        ```
        """
        result = []
        i = 0
        child_count = ctx.getChildCount()

        while i < child_count:
            id_token = ctx.getChild(i)
            id_name = id_token.getText()
            i += 1
            index = None
            if i < child_count and ctx.getChild(i).getText() == '[':
                i += 1  # 跳过 '['
                nninteger_token = ctx.getChild(i)
                index = int(nninteger_token.getText())
                i += 2
            if index is not None:
                result.append(f'{id_name}_{index}')
            else:
                result.append(id_name)
            if i < child_count and ctx.getChild(i).getText() == ',':
                i += 1  # 跳过 ','
        return result

    def visitArgument(self, ctx: OpenQASM2Parser.ArgumentContext) -> str | list[str]:
        """
        Parses gate arguments, which can be identifiers with optional indices.

        Args:
            ctx (OpenQASM2Parser.ArgumentContext): The context of the argument.

        ```antlr4
        argument
            : ID
            | ID '[' nninteger ']'
            ;
        ```
        """
        aid = ctx.ID().getText()
        if index := ctx.nninteger():
            return [f'{aid}_{index.getText()}']
        return aid

    def get_qubits(self, qubits: str | list[str]) -> list[int]:
        """
        Retrieves qubit indices for a given qubit identifier.

        Args:
            qubits (str | list[str]): The qubit identifier.
        """
        if isinstance(qubits, str):
            qubits = [qubits]
        target = []
        for qubit in qubits:
            if '_' in qubit:
                if qubit not in self.qubits:
                    raise QASMParserError(f"Qubit not defined: {qubit}")
                target.append(self.qubits.get(qubit))
                continue
            for q, i in self.qubits.items():
                if q.startswith(f'{qubit}_'):
                    target.append(i)
        return target

    def get_clbits(self, clbit: str) -> list[int]:
        """
        Retrieves classical bit indices for a given classical bit identifier.

        Args:
            clbit (str): The classical bit identifier.
        """
        if '_' in clbit:
            return [self.clbits.get(clbit)]
        return [i for q, i in self.clbits.items() if q.startswith(f'{clbit}_')]

    @staticmethod
    def execute_op(circuit: Circuit, gate: str, qubits: list[int], parameters: list[str | float]):
        """
        Executes a gate operation on the circuit.

        Args:
            circuit (Circuit): The cqlib Circuit object.
            gate (str): The name of the gate.
            qubits (list[int]): The indices of qubits the gate acts on.
            parameters (list): The parameters for the gate operation.
        """
        match gate:
            case 'u3':
                circuit.u(qubits[0], *parameters)
            case 'u2':
                circuit.u(qubits[0], np.pi / 2, *parameters)
            case 'u1':
                circuit.u(qubits[0], 0, 0, *parameters)
            case 'u':
                circuit.u(qubits[0], *parameters)
            case 'cx':
                circuit.cx(qubits[0], qubits[1])
            case 'id':
                circuit.i(qubits[0], I_DURATION)
            case 'x':
                circuit.x(qubits[0])
            case 'y':
                circuit.y(qubits[0])
            case 'z':
                circuit.z(qubits[0])
            case 'h':
                circuit.h(qubits[0])
            case 'p':
                circuit.u(qubits[0], 0, 0, *parameters)
            case 's':
                circuit.s(qubits[0])
            case 'sdg':
                circuit.sd(qubits[0])
            case 'sx':
                circuit.x2p(qubits[0])
            case 'sxdg':
                circuit.x2m(qubits[0])
            case 't':
                circuit.t(qubits[0])
            case 'tdg':
                circuit.td(qubits[0])
            case 'rx':
                circuit.rx(qubits[0], *parameters)
            case 'ry':
                circuit.ry(qubits[0], *parameters)
            case 'rz':
                circuit.rz(qubits[0], *parameters)
            case 'cz':
                circuit.cz(qubits[0], qubits[1])
            case 'cy':
                circuit.cy(qubits[0], qubits[1])
            case 'ch':
                qubit_1 = qubits[1]
                circuit.ry(qubit_1, -np.pi / 4)
                circuit.rz(qubit_1, np.pi / 2)
                circuit.cz(qubits[0], qubit_1)
                circuit.rz(qubit_1, -np.pi / 2)
                circuit.ry(qubit_1, np.pi / 4)
            case 'swap':
                circuit.swap(qubits[0], qubits[1])
            case 'cswap':
                circuit.cx(qubits[2], qubits[1])
                circuit.ccx(qubits[0], qubits[1], qubits[2])
                circuit.cx(qubits[2], qubits[1])
            case 'ccx':
                circuit.ccx(qubits[0], qubits[1], qubits[2])
            case 'crx':
                circuit.crx(qubits[0], qubits[1], *parameters)
            case 'cry':
                circuit.cry(qubits[0], qubits[1], *parameters)
            case 'crz':
                circuit.crz(qubits[0], qubits[1], *parameters)
            case 'csx':
                circuit.rz(qubits[0], math.pi / 4)
                circuit.h(qubits[1])
                circuit.cx(qubits[0], qubits[1])
                circuit.rz(qubits[1], -math.pi / 4)
                circuit.cx(qubits[0], qubits[1])
                circuit.rz(qubits[1], math.pi / 4)
                circuit.h(qubits[1])
            case _:
                raise QASMParserError(f'Unknown gate: {gate}')

    def parse_qubit_group(self, any_list: list[str]):
        """
        qreg q[3];
        qreg p[3];

        1. cx p, q;
            CX p0, q0;
            CX p1, q1;
            CX p2, q2;
        2. cx p, q[0];
            CX p0, q0;
            CX p1, q0;
            CX p2, q0;
        3. h p;
            H p0;
            H p1;
            H p2;
        """
        qubit_group = []
        result = []
        max_count = 0
        for q in any_list:
            qubits = self.get_qubits(q)
            max_count = max(len(qubits), max_count)
            qubit_group.append(qubits)
        for group in qubit_group:
            if 1 != len(group) != max_count:
                raise QASMParserError(f'Non matching quantum registers of length: '
                                      f'{[len(s) for s in qubit_group]}')
            if len(group) == 1:
                result.append(group * max_count)
            else:
                result.append(group)
        return zip(*result)

    def parse(
            self,
            qasm_file: str = None,
            qasm_str: str = None,
    ) -> Circuit:
        """
        Parses an OpenQASM 2.0 input (either a file or a string)
        and constructs the corresponding Circuit.

        Args:
            qasm_file (str): Path to the OpenQASM 2.0 file.
            qasm_str (str): The OpenQASM 2.0 circuit.
        """
        if qasm_file:
            input_stream = FileStream(qasm_file)
        elif qasm_str:
            input_stream = InputStream(qasm_str)
        else:
            raise QASMParserError('Either `qasm_file` or `qasm_str` must be provided.')
        lexer = OpenQASM2Lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = OpenQASM2Parser(token_stream)
        tree = parser.mainprogram()

        self.visit(tree)
        return self.circuit
