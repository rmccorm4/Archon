# Base class for all expression nodes.
class ExpressionNode(object): pass

# Expression class for numeric literals like "1.0"
class NumberExpressionNode(ExpressionNode):
	def __init__(self, value):
		self.value = value

# Expression class for a variable
class VariableExpressionNode(ExpressionNode):
	def __init__(self, name):
		self.name = name

# Expression class for binary operator
class BinaryOperatorExpressionNode(ExpressionNode):
	def __init__(self, operator, left, right):
		self.operator = operator
		self.left = left
		self.right = right

# Expression class for function calls
class CallExpressionNode(ExpressionNode):
	def __init(self, callee, args):
		self.callee = callee
		self.args = args

# "Turing-complete" requires having control flow

# This class represents the "prototype" for a function, which captures
# its name and arguments
class PrototypeNode(object):
	def __init__(self, name, args):
		self.name = name
		self.args = args


"""
Functions are typed by count of arguments since currently only type is floats
"""
# This class represents a function definition
class FunctionNode(object):
	def __init__(self, prototype, body):
		self.prototype = prototype
		self.body = body


################ PARSER ##################
class Parser(object):
	def __init__(self, tokens, binop_precedence):
		self.tokens = tokens
		self.binop_precedence = binop_precedence
		self.Next()

	# Provide a simple token buffer.
	# Parser.current is the current token being looked at by parser
	# Parser.Next() reads another token from lexer and updates parser.current
	def Next(self):
		self.current = self.tokens.next()

	# Handle expressions with numbers
	def ParseNumberExpr(self):
		result = NumberExpressionNode(self.current.value)
		# consume the number
		self.Next()
		return result

	# Handle expressions with parentheses
	def ParseParenExpr(self):
		# eat '('
		self.Next()
		contents = self.ParseExpression()
		if self.current != CharacterToken(')'):
			raise RuntimeError('Exprected ")".')
		# eat ')'
		self.Next()
		return contents

	# Handling variable references and function calls
	def ParseIdentifierExpr(self):
		identifierName = self.current.name
		# eat identifier
		self.Next()

		# If identifier not followed parentheses, then its a variable
		if self.current != CharacterToken('('):
			return VariableExpressionNode(identifierName)

		# If identifier followed by parentheses, its a function call
		# eat '('
		self.Next()
		args = []
		if self.current != CharacterToken(')'):
			while True:
				args.append(self.ParseExpression())
				# If there are no more arguments
				if self.current == CharacterToken(')'):
					break
				# If there was another token without a comma separator
				elif self.current != CharacterToken(','):
					raise RuntimeError('Expected ")" or "," in argument list.')
				self.Next()
		
		# eat ')'
		self.Next()
		return CallExpressionNode(identifierName, args)
	
	# Helper function to wrap everything into one entry point
	def ParsePrimary(self):
		if isinstance(self.current, IdentifierToken):
			return self.ParseIdentifierExpr()
		elif isinstance(self.current, NumberToken):
			return self.ParseNumberExpr()
		elif self.current == CharacterToken(')'):
			return self.ParseParenExpr()
		else:
			raise RuntimeError('Unknown token when expecting an expression.')

	def ParseExpression(self):
		left = self.ParsePrimary()
		return self.ParseBinOpRHS(left, 0)

	def ParseBinOpRHS(self, left, leftPrecedence):
		#if this is a binary operator, find it's precedence
		while True:
			precedence = self.GetCurrentTokenPrecedence()
			# If current has less precedence than left, return left
			if precedence < leftPrecedence:
				return left

			binaryOperator = self.current.char
			# Eat the operator
			self.Next()
			# Parse the primary expression after binary operator
			right = self.ParsePrimary()
			
			nextPrecedence = self.GetCurrentTokenPrecedence()
			if precedence < nextPrecedence:	
				# if body omitted?
				right = self.ParseBinOpRHS(right, precedence + 1)

			# Merge left and right
			left = BinaryOperatorExpressionNode(binaryOperator, left, right)

	# Gets precedence of current token, or -1 if not an operator
	def GetCurrentTokenPrecedence(self):
		if isinstance(self.current, CharacterToken):
			# default value = -1 if char not in operator dictionary
			return self.binop_precedence.get(self.current.char, -1)
		else:
			return -1



# Driver code		
def main():
	# Setup standard binary operators
	# 1 is lowest possible precedence, 40 is highest
	operatorPrecedence = {
		'<': 10, 
		'+': 20, 
		'-': 20, 
		'*': 40
	}

	# Run the main 'interpreter loop'
	while True:
		# ...?
		# raw would be some text file to process?
		# Tokenize() is in the lexer class so would be Lexer.Tokenize()
		parser = Parser(Tokenize(raw), operatorPrecedence)
