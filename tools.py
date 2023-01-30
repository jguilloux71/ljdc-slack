#------------------------------------------------------------------------------
# Import Python libraries
import os
import sys


# Import Custom libraries
from logger import logger
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def get_env(var):
    value = os.environ.get(var)

    if value is None:
        logger.error('Unable to get value from env variable: [%s]' % (var))
        print('Unable to get value from env variable: [%s]' % (var),
            file=sys.stderr)

    return value
#------------------------------------------------------------------------------