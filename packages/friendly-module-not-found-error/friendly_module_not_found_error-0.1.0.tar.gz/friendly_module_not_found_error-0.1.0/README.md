# friendly_module_not_found_error

This is a Python package that provides a custom exception class for handling module not found errors in a friendly way.

## Installation

To install the package, run the following command:

```cmd/bash
pip install friendly_module_not_found_error
```

## Usage

Don't need to import the packages. The pth file is already in the site-packages folder.

You can use the code to test the effects of the package:

```python
import ant
```

The message raised will change to : "No module named 'ant'. Did you mean 'ast'?"

```python
import multiprocessing.dumy
```

The message raised will change to : "module 'multiprocessing' has no child module 'dumy'. Did you mean 'dummy'?"

You can also run "test/test.py" to test the effects of the python.

## require

python3.12+

Below it, the suggestion cannot be supported. The change that python suggest the similar name in "traceback.py" is in "3.12".

## License

This package is licensed under the MIT License. See the LICENSE file for more information.

## issues

If you have any questions or suggestions, please open an [issue](https://github.com/Locked-chess-official/friendly_module_not_found_error/issues) on GitHub.

## Contributing

Contributions are welcome! Please submit a [pull request](https://github.com/Locked-chess-official/friendly_module_not_found_error/pulls) with your changes.

## Note

If a module that is not a package contains submodules, and those submodules also contain their own submodules, this nested module structure is not supported.
When this situation occurs, you should reorganize the code using proper package structure. This approach violates Python's packaging best practices and should be avoided.

## Credits

This package was created by [Locked-chess-official] and is maintained by [Locked-chess-official].