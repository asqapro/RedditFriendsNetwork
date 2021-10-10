import praw

class tester:
    def __init__(self):
        self.reddit = praw.Reddit("FriendsNetwork")
        
    def test_parse_subreddit(self):
        pass

    def test_parse_submission(self):
        pass

    def test_parse_user(self):
        pass

    def test_nodes(self):
        pass

    def test_edges(self):
        pass

    def test_weights(self):
        pass

    def run_all_tests(self):
        self.test_parse_subreddit()
        self.test_parse_submission()
        self.test_parse_user()
        self.test_nodes()
        self.test_edges()
        self.test_weights()

if __name__ == "main":
    test_driver = tester()
    test_driver.run_all_tests()