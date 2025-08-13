# Added by Mahesh Saggam on [29-JUNE-21] To print console in a separate log file

import logging
from logging.handlers import RotatingFileHandler
# from jproperties import Properties
import os
import traceback

base_dir = 'log'

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

for f in os.listdir(base_dir):
    os.remove(os.path.join(base_dir, f))

# The below commented code will required if the configuration is defined in Properties file

# configs = Properties()
# propDetails = {}

# with open('PythonLogger.Properties', 'rb') as read_prop:
#     configs.load(read_prop)


# prop_view = configs.items()

# for item in prop_view:
#     propDetails[item[0]] = item[1].data

# format = propDetails['FORMAT']
# filename = propDetails['FILE_NAME']
# filemode = propDetails['FILE_MODE']
# loggerName = propDetails['LOGGER_NAME']
# maxBytes = propDetails['MAX_BYTES']
# backUpcount = propDetails['BACKUP_COUNT']

format = '%(asctime)s %(levelname)s %(name)s %(message)s'
filename = 'python_server.log'
loggerName = '[BaseLogger]'
maxBytes = 5242880
backUpcount = 100

base_logger = logging.getLogger(loggerName)
base_logger.setLevel(logging.DEBUG)
base_logger.propagate = False
logging.getLogger('werkzeug').disabled = True

# File handler
base_handler = RotatingFileHandler(
    os.path.join(base_dir, filename), 
    maxBytes=maxBytes, 
    backupCount=backUpcount
)
base_handler.setFormatter(logging.Formatter(format))
base_logger.addHandler(base_handler)

def log(msg, debugLevel='0'):
    stack = traceback.extract_stack()
    fname, line, func, text = stack[-2]
    fname = os.path.basename(fname)
    msg = f'~{fname}~{func}~{msg}'

    debugLevel = int(debugLevel or 0)
    if debugLevel == 0:
        base_logger.debug(msg)
    elif debugLevel == 1:
        base_logger.exception(msg)

from .deployment_logger import trans_log as deployment_log