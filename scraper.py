#TODO: 
#Important:
#
# - Investigate whether checks for repeat submissions / redditors are robust. Need to design test for it
#
# - Continue to investigate way to show network graph in meaningful way
# - Continue to investigate efficient ways to store network graph to database / retrieve

import praw
from time import sleep, time
import networkx as nx
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation
import re

class reddit_scraper:
    def __init__(self):
        self.reddit = praw.Reddit("FriendsNetwork")

        self.replies_graph = nx.MultiDiGraph()
        #Track submissions that have already been parsed to avoid wasting API requests
        self.scraped_submissions = {}
        #Track users that have already been parsed to avoid wasting API requests
        #Maybe add a lockout timeout in the future since users are likely to post more comments eventually
        self.scraped_redditors = {}

    def count_words(self, body_as_markdown):
        #Strip reddit markdown links from comments
        #Example: `[data][https://data.com]` becomes `data`
        #Thanks to u/anon_smithsonian for the snippet (https://www.reddit.com/r/redditdev/comments/4s1z3r/check_for_a_link_within_squared_brackets/d56dtay/)
        markdown_link_pattern = r'(\[)([^\]()#\n]+)\]\(([^\]()#\n]+)\)'
        markdown_link_regex = re.compile(markdown_link_pattern, flags=re.IGNORECASE)
        msg_links = markdown_link_regex.findall(body_as_markdown)
        if msg_links:
            body_as_markdown = markdown_link_regex.sub(r'\g<2>', body_as_markdown)

        translationTable = str.maketrans("", "", punctuation)

        body_soup = BeautifulSoup(body_as_markdown, features='html.parser')
        body_text = body_soup.get_text()

        body_text = body_text.translate(translationTable).lower()
        split_body = re.split(' *\n+ *|\s+',body_text)
        count_of_words = Counter(split_body)
        print(count_of_words)
        input("Pausing...")

    def scrape_new_submissions(self, count):
        for submission in self.reddit.subreddit("all").top("hour", limit=count):
            self.add_scraped_submission(submission)

    def add_scraped_submission(self, submission):
        #Skip deleted submissions
        if submission is None:
            return
        #Skip scraped submissions
        if submission.id in self.scraped_submissions:
            return
        self.scraped_submissions[submission.id] = {"submission": submission, "parsed": False}

    def add_scraped_redditor(self, redditor):
        #Skip deleted redditors
        if redditor is None:
            return
        #Skip parsed redditors  
        if redditor.name in self.scraped_redditors:
            return
        self.scraped_redditors[redditor.name] = {"redditor": redditor, "parsed": False}

    def add_reply(self, reply_author, parent_author):
        #Track how many times each user responds to the same user
        #For example, if User X has 3 replies to User Y, User X -> User Y would have a weight of 3
        edge_weight = 1
        if (self.replies_graph.has_edge(reply_author, parent_author)):
            edge_weight = self.replies_graph.get_edge_data(reply_author, parent_author, key=0)['weight'] + 1
        self.replies_graph.add_edge(reply_author, parent_author, key=0, weight=edge_weight)

    def parse_replies(self, comment):
        for reply in comment.replies:
            #Skip deleted replies
            if reply.author is None:
                continue
            self.add_scraped_redditor(reply.author)
            self.add_reply(reply.author.name, comment.author.name)
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
        for comment in submission.comments:
            #Skip deleted comments
            if comment.author is None:
                continue
            if submission.author is not None:
                self.add_reply(submission.author.name, comment.author.name)
            self.add_scraped_redditor(comment.author)
            self.parse_replies(comment)

    def parse_redditor(self, redditor):
        for comment in redditor.comments.new(limit=100):
            self.add_scraped_submission(comment.submission)
            self.count_words(comment.body)

    def parse_scraped_submissions(self):
        for submission, metadata in self.scraped_submissions.items():
            #Skip parsed submissions
            if metadata["parsed"]:
                continue
            self.parse_submission(metadata["submission"])
            metadata["parsed"] = True

    def parse_scraped_redditors(self):
        for redditor, metadata in self.scraped_redditors.items():
            #Skip parsed redditors
            if metadata["parsed"]:
                continue
            self.parse_redditor(metadata["redditor"])
            metadata["parsed"] = True

    def display_network(self):
        for u,v,w in self.replies_graph.edges(data=True):
            print(F"Parent author (P): {v}| Reply author (R): {u} | Weight (# of times R has replied to P overall): {w['weight']}")

if __name__ == '__main__':
    scraper = reddit_scraper()
    #Only grab new posts every 3600 seconds (1 hour)
    refresh_wait = 3600
    while True:
        refresh_timer_start = time()
        scraper.scrape_new_submissions(10)
        scraper.parse_scraped_submissions()
        scraper.parse_scraped_redditors()
        refresh_timer_end = time()
        refresh_duration = refresh_timer_end - refresh_timer_start
        scraper.display_network()
        input("Pausing...")
        if refresh_duration < refresh_wait:
            sleep(refresh_wait - refresh_duration)