from typing import Dict, List, Optional, Tuple

from languageFreeAcq import CspScopesRelations

from .Relation import Relation
from .Template import Template


class CSP:
    def __init__(self, variables: list):
        self.variables = variables
        self.constraints: List[Tuple[List[int], Relation]] = []  # list of (scope, relation)

    def add_constraint(self, scope: list, relation: Relation):
        self.constraints.append((scope, relation))

    def is_solution(self, assignment: dict):
        for scope, relation in self.constraints:
            if not relation.accept([assignment[var] for var in scope]):
                return False
        return True

    def accuracy(self, examples: list, assert_positive_true: bool = False):
        """
        Compute the accuracy of the CSP on a list of examples.
        :param examples: v1, v2, ..., vn, {0, 1}
        :param assert_positive_true: if True, assert that the CSP has a solution for all examples with last element 1
        :return: the accuracy of the CSP on the examples
        """
        assert all([len(ex) == len(self.variables) + 1 for ex in examples]), "All examples must have the right length"
        correct = 0
        for ex in examples:
            assignment = {self.variables[i]: ex[i] for i in range(0, len(self.variables))}
            if ex[-1] == 0:
                if not self.is_solution(assignment):
                    correct += 1
            elif ex[-1] == 1:
                if assert_positive_true:
                    assert self.is_solution(assignment), f"The CSP should have a solution for example {ex}"
                if self.is_solution(assignment):
                    correct += 1
            else:
                assert False, f"The last element of the example must be 0 or 1 (it is {ex[-1]})"
        return correct / len(examples)

    def __str__(self):
        s = f"Variables: {self.variables}\n"
        r_to_s: Dict[Relation, List[List[int]]] = {}
        for scope, relation in self.constraints:
            if relation not in r_to_s:
                r_to_s[relation] = []
            r_to_s[relation].append(scope)
        s += f"Relations and scopes: {r_to_s}\n"
        return s


def convert_from_CspScopesRelations(csp_sr: CspScopesRelations):
    csp = CSP(csp_sr.variables)
    for i in range(0, len(csp_sr.get_scopes_relations())):
        scopes = csp_sr.get_scope(i)
        tuples = [list(t) for t in csp_sr.get_relation(i)]
        relation = Relation(accepted_tuples=tuples)
        for scope in scopes:
            csp.add_constraint(list(scope), relation)
    return csp


def convert_from_Template(template: Template) -> CSP:
    assert template is not None, "The template must not be None"
    csp: CSP = CSP(template.get_variables())
    for scope, relation in template.interpretation_constraints():
        csp.add_constraint(list(scope), relation)
    return csp


def file_to_examples(file_path: str, max_examples: Optional[int] = None):
    examples = []
    with open(file_path, "r") as f:
        count = 0
        for line in f:
            if max_examples is not None and count >= max_examples:
                break
            example = [int(val) for val in line.split(",")]
            examples.append(example)
            count += 1
    return examples
