# type: ignore
import ast
from typing import Any
import string

CONSTANTS = (
    ast.Name,
    ast.Constant,
    ast.Str,
    ast.Num,
    ast.Bytes,
    ast.Ellipsis,
    ast.NameConstant,
    ast.Attribute,
    ast.Subscript,
    ast.Tuple,
)

__all__ = (
    "StringSubscriptSimple",
    "GlobalsToVarAccess",
    "InlineConstants",
    "DunderImportRemover",
    "GetattrConstructRemover",
    "BuiltinsAccessRemover",
    "Dehexlify",
    "UselessEval",
    "UselessCompile",
    "ExecTransformer",
    "UselessLambda",
)

constants: dict[str, Any] = {}


class StringSubscriptSimple(ast.NodeTransformer):
    """Transforms Hyperion specific string slicing into a string literal"""
    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.value, ast.Str):
            if isinstance(node.slice, ast.Slice):
                code = ast.unparse(node.slice.step)
                if not any(s in code for s in string.ascii_letters):

                    s = node.value.s[:: eval(ast.unparse(node.slice.step))]
                    return ast.Str(s=s)
        return super().generic_visit(node)


class GlobalsToVarAccess(ast.NodeTransformer):
    def visit_Subscript(self, node: ast.Subscript) -> Any:
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in ("globals", "locals", "vars")
        ):
            if isinstance(node.slice, ast.Constant) and isinstance(
                node.slice.value, str
            ):
                return ast.Name(id=node.slice.value, ctx=ast.Load())
        return super().generic_visit(node)


class InlineConstants(ast.NodeTransformer):
    class FindConstants(ast.NodeTransformer):
        def visit_Assign(self, node: ast.Assign) -> Any:
            if isinstance(node.value, CONSTANTS) and isinstance(
                node.targets[0], ast.Name
            ):
                constants[node.targets[0].id] = node.value
                # delete the assignment
                return ast.Module(body=[], type_ignores=[])
            return super().generic_visit(node)

    def visit(self, node: Any) -> Any:
        self.FindConstants().visit(node)
        return super().visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        """Replace the name with the constant if it's in the constants dict"""
        if node.id in constants:
            return constants[node.id]
        return super().generic_visit(node)


class DunderImportRemover(ast.NodeTransformer):
    """Just transform all __import__ calls to the name of the module being imported"""
    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name) and node.func.id == "__import__":
            return ast.Name(id=node.args[0].s, ctx=ast.Load())
        return super().generic_visit(node)


class GetattrConstructRemover(ast.NodeTransformer):
    """Hyperion has an interesting way of accessing module attributes."""
    def visit_Call(self, node: ast.Call) -> Any:

        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            return ast.Attribute(value=node.args[0], attr=node.args[1].slice.args[0].s)

        return super().generic_visit(node)


class BuiltinsAccessRemover(ast.NodeTransformer):
    """Instead of accessing builtins, just use the name directly"""
    def visit_Attribute(self, node: ast.Attribute) -> Any:
        if isinstance(node.value, ast.Name) and node.value.id == "builtins":
            return ast.Name(id=node.attr, ctx=ast.Load())
        return super().generic_visit(node)


class Dehexlify(ast.NodeTransformer):
    """Transforms a binascii.unhexlify(b'').decode('utf8') into a string"""
    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Attribute) and node.func.attr == "decode":
            if (
                isinstance(node.func.value, ast.Call)
                and isinstance(node.func.value.func, ast.Attribute)
                and node.func.value.func.attr == "unhexlify"
            ):
                return ast.Str(
                    s=bytes.fromhex(node.func.value.args[0].s.decode()).decode("utf8")
                )
        return super().generic_visit(node)


class UselessEval(ast.NodeTransformer):
    """Eval can just be replaced with the string"""
    def visit_Call(self, node: ast.Call) -> Any:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "eval"
            and isinstance(node.args[0], ast.Str)
        ):
            return ast.parse(node.args[0].s).body[0].value
        return super().generic_visit(node)


class UselessCompile(ast.NodeTransformer):
    """An call to compile() in Hyperion is usually useless"""
    def visit_Call(self, node: ast.Call) -> Any:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "compile"
            and isinstance(node.args[0], ast.Str)
        ):
            return node.args[0]
        return super().generic_visit(node)


class ExecTransformer(ast.NodeTransformer):
    """Exec can be just transformed into bare code"""
    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name) and node.func.id == "exec":
            if result := ast.parse(node.args[0].s).body:
                return result[0]
        return super().generic_visit(node)


class UselessLambda(ast.NodeTransformer):
    # x = lambda: y() -> x = y
    class FindReferences(ast.NodeVisitor):
        def __init__(self) -> None:
            self.references: Dict[str, int] = {}

        def visit_Name(self, node: ast.Name) -> Any:
            if isinstance(node.ctx, ast.Load):
                self.references[node.id] = self.references.get(node.id, 0) + 1
            return super().generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        if isinstance(node.value, ast.Lambda):
            if isinstance(node.value.body, ast.Call):
                # make sure both call and lambda gave no arguments
                if not node.value.body.args:
                    visitor = self.FindReferences()
                    visitor.visit(node.value.body)
                    # lambda arguments not in visitor.references
                    return ast.Assign(
                        targets=node.targets,
                        value=node.value.body.func,
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                    )

        return super().generic_visit(node)
