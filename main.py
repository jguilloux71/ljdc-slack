#!/usr/bin/python3

import datetime
import feedparser
import os
import sys
import logging
import requests

from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


LJDC_RSS_URL = 'https://lesjoiesducode.fr/feed'
LJDC_DIR = str(Path.home()) + "/ljdc"

os.makedirs(LJDC_DIR, exist_ok=True)

LJDC_LAST_POST_ID_FILE = LJDC_DIR + "/.ljdc_last_post_id"
LJDC_LOGGING_FILE = LJDC_DIR + "/ljdc.log"

SLACK_CHANNEL = 'canal-test'

# Create and configure logger
logging.basicConfig(filename=LJDC_LOGGING_FILE,
                    format='%(asctime)s %(message)s',
                    filemode='a')
 
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to INFO
logger.setLevel(logging.INFO)

logger.info("Starting...")
logger.info("URL to parse: " + LJDC_RSS_URL)

logger.info('Last ID file: ' + LJDC_LAST_POST_ID_FILE)

last_post_id = ""
try:
    with open(LJDC_LAST_POST_ID_FILE, 'r') as f:
        last_post_id = f.read().strip()
except FileNotFoundError:
    logger.info(LJDC_LAST_POST_ID_FILE + ": File not yet created. Maybe it's the first execution of this script. Let's go on")
except IOError as e:
    logger.error(str(e))
    logger.error("Exit 1")
    sys.exit(1)

NewsFeed = feedparser.parse(LJDC_RSS_URL)
last_post = NewsFeed.entries[0]

# ID format: https://lesjoiesducode.fr/?p=25706
post_long_id = last_post.id.strip()
post_id = post_long_id.split('=')[1]

logger.info("Last post ID: " + last_post_id)
logger.info("RSS post ID: " + post_id)

if post_id == last_post_id:
    logger.info("Same IDs: nothing to publish")
    logger.info("Exit 0")
    sys.exit(0)

post_title = last_post.title.strip()

post_img = None
for link in last_post.links:
    # Check key 'type' exists in the dict 'link'
    if 'type' in link:
        if link.type == 'video/webm' or link.type == 'video/mp4':
            post_img = link.href.rsplit('.', 1)[0] + '.gif'
            break

logger.info('Title: ' + post_title)
logger.info('Image: ' + post_img)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

date_today = datetime.date.today()
my_date = date_today.strftime("%d %b %Y")
chat_text = 'Les joies du code, commit du ' + my_date
attachments = [{"title": post_title, "image_url": post_img}]
client.chat_postMessage(
    channel="#"+SLACK_CHANNEL,
    text='_'+ chat_text +'_',
    attachments=attachments
)

logger.info('Slack: new message posted successfully!')

try:
    with open(LJDC_LAST_POST_ID_FILE, "w") as f:
        f.write(post_id)
except IOError as e:
    logger.error(str(e))
    logger.error("Exit 1")
    sys.exit(1)

logger.info("New last id (%s): %s" %(LJDC_LAST_POST_ID_FILE, post_id))
sys.exit(0)