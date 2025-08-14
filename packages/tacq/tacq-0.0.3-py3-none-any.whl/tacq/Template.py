import itertools
import logging
import math

from typing_extensions import Optional

from .Relation import Language, Relation


class Characteristic:
    def __init__(self, name: str, width: int, empty_value: bool = False, fixed: bool = False):
        assert width is None or width > 0, f"Width must be positive or None, not {width}"
        if width is None:
            logging.debug("A characteristic of width 0 has been created (it is supposed to be for fixed char).")
        assert width is None or width > 0, "Width must be positive or None"
        self._width = width
        self._fixed = fixed
        self._name = name
        self._empty_value = empty_value

    def is_fixed(self):
        return self._fixed

    def domain(self):
        if self._empty_value:
            return list(range(self._width)) + [-1]
        return list(range(self._width))

    def update_width(self, width: int):
        assert width > 0, "Width must be positive"
        self._width = width

    def __str__(self):
        return f"{self._name}"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self._name < other.name

    @property
    def name(self):
        return self._name


class TemplateVariable:
    def __init__(self, name: int, domain: list):
        assert isinstance(name, int), "Name must be a string"
        self._name: int = name
        self._characteristics = {}
        assert isinstance(domain, list), "Domain must be a list"
        self._domain = domain

    def get_name(self) -> int:
        return self._name

    def set_char(self, char: Characteristic, char_value: int) -> None:
        if not char.is_fixed() and char_value not in char.domain():
            raise ValueError(
                f'Value out of range for characteristic "{char}" (value={char_value} and domain={char.domain()}).'
            )
        self._characteristics[char] = char_value

    def get_char_value(self, char: Characteristic) -> int:
        if char not in self._characteristics:
            raise ValueError(f'Characteristic "{char}" not found for variable {self._name}.')
        return self._characteristics[char]

    def long_description(self):
        r_str = f"Variable {self._name} with characteristics :"
        for char, value in self._characteristics.items():
            r_str += f"  {char}={value}"
        return r_str

    def __str__(self):
        return f"{self._name}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        """Check if two variables are the same only with the name."""
        if not isinstance(other, TemplateVariable):
            return False
        return self._name == other._name

    def __copy__(self):
        tv = TemplateVariable(self._name, self._domain)
        for char, value in self._characteristics.items():
            tv.set_char(char, value)
        return tv


class Condition:
    def __init__(
            self,
            name: Optional[str],
            applied_relation: Relation,
            conditions: list[tuple[Relation, tuple[int, ...], tuple[Characteristic, ...]]],
    ):
        if name is None:
            self._name = "Condition without name"
        else:
            self._name: str = name
        assert isinstance(applied_relation, Relation), "Relation must be a Relation object"
        self._applied_relation: Relation = applied_relation
        self._triggers_list: list[Relation] = []
        self._indexes_list: list[tuple[int, ...]] = []
        self._chars_list: list[tuple[Characteristic, ...]] = []
        for (condition_relation, indexes, chars) in conditions:
            assert isinstance(condition_relation, Relation), "Relation must be a Relation object"
            self._triggers_list.append(condition_relation)
            assert isinstance(indexes, tuple), "Indexes must be a tuple"
            assert all([isinstance(index, int) for index in indexes]), "Indexes must be integers"
            self._indexes_list.append(indexes)
            assert isinstance(chars, tuple), "Characteristics must be a tuple"
            assert all([isinstance(char, Characteristic) for char in chars]), "Characteristics must be Characteristic"
            self._chars_list.append(chars)

    def get_applied_triggers_indexes_chars(
            self,
    ) -> tuple[Relation, list[tuple[Relation, tuple[int, ...], tuple[Characteristic, ...]]]]:
        return self._applied_relation, list(zip(self._triggers_list, self._indexes_list, self._chars_list))

    def get_triggers_indexes_chars(
            self,
    ) -> list[tuple[Relation, tuple[int, ...], tuple[Characteristic, ...]]]:
        return list(zip(self._triggers_list, self._indexes_list, self._chars_list))

    def get_name(self) -> str:
        return self._name

    def arity_csp(self):
        return self._applied_relation.get_arity()

    def arity_trigger(self):
        """:return: the arity of the trigger (number of characteristics of different variable read)"""
        full_scope = set()
        assert len(self._indexes_list) == len(self._chars_list), "Indexes and chars must have the same length"
        for i in range(len(self._indexes_list)):
            for ind, ch in zip(self._indexes_list[i], self._chars_list[i]):
                full_scope.add((ind, ch))
        return len(full_scope)

    def get_applied_relation(self) -> Relation:
        return self._applied_relation

    def triggered(self, scope: tuple[TemplateVariable, ...]) -> bool:
        assert len(scope) == self.arity_csp(), "Scope must have the same arity as the condition"
        for trigger, indexes, chars in zip(self._triggers_list, self._indexes_list, self._chars_list):
            values = [scope[index].get_char_value(char) for index, char in zip(indexes, chars)]
            if not trigger.accept(values):
                return False
        return True

    def long_description(self):
        r_str = f"Condition {self._name} with triggers :"
        for trigger, indexes, chars in zip(self._triggers_list, self._indexes_list, self._chars_list):
            r_str += f"\n- {trigger} on {indexes} with {chars}"
        return r_str

    @property
    def triggers_list(self):
        return self._triggers_list

    @property
    def indexes_list(self):
        return self._indexes_list

    @property
    def chars_list(self):
        return self._chars_list

    def __str__(self):
        return self._name


class Template:
    """Representation of a template."""

    def __init__(
            self,
            variables: list[int],
            domain: list[int],
            characteristics: list[Characteristic],
            condition_language: Language,
    ):
        """
        Create a template.
        :param variables: the variables
        :param domain: the domain of the variables
        :param characteristics: the characteristics
        :param condition_language: the language of the conditions
        """
        self._variables = {}
        self._domain = domain
        for var in variables:
            assert isinstance(var, int), "Variables must be integers"
            self._add_variable(var, domain)
        self._conditions: list[Condition] = []
        self._condition_language: Language = condition_language
        self._characteristics: list[Characteristic] = []
        for char in characteristics:
            self.add_characteristic(char)

    def _add_variable(self, var: int, domain: list):
        """
        Add a variable to the template.
        :param var: the variable
        :param domain: the domain of the variable
        :return: None
        """
        assert var not in self._variables, "Variable already in the template"
        self._variables[var] = TemplateVariable(var, domain)

    def add_characteristic(self, char: Characteristic) -> None:
        """:param char: the characteristic to add"""
        assert isinstance(char, Characteristic), "Characteristic must be a Characteristic object"
        assert char not in self._characteristics, "Characteristic already in the template"
        self._characteristics.append(char)

    def get_characteristic_by_name(self, name: str) -> Characteristic:
        """:return: the characteristic named name"""
        for char in self._characteristics:
            if char.name == name:
                return char
        raise ValueError(f"Characteristic {name} not found in the template.")

    def get_all_characteristics(self) -> list[Characteristic]:
        """:return: all characteristics"""
        return self._characteristics.copy()

    def get_all_characteristics_names(self) -> list:
        """:return: all characteristics name"""
        return [char.name for char in self._characteristics]

    def get_variable_by_name(self, x: int) -> TemplateVariable:
        """:return: the variable named x"""
        assert x in self._variables, "Variable not found"
        return self._variables[x]

    def get_variables(self) -> list[TemplateVariable]:
        """:return: all the variables"""
        variables = list(self._variables.values())
        assert all([isinstance(var, TemplateVariable) for var in variables]), "Variables must be TemplateVariable"
        return variables

    def get_domain(self) -> list:
        """:return: the domain"""
        return self._domain

    def num_variables(self) -> int:
        """:return: the number of variables"""
        return len(self._variables)

    def add_simple_condition(
            self,
            name: Optional[str],
            csp_rel: Relation,
            trigger: Relation,
            cond_scopes: tuple[tuple[int, ...], tuple[Characteristic, ...]],
    ):
        """
        Add a condition to the template.
        :param name: the name of the condition
        :param csp_rel: the relation to apply if the condition is triggered
        :param trigger: the trigger (in the language of condition) of the condition
        :param cond_scopes: the scopes of the condition (indexes, characteristics)
        :return: None
        """
        assert isinstance(csp_rel, Relation), "Relation must be a Relation object"
        assert trigger in self._condition_language, "Relation not in the language"
        indexes, chars = cond_scopes
        assert all([isinstance(char, Characteristic) for char in chars]), "Characteristics must be Characteristic"
        assert all([isinstance(index, int) for index in indexes]), "Indexes must be integers"
        cond = Condition(name, csp_rel, [(trigger, indexes, chars)])
        self._conditions.append(cond)

    def add_conjunction_condition(
            self,
            name: str,
            csp_rel: Relation,
            conditions: list[tuple[Relation, tuple[int, ...], tuple[Characteristic, ...]]],
    ):
        """
        Add a condition to the template.
        :param name: the name of the condition
        :param csp_rel: the relation to apply if the condition is triggered
        :param conditions: set of relation, indexes and characteristics to trigger the condition
        """
        self._conditions.append(Condition(name, csp_rel, conditions))

    def get_conditions(self) -> list[Condition]:
        """:return: all conditions"""
        return self._conditions

    def get_condition_language(self) -> Language:
        """:return: the language of the conditions"""
        return self._condition_language

    def get_csp_all_scopes(self, arity: int) -> list[tuple[TemplateVariable, ...]]:
        """:return: all combination of scopes"""
        assert isinstance(arity, int), "Arity must be an integer"
        assert arity > 0, "Arity must be positive"
        assert arity <= len(self.get_variables()), "Arity must be less than the number of variables"
        return list(itertools.permutations(self.get_variables(), arity))

    def interpretation_constraints(self) -> list[tuple[tuple[TemplateVariable, ...], Relation]]:
        """:return: all constraints in the interpretation of template (scope, relation)"""
        li = []
        for cond in self._conditions:
            for scope in self.get_csp_all_scopes(cond.arity_csp()):
                if cond.triggered(scope) and (scope, cond.get_applied_relation()) not in li:
                    assert len(scope) == cond.arity_csp(), "Scope and condition arity must be equal"
                    li.append((scope, cond.get_applied_relation()))
                    if cond.get_applied_relation().is_symmetric():
                        # We add the symmetric constraint
                        if (scope[::-1], cond.get_applied_relation()) not in li:
                            li.append((scope[::-1], cond.get_applied_relation()))
        return li

    def get_num_constraints_without_symmetric(self) -> int:
        """:return: number of constraints in the interpretation of template (scope, relation)"""
        li = []
        for cond in self._conditions:
            for scope in self.get_csp_all_scopes(cond.arity_csp()):
                if cond.triggered(scope) and (scope, cond.get_applied_relation()) not in li:
                    if cond.get_applied_relation().is_symmetric():
                        if (scope[::-1], cond.get_applied_relation()) not in li:
                            li.append((scope, cond.get_applied_relation()))
                    else:
                        li.append((scope, cond.get_applied_relation()))
        return len(li)

    def get_interpretation_(self) -> list[tuple[tuple[TemplateVariable, ...], Relation]]:
        """:return: all constraints in the interpretation of template (scope, relation)"""
        li = []
        for cond in self._conditions:
            for scope in self.get_csp_all_scopes(cond.arity_csp()):
                if cond.triggered(scope) and (scope, cond.get_applied_relation()) not in li:
                    assert len(scope) == cond.arity_csp(), "Scope and condition arity must be equal"
                    li.append((scope, cond.get_applied_relation()))
                    if cond.get_applied_relation().is_symmetric():
                        # We add the symmetric constraint
                        if (scope[::-1], cond.get_applied_relation()) not in li:
                            li.append((scope[::-1], cond.get_applied_relation()))
        return li

    def interpretation_constraints_for_specific_cond(
            self, cond: Condition, sym: bool = True
    ) -> list[tuple[tuple[TemplateVariable, ...], Relation]]:
        """:return: all constraints in the interpretation of template (scope, relation)"""
        assert cond in self._conditions, "Condition not in the template"
        li = []
        for scope in self.get_csp_all_scopes(cond.arity_csp()):
            if cond.triggered(scope) and (scope, cond.get_applied_relation()) not in li:
                assert len(scope) == cond.arity_csp(), "Scope and condition arity must be equal"
                li.append((scope, cond.get_applied_relation()))
                if sym and cond.get_applied_relation().is_symmetric():
                    # We add the symmetric constraint
                    li.append((scope[::-1], cond.get_applied_relation()))
        return li

    def size(self) -> int:
        char_size: int = 0
        char: Characteristic
        for char in self._characteristics:
            char_size += math.ceil(math.log2(len(char.domain()))) * len(self._variables)
        cond_size: int = 0
        rel_size: int = 0
        cond: Condition
        for cond in self._conditions:
            cond_size += cond.arity_trigger() * math.ceil(
                math.log2(cond.arity_csp()) + math.log2(len(self._characteristics))
            )
            rel_size += math.ceil(math.log2(cond.get_applied_relation().size_to_encode())) + math.ceil(
                math.log2(len(self._condition_language))
            )
        return char_size + cond_size + rel_size

    def min_size_if_we_add(
            self,
            chars: list[Characteristic],
            conds_arity: list[int],
            relations_to_learn: list[Relation],
    ) -> float:
        initial_size = self.size()
        min_arity_relations_to_learn = min([rel.get_arity() for rel in relations_to_learn])
        min_size_relation = min([rel.size_to_encode() for rel in relations_to_learn])
        added_size = 0
        for char in chars:
            added_size += math.ceil(math.log2(len(char.domain()))) * len(self._variables)
        for arity in conds_arity:
            added_size += arity * math.ceil(math.log2(min_arity_relations_to_learn)) + math.log2(
                len(self._characteristics) + len(chars)
            )
            added_size += math.ceil(math.log2(min_size_relation)) + math.ceil(math.log2(len(self._condition_language)))
        return initial_size + added_size

    def contain_empty_char_value(self) -> bool:
        for var in self.get_variables():
            for char in self.get_all_characteristics():
                if var.get_char_value(char) == -1:
                    return True
        return False

    def copy(self) -> "Template":
        t = Template(
            [var.get_name() for var in self.get_variables()],
            self.get_domain(),
            self.get_all_characteristics(),
            self.get_condition_language(),
        )
        for char in self.get_all_characteristics():
            for var in self.get_variables():
                t.get_variable_by_name(var.get_name()).set_char(char, var.get_char_value(char))
        cond: Condition
        for cond in self.get_conditions():
            conditions = []
            for trigger, indexes, chars in zip(cond.triggers_list, cond.indexes_list, cond.chars_list):
                conditions.append((trigger, tuple(indexes), tuple(chars)))
            t.add_conjunction_condition(cond.get_name(), cond.get_applied_relation(), conditions)
        return t

    def __str__(self):
        r_str = (
            f"Template with {self.num_variables()} variables, {len(self.get_all_characteristics())} characteristics"
            f" and {len(self._conditions)} conditions. Its interpretation has "
            f"{len(self.interpretation_constraints())} \n."
        )
        for var in self.get_variables():
            r_str += var.long_description() + "\n"
        for cond in self.get_conditions():
            r_str += cond.long_description() + "\n"
        return r_str
