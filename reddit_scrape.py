import argparse
import requests
import os
from datetime import datetime
import re
import sys
import praw
import prawcore
import shutil
import subprocess
import os
import errno

# http://www.storybench.org/how-to-scrape-reddit-with-python/
# https://stackoverflow.com/a/3173388

def get_args():

    parser = argparse.ArgumentParser()

    subredditArgHelp    = 'subreddit to search'
    searchtermArgHelp   = 'search term for subreddit'
    parser.add_argument('subreddit', help=subredditArgHelp, action='store')
    parser.add_argument('searchterm',help=searchtermArgHelp,action='store')
    
    return parser.parse_args()

def get_reddit(args,scope):
    reddit = praw.Reddit(scope)
    retrieved_posts = reddit.subreddit(args.subreddit).search(args.searchterm, 'top', 'all')
    urls,titles,upvotes=[],[],[]
    try:
        for post in retrieved_posts:
            if 'jpg' in post.url:
                urls.append(post.url)
                titles.append(regexed(post.title))
                upvotes.append(post.score)
        return urls,titles,upvotes

    except prawcore.ResponseException:
        print('An error occurred during authorisation. Please check that'
              'your Reddit app credentials are set correctly and try again.')
        sys.exit(-1)
    except prawcore.OAuthException:
        print('An error occurred during authorisation. Please check that'
              'your Reddit account credentials are set correctly and try again.')
        sys.exit(-2)
    except prawcore.NotFound:
        print('Failed to find a subreddit called "{}". Please check that'
              'the subreddit exists and try again.'.format(args.subreddit))
        sys.exit(-3)

def mk_download_dir(args):
    outdir = f'downloads _ {datetime.today().strftime("%Y-%m-%d")} _ {args.subreddit} _ {args.searchterm}'
    os.chdir('.')
    if os.path.isdir(outdir) == False: os.mkdir(outdir)
    return outdir

def regexed(x): 
    return re.sub(r'[^a-zA-Z0-9.+-]',' ',x)

def download_urls_requests(urls,titles,upvotes,outdir):
    for i,url in enumerate(urls):
        name = f'{outdir}/{upvotes[i]} - {titles[i]}.jpg'
        f=open(name,'wb')
        f.write(requests.get(url).content)
        f.close()
        print(url,name,'written')

    print(len(urls),'files written')

def main():
   
    # define scope
    scope = 'funky'

    # parse args
    args = get_args()
    
    # get urls, titles, upvote
    urls,titles,upvotes = get_reddit(args,scope)
    
    # build output directory
    outdir = mk_download_dir(args)

    # download images
    download_urls_requests(urls,titles,upvotes,outdir)

if __name__ == "__main__":
    main()
