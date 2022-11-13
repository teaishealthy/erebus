import sys
from erebus import deobfuscate

if len(sys.argv) < 2:
    print("Usage: python -m erebus <filename>")
    sys.exit(1)

with open(sys.argv[1]) as f:
    code = f.read()

f = sys.stdout
if len(sys.argv) > 2:
    f = open(sys.argv[2], "w")

deobfuscated = deobfuscate(code)
f.write(deobfuscated.code)
f.flush()
f.close()
