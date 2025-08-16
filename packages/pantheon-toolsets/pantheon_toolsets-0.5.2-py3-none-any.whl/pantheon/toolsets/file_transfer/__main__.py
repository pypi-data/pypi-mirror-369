from .worker import FileTransferToolSet
from ..utils.toolset import toolset_cli


toolset_cli(FileTransferToolSet, "file-transfer")
