__author__ = 'shaurya'

import tweepy
import chatery.constants
import datetime
import dateutil

from dateutil import parser as dateparse


def generate_twitter_access_object(key,secret):
    return {"key":key,"secret":secret}


def tweet(credentials, text, retweet):
    auth = tweepy.OAuthHandler(consumer_key=constants.CONSUMER_KEY, consumer_secret=constants.CONSUMER_SECRET)
    auth.set_access_token(credentials["key"],credentials["secret"])
    msg = text.replace("tweet:","").replace("RT:","")
    status = ""

    api = tweepy.API(auth)
    try:
        if retweet:
            status = api.retweet(msg)
        else:
            status = api.update_status(msg)
    except tweepy.TweepError as e:
        print(e.reason)

    return status

def to_iso8601(tz,when=None):
  if not when:
    when = datetime.datetime.now(tz)
  if not when.tzinfo:
    when = tz.localize(when)
  _when = when.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
  return _when[:-8] + _when[-5:] # remove microseconds


def from_iso8601(tz,when=None):
  _when = dateparse.parse(when)
  if not _when.tzinfo:
    _when = tz.localize(_when)
  else:
      _when = _when.astimezone(tz)
  return _when
