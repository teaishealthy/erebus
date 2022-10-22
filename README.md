# erebus

A free and open source Hyperion deobfuscator.

## Usage

```py
from erebus import deobfuscate

with open("obfuscated.py", "r") as f:
    obfuscated = f.read()

print(deobfuscate(obfuscated))
```

It might make sense to now run the code through a formatter and/or linter.

## Notes

In my testing, I have noticed that Hyperion sometimes produces code that is not valid Python. erebus will not fix this and likely produce invalid Python code as well.


## Features

#### Default Settings
erebus produces highly readable code when Hyperion was run with the default settings.
#### Ultra Safe Mode

If Hyperion was run in Ultra Safe Mode, erebus will produce code that is extremely similar to the original code as variables have not been renamed.

#### Camouflate

erebus currently does not support the Camouflate option of Hyperion, but it is planned.


## License

erebus is licensed under the Unilicense.
See [LICENSE](LICENSE) for more information.