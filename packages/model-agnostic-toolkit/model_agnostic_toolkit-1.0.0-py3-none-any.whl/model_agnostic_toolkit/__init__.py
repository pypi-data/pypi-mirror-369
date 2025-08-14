class Analyzer:  # forward declaration
    pass

# do not change import ordering
from .model import Model, PreloadedModel
from .analyzer import Analyzer, ImportanceAnalyzer, InteractionAnalyzer
from . import types
from . import datasets
from . import plots
from . import tools

