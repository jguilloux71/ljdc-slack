#------------------------------------------------------------------------------
# Import Python libraries
from bs4 import BeautifulSoup
import sys

# Import Custom libraries
from logger import logger
import tools
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
LJDC_LAST_POST_ID_FILE = '/var/tmp/ljdc/.ljdc_last_post_id'
LJDC_URL               = 'https://lesjoiesducode.fr/'
LJDC_MAX_POST_IDS      = 5
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
        with open(LJDC_LAST_POST_ID_FILE, 'w') as f:
            for post in posts:
                f.write(post['id'] + '\n')
                logger.info('ID written: %s' % (post['id']))
    except IOError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("New list of post ids written successfully in file: %s" %
        (LJDC_LAST_POST_ID_FILE))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _display_post_info(post):
    # Display info about the last post in logger file
    for item in post.items():
        logger.info(item)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _get_post_id(img_url):
    """
    URL format: https://lesjoiesducode.fr/content/048/hZYLfUl.gif
    return: hZYLfUl
    """
    return img_url.rsplit('/', 1)[1].split('.')[0]
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _get_post_img(entry):
    # Try to find a GIF (<video>)
    try:
        post_img = entry.find('div',  class_='blog-post-content').find('video').find('object').get('data')
        post_id  = _get_post_id(post_img)
    except:

        # Try to find a static JPG (<img>)
        try:
            post_img = entry.find('div',  class_='blog-post-content').find('img').get('data-src')
            post_id  = _get_post_id(post_img)
        except:
            post_img = None
            post_id  = None

    return (post_img, post_id)
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def _get_post(entry):
    post = {}

    post['url']         = entry.find('h1',   class_='index-blog-post-title').find('a').get('href')
    post['title']       = entry.find('h1',   class_='index-blog-post-title').find('a').get_text()
    post['author-date'] = entry.find('div',  class_='post-meta-info').get_text().strip()

    (post['img'], post['id']) = _get_post_img(entry)

    _display_post_info(post)

    return post
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
def get_last_posts():
    posts = []

    page = tools.get_request(LJDC_URL)
    if page is None:
        sys.exit(1)

    soup = BeautifulSoup(page.content, "html.parser")

    # In LJDC website, a post = an article
    articles = soup.find_all("article", class_="blog-post")

    for article in articles:
        logger.info('- New post found -')
        post = _get_post(article)

        if post['img'] is None:
            logger.error('Unable to retrieve img for post: %s' % (post['url']))
        else:
            posts.append(post)
            logger.info('Post added for treatment [id=%s]' % (post['id']))

    return posts
#------------------------------------------------------------------------------
