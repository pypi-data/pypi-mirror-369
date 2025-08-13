"""CMD-LM - Command and use langauge models with ease from the command line"""

__version__ = "0.1.0"

# Configure logging early to suppress LiteLLM debug messages
import logging
import warnings

# Suppress all warnings
warnings.simplefilter("ignore")

# Set logging levels to suppress debug messages from LiteLLM and related libraries
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

from .commands import *
from .config.manager import *
from .config.providers import *
from .conversation.handler import *
