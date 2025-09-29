import re


def is_palindrome(s: str) -> bool:
    """
    Check if a given string is a palindrome.

    A palindrome is a string that reads the same forwards and backwards.
    This function ignores case, spaces, and punctuation when checking.

    Args:
        s: The string to check

    Returns:
        True if the string is a palindrome, False otherwise.
        Empty strings are considered palindromes.

    Examples:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("Racecar")
        True
        >>> is_palindrome("A man, a plan, a canal: Panama")
        True
        >>> is_palindrome("hello")
        False
        >>> is_palindrome("")
        True
    """
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    return cleaned == cleaned[::-1]


def find_longest_word(sentence: str) -> str | None:
    """
    Find and return the longest word in a sentence.

    Words are extracted by removing common punctuation. If multiple words
    have the same maximum length, the first one encountered is returned.

    Args:
        sentence: The sentence to analyze

    Returns:
        The longest word in the sentence, or None if the sentence is empty
        or contains no valid words.

    Examples:
        >>> find_longest_word("The quick brown fox")
        'quick'
        >>> find_longest_word("Hello, world!")
        'Hello'
        >>> find_longest_word("I love Python programming")
        'programming'
        >>> find_longest_word("")
        None
        >>> find_longest_word("!!!...")
        None
    """
    if not sentence or not sentence.strip():
        return None

    words = re.findall(r'\b[a-zA-Z0-9]+\b', sentence)

    if not words:
        return None

    longest = max(words, key=len)
    return longest