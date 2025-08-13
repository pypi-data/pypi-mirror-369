# hatch-adder

A command to add dependencies to hatch similar to uv, poetry, etc.

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-adder.svg)](https://pypi.org/project/hatch-adder)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-adder.svg)](https://pypi.org/project/hatch-adder)

-----

## Table of Contents

- [hatch-adder](#hatch-adder)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [License](#license)

## Installation

```console
pip install hatch-adder
```

Now use it like:
```
hatch-add requests
```

Or add dev dependencies to your `[project.optional-dependencies]`:
```
hatch-add --dev pytest
```

## License

`hatch-adder` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
