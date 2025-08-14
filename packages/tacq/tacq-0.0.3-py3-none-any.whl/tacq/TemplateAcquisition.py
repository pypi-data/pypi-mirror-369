from languageFreeAcq import Acquisition, CspScopesRelations

from .CSP import CSP, file_to_examples, convert_from_Template, convert_from_CspScopesRelations
from .Relation import Relation
from .IterativeTemplate import IterativeTemplate
from .Template import Template


class TemplateAcquisition:
    """ This class is used to learn a CSP/Template directly from examples. It is the main start point of the
    acquisition process. You can simply call the learn method with the path to the file of examples and the CSP
    will be learned. """

    def __init__(self):
        self.DOMAINS, self.VARIABLES_NUMBERS, self.TEMPLATE, self.NETWORK, self.BASELINE = None, None, None, None, None

    def get_domains(self):
        """
        @return: the domains of the variables inferred from the learning examples.
        """
        return self.DOMAINS

    def get_variables_numbers(self):
        """
        @return: the number of variables inferred from the learning examples.
        """
        return self.VARIABLES_NUMBERS

    def get_template(self) -> Template:
        """
        @return: the template learned from the examples.
        """
        return self.TEMPLATE

    def get_network(self) -> CSP:
        """
        @return: the CSP network learned from the examples.
        """
        return self.NETWORK

    def get_baseline_network(self) -> CSP:
        """
        @return: the baseline CSP network learned from the examples.
        This is the CSP that is learned from the examples without using the Template.
        """
        if self.BASELINE is None:
            raise ValueError("The network has not been learned yet. Call learn_from_file() first.")
        return self.BASELINE

    def learn_from_file(self, file_train: str, max_examples: int = 0, timeout: int = None,
              verbose: bool = False, max_cpu: int = 0) -> CSP:
        """
        Learn the compact CSP/Template from the given file of examples
        @param file_train: The path to the file of examples with the format: "var1, var2, ..., varN, weight" with var1,
        var2, ..., varN the values of the variables and weight the weight of the example (0 for a non-solution, 1 for a
        solution)
        @param max_examples: The maximum number of examples to consider in the file. If 0, all examples are considered.
        @param timeout: The maximum time in seconds for each call to the solver.
        @param verbose: If True, the logs of the optimization process are displayed. The other logs can be displayed by
        setting the logging level to DEBUG.
        @param max_cpu: The maximum number of CPU cores to use for learning the CSP. If 0, all available cores are used.
        @return: The learned CSP (a CSP object)
        """
        # Phase 1 - LFA
        if self.DOMAINS is not None or self.VARIABLES_NUMBERS is not None:
            raise ValueError("The vocabulary has already been set. You cannot use a file after.")
        NB_EXAMPLES, self.DOMAINS, self.VARIABLES_NUMBERS = self._params_from_file(file_train)
        if max_examples > 0:
            NB_EXAMPLES = max_examples
        lfa = Acquisition()
        csp_sr: CspScopesRelations = lfa.learn(
            file_train=file_train, max_examples=NB_EXAMPLES, timeout=timeout, verbose=verbose, max_cpu=max_cpu
        )
        self.BASELINE = convert_from_CspScopesRelations(csp_sr)
        csp_variables, csp_domain = (
            list(range(0, lfa.get_variables_numbers())),
            lfa.get_domains(),
        )
        self.DOMAINS, self.VARIABLES_NUMBERS = csp_domain, len(csp_variables)
        examples_train = file_to_examples(file_train, max_examples=NB_EXAMPLES)
        # Phase 2 - Template Matching
        constraints_to_learn = []
        for scopes, relations in csp_sr.get_scopes_relations():
            rel: Relation = Relation(accepted_tuples=[list(r) for r in relations])
            for scope in scopes:
                constraints_to_learn += [(tuple([csp_variables[x] for x in scope]), rel)]
        tm = IterativeTemplate(csp_variables, csp_domain)
        self.TEMPLATE = tm.learn(constraints_to_learn, timeout_solver=timeout, train_example=examples_train)
        self.NETWORK = convert_from_Template(self.TEMPLATE)
        return self.NETWORK

    def _params_from_file(self, file_path: str) -> (int, list, int):
        PARAM_NB_EXAMPLES = 0
        PARAM_DOMAINS = []
        PARAM_VARIABLES_NUMBERS = -1
        with open(file_path, 'r') as f:
            for line in f:
                if line[0] != '#':
                    PARAM_VARIABLES_NUMBERS = len(line.split(',')) - 1
                    for val in line.split(','):
                        if val != '1\n' and val != '0\n' and int(val) not in PARAM_DOMAINS:
                            PARAM_DOMAINS.append(int(val))
                    PARAM_NB_EXAMPLES += 1
                    break
            for line in f:
                if line[0] != '#':
                    assert PARAM_VARIABLES_NUMBERS == len(line.split(',')) - 1, "Inconsistent number of variables"
                    for val in line.split(','):
                        if val != '1\n' and val != '0\n' and int(val) not in PARAM_DOMAINS:
                            PARAM_DOMAINS.append(int(val))
                    PARAM_NB_EXAMPLES += 1
        if PARAM_VARIABLES_NUMBERS == -1:
            raise SyntaxError("No example found in file: " + file_path)
        return PARAM_NB_EXAMPLES, sorted(PARAM_DOMAINS), PARAM_VARIABLES_NUMBERS
