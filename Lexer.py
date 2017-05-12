"""
Lexer reads source code character by character and sends tokens to parser
"""

import re

# The lexer yields one of these types for each token.
class EOFToken(object): pass

class DefToken(object): pass

class ExternToken(object): pass

class IdentifierToken(object):
    def __init__(self, name):
        self.name = name

class NumberToken(object):
    def __init__(self, value):
        self.value = value

class CharacterToken(object):
    def __init__(self, char):
        self.char = char
    def __eq__(self, other):
		# first check they're same type, then check value
        return isinstance(other, CharacterToken) and self.char == other.char
    def __ne__(self, other):
        return not self == other

# Regular expressions that tokens and comments of our language.
REGEX_NUMBER = re.compile('[0-9]+(?:.[0-9]+)?')
REGEX_IDENTIFIER = re.compile('[a-zA-Z][a-zA-Z0-9]\ *')
REGEX_COMMENT = re.compile('#.*')

def Tokenize(string):
    while string: 
		# Ignore whitespace
        if string[0].isspace():
           string = string[1:]
           continue
