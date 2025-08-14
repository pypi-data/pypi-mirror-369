from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class Status(Enum):
    UNSOLVED = 0
    UNKNOWN = 1
    INVALID = 2
    FEASIBLE = 3
    INFEASIBLE = 4
    OPTIMAL = 5


class AbstractSolver(ABC):
    """Abstract solver class: this class defines the interface for the solvers to be used
    in the acquisition functions (it is a wrapper around max-sat solvers)."""

    @abstractmethod
    def add_var(self, index: int):
        """Add a variable to the solver."""

    @abstractmethod
    def num_vars(self) -> int:
        """Return the number of variables in the solver."""

    @abstractmethod
    def num_constr(self) -> int:
        """Return the number of constraints in the solver."""

    @abstractmethod
    def new_constr(self, indexes: list[int], polarities: list[int], weight: Optional[float] = None):
        """Add a new constraint to the solver.
        :param indexes: list of indexes of the variables in the constraint
        :param polarities: list of polarities of the variables in the constraint
                           1 for positive, -1 for negative
        :param weight: weight of the constraint (if any). Some solvers do not support weights.

        For example to add the clause ((not 1) or 2 or 3) use indexes=[1, 2, 3], polarities=[-1, 1, 1]
        """

    @abstractmethod
    def exactlyOne(self, indexes: list[int]) -> None:
        """Add a constraint to ensure exactly one variable is true."""

    @abstractmethod
    def mustBeTrue(self, index: int) -> None:
        """Add a constraint to ensure a variable is true."""

    @abstractmethod
    def mustBeFalse(self, index: int) -> None:
        """Add a constraint to ensure a variable is false."""

    @abstractmethod
    def solve(
        self,
        timeout: Optional[int] = None,
        minimum: int = 0,
        maximum: Optional[int] = None,
        optimize: bool = True,
        callback=None,
    ):
        """Solve the problem.
        :param timeout: maximum time in seconds to wait for the optimal solution
        :param minimum: minimum weight of the soft clauses to be satisfied
        :param maximum: maximum weight of the soft clauses to be satisfied (to help the solver find a solution)
        :param optimize: if True, the solver will try to optimize the objective function (else it will just find a
                         solution satisfying the minimum weight)
        :param callback: callback function to be called when the solver finds a solution
        """

    @abstractmethod
    def solution_available(self) -> bool:
        """Check if a solution is available (perhaps not the optimal if the solver timed out)."""

    @abstractmethod
    def get_value(self, index: int) -> bool:
        """Get the value of a variable in the solution."""

    @abstractmethod
    def get_int_value(self, index: int) -> int:
        """Get the value of an integer variable in the solution."""

    @abstractmethod
    def new_constr_arithm(
        self,
        x: int,
        relation: str,
        y: int,
        otherwises: Optional[list[int]] = None,
        polarities: Optional[list[int]] = None,
    ) -> None:
        """
        Adds an arithmetic constraint with optional 'otherwise' variables.
        :param x: index of the first variable
        :param relation: relation between x and y (==, !=, <, <=, >, >=)
        :param y: index of the second variable
        :param otherwises: list of indexes of the variables in the 'otherwise' conditions
        :param polarities: list of polarities of the variables in the 'otherwise' conditions
        """

    @abstractmethod
    def add_int_var(self, index: int, min_val: int, max_val: int, new_var: bool) -> None:
        """
        Adds an integer variable to the solver.
        :param index: index of the variable
        :param min_val: minimum value of the variable
        :param max_val: maximum value of the variable
        :param new_var: if True, the variable is new, else it is already defined in the initial problem
        """

    @abstractmethod
    def add_fixed_var(self, index: int, val: int) -> None:
        """
        Adds a fixed variable to the solver.
        :param index: index of the variable
        :param val: value of the variable
        """
