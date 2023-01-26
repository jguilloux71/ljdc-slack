#------------------------------------------------------------------------------
# Import Python libraries
import os


# Import Custom libraries
from logger import logger
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def get_env(var):
    value = os.environ.get(var)

    if value is None:
        logger.error('Unable to get value from env variable: [%s]' % (var))

    return value
#------------------------------------------------------------------------------