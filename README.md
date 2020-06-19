# Reverse Polish Notation Programming Language
What started off as a RPN calculator because a turing-complete stack-based programming language. 

This was a lot of fun to implement, and I could keep iterating on it indefinitely if I had the time.
Some of the next points of improvement I would make would be:
- Code refactor. The `rpnlanginterpreter.py` class is too busy. Maybe I'll make a real lexer and parser.
- Add support for interactive history via up/down arrow keys
- Write an interpreter or compiler for RPN in RPN. It's not too different from python bytecode.
- Add support for block-scoped variables and functions. Currently everything is global
- Add string support.
- Allow References as a manipulatable datatype. This might end up resulting in behavior like PHP's variable-variables.
## Proof of Turing Completeness
According to [this article](https://en.wikipedia.org/wiki/General_recursive_function#Definition), in order to prove
 turing completeness, it is sufficient to prove:
 1. We can define the constant function.
 1. We can define the successor function.
 1. We can define the identity function.
 1. We can compose these functions arbitrarily.
 
### Constant function
Just initialize a variable. For example the zero-function is defined like this:
```
 0 &$zero =
```
### The successor function
That's built into the language as `++`

### The identity function
That's built into the language as `dup`

### Arbitrary Composition
Checkout the example in `./examples`. There I implemented a recursive factorial function.

After following the setup guide below, you can run it like this:
```bash
#!/bin/bash
INPUT=5
./dist/rpn -f ./examples/factorial.rpn $INPUT
```

## Setup Guide
1. Install `bash`, `python3.8`, and the corresponding `pip3` version. This will vary from distribution to distribution. Consult [Python's documentation](https://www.python.org/downloads/) or your distribution's documentation for help.
1. Install `pipenv`. Typically this is done by running `pip3 install pipenv`.
1. From this directory, run `bash build.sh` to compile the file to `./dist/rpn`
1. Run the program. See the help page for usage: `./dist/rpn --help`

## Advanced Usage
- You can enter interactive mode with `rpn -i`
- You can indicate how many characters of a block on the stack to display with `-v <NUM_CHARS>`
- You can run a one-off calculation by not specifying `-i` or `-f`
- You can pipe from stdin using `rpn -f -`
- EXPERIMENTAL: You can display results in any of the following number bases (keep overflow or rounding errors in mind):
  - Decimal `rpn -d` (default)
  - Binary `rpn -b`
  - Octal `rpn -o`
  - Hexadecimal `rpn -x`
- Don't forget to read both help pages `rpn -h` and `rpn -H`