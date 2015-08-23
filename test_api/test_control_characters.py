# test_control_characters

import pytest
import random
import struct

import config
api = config.get_api()
import twitter

def make_control_character():
    """Generate one random control character."""
    # Add one character made up of one codepoint each from
    # (High Surrogates + High Private Use Surrogates) and Low Surrogates.
    # We expect each such pair to behave as a single high-codepoint
    # character.
    controls = ('0000', '001F')
    return [unicode_char(char)
            for char in range(int(controls[0], 16), int(controls[1], 16)+1)]

def unicode_char(n):
    """Extend `unichr` for all possible Unicode values (n)."""
    try:
        return unichr(n)
    except ValueError:
        # Generate bytes object packed as int.
        bytes_object = struct.pack('i', n)
        # Return decoded w/ utf-32 codec.
        return bytes_object.decode('utf-32')

####################
# Create parameters
argument_qty = 5
tweet_prefix = 'Sample tweet with random control character '
control_strings = make_control_character()

print control_strings

params = {'argnames': 'tweet',
          'argvalues': [
              tweet_prefix + u'{} (at left)'.
              format(control_str.encode('utf-8'))
              for control_str in control_strings
              ]
         }

params['ids'] = ['\n    ' + repr(argvalue) for argvalue in params['argvalues']]

####################

@pytest.mark.xfail
@pytest.mark.parametrize(**params)
def test_controls(tweet):
    # Post tweet. api.PostUpdate()
    status = api.PostUpdate(tweet)
    # Validate returned tweet: content and length.
    assert status.text == tweet.decode('utf-8')
    # Destroy tweet. api.DestroyStatus()
#    status2 = api.DestroyStatus(status.id)
    # Validate that tweet has been destroyed.
#    with pytest.raises(twitter.TwitterError):
#        assert api.DestroyStatus(status.id)
