# Outline:
# - Find users in reddit comment thread
# - Go through their comment history
# - Find users they consistently reply to or are replied to by
# - Analyze data

from re import sub
import praw
from time import sleep

from prawcore import auth
import networkx as nx

reddit = praw.Reddit("FriendsNetwork")

def add_reply(replies_graph, reply_author, parent_author):
    #Track how many times each user responds to the same user
    #For example, if User X has 3 replies to User Y, User X -> User Y would have a weight of 3
    if (replies_graph.has_edge(reply_author, parent_author)):
        updated_weight = replies_graph.get_edge_data(reply_author, parent_author, key=0)['weight'] + 1
        replies_graph.add_edge(reply_author, parent_author, key=0, weight=updated_weight)
    else:
        replies_graph.add_edge(reply_author, parent_author, key=0, weight=1)
    return replies_graph

def parse_replies(parent_comment):
    #Generate new graph for each comment forest
    replies_graph = nx.MultiDiGraph()
    for reply in parent_comment.replies:
        #Deleted comments will have no author, so there's no point in parsing replies to it
        #There may be nested comments replying to each other, but it's still a waste of processing power
        if reply.author is None:
            continue
        replies_graph = add_reply(replies_graph, reply.author.name, parent_comment.author.name)
        #Check if there is a comment forest under the current comment
        if (len(reply.replies) != 0):
            sub_replies = parse_replies(reply)
            for reply_author,parent_author in sub_replies.edges():
                replies_graph = add_reply(replies_graph, reply_author, parent_author)
    return replies_graph

def parse_thread_for_redditors(submission):
    #Grab all the comments in the thread
    while True:
        try:
            submission.comments.replace_more()
            break
        except:
            print("Handling replace_more exception")
            sleep(1)
    
    #Generate graph of who replies to who and how many times
    replies_graph = nx.MultiDiGraph()
    for top_level_comment in submission.comments:
        if top_level_comment.author is None:
            continue
        #Parse each comment forest
        sub_replies = parse_replies(top_level_comment)
        #Combine each comment forest into the overall graph
        replies_graph = nx.compose(replies_graph, sub_replies)

    print("Finished generating graph. Displaying nodes then edges")
    for u,v,w in replies_graph.edges(data=True):
        print(F"Parent author: {v}| Reply author: {u} | Weight: {w}")

#for submission in reddit.subreddit("all").top(time_filter="day", limit=1):
submission = reddit.submission("pzrr9w")
print("Parsing thread...")
parse_thread_for_redditors(submission)