# Motoevsentiment 
A package for extracting and analyzing sentiment from EV motorcycle feedback provided by customers and employees.

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
