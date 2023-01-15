#-------------------------------------------------------------------------------------------------------------
# Import Python libraries
import feedparser
import sys

# Import Custom libraries
from logger import logger
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
LJDC_LAST_POST_ID_FILE = '/var/tmp/ljdc/.ljdc_last_post_id'
LJDC_RSS_URL           = 'https://lesjoiesducode.fr/feed'
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def _get_gif_img_from_post(post):
    post_img = None
    
    for link in post.links:

        # Check key 'type' exists in the dict 'link'
        if 'type' in link:

            # Dict returned:
            # {'length': '0', 'type': 'video/webm', 'href': 'https://lesjoiesducode.fr/content/036/r3HSp6n.webm', 'rel': 'enclosure'}
            if link.type == 'video/webm' or link.type == 'video/mp4':

                # Replace extension by '.gif'
                post_img = link.href.rsplit('.', 1)[0] + '.gif'
                break

    return post_img
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def post_already_published(post):
    logger.info('Last post id file: ' + LJDC_LAST_POST_ID_FILE)
    last_post_id = None

    try:
        with open(LJDC_LAST_POST_ID_FILE, 'r') as f:
            last_post_id = f.read().strip()
    except FileNotFoundError:
        logger.info(LJDC_LAST_POST_ID_FILE + ": File not yet created. Maybe it's the first execution of this script. Let's go on")
    except IOError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info('Last post id: %s' % (last_post_id))
    return last_post_id == post['id']
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def save_post_id_in_file(post):
    try:
        with open(LJDC_LAST_POST_ID_FILE, "w") as f:
            f.write(post['id'])
    except IOError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("New id [%s] in file [%s] saved" %(post['id'], LJDC_LAST_POST_ID_FILE))
#-------------------------------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------------------------------
def get_last_post():
    post = {}
    logger.info("URL to parse: " + LJDC_RSS_URL)

    news_feed = feedparser.parse(LJDC_RSS_URL)
    last_post = news_feed.entries[0]
    
    # ID format from URL: https://lesjoiesducode.fr/?p=25706
    post['id']    = last_post.id.strip().split('=')[1]
    post['title'] = last_post.title.strip()
    post['img']   = _get_gif_img_from_post(last_post)
    
    if post['img'] is None:
        logger.error('Unable to retrieve GIF image from the last post')
        sys.exit(1)

    # Display info about the last post in logger file
    for i in post.items():
        logger.info(i)

    return post
#-------------------------------------------------------------------------------------------------------------