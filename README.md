# Setup

### Requirements:

- [Pyenv](https://github.com/pyenv/pyenv)
- [Poetry](https://python-poetry.org/)

### Install Python specified in `.python-version`
    pyenv install
### Install dependencies specified in `pyproject.toml`
    poetry install

# Running tests

Run local unit tests with:

    ./check.sh

# Calling the compiler

A source code file can be compiled like this:

    ./compiler.sh compile path/to/source/code --output=path/to/output/file

Or the source code can be compiled directly from the command line like this:

    ./compiler.sh compile --output=path/to/output/file <<<'source code'

# Language example

    fun square(x: Int): Int {
    return x * x;
    }

    var n: Int = read_int();
    print_int(n);
    while n > 1 do {
        if n % 2 == 0 then {
            n = n / 2;
        } else {
            n = 3*n + 1;
        }
        print_int(n);
    }

    print_int(square(5))
