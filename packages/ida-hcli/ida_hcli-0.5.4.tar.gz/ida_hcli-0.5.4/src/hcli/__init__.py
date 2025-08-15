import os

__version__ = "0.5.4"
HCLI_BINARY_NAME = os.environ.get("HCLI_BINARY_NAME", "hcli")
HCLI_BINARY_VERSION = os.environ.get("HCLI_BINARY_VERSION", __version__)
