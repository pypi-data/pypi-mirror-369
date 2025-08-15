# Motoevsentiment 
A package for extracting and analyzing sentiment from EV motorcycle feedback provided by customers and employees.

## Source Code
The full source code for this project is available on [GitHub](https://github.com/richardayikwei/sentiment_package).

## wsentiment subpackage
This subpackage analyses WhatsApp related messages for sentiment.

## Using wsentiment

import by using
```
from evmotosentiment.wsentiment import wsentiment_score
```
wsentiment_score takes only string inputs.

- example

```
wsentiment_score('kofi has lights out')
>> -2
```

## wdataframe
This subpackage changes WhatsApp text export file *(.txt)* into a dataframe

## Using wdataframe

import using
```
from evmotosentiment.wsentiment import wdataframe
```

- example
```
# Suppose you have a text file with data
test_file = "sample.txt"

# Read the text file into a Pandas DataFrame
df = wdataframe(test_file)

# Display the DataFrame
print(df)

              datetime       sender     message
0  2023-09-29 07:49:00    John Doe          ok
1  2023-09-29 08:15:00    Jane Doe  swapped battery
```

### Running using pytest
To run tests in your current Python environment:

```bash
pytest
```

## Running Tests with Tox

This project uses [Tox](https://tox.wiki/) to automate testing across multiple Python versions.

### Test Environments
The `tox.ini` is configured to run tests with:
- Python 3.9
- Python 3.10
- Python 3.11

Each environment installs:
- `pytest` (for running tests)
- `pandas` (project dependency)

### Prerequisites
- Python 3.9, 3.10, and 3.11 installed on your system
- [uv](https://github.com/astral-sh/uv) for faster installs (optional but recommended)
- Install tox with uv:
```bash
uv pip install tox tox-uv
```
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)