# ia_activate

## Overview

`ia_activate` is a Python module designed to manage the activation and deactivation of Python virtual environments (venvs) in an asynchronous context. It provides decorators and context managers to ensure that the virtual environment is activated when executing specific functions or coroutines, allowing for a clean and efficient development workflow.

## Features

- **Asynchronous Context Management**: Use `async with` to activate a virtual environment within an asynchronous context, ensuring that the environment is properly set up and torn down.
- **Decorator Support**: Easily decorate functions or coroutines to activate the virtual environment automatically when they are called.
- **Cross-Platform Compatibility**: Designed to work on both Unix-like systems and Windows, handling environment variable adjustments appropriately.
- **Logging**: Integrated logging to provide insights into the activation and deactivation processes, aiding in debugging and monitoring.

## Installation

To use `ia_activate`, simply include it in your Python project. Ensure you have Python 3.7 or higher installed, as well as any necessary dependencies.

```bash
pip install ia_activate
```

*EDITORS NOTE: no.*

## Usage

Activating a Virtual Environment
You can activate a virtual environment using the activate context manager or the activated decorator.
Using the Context Manager

```python
from ia_activate import activate
from pathlib import Path

async def main():
    async with activate(Path('/path/to/your/venv')):
        # Your code here will run with the virtual environment activated
        pass
if name == 'main':
    import asyncio
    asyncio.run(main())
```

#### Using the Decorator

```python
from ia_activate import activated
from pathlib import Path

@activated(Path('/path/to/your/venv'))
async def my_function():
    # This function will run with the virtual environment activated
    pass
```

### Deactivating the Virtual Environment

The virtual environment is automatically deactivated when exiting the context manager or when the decorated function completes. You can also manually call the `deactivate` function if needed.

```python
from ia_activate import deactivate

deactivate()
```

## Logging

The module uses Python's built-in logging library to provide debug and info messages during the activation and deactivation processes. You can configure the logging level as needed in your application.

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

*EDITORS NOTE: structlog*

## Contributing

Contributions to `ia_activate` are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

*EDITORS NOTE: lol*

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Developed by InnovAnon, Inc.
