class Parser(object):
	def __init__(self, tokens, binop_precedence):
		self.tokens = tokens
		self.binop_precedence = binop_precedence
		self.Next()

	# Provide a simple token buffer.
	# Parser.current is the current token being looked at by parser
	# Parser.Next() reads another token from lexer and updates parser.current
	def Next(self):
		self.current = next(self.tokens)

	# Gets precedence of current token, or -1 if not an operator
	def GetCurrentTokenPrecedence(self):
		if isinstance(self.current, CharacterToken):
			# default value = -1 if char not in operator dictionary
			return self.binop_precedence.get(self.current.char, -1)
		else:
			return -1
	
	# Handling variable references and function calls
	def ParseIdentifierExpr(self):
		identifierName = self.current.name
		# eat identifier
		self.Next()

		# If identifier not followed by parentheses, then its a variable
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

	def ParseExpression(self):
		left = self.ParsePrimary()
		return self.ParseBinOpRHS(left, 0)

	def ParsePrototype(self):
		# what is IdentifierToken? class variable?
		if not isinstance(self.current, IdentifierToken):
			raise RuntimeError('Expected function name in prototype.')

		functionName = self.current.name
		# eat function name
		self.Next()

		if self.current != CharacterToken('('):
			raise RuntimeError('Expected "(" in prototype.')
		# eat '('
		self.Next()

		argNames = []
		while isinstance(self.current, IdentifierToken):
			argNames.append(self.current.name)
			self.Next()

		if self.current != CharacterToken(')'):
			raise RuntimeError('Expected ")" in prototype.')

		# Success. Eat ')'
		self.Next()	
		return PrototypeNode(functionName, argNames)

	def ParseDefinition(self):
		# Eat def
		self.Next()
		proto = self.ParsePrototype()
		body = self.ParseExpression()
		return FunctionNode(proto, body)
	
	def ParseTopLevelExpr(self):
		proto = PrototypeNode('', [])
		return FunctionNode(proto, self.ParseExpression())

	def ParseExtern(self):
		# Eat extern
		self.Next()
		return self.ParsePrototype()

	# Top-level parsing
	def HandleDefinition(self):
		self.Handle(self.ParseDefinition, 'Parsed a function definition.')

	def HandleExtern(self):
		self.Handle(self.ParseExtern, 'Parsed an extern.')

	def HandleTopLevelExpression(self):
		self.Handle(self.ParseTopLevelExpr, 'Parsed a top-level expression.')

	def Handle(self, function, message):
		try:
			function()
			print(message)
		except Exception as error:
			print('Error:', error)
			try:
				# Skip for error recovery (what does this mean?)
				self.Next()
			except:
				pass
