import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from util import logging
logger = logging.setup(__name__)
logger.level = 10
