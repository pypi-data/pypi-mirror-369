import time
import logging
import sys
import platform
import os
import threading
import inspect
from enum import Enum

logging.basicConfig(filename="logFile_API.log",level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')