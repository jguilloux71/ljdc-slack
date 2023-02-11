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

    def test_get_request_error(self):
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
        self.assertEqual(post['url'], 'https://my-fake.url')
        self.assertEqual(post['title'], 'My fake title')
        self.assertEqual(post['author-date'], 'My fake author, my fake date')
        self.assertEqual(post['img'], 'https://my-fake/img/my-fake-id.gif')
        self.assertEqual(post['id'], 'my-fake-id')

    def test_get_post_jpg(self):
        post = ljdc._get_post(self.article_jpg)
        self.assertEqual(post['url'], 'https://my-fake.url')
        self.assertEqual(post['title'], 'My fake title')
        self.assertEqual(post['author-date'], 'My fake author, my fake date')
        self.assertEqual(post['img'], 'https://my-fake/img/my-fake-id.jpg')
        self.assertEqual(post['id'], 'my-fake-id')

    @requests_mock.Mocker()
    def test_get_last_posts(self, m):
        # Mock GET request with fake data
        m.get(ljdc.LJDC_URL, text=self.article_gif_data+self.article_jpg_data)
        last_posts = ljdc.get_last_posts()
        self.assertEqual(len(last_posts), 2)
        self.assertEqual(last_posts[0]['img'], 'https://my-fake/img/my-fake-id.gif')
        self.assertEqual(last_posts[1]['img'], 'https://my-fake/img/my-fake-id.jpg')

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

    """ This test allows to verify there is weel an exception
    when SLACK_BOT_TOKEN and SLACK_CHANNEL are not defined.
    To be sure to don't be impacted by these "real" env variables
    on your own environment, we mock SLACK_ENV_AUTH_TOKEN and 
    SLACK_ENV_CHANNEL"""
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
    def test_slack_env_var_ok_but_bad_token(self):
        with self.assertRaises(SlackApiError) as context:
            slack.Slack()

    # Mock POST request to Slack API
    @requests_mock.Mocker()
    def test_slack_ok(self, m):
        my_slack = slack.Slack()
        self.assertIsNotNone(my_slack)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------