# Generated from OpenQASM2.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .OpenQASM2Parser import OpenQASM2Parser
else:
    from OpenQASM2Parser import OpenQASM2Parser

# This class defines a complete listener for a parse tree produced by OpenQASM2Parser.
class OpenQASM2Listener(ParseTreeListener):

    # Enter a parse tree produced by OpenQASM2Parser#mainprogram.
    def enterMainprogram(self, ctx:OpenQASM2Parser.MainprogramContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#mainprogram.
    def exitMainprogram(self, ctx:OpenQASM2Parser.MainprogramContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#program.
    def enterProgram(self, ctx:OpenQASM2Parser.ProgramContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#program.
    def exitProgram(self, ctx:OpenQASM2Parser.ProgramContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#statement.
    def enterStatement(self, ctx:OpenQASM2Parser.StatementContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#statement.
    def exitStatement(self, ctx:OpenQASM2Parser.StatementContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#includeStatement.
    def enterIncludeStatement(self, ctx:OpenQASM2Parser.IncludeStatementContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#includeStatement.
    def exitIncludeStatement(self, ctx:OpenQASM2Parser.IncludeStatementContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#decl.
    def enterDecl(self, ctx:OpenQASM2Parser.DeclContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#decl.
    def exitDecl(self, ctx:OpenQASM2Parser.DeclContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#gatedecl.
    def enterGatedecl(self, ctx:OpenQASM2Parser.GatedeclContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#gatedecl.
    def exitGatedecl(self, ctx:OpenQASM2Parser.GatedeclContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#goplist.
    def enterGoplist(self, ctx:OpenQASM2Parser.GoplistContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#goplist.
    def exitGoplist(self, ctx:OpenQASM2Parser.GoplistContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#qop.
    def enterQop(self, ctx:OpenQASM2Parser.QopContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#qop.
    def exitQop(self, ctx:OpenQASM2Parser.QopContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#uop.
    def enterUop(self, ctx:OpenQASM2Parser.UopContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#uop.
    def exitUop(self, ctx:OpenQASM2Parser.UopContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#anylist.
    def enterAnylist(self, ctx:OpenQASM2Parser.AnylistContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#anylist.
    def exitAnylist(self, ctx:OpenQASM2Parser.AnylistContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#idlist.
    def enterIdlist(self, ctx:OpenQASM2Parser.IdlistContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#idlist.
    def exitIdlist(self, ctx:OpenQASM2Parser.IdlistContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#mixedlist.
    def enterMixedlist(self, ctx:OpenQASM2Parser.MixedlistContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#mixedlist.
    def exitMixedlist(self, ctx:OpenQASM2Parser.MixedlistContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#argument.
    def enterArgument(self, ctx:OpenQASM2Parser.ArgumentContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#argument.
    def exitArgument(self, ctx:OpenQASM2Parser.ArgumentContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#explist.
    def enterExplist(self, ctx:OpenQASM2Parser.ExplistContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#explist.
    def exitExplist(self, ctx:OpenQASM2Parser.ExplistContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#exp.
    def enterExp(self, ctx:OpenQASM2Parser.ExpContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#exp.
    def exitExp(self, ctx:OpenQASM2Parser.ExpContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#additiveExp.
    def enterAdditiveExp(self, ctx:OpenQASM2Parser.AdditiveExpContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#additiveExp.
    def exitAdditiveExp(self, ctx:OpenQASM2Parser.AdditiveExpContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#multiplicativeExp.
    def enterMultiplicativeExp(self, ctx:OpenQASM2Parser.MultiplicativeExpContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#multiplicativeExp.
    def exitMultiplicativeExp(self, ctx:OpenQASM2Parser.MultiplicativeExpContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#exponentialExp.
    def enterExponentialExp(self, ctx:OpenQASM2Parser.ExponentialExpContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#exponentialExp.
    def exitExponentialExp(self, ctx:OpenQASM2Parser.ExponentialExpContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#unaryExp.
    def enterUnaryExp(self, ctx:OpenQASM2Parser.UnaryExpContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#unaryExp.
    def exitUnaryExp(self, ctx:OpenQASM2Parser.UnaryExpContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#primaryExp.
    def enterPrimaryExp(self, ctx:OpenQASM2Parser.PrimaryExpContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#primaryExp.
    def exitPrimaryExp(self, ctx:OpenQASM2Parser.PrimaryExpContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#unaryop.
    def enterUnaryop(self, ctx:OpenQASM2Parser.UnaryopContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#unaryop.
    def exitUnaryop(self, ctx:OpenQASM2Parser.UnaryopContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#real.
    def enterReal(self, ctx:OpenQASM2Parser.RealContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#real.
    def exitReal(self, ctx:OpenQASM2Parser.RealContext):
        pass


    # Enter a parse tree produced by OpenQASM2Parser#nninteger.
    def enterNninteger(self, ctx:OpenQASM2Parser.NnintegerContext):
        pass

    # Exit a parse tree produced by OpenQASM2Parser#nninteger.
    def exitNninteger(self, ctx:OpenQASM2Parser.NnintegerContext):
        pass



del OpenQASM2Parser