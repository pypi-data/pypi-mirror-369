# Generated from OpenQASM2.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .OpenQASM2Parser import OpenQASM2Parser
else:
    from OpenQASM2Parser import OpenQASM2Parser

# This class defines a complete generic visitor for a parse tree produced by OpenQASM2Parser.

class OpenQASM2Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by OpenQASM2Parser#mainprogram.
    def visitMainprogram(self, ctx:OpenQASM2Parser.MainprogramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#program.
    def visitProgram(self, ctx:OpenQASM2Parser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#statement.
    def visitStatement(self, ctx:OpenQASM2Parser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#includeStatement.
    def visitIncludeStatement(self, ctx:OpenQASM2Parser.IncludeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#decl.
    def visitDecl(self, ctx:OpenQASM2Parser.DeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#gatedecl.
    def visitGatedecl(self, ctx:OpenQASM2Parser.GatedeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#goplist.
    def visitGoplist(self, ctx:OpenQASM2Parser.GoplistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#qop.
    def visitQop(self, ctx:OpenQASM2Parser.QopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#uop.
    def visitUop(self, ctx:OpenQASM2Parser.UopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#anylist.
    def visitAnylist(self, ctx:OpenQASM2Parser.AnylistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#idlist.
    def visitIdlist(self, ctx:OpenQASM2Parser.IdlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#mixedlist.
    def visitMixedlist(self, ctx:OpenQASM2Parser.MixedlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#argument.
    def visitArgument(self, ctx:OpenQASM2Parser.ArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#explist.
    def visitExplist(self, ctx:OpenQASM2Parser.ExplistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#exp.
    def visitExp(self, ctx:OpenQASM2Parser.ExpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#additiveExp.
    def visitAdditiveExp(self, ctx:OpenQASM2Parser.AdditiveExpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#multiplicativeExp.
    def visitMultiplicativeExp(self, ctx:OpenQASM2Parser.MultiplicativeExpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#exponentialExp.
    def visitExponentialExp(self, ctx:OpenQASM2Parser.ExponentialExpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#unaryExp.
    def visitUnaryExp(self, ctx:OpenQASM2Parser.UnaryExpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#primaryExp.
    def visitPrimaryExp(self, ctx:OpenQASM2Parser.PrimaryExpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#unaryop.
    def visitUnaryop(self, ctx:OpenQASM2Parser.UnaryopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#real.
    def visitReal(self, ctx:OpenQASM2Parser.RealContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OpenQASM2Parser#nninteger.
    def visitNninteger(self, ctx:OpenQASM2Parser.NnintegerContext):
        return self.visitChildren(ctx)



del OpenQASM2Parser