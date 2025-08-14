# TAcq - Framework for Learning Compact Representations of Constraint Networks
A framework for learning compact representations of constraint networks.
This project is based on the paper “Learning Compact Representations of Constraint Networks” to be published.

The code is organized in the following way:
- `src/`: Contains the code for the experiments and the models.
- `data/`: Contains data used for some experiments.

You need to have the following dependencies installed:
- "languageFreeAcq~=0.0.7"
- "typing_extensions~=4.12.2"
- "ortools~=9.11.4210"

You can install them using pip:
```bash
pip install ortools
pip install tqdm
pip install languageFreeAcq
```

## Use the TAcq framework in your code
You can install the TAcq framework using pip:
```bash
pip install tacq
```

Then, you can use it in your code as follows:
```python
from tacq import TemplateAcquisition

ta = TemplateAcquisition()
ta.learn_from_file("examtimetabling_2.csv", 300, 1000)
print(ta.get_network())
print(ta.get_template())
```

## Running using CLI
To run an experiment using CLI, you may use the following command:
```bash
python src/main.py <nb_examples> <examples_file> <timeout_solver> <verbose> <max_cpu>
```
Where `<nb_examples>` is the number of examples to use as training set, `<examples_file>` is the file containing 
the examples (some are provided in the `data/` directory), `<max_cpu>` is the maximum number of CPU cores,
`<timeout_solver>` is the timeout for each call to the solver in seconds, `<verbose>` is a flag to enable verbose
mode (1 for true, 0 for false),
