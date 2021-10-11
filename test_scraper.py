import pytest
import praw
from scraper import reddit_scraper

#Current dataset:
# 4 submissions (and 1 deleted)
#    r/FriendsNetwork Lounge (autocreated)
#      No comments
#    [User1]
#      No comments
#    [User1][Replies]
#      1 top level comment
#      1 reply
#      User1 replied to User1 2 times total
#    [User1][Deleted Replies]
#      4 top level comments (and 2 deleted)
#      1 reply (and 3 with deleted parents so are not be counted)
#      User1 replied to User1 5 times total
#    [User1][Replies][Deleted]
#      2 top level comments
#      1 reply
#      User1 replied to User1 1 times total

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
def submission_user1_deleted_replies(reddit):
    return reddit.submission("q5q7s3")

@pytest.fixture
def submission_user1_deleted_submission(reddit):
    return reddit.submission("q5s94r")

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
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 2

def test_parse_submission_no_replies(scraper, submission_user1_no_replies):
    scraper.parse_submission(submission_user1_no_replies)
    assert scraper.replies_graph.number_of_nodes() == 0
    assert scraper.replies_graph.number_of_edges() == 0

def test_parse_submission_deleted_replies(scraper, submission_user1_deleted_replies, redditor_user1):
    scraper.parse_submission(submission_user1_deleted_replies)
    assert scraper.replies_graph.number_of_nodes() == 1
    assert scraper.replies_graph.number_of_edges() == 1
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 5
    pass

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
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 2
    scraper.parse_scraped_submissions()
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 2

def test_parse_subreddit(scraper, subreddit, redditor_user1):
    for submission in subreddit.top("all"):
        scraper.add_scraped_submission(submission)
    scraper.parse_scraped_submissions()
    assert scraper.replies_graph.number_of_nodes() == 1
    assert scraper.replies_graph.number_of_edges() == 1
    assert scraper.replies_graph.get_edge_data(redditor_user1.name, redditor_user1.name, key=0)["weight"] == 7

def test_scrape_redditor(scraper, redditor_user1):
    scraper.add_scraped_redditor(redditor_user1)
    assert redditor_user1.name in scraper.scraped_redditors

def test_parse_redditor(scraper, redditor_user1, submission_user1_replies):
    scraper.parse_redditor(redditor_user1)
    assert submission_user1_replies.id in scraper.scraped_submissions

def test_parse_redditor_deleted_post(scraper, redditor_user1, submission_user1_deleted_submission):
    scraper.parse_redditor(redditor_user1)
    assert submission_user1_deleted_submission.id in scraper.scraped_submissions

def test_mark_redditor_parsed(scraper, redditor_user1):
    scraper.add_scraped_redditor(redditor_user1)
    scraper.parse_scraped_redditors()
    assert scraper.scraped_redditors[redditor_user1.name]["parsed"] is True

def test_avoid_reparse_redditor(scraper, redditor_user1, submission_user1_replies):
    scraper.add_scraped_redditor(redditor_user1)
    scraper.parse_scraped_redditors()
    scraper.parse_scraped_submissions()
    assert scraper.scraped_submissions[submission_user1_replies.id]["parsed"] is True
    scraper.parse_scraped_redditors()
    assert scraper.scraped_submissions[submission_user1_replies.id]["parsed"] is True