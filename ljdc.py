#------------------------------------------------------------------------------
# Import Python libraries
import feedparser
import sys

# Import Custom libraries
from logger import logger
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
LJDC_LAST_POST_ID_FILE = '/var/tmp/ljdc/.ljdc_last_post_id'
LJDC_RSS_URL           = 'https://lesjoiesducode.fr/feed'
LJDC_MAX_POST_IDS      = 5
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _get_gif_img_from_post(post):
    post_img = None
    
    for link in post.links:
        logger.info(link)

        # Check key 'type' exists in the dict 'link'
        if 'type' in link:

            # Dict returned:
            # {'length': '0', 'type': 'video/webm', 'href': 'https://lesjoiesducode.fr/content/036/r3HSp6n.webm', 'rel': 'enclosure'}
            if link.type == 'video/webm' or link.type == 'video/mp4':

                # Replace extension by '.gif'
                post_img = link.href.rsplit('.', 1)[0] + '.gif'
                break

    return post_img
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
# This list is stored in the file: LJDC_LAST_POST_ID_FILE
#------------------------------------------------------------------------------
def get_post_ids_already_published():
    logger.info('Last post ids file: ' + LJDC_LAST_POST_ID_FILE)
    last_post_ids = []

    try:
        with open(LJDC_LAST_POST_ID_FILE, 'r') as f:
            for line in (f.readlines()[:LJDC_MAX_POST_IDS]):
                last_post_ids.append(line.strip())
    except FileNotFoundError:
        logger.info("%s: File not yet created. Maybe it's the first execution of this script. Let's go on" %
            (LJDC_LAST_POST_ID_FILE))
    except IOError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info('List of last post ids already published: %s' %
        (str(last_post_ids)[1:-1]))

    return last_post_ids
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def save_post_ids_in_file(posts):
    try:
        with open(LJDC_LAST_POST_ID_FILE, "w") as f:
            for post in posts:
                f.write(post['id'] + '\n')
    except IOError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("New list of post ids written successfully in file: %s" %
        LJDC_LAST_POST_ID_FILE))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _display_post_info(post):
    # Display info about the last post in logger file
    for item in post.items():
        logger.info(item)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _get_post(entry):
    post = {}

    # ID format from URL: https://lesjoiesducode.fr/?p=25706
    post['id']    = entry.id.strip().split('=')[1]
    post['title'] = entry.title.strip()
    post['img']   = _get_gif_img_from_post(entry)

    _display_post_info(post)

    return post
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def get_last_posts():
    posts = []
    logger.info("URL to parse: " + LJDC_RSS_URL)
    news_feed = feedparser.parse(LJDC_RSS_URL)

    for i in range(LJDC_MAX_POST_IDS):
        logger.info('RSS entry number: %d' % (i))
        post = _get_post(news_feed.entries[i])

        if post['img'] is None:
            logger.error('Unable to retrieve GIF image [id=%s]' % (post['id']))
        else:
            posts.append(post)
            logger.info('Post added for treatment [id=%s]' % (post['id']))

    return posts
#------------------------------------------------------------------------------