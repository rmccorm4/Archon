import Lexer
import Parser
import AbstractSyntaxTree

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
		try:
			raw = input('archon> ')
		# Allow user to quit with Ctrl+C
		except KeyboardInterrupt:
			break

		# Tokenize() is in the lexer class so would be Lexer.Tokenize()
		# And need to import Lexer
		parser = Parser.Parser(Lexer.Tokenize(raw), operatorPrecedence)

		while True:
			# If you hit EOF then stop
			if isinstance(parser.current, Lexer.EOFToken):
				break
			if isinstance(parser.current, Lexer.DefToken):
				parser.HandleDefinition()
			elif isinstance(parser.current, Lexer.ExternToken):
				parser.HandleExtern()
			else:
				parser.HandleTopLevelExpression()

	print('\n', AbstractSyntaxTree.g_llvm_module)

if __name__ == '__main__':
	main()
