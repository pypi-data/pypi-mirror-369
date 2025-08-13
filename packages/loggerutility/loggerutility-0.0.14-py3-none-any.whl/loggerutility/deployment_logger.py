# Added by Mahesh Saggam on [29-JUNE-21] To print console in a separate log file

import logging
from logging.handlers import RotatingFileHandler
# from jproperties import Properties
import os
import traceback
from datetime import datetime
import random

trans_dir = 'transaction_log'

if not os.path.exists(trans_dir):
    os.makedirs(trans_dir)

for f in os.listdir(trans_dir):
    os.remove(os.path.join(trans_dir, f))

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
maxBytes = 5242880
backUpcount = 100

random_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
trans_filename = f'{random_number}_{timestamp}.log'
trans_loggerName = '[TransLogger]'

trans_logger = logging.getLogger(trans_loggerName)
trans_logger.setLevel(logging.DEBUG)
trans_logger.propagate = False
logging.getLogger('werkzeug').disabled = True

trans_handler = RotatingFileHandler(
    os.path.join(trans_dir, trans_filename), 
    maxBytes=maxBytes, 
    backupCount=backUpcount
)
trans_handler.setFormatter(logging.Formatter(format))
trans_logger.addHandler(trans_handler)

def trans_log(msg, debugLevel='0'):
    stack = traceback.extract_stack()
    fname, line, func, text = stack[-2]
    fname = os.path.basename(fname)
    msg = f'~{fname}~{func}~{msg}'

    debugLevel = int(debugLevel or 0)
    if debugLevel == 0:
        trans_logger.debug(msg)
    elif debugLevel == 1:
        trans_logger.exception(msg)
