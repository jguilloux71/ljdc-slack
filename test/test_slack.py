#!/usr/bin/python3


#------------------------------------------------------------------------------
# Import Python libraries
import os
import sys
import unittest

from pathlib import Path
from unittest import mock
from unittest.mock import patch

# Add the current execution directory name to SYSPATH to import easily the custom libraries
full_path = os.path.dirname(Path(__file__))
src_full_path = full_path + '/../src'
sys.path.append(str(src_full_path))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import slack
from slack_sdk import web
from slack_sdk.errors import SlackApiError

class TestSlack(unittest.TestCase):

    fake_post ={
        'id' : 'fake-id',
        'img' : 'https://fake.img',
        'title' : 'Fake title',
        'url' : 'https://fake.url',
        'author-date' : 'fake date'
    }
    
    """ This test allows to verify there is well an exception
    when SLACK_BOT_TOKEN and SLACK_CHANNEL are not defined.
    To be sure to don't be impacted by these "real" env variables
    on your own environment, we mock SLACK_ENV_AUTH_TOKEN and 
    SLACK_ENV_CHANNEL variables (Python variables)"""
    @patch('slack.SLACK_ENV_AUTH_TOKEN', 'FAKE_SLACK_BOT_TOKEN')
    @patch('slack.SLACK_ENV_CHANNEL',    'FAKE_SLACK_CHANNEL')
    def test_slack_no_env_var(self):
        with self.assertRaises(slack.SlackGetEnvError) as context:
            slack.Slack()

    @patch('slack.SLACK_ENV_AUTH_TOKEN', 'FAKE_SLACK_BOT_TOKEN')
    @patch('slack.SLACK_ENV_CHANNEL',    'FAKE_SLACK_CHANNEL')
    @mock.patch.dict(os.environ, {'FAKE_SLACK_BOT_TOKEN' : 'My fake token'})
    def test_slack_no_env_slack_channel(self):
        with self.assertRaises(slack.SlackGetEnvError) as context:
            slack.Slack()

    """This test returns a SlackApiError: all ENV variables are defined
    but 'token' is not the right token"""
    @patch('slack.SLACK_ENV_AUTH_TOKEN', 'FAKE_SLACK_BOT_TOKEN')
    @patch('slack.SLACK_ENV_CHANNEL',    'FAKE_SLACK_CHANNEL')
    @mock.patch.dict(os.environ, {'FAKE_SLACK_BOT_TOKEN' : 'My fake token'})
    @mock.patch.dict(os.environ, {'FAKE_SLACK_CHANNEL'   : 'My fake channel'})
    @patch('slack_sdk.WebClient.auth_test')
    def test_slack_env_var_ok_but_bad_token(self, mock_test):
        resp = web.SlackResponse(client='', http_verb='', api_url='',
            req_args={}, data={'ok': False, 'error': 'fake invalid error'}, headers={}, status_code=1)
        mock_test.side_effect = SlackApiError('', resp)
        with self.assertRaises(SlackApiError) as context:
            slack.Slack()

    @patch('slack.SLACK_ENV_AUTH_TOKEN', 'FAKE_SLACK_BOT_TOKEN')
    @patch('slack.SLACK_ENV_CHANNEL',    'FAKE_SLACK_CHANNEL')
    @mock.patch.dict(os.environ, {'FAKE_SLACK_BOT_TOKEN' : 'My fake token'})
    @mock.patch.dict(os.environ, {'FAKE_SLACK_CHANNEL'   : 'My fake channel'})
    @patch('slack_sdk.WebClient.auth_test')
    @patch('slack_sdk.WebClient.chat_postMessage')
    def test_slack_send_img_ok(self, c, a):
        my_slack = slack.Slack()
        self.assertIsNotNone(my_slack)
        res = my_slack.send_img_to_channel(self.fake_post)
        self.assertTrue(res)

    @patch('slack.SLACK_ENV_AUTH_TOKEN', 'FAKE_SLACK_BOT_TOKEN')
    @patch('slack.SLACK_ENV_CHANNEL',    'FAKE_SLACK_CHANNEL')
    @mock.patch.dict(os.environ, {'FAKE_SLACK_BOT_TOKEN' : 'My fake token'})
    @mock.patch.dict(os.environ, {'FAKE_SLACK_CHANNEL'   : 'My fake channel'})
    @patch('slack_sdk.WebClient.auth_test')
    @patch('slack_sdk.WebClient.chat_postMessage')
    def test_slack_send_img_nok(self, mock_message, mock_test):
        my_slack = slack.Slack()
        self.assertIsNotNone(my_slack)
        resp = web.SlackResponse(client='', http_verb='', api_url='',
            req_args={}, data={'ok': False, 'error': 'fake message error'}, headers={}, status_code=1)
        mock_message.side_effect = SlackApiError('', resp)
        res = my_slack.send_img_to_channel(self.fake_post)
        self.assertFalse(res)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------