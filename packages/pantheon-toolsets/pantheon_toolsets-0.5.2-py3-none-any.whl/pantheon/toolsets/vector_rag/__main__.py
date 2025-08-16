from .rag import VectorRAGToolSet
from ..utils.toolset import toolset_cli


toolset_cli(VectorRAGToolSet, "vector-rag")
