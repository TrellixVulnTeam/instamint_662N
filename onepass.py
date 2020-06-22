from instapy import InstaPy

#from instapy.like_util import check_link
#from instapy.like_util import verify_liking
#from instapy.like_util import get_links_for_tag
#from instapy.like_util import get_links_from_feed
#from instapy.like_util import get_tags
#from instapy.like_util import get_links_for_location
#from instapy.like_util import like_image
#from instapy.like_util import like_comment
#from instapy.util import web_address_navigator

import csv
from datetime import datetime, timezone

from instapy.constants import MEDIA_PHOTO
from instapy.util import get_relationship_counts

from instapy.time_util import sleep
from my_like_util import get_links_for_username
from my_like_util import get_likes
from my_like_util import check_link2
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from my_database_util import storeRecord


csvfile = "link.csv"

username = "lovin_the_rva"
password = "yellowbrickroad"

session = InstaPy(username=username, password=password)
session.login()


# shopthemint, shopreddress, thepinklilyboutique


username1 = "shopthemint"
amount = 15
randomize = False
media = MEDIA_PHOTO
taggedImages = True


# Get "amount" links from username1/tagged images. 
# This is a fairly light-weight activity, and shouldn't consume any instragram-resources

try:
   links = get_links_for_username(
    session.browser,
    session.username,
    username1,
    amount,
    session.logger,
    session.logfolder,
    randomize,
    media,
    taggedImages
    )
except NoSuchElementException:
    session.logger.error("Element not found, skipping this username")

i = 0
# for each link in the list, follow it and grab lots of statistics.  This consumes instagram resources.
# then follow the posting username and get their statistics.  This consumes instragram resources.

sleep( 1.2 )

for i, posted_link in enumerate(links):

    try:
        try:
            inappropriate, posted_by_username, posted_link_likes_count, posted_link_comments_count, posted_link_datetime_str, posted_link_location_name, posted_link_image_text, is_video, reason, scope = check_link2(
                session.browser,
                posted_link,
                session.dont_like,
                session.mandatory_words,
                session.mandatory_language,
                session.is_mandatory_character,
                session.mandatory_character,
                session.check_character_set,
                session.ignore_if_contains,
                session.logger,
            )
        except:
            inappropriate = True


        if not inappropriate:

            sleep( 1.5 )
            try:
               posted_by_followers_count, posted_by_following_count = get_relationship_counts(
                    session.browser, posted_by_username, session.logger
                )
            except:
                posted_by_followers_count = None
                posted_by_following_count = None

            now = datetime.now(timezone.utc)
            last_checked_datetime_str = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            posted_link_datetime = datetime.strptime(posted_link_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            last_checked_datetime = datetime.strptime(last_checked_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")

            deltatime = (last_checked_datetime - posted_link_datetime)
            last_checked_age_in_hrs = deltatime.seconds / 3600.00

            storeRecord(
                username1,
                last_checked_age_in_hrs,
                last_checked_datetime,
                posted_link,
                posted_link_datetime,
                posted_link_location_name,
                posted_link_image_text,
                posted_link_likes_count,
                posted_link_comments_count,
                posted_by_username,
                posted_by_followers_count,
                posted_by_following_count
            )

    except NoSuchElementException as err:
        session.logger.error("Invalid Page: {}".format(err))


session.end()
