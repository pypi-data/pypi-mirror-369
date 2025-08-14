import logging
from math import ceil

from typing_extensions import Optional

from .SolverOrTools import SolverOrTools
from .CSP import convert_from_Template
from .Relation import Relation, default_language
from .Template import Characteristic, Template, TemplateVariable
from .AddRule import AddRule


def constraints_without_symmetric(constraints) -> list[tuple[list[TemplateVariable], Relation]]:
    """Compute the number of remaining constraints without symmetric constraints."""
    cons = []
    for scope, relation in constraints:
        if relation.is_symmetric():
            if (scope, relation) not in cons and (scope[::-1], relation) not in cons:
                cons.append((scope, relation))
        else:
            cons.append((scope, relation))
    return cons


class IterativeTemplate:
    """Class to implement the iterative learning process."""

    def __init__(self, csp_variables: list, csp_domain: list, examples: Optional[list] = None):
        language = default_language()
        self._initial_template: Template = Template(csp_variables, csp_domain, [], language)
        self._constraints_to_cover = None
        self._solver_timeout: Optional[int] = None
        self._conjunction = True
        logging.debug("Conjunctions are used." if self._conjunction else "Conjunctions are not used.")
        self._examples_test = examples
        self._alpha = 0.3
        self._log = logging.getLogger().getEffectiveLevel() == logging.DEBUG

    def min_constraints_required(self, old_template: Template) -> int:
        """Compute the number of constraints to reach with a new condition."""
        old_cover = old_template.get_num_constraints_without_symmetric()
        old_cond_num = max(len(old_template.get_conditions()), 1)
        return ceil((old_cover / old_cond_num) * self._alpha)

    def saturate(self, init_t: Template, constraints: list) -> Template:
        """Saturate the template with new conditions.
        :param init_t: the initial template.
        :param constraints: the constraints to learn (including the already covered ones).
        :return: the saturated template (the initial template if no new conditions are found).
        """
        template = init_t
        while True:
            # Calculate the minimum number of constraints needed for this iteration
            constraints_needed = self.min_constraints_required(template)

            # Get current coverage metrics
            covered_constraints = template.get_num_constraints_without_symmetric()
            remaining_constraints = len(constraints_without_symmetric(constraints)) - covered_constraints
            total_constraints = len(constraints_without_symmetric(constraints))

            logging.debug(
                f"Saturating the template with a new condition. "
                f"Target: {constraints_needed} constraints minimum. "
                f"Before: {covered_constraints}/{total_constraints} covered, "
                f"{remaining_constraints} remaining."
            )

            # Check if our target exceeds the total available constraints
            if constraints_needed + covered_constraints > total_constraints:
                logging.debug(
                    f"Cannot continue: target constraints ({constraints_needed}) "
                    f"exceeds available constraints ({total_constraints})."
                )
                return template

            # Try to acquire a new template that covers more constraints
            enhanced_template = self.solving(template, [], constraints, constraints_needed)

            # If no better template found, we've reached saturation
            if enhanced_template is None:
                return template

            # Else, we have a better template and we keep saturating
            template = enhanced_template

    def solving(
        self, init_t: Template, chs: list[Characteristic], constraints: list, to_reach: int
    ) -> Optional[Template]:
        """Solve the template matching problem.
        :param init_t: The initial template.
        :param chs: The domain of the new characteristics.
        :param constraints: The list of constraints to learn (including those already learned).
        :param to_reach: Number of constraints to reach
        :return: Solved template (None if no template can reach the desired number of constraints before the timeout)
        """
        logging.debug("Starting solving from template matching.")
        assert to_reach >= 0, "to_reach must be greater than or equal to 0"
        ta = AddRule(
            initial_template=init_t,
            new_chars=chs,
            constraints_to_learn=constraints,
            log=self._log,
            conjunction=self._conjunction,
            solver=SolverOrTools(log=self._log),
        )
        ta.real_solve(to_reach, self._solver_timeout)
        t_conj = ta.get_template()
        if t_conj is None:
            logging.debug("No template found during solving.")
        return t_conj

    def add_attribute(self, init_t: Template, constraints: list) -> tuple[bool, Template]:
        """Find the next attribute to add to the template.
        :param init_t: The initial template.
        :param constraints: The list of constraints to learn.
        :return: A tuple containing a boolean indicating whether the attribute was added successfully and the updated template.
        """
        # Get initial template coverage and number of characteristics
        attribute_count = len(init_t.get_all_characteristics())

        # Calculate the minimum number of constraints to reach
        constraints_needed = self.min_constraints_required(init_t)

        # Get current coverage metrics
        already_covered_constraints = init_t.get_num_constraints_without_symmetric()
        for c in init_t.interpretation_constraints():
            assert c in constraints, f"Constraint {c} not in constraints"
        remaining_constraints = len(constraints_without_symmetric(constraints)) - already_covered_constraints
        total_constraints = len(constraints_without_symmetric(constraints))

        logging.debug(
            f"Adding attribute number {attribute_count + 1} to the template with a new condition. "
            f"Target: {constraints_needed} constraints minimum. "
            f"Before: {already_covered_constraints}/{total_constraints} covered, "
            f"{remaining_constraints} remaining."
        )

        # Check if our target exceeds the total available constraints
        if constraints_needed + already_covered_constraints > total_constraints:
            logging.debug(
                f"Cannot continue: target constraints ({constraints_needed}) "
                f"exceeds available constraints ({total_constraints})."
            )
            return False, init_t

        # Determine the domain size (we use an hard limit of the number of variables)
        variable_count = self._initial_template.num_variables()
        # variable_count = min(self._initial_template.num_variables(), 10)

        # Create a new characteristic
        new_characteristic = Characteristic(f"Char_{attribute_count + 1}", variable_count)

        # Attempt to acquire a new template with the new characteristic
        candidate_template = self.solving(init_t, [new_characteristic], constraints, constraints_needed)

        # If a new template is found, update the best template
        if candidate_template is not None:
            return True, candidate_template

        # The new template could not be found
        return False, init_t

    def learn(
        self, constraints_to_learn: list[tuple[list[int], Relation]], timeout_solver: int, train_example,
            verbose: bool = False
    ) -> Template:
        """Learn the template.
        :param constraints_to_learn: The list of constraints to learn.
        :param timeout_solver: The timeout for each solver call in seconds.
        :param train_example: The training example to use for learning.
        :param verbose: If True, the logs of the optimization process are displayed.
        :return: The learned template.
        """
        if len(constraints_to_learn) == len(set(constraints_to_learn)):
            logging.warning("Constraints to learn cannot be repeated (unexpected). We remove it.")
            constraints_to_learn = list(set(constraints_to_learn))

        # We need to convert the constraints to learn into a list of tuples
        self._constraints_to_cover: list[tuple[tuple[TemplateVariable, ...], Relation]] = []
        for sc, rel in constraints_to_learn:
            if len(set(sc)) == len(sc):
                self._constraints_to_cover.append(
                    (tuple([self._initial_template.get_variable_by_name(int(x)) for x in sc]), rel)
                )
            else:
                logging.debug(f"Scopes contains repeated variables: {sc} (relation: {rel}).")
                new_sc, new_rel = rel.relation_projection(sc)
                if new_rel.is_empty():
                    logging.debug("Relation is empty. Skipping.")
                else:
                    logging.debug(f"We have converted. New scope: {new_sc}, new relation: {new_rel}")
                    self._constraints_to_cover.append(
                        (tuple([self._initial_template.get_variable_by_name(int(x)) for x in new_sc]), new_rel)
                    )

        self._solver_timeout = timeout_solver
        t: Template = self._initial_template

        # We enumerate the characteristics to add to the template
        while True:
            # [1] We first add the new attribute to the template (and the first condition with it)
            new_attribute_added, t = self.add_attribute(t, self._constraints_to_cover)
            if not new_attribute_added:
                assert train_example, "Training example must (now) be provided."
                csp_template = convert_from_Template(t)
                recall = csp_template.accuracy(train_example, assert_positive_true=True)
                # If the recall is 1, we can stop the whole process and return the template
                if recall == 1:
                    logging.debug("No attribute can be added and the recall is 1. End of the process.")
                    return t
                # If the recall is not 1, we must update alpha
                self._alpha = 0.9 * self._alpha
                logging.debug(f"No attribute can be added and the recall is {recall}, updating alpha to {self._alpha}.")
            # [2] We saturate the template with all the new profitable conditions (or after updating alpha)
            t = self.saturate(t, self._constraints_to_cover)
