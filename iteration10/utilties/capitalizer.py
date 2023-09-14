# this utility capitalizes the first letter of every non function word in a string
def capitalize_non_function_words(s):
    function_words = {'and', 'of', 'or', 'with', 'the', 'a', 'an', 'in', 'is', 'it', 'for', 'on', 'at'}
    return ' '.join(word if word in function_words else word.capitalize() for word in s.lower().split())