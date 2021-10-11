import pytest
import praw
from scraper import reddit_scraper

#Current dataset:
# 3 submissions
#    r/FriendsNetwork Lounge (autocreated)
#      No comments
#    [User1]
#      No comments
#    [User1][Replies]
#      2 comments
#      User1 replied to User1 1 time

@pytest.fixture
def reddit():
    return praw.Reddit("FriendsNetwork")

@pytest.fixture
def scraper():
    return reddit_scraper()

@pytest.fixture
def subreddit(reddit):
    return reddit.subreddit("FriendsNetwork")

@pytest.fixture
def submission_user1_no_replies(reddit):
    return reddit.submission("q5jlig")

@pytest.fixture
def submission_user1_replies(reddit):
    return reddit.submission("q5mqas")

@pytest.fixture
def redditor_user1(reddit):
    return reddit.redditor("FriendsNetworkDev")

@pytest.fixture
def redditor_user2(reddit):
    return reddit.redditor("asqapro")

def test_scrape_submission(scraper, submission_user1_no_replies):
    scraper.add_scraped_submission(submission_user1_no_replies)
    assert submission_user1_no_replies.id in scraper.scraped_submissions

def test_parse_submission_with_replies(scraper, submission_user1_replies, redditor_user1):
    scraper.parse_submission(submission_user1_replies)
    assert scraper.replies_graph.number_of_nodes() == 1
    assert scraper.replies_graph.number_of_edges() == 1
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 1

def test_parse_submission_no_replies(scraper, submission_user1_no_replies):
    scraper.parse_submission(submission_user1_no_replies)
    assert scraper.replies_graph.number_of_nodes() == 0
    assert scraper.replies_graph.number_of_edges() == 0

def test_mark_submissions_parsed(scraper, submission_user1_no_replies):
    scraper.add_scraped_submission(submission_user1_no_replies)
    scraper.parse_scraped_submissions()
    assert scraper.scraped_submissions[submission_user1_no_replies.id]["parsed"] is True

def test_avoid_rescrape_submission(scraper, submission_user1_no_replies):
    scraper.add_scraped_submission(submission_user1_no_replies)
    scraper.scraped_submissions[submission_user1_no_replies.id]["parsed"] = True
    scraper.add_scraped_submission(submission_user1_no_replies)
    assert scraper.scraped_submissions[submission_user1_no_replies.id]["parsed"] is True

def test_avoid_reparse_submission(scraper, submission_user1_replies,redditor_user1):
    scraper.add_scraped_submission(submission_user1_replies)
    scraper.parse_scraped_submissions()
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 1
    scraper.parse_scraped_submissions()
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 1

def test_parse_subreddit(scraper, subreddit, redditor_user1):
    for submission in subreddit.top("all"):
        scraper.add_scraped_submission(submission)
    scraper.parse_scraped_submissions()
    assert scraper.replies_graph.number_of_nodes() == 1
    assert scraper.replies_graph.number_of_edges() == 1
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 1

def test_parse_user():
    pass

def test_nodes():
    pass

def test_edges():
    pass

def test_weights():
    pass