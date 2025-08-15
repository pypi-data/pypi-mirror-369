# SRinputs - Static Repetitive inputs
![License](https://img.shields.io/github/license/keyles-Py/SRinputs)

A small Python package that improves the usage of the built-in input() function with functionalities such as static and multiple inputs.

## Instalation

You can install it using pip.

```bash
pip install SRinputs
```

## Features

* **Type validation:** Requests and validates inputs such as `int`, `float` or `str`.
* **Error handling:** Catch `KeyboardInterrupt` and `EOFError` in a user friendly way, allowing the program to continue.
* Mandatory entries:** Ensures that the user enters a valid value before continuing, avoiding empty entries by default.
* Multiple entries:** Requests a specific number of entries and returns them in a list.

## Usage and Examples
Here are some examples of how to use the functions to get validated inputs.

## Getting a Single Validated Input
These functions will repeatedly prompt the user until a valid input of the requested data type is provided.

```bash
from SRinputs import IntInput

# Prompt for an integer, does not allow empty input by default
age = IntInput("Please enter your age: ")
print(f"Your age is: {age}")
```

```bash
from SRinputs import StrInput

# Prompt for a string, does not allow empty input by default
name = StrInput("Please enter your name: ")
print(f"Your name is: {name}")
```

```bash
from SRinputs import FloatInput

# Prompt for a float, does not allow empty input by default
price = FloatInput("Please enter the price: ")
print(f"The price is: {price}")
```
## Getting Multiple Inputs

This function ensures a specific number of valid inputs are collected before continuing.

```bash
from SRinputs import multiInput

# Prompt for 'n' inputs, does not allow empty input by default
names = multiInput(5, "Please enter one name: ")
print(f"The names are: {names}")
```

