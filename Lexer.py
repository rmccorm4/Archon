"""
Lexer reads source code character by character and sends tokens to parser

Do I need the following line uncommented?
#!/usr/bin/env python
"""

import re

# The lexer yields one of these types for each token.
class EOFToken(object): 
	pass

class DefToken(object): 
	pass

class ExternToken(object): 
	pass

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
    def __neq__(self, other):
        return not self == other

# Regular expressions that tokens and comments of our language.
REGEX_NUMBER = re.compile('[0-9]+(?:.[0-9]+)?')
REGEX_IDENTIFIER = re.compile('[a-zA-Z][a-zA-Z0-9]\ *')
REGEX_COMMENT = re.compile('#.*')

# Look into yield and why its used for this?
def Tokenize(string):
    while string: 
		# Ignore whitespace
        if string[0].isspace():
           string = string[1:]
           continue

		# Run regexes.
		comment_match = REGEX_COMMENT.match(string)
		number_match = REGEX_NUMBER.match(string)
		identifier_match = REGEX_IDENTIFIER.match(string)

		# Check if any of the regexes matched and yield
		# the appropriate result.
		if comment_match:
			comment = comment_match.group(0)
			string = string[len(comment):]

		# For numbers, we yield the captured match, converted to a float and
		# tagged with the appropriate token type:
		elif number_match:
			number = number_match.group(0)
			yield NumberToken(float(number))
			string = string[len(number):]

		# The identifier case is a little more complex. We have to check for
		# keywords to decide whether we have captured an identifier or a keyword:
		elif identifier_match:
			identifier = identifier_match.group(0)
			# Check if we matched a keyword.
			if identifier == 'def':
				yield DefToken()
			elif identifier == 'extern':
				yield ExternToken()
		  	else:
				yield IdentifierToken(identifier)
		  	string = string[len(identifier):]

		# Finally, if we haven't recognized a comment, a number of an identifier,
		# we yield the current character as an "unknown character" token. This is
		# used, for example, for operators like ``+`` or ``*``:
		else: # Yield the unknown character.
			yield CharacterToken(string[0])
		  	string = string[1:]

	# Once we're done with the loop, we return a final end-of-file token:
	yield EOFToken()
