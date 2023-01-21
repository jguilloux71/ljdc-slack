#-------------------------------------------------------------------------------------------------------------
# Import Python libraries
import datetime
import os
import sys

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Import Custom libraries
from logger import logger
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
SLACK_CHANNEL        = '#canal-test'
SLACK_ENV_AUTH_TOKEN = 'SLACK_BOT_TOKEN'
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def _get_img_text():
    # Get date of day at format: '03 Fev 2023'
    date_today = datetime.date.today().strftime("%d %b %Y")
    return 'Les joies du code, commit du ' + date_today
#-------------------------------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------------------------------
def _get_token_from_env():
    token = os.environ.get(SLACK_ENV_AUTH_TOKEN)

    if token is None:
        logger.error('Unable to get token from env variable: [%s]' % (SLACK_ENV_AUTH_TOKEN))
        sys.exit(1)

    return token
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def _create_slack_client():
    client = WebClient(
        token = _get_token_from_env()
    )
    
    try:
        client.auth_test()
    except SlackApiError as e:
        logger.error('Slack API test error: ' + str(e.response['error']))
        sys.exit(1)

    return client
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def send_img_to_channel(post):
    client = _create_slack_client()

    # attachment is mandatory to display successfully a GIF image in a Slack channel
    attachments = [{
        "title"     : post['title'],
        "image_url" : post['img']
    }]

    try:
        client.chat_postMessage(
            channel     = SLACK_CHANNEL,
            text        = '_' + _get_img_text() + '_',
            attachments = attachments
        )
    except SlackApiError as e:
        logger.error('Slack: unable to send GIF image to channel [%s]: ' % (SLACK_CHANNEL, str(e.response['error'])))
        sys.exit(1)

    logger.info('Slack: new message/img posted successfully [id=%s]' % (post['id']))
#-------------------------------------------------------------------------------------------------------------