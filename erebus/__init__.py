from .deobfuscator.deobfuscator import Deobfuscator, Result
from .deobfuscator.unwrapper import unwrap

__all__ = ("deobfuscate",)


def deobfuscate(code: str) -> Result:
    """Deobfuscate a string of code"""
    return Deobfuscator(unwrap(code)).deobfuscate()
