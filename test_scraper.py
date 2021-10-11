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

@pytest.fixture
def submission_user1_no_replies(reddit_instance):
    return reddit_instance.submission("q5jlig")

@pytest.fixture
def submission_user1_replies(reddit_instance):
    return reddit_instance.submission("q5mqas")

def test_parse_subreddit():
    pass

def test_scrape_submission(scraper_instance, submission_user1_no_replies):
    scraper_instance.add_scraped_submission(submission_user1_no_replies)
    assert submission_user1_no_replies.id in scraper_instance.scraped_submissions

def test_mark_submissions_parsed(scraper_instance, submission_user1_no_replies):
    scraper_instance.add_scraped_submission(submission_user1_no_replies)
    scraper_instance.parse_scraped_submissions()
    assert scraper_instance.scraped_submissions[submission_user1_no_replies.id]["parsed"] is True

def test_avoid_rescrape_submission(scraper_instance, submission_user1_no_replies):
    scraper_instance.add_scraped_submission(submission_user1_no_replies)
    scraper_instance.scraped_submissions[submission_user1_no_replies.id]["parsed"] = True
    scraper_instance.add_scraped_submission(submission_user1_no_replies)
    assert scraper_instance.scraped_submissions[submission_user1_no_replies.id]["parsed"] is True

def test_avoid_reparse_submission(scraper_instance, submission_user1_replies):
    scraper_instance.add_scraped_submission(submission_user1_replies)
    scraper_instance.parse_scraped_submissions()
    assert scraper_instance.replies_graph.get_edge_data("FriendsNetworkDev", "FriendsNetworkDev", key=0)["weight"] == 1
    scraper_instance.parse_scraped_submissions()
    assert scraper_instance.replies_graph.get_edge_data("FriendsNetworkDev", "FriendsNetworkDev", key=0)["weight"] == 1

def test_parse_submission_no_replies(scraper_instance, submission_user1_no_replies):
    scraper_instance.parse_submission(submission_user1_no_replies)
    assert scraper_instance.replies_graph.number_of_nodes() == 0
    assert scraper_instance.replies_graph.number_of_edges() == 0

def test_parse_user():    
    pass

def test_nodes():
    pass

def test_edges():
    pass

def test_weights():
    pass