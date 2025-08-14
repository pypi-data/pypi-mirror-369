""" TAcq: A package for learning a compact representation of a constraint network from examples."""
from importlib.metadata import version, PackageNotFoundError

from .SolverOrTools import SolverOrTools
from .TemplateAcquisition import TemplateAcquisition
from .IterativeTemplate import IterativeTemplate
from .Template import Template
from .Relation import Relation
from .CSP import CSP, file_to_examples, convert_from_Template

try:
    __version__ = version("tacq")
except PackageNotFoundError:
    __version__ = "unknown"
