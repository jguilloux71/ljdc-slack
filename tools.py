#------------------------------------------------------------------------------
# Import Python libraries
import os
import requests
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




#------------------------------------------------------------------------------
def get_request(url):
    headers = {
        "Cache-Control" : "no-cache",
        "Pragma"        : "no-cache"
    }

    logger.info('URL to fecth: %s' % (url))
    try:
        page = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.error(str(e))
        page = None

    return page
#------------------------------------------------------------------------------
