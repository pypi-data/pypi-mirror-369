import itertools
import logging
from math import log2
from typing import Optional


class Relation:
    def __init__(self, relation_descr: Optional[str] = None, accepted_tuples: Optional[list[list[int]]] = None):
        self._relation_descr: Optional[str] = None
        self._accepted_tuples: Optional[set[tuple[int, ...]]] = None
        self._arity: int = 2
        if relation_descr is not None and accepted_tuples is None:
            self._relation_descr = relation_descr
        elif relation_descr is None and accepted_tuples is not None:
            self._accepted_tuples = set()
            if not accepted_tuples:
                logging.warning("Empty relation provided")
                self._arity = 0
            else:
                self._arity = len(accepted_tuples[0])
            for e in accepted_tuples:
                self._accepted_tuples.add(tuple(e))
        else:
            raise ValueError("Either relation description or accepted tuples must be provided but not both.")

    def accept(self, values: list[int]) -> bool:
        for v in values:
            if v == -1:  # -1 is a special value for missing values (it is not used with the current implementation)
                logging.warning("Missing value (-1) in relation acceptance check.")
                return False
        if self._relation_descr is not None:
            if self._relation_descr == "all":
                return True
            elif self._relation_descr == "empty":
                return False
            elif self._relation_descr == "a==b":
                return values[0] == values[1]
            elif self._relation_descr == "a!=b":
                return values[0] != values[1]
            elif self._relation_descr == "a<b":
                return values[0] < values[1]
            elif self._relation_descr == "a>b":
                return values[0] > values[1]
            elif self._relation_descr == "a>=b":
                return values[0] >= values[1]
            elif self._relation_descr == "a<=b":
                return values[0] <= values[1]
            elif self._relation_descr == "a=b+1":
                return values[0] == values[1] + 1
            elif self._relation_descr == "a!=b+1":
                return values[0] != values[1] + 1
            else:
                logging.error(f"Unknown relation description: {self._relation_descr}. Returning False.")
                return False
        elif self._accepted_tuples is not None:
            return tuple(values) not in self._accepted_tuples
        else:
            logging.error("No accepted tuples provided. (This is unexpected.)")
            return False

    short_name_dict = {
        "all": "all",
        "empty": "empty",
        "a==b": "=",
        "a!=b": "!=",
        "a<b": "<",
        "a>b": ">",
        "a>=b": ">=",
        "a<=b": "<=",
        "a=b+1": "=+1",
        "a!=b+1": "!=+1",
    }

    def short_name(self) -> str:
        assert self._relation_descr is not None
        return self.short_name_dict[self._relation_descr]

    opposite_short_name_dict = {
        "all": "empty",
        "empty": "all",
        "a==b": "!=",
        "a!=b": "=",
        "a<b": ">=",
        "a>b": "<=",
        "a>=b": "<",
        "a<=b": ">",
        "a=b+1": "!=+1",
        "a!=b+1": "=+1",
    }

    def opposite_short_name(self):
        assert self._relation_descr is not None
        return self.opposite_short_name_dict[self._relation_descr]

    def forbidden_tuples(self, domains: Optional[list[list[int]]] = None) -> list:
        assert domains is not None, "The domain must be provided to generate the forbidden tuples."
        assert len(domains) == self.get_arity(), "The domain must have the same size as the arity of the relation."
        if self._accepted_tuples is not None:
            return [t for t in itertools.product(domains, repeat=self.get_arity()) if t not in self._accepted_tuples]
        else:
            forbidden_tuples = []
            for i in itertools.product(*domains):
                if not self.accept(list(i)):
                    forbidden_tuples.append(list(i))
            return forbidden_tuples

    def __str__(self):
        return self._relation_descr if self._relation_descr is not None else str(self._accepted_tuples)

    def __repr__(self):
        return self.__str__()

    def get_arity(self):
        if self._relation_descr is not None:
            if self._relation_descr in [
                "all",
                "empty",
                "a==b",
                "a!=b",
                "a<b",
                "a>b",
                "a>=b",
                "a<=b",
                "a=b+1",
                "a!=b+1",
            ]:
                return 2
            else:
                assert False, f"The relation {self._relation_descr} is not implemented yet (this error is unexpected)."
        else:
            return self._arity

    def is_symmetric(self):
        if self._relation_descr is not None:
            if self._relation_descr in ["all", "empty", "a==b", "a!=b"]:
                return True
            elif self._relation_descr in ["a<b", "a>b", "a>=b", "a<=b", "a=b+1", "a!=b+1"]:
                return False
            else:
                assert False, f"The relation {self._relation_descr} is not implemented yet (this error is unexpected)."
        else:
            assert self._accepted_tuples is not None, "The relation as no accepted tuples and no description."
            return all([t[::-1] in self._accepted_tuples for t in self._accepted_tuples])

    def _domain_size(self):
        assert self._accepted_tuples is not None, "The domain size is only defined for relations with tuples."
        return max([max(t) for t in self._accepted_tuples]) - min([min(t) for t in self._accepted_tuples])

    def size_to_encode(self):
        """:return the size to encode the relation. That is the size of the description or the
        encoding size of accepted tuples."""
        if self._relation_descr is not None:
            # If the relation can be described by a string, we use the string length
            return len(self._relation_descr)
        else:
            # If the relation is a list of tuples, we use the size of the list times the size to encode a tuple
            assert self._accepted_tuples is not None, "The relation as no accepted tuples and no description."
            return len(self._accepted_tuples) * log2(self._domain_size())

    def relation_projection(self, vars_v: list[int]) -> tuple[list[int], 'Relation']:
        """
        Takes a list of variables and returns a new scope and the relation that is the projection of the original
        relation on those variables. For example, if the original relation is [(1,2,1), (1,2,2)] with vars [8,2,8], it
        returns [8,2] and [(1,2)].
        :param vars_v: List of variables to project on.
        :return: A new scope and the relation that is the projection of the original relation on those variables.
        """
        # For string-based relations, check projections by analyzing equality conditions
        unique_vars = []
        for var in vars_v:
            if var not in unique_vars:
                unique_vars.append(var)
        if self._relation_descr is not None:
            if len(unique_vars) < len(vars_v):
                if self._relation_descr in ["all", "a==b", "a>=b", "a<=b", "a!=b+1"]:
                    raise NotImplementedError("Projection not implemented for this relation")
                elif self._relation_descr in ["empty", "a!=b", "a<b", "a>b", "a=b+1"]:
                    raise NotImplementedError("Projection not implemented for this relation")
                else:
                    raise NotImplementedError("Projection not implemented for this relation")
            else:
                return vars_v, self
        # For tuple-based relations
        elif self._accepted_tuples is not None:
            new_tuples: list[list[int]] = []
            for tu in self._accepted_tuples:
                new_tu: Optional[list[int]] = []
                for uv in unique_vars:
                    val: Optional[int] = None
                    for i in range(self.get_arity()):
                        if vars_v[i] == uv:
                            if val is None:
                                val = tu[i]
                            elif val != tu[i]:
                                val = None
                                break
                    if val is not None:
                        new_tu.append(int(val))
                    else:
                        new_tu = None
                        break
                if new_tu is not None:
                    new_tuples.append(new_tu)
            return unique_vars, Relation(accepted_tuples=new_tuples)
        raise NotImplementedError("Unexpected relation type for projection.")

    def is_empty(self):
        if self._accepted_tuples is None:
            return self._relation_descr == "empty"
        return len(self._accepted_tuples) == 0

    def __len__(self):
        if self._accepted_tuples is not None:
            return self._arity
        else:
            # If the relation can be described by a string, it has a fixed arity
            return 1

    def __hash__(self):
        return hash(self._relation_descr) if self._relation_descr is not None else hash(str(self._accepted_tuples))

    def __eq__(self, other):
        return self._relation_descr == other.get_relation_descr() and self._accepted_tuples == other.get_accepted_tuples()

    def get_relation_descr(self):
        return self._relation_descr

    def get_accepted_tuples(self):
        return self._accepted_tuples


class Language:
    def __init__(self):
        self.relations = []

    def add(self, relation):
        assert isinstance(relation, Relation)
        assert relation not in self.relations
        self.relations.append(relation)

    def all_relations(self):
        return self.relations.copy()

    def num_relations(self):
        return len(self.relations)

    def __contains__(self, item):
        return item in self.relations

    def __str__(self):
        rels = ""
        for relation in self.relations:
            rels += str(relation)
        return rels

    def __len__(self):
        return len(self.relations)


def default_language() -> Language:
    lang = Language()
    lang.add(Relation("all"))
    # lang.add(Relation("empty"))
    lang.add(Relation("a==b"))
    lang.add(Relation("a!=b"))
    lang.add(Relation("a<b"))
    lang.add(Relation("a>b"))  # Mandatory for optimization
    lang.add(Relation("a>=b")) # Mandatory for optimization
    lang.add(Relation("a<=b"))
    lang.add(Relation("a=b+1"))
    return lang
