#!/usr/bin/python3


#------------------------------------------------------------------------------
# Import Python libraries
import os
import requests
import requests_mock
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
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------