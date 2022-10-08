from ast import NodeTransformer, parse, unparse
from typing import NamedTuple, Tuple, Type
from .transformers import *


class Result(NamedTuple):
    code: str
    passes: int


class Deobfuscator:
    TRANSFORMERS: Tuple[Type[NodeTransformer], ...] = (
        StringSubscriptSimple,
        GlobalsToVarAccess,
        InlineConstants,
        DunderImportRemover,
        GetattrConstructRemover,
        BuiltinsAccessRemover,
        Dehexlify,
        UselessEval,
        UselessCompile,
        ExecTransformer,
        UselessLambda,
    )

    def __init__(self, code: str) -> None:
        self.code = code
        self.tree = parse(code)

    def deobfuscate(self) -> Result:
        passes = 0
        code = self.code
        while True:
            for transformer in self.TRANSFORMERS:
                self.tree = transformer().visit(self.tree)
            # If nothing changed after a full pass, we're done
            if (result := unparse(self.tree)) == code:
                break
            code = result
            passes += 1
        return Result(code, passes)
