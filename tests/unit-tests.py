#!/usr/bin/python3


#------------------------------------------------------------------------------
# Import Python libraries
import os
import pytest
import requests
import requests_mock
import sys
import unittest

# let's use the pprint module for readability
from pprint import pprint
from slack_sdk import web
from slack_sdk.errors import SlackApiError


# import inspect module
import inspect

from pathlib import Path
from unittest import mock
from unittest.mock import mock_open, patch

# Add the current execution directory name to SYSPATH to import easily the custom libraries
full_path = os.path.dirname(Path(__file__))
src_full_path = full_path + '/../src'
sys.path.append(str(src_full_path))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import tools

class TestTools(unittest.TestCase):

    fake_url  = 'http://fake.url'
    fake_env  = 'FAKE_ENV'
    fake_chan = 'fake-chan'

    def test_get_env_none(self):
        channel = tools.get_env(self.fake_env)
        self.assertIsNone(channel)

    @mock.patch.dict(os.environ, {fake_env : fake_chan})
    def test_get_env_ok(self):
        channel = tools.get_env(self.fake_env)
        self.assertEqual(channel, self.fake_chan)

    @patch('requests.get')
    def test_get_request_error(self, m):
        m.side_effect = requests.exceptions.RequestException(
            'HTTP connection error, unable to reach: %s' % (self.fake_url)
        )
        response = tools.get_request(self.fake_url)
        self.assertIsNone(response)

    @requests_mock.Mocker()
    def test_get_request_ok(self, m):
        m.get(self.fake_url, text='data')
        response = tools.get_request(self.fake_url)
        self.assertEqual(response.text, 'data')
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import ljdc
from bs4 import BeautifulSoup

class TestLjdc(unittest.TestCase):
    article_gif_data_file = full_path + '/ljdc-article-gif.data'
    article_jpg_data_file = full_path + '/ljdc-article-jpg.data'
    fake_id  = 'fake-id'
    fake_url = 'https://lesjoiesducode.fr/content/048/%s.gif' % (fake_id)
    fake_content_ids_file = """id-number-1
        id-number-2
        id-number-3
        id-number-4
        id-number-5"""
    fake_ids_list = [
        'id-number-1',
        'id-number-2',
        'id-number-3',
        'id-number-4',
        'id-number-5'
    ]
    fake_new_ids = [
        {'id' : 'last-id-1'},
        {'id' : 'last-id-2'},
        {'id' : 'last-id-3'}
    ]
    fake_new_ids_file = [
        mock.call('last-id-1\n'),
        mock.call('last-id-2\n'),
        mock.call('last-id-3\n')
    ]

    def setUp(self):
        # Special data for GIF article
        with open(self.article_gif_data_file, "r") as f:
            self.article_gif_data = f.read()

        soup = BeautifulSoup(self.article_gif_data, "html.parser")
        self.article_gif = soup.find("article", class_="blog-post")

        # Special data for JPG article
        with open(self.article_jpg_data_file, "r") as f:
            self.article_jpg_data = f.read()

        soup = BeautifulSoup(self.article_jpg_data, "html.parser")
        self.article_jpg = soup.find("article", class_="blog-post")

    def test_get_post_id(self):
        id_post = ljdc._get_post_id(self.fake_url)
        self.assertEqual(id_post, self.fake_id)

    def test_get_post_gif(self):
        post = ljdc._get_post(self.article_gif)
        self.assertEqual(post['url'], 'https://my-fake-GIF.url')
        self.assertEqual(post['title'], 'My fake title GIF')
        self.assertEqual(post['author-date'], 'My fake author GIF, my fake date GIF')
        self.assertEqual(post['img'], 'https://my-fake/img/my-fake-id-GIF.gif')
        self.assertEqual(post['id'], 'my-fake-id-GIF')

    def test_get_post_jpg(self):
        post = ljdc._get_post(self.article_jpg)
        self.assertEqual(post['url'], 'https://my-fake-JPG.url')
        self.assertEqual(post['title'], 'My fake title JPG')
        self.assertEqual(post['author-date'], 'My fake author JPG, my fake date JPG')
        self.assertEqual(post['img'], 'https://my-fake/img/my-fake-id-JPG.jpg')
        self.assertEqual(post['id'], 'my-fake-id-JPG')

    @patch('requests.get')
    def test_get_last_posts(self, m):
        # Mock GET request with fake data
        m.return_value.ok = True
        m.return_value.content = self.article_gif_data+self.article_jpg_data
        last_posts = ljdc.get_last_posts()
        self.assertEqual(len(last_posts), 2)
        self.assertEqual(last_posts[0]['img'], 'https://my-fake/img/my-fake-id-GIF.gif')
        self.assertEqual(last_posts[1]['img'], 'https://my-fake/img/my-fake-id-JPG.jpg')

    @patch('ljdc.LJDC_LAST_POST_ID_FILE', '/var/tmp/ll')
    def test_ids_file_does_not_exist(self):
        post_ids = ljdc.get_post_ids_already_published()
        self.assertListEqual(post_ids, [])

    @patch('builtins.open', mock_open())
    def test_read_ids_file_io_error_and_exit(self):
        open.side_effect=IOError('Fake IO error')
        with self.assertRaises(SystemExit) as context:
            ljdc.get_post_ids_already_published()
        self.assertEqual('1', str(context.exception))

    # Mock the next opening of a file with a fake content
    @patch('builtins.open', mock_open(read_data=fake_content_ids_file))
    def test_get_post_ids_already_published(self):
        post_ids = ljdc.get_post_ids_already_published()
        open.assert_called_with(ljdc.LJDC_LAST_POST_ID_FILE, 'r')
        self.assertListEqual(post_ids, self.fake_ids_list)

    @patch('builtins.open', mock_open())
    def test_write_ids_file_io_error_and_exit(self):
        open.side_effect=IOError('Fake IO error')
        with self.assertRaises(SystemExit) as context:
            ljdc.save_post_ids_in_file(self.fake_new_ids)
        self.assertEqual('1', str(context.exception))

    # Mock the next opening of a file
    @patch('builtins.open', mock_open())
    def test_save_post_ids_in_file(self):
        ljdc.save_post_ids_in_file(self.fake_new_ids)
        open.assert_called_with(ljdc.LJDC_LAST_POST_ID_FILE, 'w')
        open().write.assert_has_calls(self.fake_new_ids_file)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import slack
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