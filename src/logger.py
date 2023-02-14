#-------------------------------------------------------------------------------------------------------------
# Import Python libraries
import logging
import os
import sys
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
LJDC_LOG_FILE = '/var/tmp/ljdc/ljdc.log'
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def _initialize():
    # Create and configure logger
    logging.basicConfig(
        filename = LJDC_LOG_FILE,
        format   = '%(asctime)s [%(module)s] %(message)s',
        filemode = 'a'  # append
    )
 
    # Creating an object
    logger = logging.getLogger()
 
    # Setting the threshold of logger to INFO
    logger.setLevel(logging.INFO)
    
    return logger
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
# Create data directory if doesn't exist
#-------------------------------------------------------------------------------------------------------------
try:
    os.makedirs(os.path.dirname(LJDC_LOG_FILE), exist_ok=True)
except OSError as e:    # pragma: no cover
    print("Unable to create directory: %s" % (str(e)), file=sys.stderr)
    # Fatal error
    sys.exit(1)
    

# Global variable
logger = _initialize()
#-------------------------------------------------------------------------------------------------------------