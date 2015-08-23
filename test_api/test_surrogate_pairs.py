# test_surrogate_pairs

import pytest
import random
import struct

import config
api = config.get_api()
import twitter

def make_surrogate_pair():
    """Generate one random surrogate pair."""
    # Add one character made up of one codepoint each from
    # (High Surrogates + High Private Use Surrogates) and Low Surrogates.
    # We expect each such pair to behave as a single high-codepoint
    # character.
    high_surrogates = ('D800', 'DBFF') # including High Private Use Surrogates
    high_surrogates = ('D840', 'D87E') # This covers mostly CJK.
    low_surrogates = ('DC00', 'DFFF')
    return (unicode_char(random.randint(
                int(high_surrogates[0], 16), int(high_surrogates[1], 16))) +
            unicode_char(random.randint(
                int(low_surrogates[0], 16), int(low_surrogates[1], 16)))
            )

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
tweet_prefix = 'Sample tweet with random surrogate-pair characters '
surrogate_pair_qty = 20
surrogate_pair_strings = []
for _ in range(argument_qty):
    # Choose random codepoints and convert to characters.
    surrogate_pair_strings.append(
            'from high and low surrogate-pair blocks, combined ' +
            ' '.join([make_surrogate_pair()
                for _ in range(surrogate_pair_qty)])
            )

params = {'argnames': 'tweet',
          'argvalues': [
              tweet_prefix + u'{}'.format(surrogate_pair_str).encode('utf-8')
              for surrogate_pair_str in surrogate_pair_strings
              ]
         }

params['ids'] = ['\n    ' + argvalue for argvalue in params['argvalues']]

####################

@pytest.mark.parametrize(**params)
def test_surrogate_pairs(tweet):
    # Post tweet. api.PostUpdate()
    status = api.PostUpdate(tweet)
    # Validate returned tweet: content and length.
    assert status.text == tweet.decode('utf-8')
    # Destroy tweet. api.DestroyStatus()
#    status2 = api.DestroyStatus(status.id)
    # Validate that tweet has been destroyed.
#    with pytest.raises(twitter.TwitterError):
#        assert api.DestroyStatus(status.id)
