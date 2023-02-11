#!/usr/bin/python3


#------------------------------------------------------------------------------
# Import Python libraries
import os
import sys
from pathlib import Path

# Add the current execution directory name to SYSPATH to import easily the custom libraries
full_path = os.path.dirname(Path(__file__))
sys.path.append(str(full_path))

# Import Custom libraries
from logger import logger
import ljdc
import slack
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
logger.info("-- Let's get started --")
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
# Creating Slack object before all. To be sure env variables are correctly set
#------------------------------------------------------------------------------
try:
    my_slack = slack.Slack()
except:
    sys.exit(1)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
# Get the list of post IDs already published
#------------------------------------------------------------------------------
post_ids_already_published = ljdc.get_post_ids_already_published()
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
# Get the last post from "Les joies du Code" website and send GIF img
# (and only GIF, not JPG or another format) to Slack channelo
#------------------------------------------------------------------------------
try:
    last_posts = ljdc.get_last_posts()
except Exception as e:
    logger.error('Error: %s' % (str(e)))
    sys.exit(1)

for post in last_posts:
    if post['id'] in post_ids_already_published:
        logger.info("This post has already been published. Nothing to do [id=%s]" %
            (post['id']))
    else:
        my_slack.send_img_to_channel(post)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
# Save new IDs in file to avoid to publish these posts already published
# for the next time
#------------------------------------------------------------------------------
ljdc.save_post_ids_in_file(last_posts)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
logger.info("-- End of script. Success! --")
#------------------------------------------------------------------------------




sys.exit(0)