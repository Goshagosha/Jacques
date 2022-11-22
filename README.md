# Jacques
Inferring DSL-to-code translation rule sets.  
---
Web hosted documenration is available at https://goshagosha.github.io/Jacques/modules.html

# Requirements
`python>=3.10`
The rest is supplied with `requirements.txt`

# One click-demo
```
git clone git@github.com:Goshagosha/Jacques.git  
cd Jacques 
python3.10 -m pip install -r requirements.txt
python3.10 demo.py
```

# Getting started
## Building from source (Optional)
```
python3.10 -m pip install -r requirements.txt
python3.10 -m pip install build
python3.10 -m build
```

## Installing a release
You can grab a compiled wheel file from [releases](https://github.com/Goshagosha/Jacques/releases/tag/v1.0.0)
```
python3.10 -m pip install dist/jacques-1.0.0-py3-none-any.whl
```

## Running Jacques
```
from jacques import Jacques
j = Jacques()
```
To push individual example:
```
j.push_example(
    '## on data | select columns "Confirmed"',
    'data[["Confirmed"]]'
)
```
To push set of examples from a file:
```
j.push_examples_from_file(<path to the file>)
```
Finally, to generate rules:
```
j.process_all_examples()
```

To see the list of generated rules:
```
for rule in j.ruleset.values():
    print(rule)
```

... or export generated rules into standalone (NLDSL-dependant) script
```
j.export_rules()
```

## Running server
To host a backend server for your purposes
```
from jacques import JacquesServer
server = JacquesServer(host="127.0.0.1", port=8000)
```

## Research
Learning data for used for evaluation is available in [training_examples](training_examples) under `<library_name>_v2/`.  
Results of evaluation are published in the original paper, but logs and relevant jupyter notebook are [here](research).

### Research check
The training data used for evaluation was processed by Jacques. The relevant log files were then inspected, and metrics manually recorded into three [pandas.csv](research/pandas.csv), [polars.csv](research/polars.csv), and [spark.csv](research/spark.csv). The data from these CSV files is then used in a [notebook](research/prep.ipynb), to produce resulting tables and charts published in the paper.  
If you wish to confirm our findings, we provide a bash script `research_check.sh` which runs evaluation for every training set again, and diffs the latest logs with the ones stored in `research` folder to show no deviation. Then you can inspect either of the log files (go straight to the end of the file) to compare them against metrics recorded in CSVs.  
Finally, aforementioned notebook contains full scripts used to generate latex tables and pyplot charts from CSV files, which process can be executed again any time. (Recent VSCode versions should support notebooks out-of-the-box).

# Statistics
```
>> python3.10 -m pylint --good-names=i,j,k,id,e,_,y,x,m,v --disable=E0402 src
...
Your code has been rated at 8.82/10
```

## Source
| path | files | code | comment | blank | total |
| :--- | ---: | ---: | ---: | ---: | ---: |
| . | 23 | 2,018 | 204 | 391 | 2,613 |
| jacques | 23 | 2,018 | 204 | 391 | 2,613 |
| jacques/ast | 8 | 719 | 77 | 137 | 933 |
| jacques/ast/parsers | 2 | 163 | 2 | 29 | 194 |
| jacques/core | 9 | 1,114 | 87 | 192 | 1,393 |
| jacques/core/nldsl_utils | 3 | 64 | 13 | 16 | 93 |
| jacques/tests | 2 | 21 | 0 | 6 | 27 |

## Trainind data
| path | files | code | comment | blank | total |
| :--- | ---: | ---: | ---: | ---: | ---: |
| . | 46 | 564 | 1,499 | 796 | 2,859 |
| blank | 9 | 0 | 250 | 134 | 384 |
| pandas | 4 | 76 | 157 | 75 | 308 |
| pandas_v2 | 9 | 144 | 288 | 152 | 584 |
| polars | 2 | 42 | 95 | 47 | 184 |
| polars_v2 | 9 | 58 | 271 | 143 | 472 |
| spark | 4 | 82 | 150 | 82 | 314 |
| spark_v2 | 9 | 162 | 288 | 163 | 613 |

## Tests
I have to admit I have not provided anyhow sufficient tests. At the beginning of development I have configured pytest, but in the process I found myself staring at execution logs (DEBUG level logging is implemented exceptionally verbose) much more. By the end I have ran out of time to write sufficient tests. I realize, nevertheless, that logging is no replacement for testing, and this complicates potential development for other people.
