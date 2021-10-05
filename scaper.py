#TODO: 
#Important:
#
# - Investigate whether checks for repeat submissions / redditors are robust. Need to design test for it
# - Also investigate how deleted submissions coming from a redditor's profile are handled
# - Possibly change way parsed submissions are tracked to show the difference between a parsed and deleted submission
#
# - Continue to investigate way to show network graph in meaningful way
# - Continue to investigate efficient ways to store network graph to database / retrieve

import praw
from time import sleep, time
import networkx as nx

class reddit_scraper:
    def __init__(self):
        self.replies_graph = nx.MultiDiGraph()
        #Track submissions that have already been parsed to avoid wasting API requests
        self.scraped_submissions = {}
        #Track users that have already been parsed to avoid wasting API requests
        #Maybe add a lockout timeout in the future since users are likely to post more comments eventually
        self.scraped_redditors = {}

    def scrape_new_submissions(self):
        for submission in reddit.subreddit("all").top("hour", limit=100):
            if submission is not None:
                scraper.scraped_submissions[submission.id] = submission

    def add_reply(self, reply_author, parent_author):
        #Track how many times each user responds to the same user
        #For example, if User X has 3 replies to User Y, User X -> User Y would have a weight of 3
        edge_weight = 1
        if (self.replies_graph.has_edge(reply_author, parent_author)):
            edge_weight = self.replies_graph.get_edge_data(reply_author, parent_author, key=0)['weight'] + 1
        self.replies_graph.add_edge(reply_author, parent_author, key=0, weight=edge_weight)

    def parse_replies(self, parent_comment):
        for reply in parent_comment.replies:
            #Deleted comments will have no author, so there's no point in parsing replies to it
            #There may be nested comments replying to each other, but it's still a waste of processing power
            if reply.author is None:
                continue
            if reply.author.name not in self.scraped_redditors:
                self.scraped_redditors[reply.author.name] = reply.author
            self.add_reply(reply.author.name, parent_comment.author.name)
            self.parse_replies(reply)

    def parse_submission(self, submission):
        #Grab all the comments in the thread
        while True:
            try:
                submission.comments.replace_more()
                break
            except:
                print("Handling replace_more exception")
                sleep(1)
        
        for top_level_comment in submission.comments:
            if top_level_comment.author is None:
                continue
            if top_level_comment.author.name not in self.scraped_redditors:
                self.scraped_redditors[top_level_comment.author.name] = top_level_comment.author
            self.parse_replies(top_level_comment)
        self.scraped_submissions[submission.id] = None

    def parse_redditor(self, redditor):
        for comment in redditor.comments.new(limit=100):
            if comment.submission.id not in self.scraped_submissions:
                self.scraped_submissions[comment.submission.id] = comment.submission
        self.scraped_redditors[redditor.name] = None

    def parse_scraped_submissions(self):
        for submission in self.scraped_submissions.values():
            #Skip parsed submissions
            if submission is None:
                continue
            self.parse_submission(submission)

    def parse_scraped_redditors(self):
        for redditor in self.scraped_redditors.values():
            #Skip parsed redditors
            if redditor is None:
                continue
            self.parse_redditor(redditor)

    def display_network(self):
        for u,v,w in self.replies_graph.edges(data=True):
            print(F"Parent author (P): {v}| Reply author (R): {u} | Weight (# of times R has replied to P overall): {w['weight']}")
        

def example_run():
    reddit = praw.Reddit("FriendsNetwork")
    scraper = reddit_scraper()

    example_submission = reddit.submission("pzrr9w")
    example_user = reddit.redditor('asqapro')

    scraper.parse_submission(example_submission)
    scraper.parse_redditor(example_user)

if __name__ == '__main__':
    reddit = praw.Reddit("FriendsNetwork")
    scraper = reddit_scraper()
    #Only grab new posts every 3600 seconds (1 hour)
    refresh_wait = 3600
    while True:
        refresh_timer_start = time()
        scraper.scrape_new_submissions()
        scraper.parse_scraped_submissions()
        scraper.parse_scraped_redditors()
        refresh_timer_end = time()
        refresh_duration = refresh_timer_end - refresh_timer_start
        scraper.display_network()
        input("Pausing...")
        if refresh_duration < refresh_wait:
            sleep(refresh_wait - refresh_duration)

    
