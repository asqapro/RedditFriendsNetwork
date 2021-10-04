# Outline:
# - Find users in reddit comment thread
# - Go through their comment history
# - Find users they consistently reply to or are replied to by
# - Analyze data

import praw
from time import sleep
import networkx as nx

class scraper:
    def __init__(self):
        self.replies_graph = nx.MultiDiGraph()
        self.scraped_submissions = {}
        self.scraped_redditors = {}

    def add_reply(self, reply_author, parent_author):
        #Track how many times each user responds to the same user
        #For example, if User X has 3 replies to User Y, User X -> User Y would have a weight of 3
        edge_weight = 1
        if (self.replies_graph.has_edge(reply_author, parent_author)):
            edge_weight = self.replies_graph.get_edge_data(reply_author, parent_author, key=0)['weight'] + 1
        self.replies_graph.add_edge(reply_author, parent_author, key=0, weight=edge_weight)

    def parse_replies(self, parent_comment):
        for reply in parent_comment.replies:
            if reply.author is None:
                continue
            if reply.author.name not in self.scraped_redditors:
                self.scraped_redditors[reply.author.name] = False
            self.add_reply(reply.author.name, parent_comment.author.name)
            self.parse_replies(reply)

    def parse_submission(self, submission):
        if self.scraped_submissions[submission.id] is True:
            return
        #Grab all the comments in the thread
        while True:
            try:
                submission.comments.replace_more()
                break
            except:
                print("Handling replace_more exception")
                sleep(1)
        
        for top_level_comment in submission.comments:
            #Deleted comments will have no author, so there's no point in parsing replies to it
            #There may be nested comments replying to each other, but it's still a waste of processing power
            if top_level_comment.author is None:
                continue
            if top_level_comment.author.name not in self.scraped_redditors:
                self.scraped_redditors[top_level_comment.author.name] = False
            self.parse_replies(top_level_comment)
        self.scraped_submissions[submission.id] = True

    def parse_redditor(self, redditor):
        if self.scraped_redditors[redditor.name] is True:
            return
        for comment in redditor.comments.new(limit=5):
            if comment.submission.id not in self.scraped_submissions:
                self.scraped_submissions[comment.submission.id] = False
            self.parse_submission(comment.submission)
        self.scraped_redditors[redditor.name] = True
        

reddit = praw.Reddit("FriendsNetwork")
example_submission = reddit.submission("pzrr9w")
example_user = reddit.redditor('asqapro')
thread_scraper = scraper()
#thread_scraper.parse_submission(submission)
thread_scraper.parse_redditor(example_user)
print("Finished generating graph. Displaying nodes then edges")
for u,v,w in thread_scraper.replies_graph.edges(data=True):
    print(F"Parent author: {v}| Reply author: {u} | Weight: {w}")