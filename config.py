import ConfigParser
import os
import twitter

class TweetRc(object):
    """Get options from .tweetrc file."""
    def __init__(self):
        self._config = None

    def GetConsumerKey(self):
        return self._GetOption('consumer_key')

    def GetConsumerSecret(self):
        return self._GetOption('consumer_secret')

    def GetAccessKey(self):
        return self._GetOption('access_key')

    def GetAccessSecret(self):
        return self._GetOption('access_secret')

    def _GetOption(self, option):
        try:
            return self._GetConfig().get('Tweet', option)
        except:
            return None

    def _GetConfig(self):
        if not self._config:
            self._config = ConfigParser.ConfigParser()
            self._config.read(os.path.expanduser('~/.tweetrc'))
        return self._config

def get_api():
    conf = TweetRc()._GetConfig()
    return twitter.Api(consumer_key=conf.get('Tweet', 'consumer_key'),
                       consumer_secret=conf.get('Tweet', 'consumer_secret'),
                       access_token_key=conf.get('Tweet', 'access_key'),
                       access_token_secret=conf.get('Tweet', 'access_secret')
                       )


