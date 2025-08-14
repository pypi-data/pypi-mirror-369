# tetrascience protocol virtual machine

## compiler

Example usage for python 3.10+

```python
from ts_protocol_virtual_machine import compiler
from ts_protocol_virtual_machine.result import Ok, Err

INPUT = """
protocolSchema: v3

steps: []
"""

match compiler.yaml.to.protocol_v2(INPUT):
    case Ok(program, warnings):
        print("SUCCESS", program, warnings)
    case Err(errors, warnings):
        print("ERROR", errors, warnings)
```

Example usage for python 3.9:

```python
from ts_protocol_virtual_machine import compiler

INPUT = """
protocolSchema: v3

steps: []
"""

compiler.yaml.to.pvm(INPUT).match(
    lambda program, warnings: print("SUCCESS", program, warnings),
    lambda errors, warnings: print("ERROR", errors, warnings),
)
```
