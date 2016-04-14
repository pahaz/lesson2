import random
import string

__author__ = 'pahaz'


def get_random_string(
        length=12,
        alphabet=string.digits + string.ascii_letters
):
    """
    >>> s = get_random_string(11)
    >>> len(s) == 11
    True
    >>> get_random_string(4, 'q')
    'qqqq'
    """
    return ''.join(random.choice(alphabet) for _ in range(length))
