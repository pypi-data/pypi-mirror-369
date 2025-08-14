def reverse_string(s):
    """Reverses a given string."""
    return f'original string: {s} => {s[::-1]}'

def count_words(text):
    """Counts the number of words in a string."""
    #return len(text.split())
    #return len(text)
    return f'original text: {text} => {len(text)}'

def count_vowels(text):
    """Counts the number of vowels in a string."""
    vowels = "aeiouAEIOU"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    #return count
    return f'original text: {text} => count'

def max_char_count(string):
    max_char = ''
    max_count = 0
    for char in set(string):
        count = string.count(char)
        if count > max_count:
            max_count = count
            max_char = char
    return f'string:{string} => max char exist: {max_char}'

#print(max_char_count('apple'))
#print(reverse_string('hello'))
#print(count_words('hello'))
#print(count_vowels('hello'))