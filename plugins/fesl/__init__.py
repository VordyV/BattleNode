from .fesl import Fesl
from . import services
import logging

logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("asyncmy").setLevel(logging.CRITICAL)
