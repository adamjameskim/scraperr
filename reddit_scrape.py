import argparse
import requests
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

        reddit = praw.Reddit("funky")
    parser = argparse.ArgumentParser()

    subredditArgHelp = 'The subreddit from which you wish to download the pictures'
    limitArgHelp = 'Limit the number of posts to download (default: 10)'
    periodArgHelp = ("The period from when to "
                     "download the pictures (default: day) -- options: day,"
                     " month, year, all")
    directoryArgHelp = ('The directory for the pictures'
                        'to be downloaded into (default: reddit-wallpapers/)')
    searchtermArgHelp = 'search term for subreddit'

    parser.add_argument('subreddit', help=subredditArgHelp, action='store')
    parser.add_argument('searchterm',help=searchtermArgHelp,action='store')
    parser.add_argument('-l', '--limit',     default=10, help=limitArgHelp,type=int, action='store')
    parser.add_argument('-d', '--directory', default='../reddit_downloads/',help=directoryArgHelp, action='store')
    args = parser.parse_args()

    return args,reddit

def get_reddit(args,reddit):
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

def main():
    
    args,reddit = get_args()
    urls,titles,upvotes = get_reddit(args,reddit)
    download_urls_requests(urls,titles,upvotes)

def regexed(x): 
    return re.sub(r'[^a-zA-Z0-9.+-]',' ',x)

def download_urls_requests(urls,titles,upvotes):
    for i,url in enumerate(urls):
        name = f'downloads/{upvotes[i]} - {titles[i]}.jpg'
        f=open(name,'wb')
        f.write(requests.get(url).content)
        f.close()
        print(url,name,'written')

if __name__ == "__main__":
    main()
