import pytest
import praw
from scraper import reddit_scraper

reddit = praw.Reddit("FriendsNetwork")
single_user1_submission = reddit.submission("XXXXX")
example_user = reddit.redditor('asqapro')

@pytest.fixture
def reddit_instance():
    return praw.Reddit("FriendsNetwork")

@pytest.fixture
def scraper_instance():
    return reddit_scraper()

def test_parse_subreddit(self):
    pass

def test_parse_submission_no_replies(reddit_instance, scraper_instance):
    submission = reddit_instance.submission("q5jlig")
    scraper_instance.parse_submission(submission)
    assert scraper_instance.scraped_submissions[submission.id]["parsed"]

def test_parse_user(self):
    
    pass

def test_nodes(self):
    pass

def test_edges(self):
    pass

def test_weights(self):
    pass