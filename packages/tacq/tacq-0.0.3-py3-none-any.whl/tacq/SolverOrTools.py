import logging
from typing import Optional

from ortools.sat.python import cp_model

from .abstractSolver import AbstractSolver, Status


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar], callback_function):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self._callback_function = callback_function
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        values = [self.Value(var) for var in self.__variables]
        self._callback_function(values)

    @property
    def solution_count(self) -> int:
        return self.__solution_count


class SolverOrTools(AbstractSolver):
    """Implements the interface with the OR-Tools solver."""

    def exactlyOne(self, indexes: list[int]):
        """Add a constraint to ensure exactly one variable is true."""
        self._model.AddExactlyOne([self._variables[name] for name in indexes])

    def __init__(self, log: bool = False):
        self._model: cp_model.CpModel = cp_model.CpModel()
        self._count_vars: int = 0
        self._count_constraints: int = 0
        self._variables: list[cp_model.IntVar] = []
        self._variables_additional: list[cp_model.IntVar] = []
        self._maximization_variables: list[cp_model.IntVar] = []
        self._solver: cp_model.CpSolver = cp_model.CpSolver()
        self._status: Status = Status.UNSOLVED
        self._log: bool = log
        self._max_dom_var: Optional[cp_model.IntVar] = None
        self._max_dom_value: Optional[int] = None
        self._suggest: list[cp_model.IntVar] = []

    def add_var(self, index, suggest=False):
        assert self._count_vars == index, f"Variable {index} is not the next one."
        bv = self._model.NewBoolVar("")
        self._variables.append(bv)
        if suggest:
            self._suggest.append(bv)
        self._count_vars += 1

    def add_fixed_var(self, index, val):
        assert self._count_vars == index, f"Variable {index} is not the next one."
        self._variables.append(self._model.NewConstant(val))
        self._count_vars += 1

    def add_int_var(self, index, min_val, max_val, new_var=False):
        assert self._count_vars == index, f"Variable {index} is not the next one."
        var = self._model.NewIntVar(min_val, max_val, "")
        self._variables.append(var)
        self._count_vars += 1
        if new_var:
            if self._max_dom_var is None:
                self._max_dom_var = self._model.NewIntVar(min_val, max_val, "max_dom")
                self._variables_additional.append(self._max_dom_var)
                self._max_dom_value = max_val
            assert max_val == self._max_dom_value
            self._model.Add(var <= self._max_dom_var)

    def new_constr_arithm(
            self,
            x: int,
            relation: str,
            y: int,
            otherwises: Optional[list[int]] = None,
            polarities: Optional[list[int]] = None,
    ):
        """
        Adds an arithmetic constraint with optional 'otherwise' conditions.
        :param x: Index of the first variable.
        :param relation: The arithmetic relation ("=", "!=", ">", "<", ">=", "<=", "=+1", "!=+1").
        :param y: Index of the second variable.
        :param otherwises: List of indices of 'otherwise' variables.
        :param polarities: List of polarities (1 for positive, 0 for negative) corresponding to 'otherwise' variables.
        """
        otherwises_vars = []
        if otherwises is not None:
            if polarities is None or len(otherwises) != len(polarities):
                raise ValueError(
                    "If otherwises is provided, polarities must also be provided and have the same length."
                )

            for i in range(len(otherwises)):
                if polarities[i] == 1:
                    otherwises_vars.append(self._variables[otherwises[i]])
                elif polarities[i] == -1:
                    otherwises_vars.append(self._variables[otherwises[i]].Not())
                else:
                    raise ValueError(f"Polarity at index {i} must be 0 or 1, but was {polarities[i]}.")

        # Create the main constraint as a boolean variable
        main_constraint = self._model.NewBoolVar("")
        self._variables_additional.append(main_constraint)
        if relation == "all":
            self._model.Add(main_constraint == 1)
        elif relation == "empty":
            self._model.Add(main_constraint == 0)
        elif relation == "=":
            self._model.Add(self._variables[x] == self._variables[y]).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] != self._variables[y]).OnlyEnforceIf(main_constraint.Not())
        elif relation == "!=":
            self._model.Add(self._variables[x] != self._variables[y]).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] == self._variables[y]).OnlyEnforceIf(main_constraint.Not())
        elif relation == ">":
            self._model.Add(self._variables[x] > self._variables[y]).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] <= self._variables[y]).OnlyEnforceIf(main_constraint.Not())
        elif relation == "<":
            self._model.Add(self._variables[x] < self._variables[y]).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] >= self._variables[y]).OnlyEnforceIf(main_constraint.Not())
        elif relation == ">=":
            self._model.Add(self._variables[x] >= self._variables[y]).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] < self._variables[y]).OnlyEnforceIf(main_constraint.Not())
        elif relation == "<=":
            self._model.Add(self._variables[x] <= self._variables[y]).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] > self._variables[y]).OnlyEnforceIf(main_constraint.Not())
        elif relation == "=+1":
            self._model.Add(self._variables[x] == self._variables[y] + 1).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] != self._variables[y] + 1).OnlyEnforceIf(main_constraint.Not())
        elif relation == "!=+1":
            self._model.Add(self._variables[x] != self._variables[y] + 1).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[x] == self._variables[y] + 1).OnlyEnforceIf(main_constraint.Not())
        elif relation == "00":
            self._model.Add(self._variables[x] + self._variables[y] == 0).OnlyEnforceIf(main_constraint)
        elif relation == "01":
            self._model.Add(self._variables[x] == 0).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[y] == 1).OnlyEnforceIf(main_constraint)
        elif relation == "10":
            self._model.Add(self._variables[x] == 1).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[y] == 0).OnlyEnforceIf(main_constraint)
        elif relation == "not00":
            self._model.Add(self._variables[x] + self._variables[y] > 0).OnlyEnforceIf(main_constraint)
        elif relation == "not01":
            self._model.Add(self._variables[x] != 0).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[y] != 1).OnlyEnforceIf(main_constraint)
        elif relation == "not10":
            self._model.Add(self._variables[x] != 1).OnlyEnforceIf(main_constraint)
            self._model.Add(self._variables[y] != 0).OnlyEnforceIf(main_constraint)
        else:
            raise ValueError(f"Relation {relation} is not implemented.")
        list_res = [main_constraint] + otherwises_vars
        if otherwises_vars:
            self._model.AddBoolOr(list_res)
        else:
            self._model.Add(main_constraint == 1)

    def num_vars(self):
        return self._count_vars

    def new_constr(self, indexes: list[int], polarities: list[int], weight: Optional[int] = None):
        # list_sorted = [indexes[i] * polarities[i] for i in range(len(indexes))]
        # list_sorted.sort()
        # if list_sorted in self._constrs:
        #     print(f"{list_sorted} Constraint already exists")
        #     return
        if weight is None:
            self._count_constraints += 1
            literals = []
            for i in range(0, len(indexes)):
                if polarities[i] == 1:
                    literals.append(self._variables[indexes[i]])
                elif polarities[i] == -1:
                    literals.append(self._variables[indexes[i]].Not())
                else:
                    assert False, "Not implemented yet"
            self._model.AddBoolOr(literals)
        elif weight > 0:
            assert weight == int(weight)
            self._count_constraints += 1
            literals = []
            for i in range(0, len(indexes)):
                if polarities[i] == 1:
                    literals.append(self._variables[indexes[i]])
                elif polarities[i] == -1:
                    literals.append(self._variables[indexes[i]].Not())
                else:
                    assert False, "Not implemented yet"
            self._count_vars += 1
            var_maximization = self._model.NewBoolVar(f"max_{self._count_vars}")
            self._variables_additional.append(var_maximization)
            for i in range(weight):
                self._maximization_variables.append(var_maximization)
            self._model.AddBoolOr(literals + [var_maximization.Not()])
        else:
            assert False, f"Weight {weight} is not implemented yet."

    def mustBeTrue(self, index):
        self._model.Add(self._variables[index] == 1)

    def mustBeFalse(self, index):
        self._model.Add(self._variables[index] == 0)

    def num_constr(self) -> int:
        return self._count_constraints

    def solve(
            self,
            timeout: Optional[int] = None,
            minimum=0,
            maximum: Optional[int] = None,
            optimize: bool = True,
            callback=None,
            show_solution_for_each_width: bool = False,
    ):
        # global toggle_temp
        assert optimize, "No optimize will be removed in the future."
        # Solver parameters
        self._solver.parameters.cp_model_presolve = True
        self._solver.parameters.num_search_workers = 8
        self._solver.parameters.symmetry_level = 4
        self._solver.parameters.max_memory_in_mb = 16000
        self._solver.parameters.log_search_progress = self._log
        logger = logging.getLogger("ortools")
        self._solver.log_callback = logger.debug  # (str) -> None
        self._solver.parameters.log_to_stdout = False
        if timeout is not None and timeout > 0:
            self._solver.parameters.max_time_in_seconds = timeout

        logging.debug(f"Minimum value: {minimum}")
        if minimum is not None and minimum > 0 and not show_solution_for_each_width:
            logging.warning(f"Adding constraint to reach at least {minimum}")
            self._model.Add(sum(self._maximization_variables) >= minimum)

        self._model.Maximize(sum(self._maximization_variables))
        if callback is None:
            status = self._solver.Solve(self._model)
        else:
            callback_object = SolutionPrinter(self._variables, callback)
            status = self._solver.SolveWithSolutionCallback(self._model, callback_object)

        # We now reduce the domain
        if self._max_dom_var is not None and self._max_dom_value is not None and self._max_dom_value > 0:
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                logging.debug("Hinting variables to speed up next search.")
                for var in self._variables:
                    self._model.AddHint(var, self._solver.Value(var))
                for var in self._variables_additional:
                    self._model.AddHint(var, self._solver.Value(var))
                f_x_max = sum([self._solver.Value(x) for x in self._maximization_variables])
                # self._solver.parameters.debug_crash_on_bad_hint = True
                self._model.clear_objective()
                assert self._max_dom_value is not None
                self._model.Maximize(
                    sum(self._maximization_variables) - self._max_dom_var * (f_x_max / self._max_dom_value)
                )
                if callback is None:
                    status = self._solver.Solve(self._model)
                else:
                    callback_object = SolutionPrinter(self._variables, callback)
                    status = self._solver.SolveWithSolutionCallback(self._model, callback_object)

            if show_solution_for_each_width and (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
                if sum([self._solver.Value(x) for x in self._maximization_variables]) < minimum:
                    status = cp_model.UNKNOWN

            if status == cp_model.OPTIMAL:
                self._status = Status.OPTIMAL
                logging.debug("Optimal solution found.")
            elif status == cp_model.FEASIBLE:
                self._status = Status.FEASIBLE
                logging.debug("Feasible solution found.")
            elif status == cp_model.INFEASIBLE:
                self._status = Status.INFEASIBLE
                logging.debug("Infeasible problem.")
            elif status == cp_model.MODEL_INVALID:
                self._status = Status.INVALID
                logging.debug("Invalid model.")
            elif status == cp_model.UNKNOWN:
                self._status = Status.UNKNOWN
                logging.warning("Unknown status.")
            else:
                logging.error("Other status.")

            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                logging.info(
                    f"The sum is {[sum([self._solver.Value(x) for x in self._maximization_variables])]} "
                    f"with the linear objective."
                )

        ###############
        # The next code is for research purposes only.
        # It is used to find the solution for each width.
        # Before setting _SolverOrTools_SHOW_THE_SOLUTION_FOR_EACH_WIDTH be sure to deactivate all optimization in the
        # acquisition process that is noted with a comment (SHOW_THE_SOLUTION_FOR_EACH_WIDTH).
        ###############
        if show_solution_for_each_width:
            if self._max_dom_var is None:
                logging.error("Not applicable. Skipping.")
                return
            # if not toggle_temp:
            #     logging.debug("Skipping the solution for each width.")
            #     toggle_temp = True
            #     return
            logging.debug("Looking for the solution for each width.")
            current_w: int = 0
            while current_w <= 30:
                temp_model = self._model.Clone()
                temp_solver = cp_model.CpSolver()
                temp_solver.parameters.cp_model_presolve = True
                temp_solver.parameters.num_search_workers = 8
                temp_solver.parameters.symmetry_level = 4
                temp_solver.parameters.max_memory_in_mb = 16000
                temp_solver.parameters.log_search_progress = self._log
                logger = logging.getLogger("ortools_width")
                temp_solver.log_callback = logger.debug  # (str) -> None
                temp_solver.parameters.log_to_stdout = False
                if timeout is not None and timeout > 0:
                    temp_solver.parameters.max_time_in_seconds = timeout
                temp_model.clear_hints()
                temp_model.add(self._max_dom_var <= current_w)
                temp_model.clear_objective()
                temp_model.Maximize(sum(self._maximization_variables))
                if callback is None:
                    status = temp_solver.Solve(temp_model)
                else:
                    callback_object = SolutionPrinter(self._variables, callback)
                    status = temp_solver.SolveWithSolutionCallback(temp_model, callback_object)
                if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                    logging.info(
                        f"The sum is {[sum([temp_solver.Value(x) for x in self._maximization_variables])]} "
                        f"with maximization objective and width lower than {current_w}"
                    )
                else:
                    logging.info(f"Solver status is {status}")
                current_w += 1

    def solution_available(self):
        return self._status == Status.OPTIMAL or self._status == Status.FEASIBLE

    def get_int_value(self, index: int) -> int:
        if self._status == Status.OPTIMAL or self._status == Status.FEASIBLE:
            return self._solver.Value(self._variables[index])
        else:
            logging.error(f"Solver status is {self._status}. Cannot get integer value. Returning 0.")
            return 0

    def get_value(self, index: int):
        if self._status == Status.OPTIMAL or self._status == Status.FEASIBLE:
            return self._solver.Value(self._variables[index]) == 1
        else:
            assert False, f"Solver status is {self._status}."
