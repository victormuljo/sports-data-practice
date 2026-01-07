# sports-data-practice
This repository is used to practice data analytics with python and pandas using dummy sports data!

My goal is to obtain proficiency in python and pandas with this project and use it as a building block to create a data-driven sports-focused product

### How to run the main script
1. Install requirements.txt using pip install -r requirements.txt
2. In terminal, run python3 main.py

### How to run tests
In terminal, run python3 -m tests.test_validation

### Folder structure

```
.
sports-data-practice/
├─ __pycache__/
├─ .git/
├─ datasets/
│  └─ player_stats.csv
├─ src/
│  ├─ __pycache__/
│  ├─ __init__.py
│  ├─ data.py
│  ├─ metrics.py
│  └─ validation.py
├─ tests/
│  ├─ __pycache__/
│  ├─ __init__.py
│  ├─ test_player_analysis.ipynb
│  └─ test_validation.py
├─ .gitignore
├─ main.py
├─ README.md
└─ requirements.txt

```


The folders of this project consist of src, datasets, and tests

The src folder holds all the modules of this project

The tests folder holds all the test modules of this project that I use to test dummy data and validation

The datasets folder holds all the dummy datasets I use to load into my project from the csv file.

