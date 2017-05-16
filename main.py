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
		print('ready>', 
		try:
			raw = input()
		# Allow user to quit with Ctrl+C
		except KeyboardInterrupt:
			return
		)

		# Tokenize() is in the lexer class so would be Lexer.Tokenize()
		# And need to import Lexer
		parser = Parser(Tokenize(raw), operatorPrecedence)

		while True:
			# If you hit EOF then stop
			if isinstance(parser.current, EOFToken):
				break
			if isinstance(parser.current, DefToken):
				parser.HandleDefinition()
			elif isinstance(parser.current, ExternToken):
				parser.HandleExtern()
			else:
				parser.HandleTopLevelExpression()

if __name__ == '__main__':
	main()
