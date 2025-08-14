import datetime
import logging
import math
from itertools import permutations, product
from typing import Optional

from .abstractSolver import AbstractSolver
from .Relation import Relation
from .SolverOrTools import SolverOrTools
from .Template import Characteristic, Template, TemplateVariable


class AddRule:
    def __init__(
            self,
            initial_template: Template,
            new_chars: list[Characteristic],
            constraints_to_learn: list[tuple[list[TemplateVariable], Relation]],
            timeout: Optional[datetime.datetime] = None,
            log=False,
            solver: Optional[AbstractSolver] = None,
            conjunction: bool = True,
    ):
        """Constructor of the TemplateAcquisition class.
        :param initial_template: The initial template to extend.
        :param new_chars: The new characteristics to use as a list of Characteristic.
        :param constraints_to_learn: The constraints to learn as a list of tuples (scope, relation)
         (including already learned constraints).
        :param timeout: The timeout for the acquisition as a datetime.datetime.
        :param log: True to display solver logs, False otherwise.
        :param solver: The solver to use (must implement method in AbstractSolver).
        """
        # This flag controls whether the solver should print the solution found for each width possible
        # from 0 to the maximum width.
        self._SHOW_THE_SOLUTION_FOR_EACH_WIDTH: bool = False

        self._initial_template: Template = initial_template
        self._new_chars: list[Characteristic] = new_chars
        self._all_chars: list[Characteristic] = initial_template.get_all_characteristics() + new_chars
        self._initial_constraints = self._initial_template.interpretation_constraints()
        self._constraints_to_learn: list[tuple[list[TemplateVariable], Relation]] = list(
            set(constraints_to_learn).difference(self._initial_constraints)
        )
        assert len(self._constraints_to_learn) > 0, "No constraints to learn."
        self._timeout: Optional[datetime.datetime] = timeout
        self._solver: AbstractSolver = solver if solver is not None else SolverOrTools(log=log)
        self._conjunction: bool = conjunction
        # Check if conjunction can be used (is there at least two attributes)
        if len(self._all_chars) < 2:
            logging.debug("Conjunction is disabled because there are less than two attributes.")
            self._conjunction = False
        self._variables: list[TemplateVariable] = initial_template.get_variables()

        # Dictionary to store the variables of the solver
        self._count_vars = 0
        self._dict_ch: dict[tuple[str, int], int] = {}
        self._dict_rel: dict = {}
        self._dict_rc_1: dict = {}
        self._dict_pc_1: dict = {}
        self._dict_c: dict = {}

        if self._conjunction:
            self._dict_rc_2, self._dict_pc_2 = {}, {}

        logging.debug(f"[~0%] Adding attributes variables (time: {datetime.datetime.now()}).")
        self._characteristics()
        logging.debug(f"[~3%] New conditions variables and constraints (time: {datetime.datetime.now()}).")
        self._new_condition()
        logging.debug(f"[~7%] Keeping old conditions constraints (time: {datetime.datetime.now()}).")
        self._old_conditions()
        logging.debug(f"[~12%] Template must learn only candidates contraints (time: {datetime.datetime.now()}).")
        self._constraints_not_learned()
        logging.debug(f"[~70%] Template want learn candidates contraints (time: {datetime.datetime.now()}).")
        self._constraints_learned()
        logging.debug(f"[~99%] Setting covering objective (time: {datetime.datetime.now()}).")
        already_counted = set()
        for csp_c, csp_r in self._constraints_to_learn:
            if csp_r.is_symmetric() and (csp_c[::-1], csp_r) in self._constraints_to_learn:
                if (csp_c, csp_r) not in already_counted:
                    self._solver.new_constr([self._dict_c[csp_c, csp_r], self._dict_c[csp_c[::-1], csp_r]], [1, 1], 1)
                    already_counted.add((csp_c, csp_r))
                    already_counted.add((csp_c[::-1], csp_r))
            else:
                logging.debug(f"Adding constraint {csp_c} (asymmetric {csp_r})")
                self._solver.new_constr([self._dict_c[csp_c, csp_r]], [1], 1)
        logging.debug("[100%] Ready to solve.")

    def _characteristics(self):
        for char in self._all_chars:
            if not char.is_fixed():
                for v in self._variables:
                    self._dict_ch[char.name, v.get_name()] = self._count_vars
                    if char in self._new_chars and not char.is_fixed():
                        self._solver.add_int_var(
                            self._count_vars, min_val=0, max_val=len(char.domain()) - 1, new_var=True
                        )
                    else:
                        self._solver.add_int_var(
                            self._count_vars, min_val=0, max_val=len(char.domain()) - 1, new_var=False
                        )
                    self._count_vars += 1
            else:
                for v in self._variables:
                    self._dict_ch[char.name, v.get_name()] = self._count_vars
                    value = v.get_char_value(char)
                    self._solver.add_fixed_var(self._count_vars, val=value)
                    self._count_vars += 1

    def _new_condition(self):
        #######################################
        # The relation in the CSP`
        clause: list[int] = []
        for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
            self._dict_rel[csp_r] = self._count_vars
            self._solver.add_var(self._count_vars)
            clause.append(self._count_vars)
            self._count_vars += 1
        self._solver.exactlyOne(clause)
        # FIRST PART OF THE CONDITION
        # The relation of the condition
        # We only consider arity 2 but the conjunction allow finally to consider more than arity 2
        clause: list[int] = []
        for rel_cond in self.all_relations(2):
            self._dict_rc_1[rel_cond] = self._count_vars
            self._solver.add_var(self._count_vars)
            clause.append(self._count_vars)
            self._count_vars += 1
        self._solver.exactlyOne(clause)
        # The position of the trigger
        clause: list[int] = []
        max_csp_arity = max([csp_r.get_arity() for (_, csp_r) in self._constraints_to_learn])
        for pos in self.all_positions(2, max_csp_arity, False):
            self._dict_pc_1[pos] = self._count_vars
            self._solver.add_var(self._count_vars)
            clause.append(self._count_vars)
            self._count_vars += 1
        self._solver.exactlyOne(clause)
        # We make sure that the positions is coherent with the arity of the constraints
        for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
            for char, indexes in self.all_positions(2, max_csp_arity, False):
                if not all([i < csp_r.get_arity() for i in indexes]):
                    self._solver.new_constr([self._dict_rel[csp_r], self._dict_pc_1[(char, indexes)]], [-1, -1])
        # SECOND PART OF THE CONDITION
        if self._conjunction:
            # The relation of the trigger
            clause: list[int] = []
            for rel_cond in self.all_relations(2):
                self._dict_rc_2[rel_cond] = self._count_vars
                if rel_cond.short_name() == "all":
                    self._solver.add_var(self._count_vars)
                    # If the first part is universal, we force the universal relations for the second part
                    # This doesn't change the solution at all
                    self._solver.new_constr([self._dict_rc_1[rel_cond], self._dict_rc_2[rel_cond]], [-1, 1])
                else:
                    self._solver.add_var(self._count_vars)
                clause.append(self._count_vars)
                self._count_vars += 1
            self._solver.exactlyOne(clause)
            # The position of the trigger
            clause: list[int] = []
            max_csp_arity = max([csp_r.get_arity() for (_, csp_r) in self._constraints_to_learn])
            for pos in self.all_positions(2, max_csp_arity, True):
                self._dict_pc_2[pos] = self._count_vars
                self._solver.add_var(self._count_vars)
                clause.append(self._count_vars)
                self._count_vars += 1
                # We force the position to be different of the first (WARN: this small opt depends on the language)
                if pos in self.all_positions(2, max_csp_arity, False):
                    self._solver.new_constr([self._dict_pc_1[pos], self._dict_pc_2[pos]], [-1, -1])
            # We make sure that the positions is coherent with the arity of the constraints
            for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
                for char, indexes in self.all_positions(2, max_csp_arity, True):
                    if not all([i < csp_r.get_arity() for i in indexes]):
                        self._solver.new_constr([self._dict_rel[csp_r], self._dict_pc_2[(char, indexes)]], [-1, -1])
            self._solver.exactlyOne(clause)

    def _forbidden_tuples(
            self, cond_rel: Relation, csp_c: tuple[TemplateVariable], indexes: tuple[int], chars: tuple[Characteristic]
    ) -> list[list[int]]:
        li = []
        for i in range(len(indexes)):
            if chars[i].is_fixed():
                li.append(
                    [self._initial_template.get_variable_by_name(csp_c[indexes[i]].get_name()).get_char_value(chars[i])]
                )
            else:
                li.append(chars[i].domain())
        return cond_rel.forbidden_tuples(li)

    def _old_conditions(self):
        for c in self._initial_template.get_conditions():
            cond_constraints = [
                s for (s, _) in self._initial_template.interpretation_constraints_for_specific_cond(c, False)
            ]
            for csp_c in self._csp_scopes(c.arity_csp()):
                if csp_c in cond_constraints:
                    for cond_rel, indexes, chars in c.get_triggers_indexes_chars():
                        self._solver.new_constr_arithm(
                            self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                            cond_rel.short_name(),
                            self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                        )
                else:
                    if len(c.get_triggers_indexes_chars()) == 1:
                        cond_rel, indexes, chars = c.get_triggers_indexes_chars()[0]
                        self._solver.new_constr_arithm(
                            self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                            cond_rel.opposite_short_name(),
                            self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                        )
                    else:
                        self._solver.add_var(self._count_vars)
                        temp_var = self._count_vars  # We create a temporary variable to link the conjunction
                        self._count_vars += 1
                        cond_rel, indexes, chars = c.get_triggers_indexes_chars()[0]
                        self._solver.new_constr_arithm(
                            self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                            cond_rel.opposite_short_name(),
                            self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                            [temp_var],
                            [1],
                        )
                        cond_rel_2, indexes_2, chars_2 = c.get_triggers_indexes_chars()[1]
                        self._solver.new_constr_arithm(
                            self._dict_ch[chars_2[0].name, csp_c[indexes_2[0]].get_name()],
                            cond_rel_2.opposite_short_name(),
                            self._dict_ch[chars_2[1].name, csp_c[indexes_2[1]].get_name()],
                            [temp_var],
                            [-1],
                        )

    def _constraints_not_learned(self):
        if self._conjunction:
            for csp_c, csp_r in self._constraints_forbidden():
                self._solver.add_var(self._count_vars)
                temp_var = self._count_vars  # We create a temporary variable to link the conjunction
                self._count_vars += 1
                for cond_rel, chars, indexes in self.all_positions_relation_eligible(csp_r.get_arity(), False):
                    self._solver.new_constr_arithm(
                        self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                        cond_rel.opposite_short_name(),
                        self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                        [self._dict_rel[csp_r], self._dict_rc_1[cond_rel], self._dict_pc_1[(chars, indexes)], temp_var],
                        [-1, -1, -1, 1],
                    )
                for cond_rel, chars, indexes in self.all_positions_relation_eligible(csp_r.get_arity(), True):
                    self._solver.new_constr_arithm(
                        self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                        cond_rel.opposite_short_name(),
                        self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                        [self._dict_rel[csp_r], self._dict_rc_2[cond_rel], self._dict_pc_2[(chars, indexes)], temp_var],
                        [-1, -1, -1, -1],
                    )
        else:
            for csp_c, csp_r in self._constraints_forbidden():
                for cond_rel, chars, indexes in self.all_positions_relation_eligible(csp_r.get_arity(), False):
                    self._solver.new_constr_arithm(
                        self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                        cond_rel.opposite_short_name(),
                        self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                        otherwises=[
                            self._dict_rel[csp_r],
                            self._dict_rc_1[cond_rel],
                            self._dict_pc_1[(chars, indexes)],
                        ],
                        polarities=[-1, -1, -1],
                    )

    def _constraints_learned(self):
        for csp_c, csp_r in self._constraints_to_learn:
            self._dict_c[csp_c, csp_r] = self._count_vars
            self._solver.add_var(self._count_vars)
            self._count_vars += 1
            self._solver.new_constr([self._dict_rel[csp_r], self._dict_c[csp_c, csp_r]], [1, -1])
            for cond_rel, chars, indexes in self.all_positions_relation_eligible(csp_r.get_arity(), False):
                self._solver.new_constr_arithm(
                    self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                    cond_rel.short_name(),
                    self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                    [
                        self._dict_rel[csp_r],
                        self._dict_rc_1[cond_rel],
                        self._dict_pc_1[(chars, indexes)],
                        self._dict_c[csp_c, csp_r],
                    ],
                    [-1, -1, -1, -1],
                )
            if self._conjunction:
                for cond_rel, chars, indexes in self.all_positions_relation_eligible(csp_r.get_arity(), True):
                    self._solver.new_constr_arithm(
                        self._dict_ch[chars[0].name, csp_c[indexes[0]].get_name()],
                        cond_rel.short_name(),
                        self._dict_ch[chars[1].name, csp_c[indexes[1]].get_name()],
                        [
                            self._dict_rel[csp_r],
                            self._dict_rc_2[cond_rel],
                            self._dict_pc_2[(chars, indexes)],
                            self._dict_c[csp_c, csp_r],
                        ],
                        [-1, -1, -1, -1],
                    )

    def all_relations(self, arity) -> list[Relation]:
        assert arity == 2, "Only arity 2 is supported for now."
        return self._initial_template.get_condition_language().all_relations()

    def all_positions(
            self, arity_cond: int, arity_csp: int, conj: bool
    ) -> list[tuple[tuple[Characteristic, ...], tuple[int, ...]]]:
        li = []
        new_chars_or_all = self._all_chars if self._new_chars == [] else self._new_chars
        for chars in product(self._all_chars, repeat=arity_cond):
            for indexes in product(range(0, arity_csp), repeat=arity_cond):
                # If it does not contain twice the same (ind, char) (WARN: this small opt depends on the language)
                if len(indexes) == len(set(zip(chars, indexes))):
                    # The position must start with 0 or be a conjunction
                    if conj or indexes[0] == 0 or self._SHOW_THE_SOLUTION_FOR_EACH_WIDTH:
                        # If the scope contain at least one new characteristics (if there are new characteristics)
                        if conj or any([c in new_chars_or_all for c in chars]):
                            # If there is the same position in different order, we remove it
                            if set(zip(chars, indexes)) not in [set(zip(c, v)) for (c, v) in li]:
                                li.append((chars, indexes))
        return li

    def all_positions_relation_eligible(
            self, arity_csp: int, conj: bool
    ) -> list[tuple[Relation, tuple[Characteristic, ...], tuple[int, ...]]]:
        """Return all the candidates positions."""
        listr = []
        if conj:
            for cond_rel in self.all_relations(2):
                for chars, indexes in self.all_positions(2, arity_csp, True):
                    listr.append((cond_rel, chars, indexes))
        else:
            for cond_rel in self.all_relations(2):
                for chars, indexes in self.all_positions(2, arity_csp, False):
                    listr.append((cond_rel, chars, indexes))
        return listr

    def _csp_scopes(self, arity: int) -> list[tuple[TemplateVariable, ...]]:
        return list(permutations(self._variables, r=arity))

    def _constraints_forbidden(self) -> list[tuple[tuple[TemplateVariable, ...], Relation]]:
        listr = []
        for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
            arity = csp_r.get_arity()
            for csp_c in self._csp_scopes(arity):
                if (csp_c, csp_r) not in self._constraints_to_learn and (csp_c, csp_r) not in self._initial_constraints:
                    listr.append((csp_c, csp_r))
        return listr

    def real_solve(self, min_reach: int, timeout: int):
        """Solve the CSP to learn the constraints.
        :param min_reach: the minimum number of constraints to reach (NOT including already learned constraints)
        :param timeout: the timeout for the acquisition in seconds
        """
        if self._timeout is None:
            timeout_s = timeout
        else:
            timeout_s = min(math.ceil((self._timeout - datetime.datetime.now()).total_seconds()), timeout)
        to_reach: int = min_reach
        assert to_reach >= 0, "min_reach must be non-negative"
        if self._SHOW_THE_SOLUTION_FOR_EACH_WIDTH:
            self._solver.solve(
                minimum=to_reach,
                maximum=len(self._constraints_to_learn),
                timeout=timeout_s,
                callback=self.solver_callback,
            )
        else:
            self._solver.solve(
                minimum=to_reach,
                maximum=len(self._constraints_to_learn),
                timeout=timeout_s,
                callback=self.solver_callback,
            )

    def get_template(self, result_queue=None) -> Optional[Template]:
        """:return: the template learned or None if no solution is available"""
        if not self._solver.solution_available():
            if result_queue is not None:
                result_queue.put(None)
            return None
        t: Template = self._initial_template.copy()
        for char in self._all_chars:
            if char in self._new_chars:
                real_dom: int = 0
                for var in self._variables:
                    value = self._solver.get_int_value(self._dict_ch[char.name, var.get_name()])
                    real_dom = max(real_dom, value)
                char.update_width(real_dom + 1)
                logging.debug(f"New domain for {char.name}: {real_dom + 1}")
                t.add_characteristic(char)
            if not char.is_fixed():
                for v in self._variables:
                    value = self._solver.get_int_value(self._dict_ch[char.name, v.get_name()])
                    t.get_variable_by_name(v.get_name()).set_char(char, value)
        csp_rel_used: Optional[Relation] = None
        rel_cond_used_1: Optional[Relation] = None
        chars_used_1: Optional[tuple[Characteristic, ...]] = None
        indexes_used_1: Optional[tuple[int, ...]] = None
        rel_cond_used_2: Optional[Relation] = None
        chars_used_2: Optional[tuple[Characteristic, ...]] = None
        indexes_used_2: Optional[tuple[int, ...]] = None
        for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
            if self._solver.get_value(self._dict_rel[csp_r]) == 1:
                csp_rel_used = csp_r
                break
        assert csp_rel_used is not None
        for rel_cond in self.all_relations(2):
            if self._solver.get_value(self._dict_rc_1[rel_cond]) == 1:
                rel_cond_used_1 = rel_cond
                break
        for chars, indexes in self.all_positions(2, csp_rel_used.get_arity(), False):
            if self._solver.get_value(self._dict_pc_1[(chars, indexes)]) == 1:
                chars_used_1, indexes_used_1 = chars, indexes
                break
        if self._conjunction:
            for rel_cond in self.all_relations(2):
                if self._solver.get_value(self._dict_rc_2[rel_cond]) == 1:
                    rel_cond_used_2 = rel_cond
                    break
            for chars, indexes in self.all_positions(2, csp_rel_used.get_arity(), True):
                if self._solver.get_value(self._dict_pc_2[(chars, indexes)]) == 1:
                    chars_used_2, indexes_used_2 = chars, indexes
                    break
        assert (
                csp_rel_used is not None
                and rel_cond_used_1 is not None
                and chars_used_1 is not None
                and indexes_used_1 is not None
        ), f"csp_rel={csp_rel_used}, rel_cond={rel_cond_used_1}, pos=({indexes_used_1}, {chars_used_1}) cannot be None"
        if self._conjunction:
            assert rel_cond_used_2 is not None and indexes_used_2 is not None and chars_used_2 is not None
            str_cond = (
                f"{csp_rel_used}, {rel_cond_used_1}, ({indexes_used_1}, {chars_used_1}), "
                f"{rel_cond_used_2}, ({indexes_used_2}, {chars_used_2})"
            )
            t.add_conjunction_condition(
                str_cond,
                csp_rel_used,
                [(rel_cond_used_1, indexes_used_1, chars_used_1), (rel_cond_used_2, indexes_used_2, chars_used_2)],
            )
        else:
            str_cond = f"{csp_rel_used}, {rel_cond_used_1}, ({indexes_used_1}, {chars_used_1})"
            t.add_simple_condition(str_cond, csp_rel_used, rel_cond_used_1, (indexes_used_1, chars_used_1))
        logging.debug(t)
        if result_queue is not None:
            result_queue.put(t)
        return t

    def solver_callback(self, variables_values: list[int]) -> None:
        """Callback function for the solver.
        :param variables_values: the values of the variables of the solver
        """
        csp_rel_used: Optional[Relation] = None
        rel_cond_used_1: Optional[Relation, ...] = None
        chars_used_1: Optional[tuple[Characteristic, ...]] = None
        indexes_used_1: Optional[tuple[int, ...]] = None
        rel_cond_used_2: Optional[Relation] = None
        chars_used_2: Optional[tuple[Characteristic, ...]] = None
        indexes_used_2: Optional[tuple[int, ...]] = None
        for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
            if variables_values[self._dict_rel[csp_r]]:
                csp_rel_used = csp_r
                break
        assert csp_rel_used is not None
        for rel_cond in self.all_relations(2):
            if variables_values[self._dict_rc_1[rel_cond]]:
                rel_cond_used_1 = rel_cond
                break
        for chars, indexes in self.all_positions(2, csp_rel_used.get_arity(), False):
            if variables_values[self._dict_pc_1[(chars, indexes)]]:
                chars_used_1, indexes_used_1 = chars, indexes
                break
        logging.debug(f"The condition learned is {csp_rel_used}")
        logging.debug(f"{rel_cond_used_1}, ({indexes_used_1}, {chars_used_1})")
        if self._conjunction:
            for rel_cond in self.all_relations(2):
                if variables_values[self._dict_rc_2[rel_cond]]:
                    rel_cond_used_2 = rel_cond
                    break
            for chars, indexes in self.all_positions(2, csp_rel_used.get_arity(), True):
                if variables_values[self._dict_pc_2[(chars, indexes)]]:
                    chars_used_2, indexes_used_2 = chars, indexes
                    break
            logging.debug(f"{rel_cond_used_2}, ({indexes_used_2}, {chars_used_2})")
        count_c = 0
        csp_r_learned = None
        for csp_r in set([rel for (_, rel) in self._constraints_to_learn]):
            if variables_values[self._dict_rel[csp_r]]:
                csp_r_learned = csp_r
        list_csp_c = []
        for csp_c, csp_r in self._constraints_to_learn:
            if csp_r.is_symmetric() and (csp_c[::-1], csp_r) in self._constraints_to_learn:
                if variables_values[self._dict_c[csp_c, csp_r]] or variables_values[self._dict_c[csp_c[::-1], csp_r]]:
                    csp_r_learned = csp_r
                    list_csp_c.append(csp_c)
                    count_c += 1
            else:
                if variables_values[self._dict_c[csp_c, csp_r]]:
                    csp_r_learned = csp_r
                    list_csp_c.append(csp_c)
                    count_c += 1

        list_var_attr: dict[int, list[int]] = {x.get_name(): [] for x in self._variables}
        for char in self._all_chars:
            if char in self._new_chars:
                width: int = 0
                for var in self._variables:
                    value = variables_values[self._dict_ch[char.name, var.get_name()]]
                    width = max(width, value)
                logging.info(f"Attribute {char} has width {width}")
            if not char.is_fixed():
                for v in self._variables:
                    value = variables_values[self._dict_ch[char.name, v.get_name()]]
                    list_var_attr[v.get_name()].append(value)
        logging.debug(f"Attribute values: {list_var_attr}")
        logging.debug(f"CSP Relation learned: {csp_r_learned}")
        logging.debug(f"CSP Scopes learned: {list_csp_c}")
        logging.debug(f"Number of constraints learned: {count_c}")

    def __str__(self) -> str:
        return ""
