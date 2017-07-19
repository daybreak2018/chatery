__author__ = 'shaurya'

import tweepy
import constants

def generate_twitter_access_object(key,secret):
    return {"key":key,"secret":secret}


def tweet(credentials, text, retweet):
    auth = tweepy.OAuthHandler(consumer_key=constants.CONSUMER_KEY, consumer_secret=constants.CONSUMER_SECRET)
    auth.set_access_token(credentials["key"],credentials["secret"])
    msg = text.replace("tweet:","").replace("RT:","")

    api = tweepy.API(auth)
    try:
        if retweet:
            status = api.retweet(msg)
        else:
            status = api.update_status(msg)
    except tweepy.TweepError as e:
        print(e.reason)
    return status