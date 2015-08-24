# test_surrogate_pairs

import pytest
import random
import struct
import unicodedata

import config
api = config.get_api()
import twitter

high_surrogates = ('D800', 'DBFF') # including High Private Use Surrogates
high_surrogates_cjk = ('D840', 'D87E') # This covers mostly CJK.
low_surrogates = ('DC00', 'DFFF')

def make_surrogate_pair():
    """Generate one random surrogate pair."""
    # Add one character made up of one codepoint each from
    # (High Surrogates + High Private Use Surrogates) and Low Surrogates.
    # We expect each such pair to behave as a single high-codepoint
    # character.
    return (unicode_char(random.randint(
                int(high_surrogates_cjk[0], 16),
                int(high_surrogates_cjk[1], 16))) +
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
argument_qty = 1
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

params = {
        'argnames': 'tweet',
        'argvalues': [
              tweet_prefix + u'{}'.format(surrogate_pair_str).encode('utf-8')
              for surrogate_pair_str in surrogate_pair_strings
              ]
         }
params['ids'] = ['\n    ' + argvalue for argvalue in params['argvalues']]

unmatched_chars = set()
# Choose high or low surrogate block at random, then choose one random char.
while len(unmatched_chars) < argument_qty:
    collection = random.choice([high_surrogates, low_surrogates])
    char = random.randint( int(collection[0], 16), int(collection[1], 16))
    unmatched_chars.add(unicode_char(char))
half_pair_params = {
        'argnames': 'tweet, unmatched_char',
        'argvalues': [
            ('''Sample tweet with unmatched surrogate pair component: {} '''
             '''({} at left).'''.
             format(char.encode('utf-8'), repr(char)), char)
             for char in unmatched_chars]
        }
half_pair_params['ids'] = ['\n    ' + argvalue[0]
        for argvalue in half_pair_params['argvalues']]

####################

@pytest.mark.parametrize(**params)
def test_surrogate_pairs(tweet):
    # Post tweet. api.PostUpdate()
    status = api.PostUpdate(tweet)
    # Validate returned tweet: content and length.
    assert status.text == tweet.decode('utf-8')
    # Destroy tweet. api.DestroyStatus()
    status2 = api.DestroyStatus(status.id)
    # Validate that tweet has been destroyed.
    with pytest.raises(twitter.TwitterError):
        assert api.DestroyStatus(status.id)

@pytest.mark.parametrize(**half_pair_params)
def test_half_surrogate_pairs(tweet, unmatched_char):
    # Post tweet. api.PostUpdate()
    status = api.PostUpdate(tweet)
    # Validate returned tweet: content and length.
    assert unmatched_char not in status.text
    assert unichr(int('FFFD', 16)) in status.text
    # Destroy tweet. api.DestroyStatus()
    status2 = api.DestroyStatus(status.id)
    # Validate that tweet has been destroyed.
    with pytest.raises(twitter.TwitterError):
        assert api.DestroyStatus(status.id)
