#------------------------------------------------------------------------------
# Import Python libraries
import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Import Custom libraries
from logger import logger
import tools
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
SLACK_ENV_CHANNEL    = 'SLACK_CHANNEL'
SLACK_ENV_AUTH_TOKEN = 'SLACK_BOT_TOKEN'
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
class SlackGetEnvError(Exception): 
    pass
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
class Slack:

    #--- CONSTRUCTOR : START --------------------------------------------------
    def __init__(self):
        self.auth_token = tools.get_env(SLACK_ENV_AUTH_TOKEN)
        if self.auth_token is None:
            raise SlackGetEnvError

        self.channel = tools.get_env(SLACK_ENV_CHANNEL)
        if self.channel is None:
            raise SlackGetEnvError

        self.client = self._create_slack_client()
    #--- CONSTRUCTOR : END ----------------------------------------------------


    def _create_slack_client(self):
        client = WebClient(
            token = self.auth_token
        )

        try:
            client.auth_test()
        except SlackApiError as e:
            logger.error('Slack API test error: ' + str(e.response['error']))
            raise e

        return client


    def send_img_to_channel(self, post):
        """ attachment is mandatory to display successfully a GIF image
        in a Slack channel"""
        attachments = [{
            "title"     : post['title'],
            "image_url" : post['img']
        }]

        try:
            self.client.chat_postMessage(
                channel     = self.channel,
                # Slack markdown syntax for HTML link: <http://www.example.com|This message *is* a link>
                text        = '<' + post['url'] + '|_' + post['author-date'] + '_>',
                attachments = attachments
        )
        except SlackApiError as e:
            logger.error('Unable to send GIF image to channel [%s]: %s' %
                (self.channel, str(e.response['error'])))
            return

        logger.info('[%s] New message/img posted successfully [id=%s]' %
            (self.channel, post['id']))


    def print_env(self):
        print (self.auth_token)
        print (self.channel)
#------------------------------------------------------------------------------
