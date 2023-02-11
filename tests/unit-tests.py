#!/usr/bin/python3


#------------------------------------------------------------------------------
# Import Python libraries
import os
import pytest
import requests
import requests_mock
import sys
import unittest

from pathlib import Path
from unittest import mock

# Add the current execution directory name to SYSPATH to import easily the custom libraries
full_path = os.path.dirname(Path(__file__)) + '/../src'
sys.path.append(str(full_path))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import tools

class TestTools(unittest.TestCase):

    def test_get_env_none(self):
        channel = tools.get_env("SLACK_CHANNEL")
        self.assertIsNone(channel)

    @mock.patch.dict(os.environ, {"SLACK_CHANNEL": "my-chan"})
    def test_get_env_ok(self):
        channel = tools.get_env("SLACK_CHANNEL")
        self.assertEqual(channel, "my-chan")

    def test_get_request_error(self):
        url = "http://fake.url"
        response = tools.get_request(url)
        self.assertIsNone(response)

    @requests_mock.Mocker()
    def test_get_request_ok(self, m):
        url = "http://fake.url"
        m.get(url, text='data')
        response = tools.get_request(url)
        self.assertEqual(response.text, 'data')
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------