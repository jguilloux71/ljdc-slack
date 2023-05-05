#!/usr/bin/python3


#------------------------------------------------------------------------------
# Import Python libraries
import os
import requests
import sys
import unittest

from pathlib import Path
from unittest import mock
from unittest.mock import mock_open, patch

# Add the current execution directory name to SYSPATH to import easily the custom libraries
full_path = os.path.dirname(Path(__file__))
src_full_path = full_path + '/../src'
sys.path.append(str(src_full_path))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import ljdc
from bs4 import BeautifulSoup

class TestLjdc(unittest.TestCase):
    article_gif_data_file          = full_path + '/ljdc-article-gif.data'
    article_jpg_data_file          = full_path + '/ljdc-article-jpg.data'
    article_jpg_with_tag_data_file = full_path + '/ljdc-article-jpg-with-tag.data'
    article_no_img_data_file       = full_path + '/ljdc-article-no-img.data'

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

    def _soup_data(self, data_file):
        with open(data_file, "r") as f:
            f_data = f.read()
        return (BeautifulSoup(f_data, "html.parser")\
                .find("article", class_="blog-post"), f_data)

    def setUp(self):
        (self.article_gif,          self.article_gif_data)    = self._soup_data(self.article_gif_data_file)
        (self.article_jpg,          self.article_jpg_data)    = self._soup_data(self.article_jpg_data_file)
        (self.article_jpg_with_tag, self.article_jpg_data)    = self._soup_data(self.article_jpg_with_tag_data_file)
        (self.article_no_img,       self.article_no_img_data) = self._soup_data(self.article_no_img_data_file)

    def test_get_post_id(self):
        id_post = ljdc._get_post_id(self.fake_url)
        self.assertEqual(id_post, self.fake_id)

    def test_get_post_no_img(self):
        post = ljdc._get_post(self.article_no_img)
        self.assertEqual(post['url'], 'https://my-fake-NO-IMG.url')
        self.assertEqual(post['title'], 'My fake title NO-IMG')
        self.assertEqual(post['author-date'], 'My fake author NO-IMG, my fake date NO-IMG')
        self.assertIsNone(post['img'])
        self.assertIsNone(post['id'])

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

    def test_get_post_jpg_with_tag(self):
        post = ljdc._get_post(self.article_jpg_with_tag)
        self.assertEqual(post['url'], 'https://my-fake-JPG.url')
        self.assertEqual(post['title'], 'My fake title JPG')
        self.assertEqual(post['author-date'], 'My fake author JPG, my fake date JPG')
        self.assertEqual(post['img'], 'https://my-fake/img/my-fake-id-JPG.jpg')
        self.assertEqual(post['id'], 'my-fake-id-JPG')

    @patch('requests.get')
    def test_get_last_posts_nok(self, m):
        # Mock GET request with fake data
        m.return_value.ok = False
        m.side_effect=requests.exceptions.RequestException('Network error')
        with self.assertRaises(SystemExit) as context:
            last_posts = ljdc.get_last_posts()
        self.assertEqual('1', str(context.exception))


    @patch('requests.get')
    def test_get_last_posts_ok(self, m):
        # Mock GET request with fake data
        m.return_value.ok = True
        m.return_value.content = self.article_gif_data + self.article_jpg_data
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
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
