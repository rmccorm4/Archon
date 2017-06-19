from llvm.core import Module, Constant, Type, Function, Builder, FCMP_ULT

# LLVM module which holds all the IR code
g_llvm_module = Module.new('Archon jit')

# LLVM instruction builder. Created whenever a new function is entered
g_llvm_builder = None

# Dictionary that keeps track of which values are defined in the current scope
# and their LLVM representations
g_name_values = {}

# The function optimization passes manager.
g_llvm_pass_manager = FunctionPassManager.new(g_llvm_module)

# Base class for all expression nodes.
class ExpressionNode(object): 
	pass

# Expression class for numeric literals like "1.0"
class NumberExpressionNode(ExpressionNode):
	def __init__(self, value):
		self.value = value
	def CodeGen(self):
		# Here is where things can be changed for types other than double
		# This returns a 'ConstantFloatingPoint' number from the
		# llvm.core.Constant class
		return Constant.real(Type.double(), self.value)

# Expression class for a variable
class VariableExpressionNode(ExpressionNode):
	def __init__(self, name):
		self.name = name
	# This only really supports function arguments at the moment
	# Local variables / loop variables will be introduced later
	def CodeGen(self):
		if self.name in g_named_values:
			return g_named_values[self.name]
		else:
			raise RuntimeError('Unknown variable name: ' + self.name)

# Expression class for binary operator
class BinaryOperatorExpressionNode(ExpressionNode):
	def __init__(self, operator, left, right):
		self.operator = operator
		self.left = left
		self.right = right
	def CodeGen(self):
		left = self.left.CodeGen()
		right = self.right.CodeGen()

		# builder.f<operation> is llvm's builtin floating point operations
		# TODO: Lookup the string args at the end of each instruction below
		if self.operator == '+':
			return g_llvm_builder.fadd(left, right, 'addtmp')
		elif self.operator == '-':
			return g_llvm_builder.fsub(left, right, 'subtmp')
		elif self.operator == '*':
			return g_llvm_build.fmul(left, right, 'multmp')
		# This should be changed later on when ints are supported to return 0/1
		elif self.operator == '<':
			result = g_llvm_build.fcmpl(FCMP_ULT, left, right, 'cmptmp')
			# Convert bool 0/1 to 0.0/1.0
			return g_llvm_builder.uitofp(result, Type.double(), 'booltmp')
		else:
			raise RuntimeError('Unknown binary operator.')

# Expression class for function calls
class CallExpressionNode(ExpressionNode):
	def __init(self, callee, args):
		self.callee = callee
		self.args = args
	def CodeGen(self):
		# Look up name in global module table
		callee = g_llvm_module.get_function_named(self.callee)

		# Check for argument mismatch error
		if len(callee.args) != len(self.args):
			raise RuntimeError('Incorrect number of arguments passed.')

		arg_values = [i.CodeGen() for i in self.args]

		return g_llvm_builder.call(callee, arg_values, 'calltmp')

# "Turing-complete" requires having control flow

# This class represents the "prototype" for a function, which captures
# its name and arguments
class PrototypeNode(object):
	def __init__(self, name, args):
		self.name = name
		self.args = args
	def CodeGen(self):
		# Make the function type, ex: double(double, double).
		function_type = Type.function( Type.double(),
									   [Type.double()] * len(self.args), False)

		function = Function.new(g_llvm_module, function_type, self.name)

		# If the name conflicts, already something with the same name
		# If it has a body, don't allow redefinition or re-extern
		if function.name != self.name:
			function.delete()
			function = g_llvm_module.get_function_named(self.name)

			# If the function already has a body, reject it
			if not function.is_declaration:
				raise RuntimeError('Redefinition of function.')

			# THIS IS ESSENTIALLY FUNCTION OVERLOADING, MAYBE CHANGE IN FUTURE
			# If function took different number of args, reject it
			if len(callee.args) != len(self.args):
				raise RuntimeError('Redeclaration of function with different' +
									' number of args')

			# Set names for all args and add them to var symbol table
			for arg, arg_name in zip(function.args, self.args):
				arg.name = arg_name
				# add args to variable symbol table
				g_named_values[arg_name] = arg
			
			return function

"""
Functions are typed by count of arguments since currently only type is floats
"""
# This class represents a function definition
class FunctionNode(object):
	def __init__(self, prototype, body):
		self.prototype = prototype
		self.body = body
	def CodeGen(self):
		# Clear scope
		g_named_values.clear()

		# Create function object
		function = self.prototype.CodeGen()

		# LOOK INTO WHAT THIS DOES, NOT SURE
		# Create new basic block to start insertion into
		block = function.append_basic_block('entry')
		global g_llvm_builder
		g_llbm_builder = Builder.new(block)

		# Finish off the function
		try:
			return_value = self.body.CodeGen()
			g_llvm_builder.ret(return_value)

			# Validate the generated code, check for consistency
			function.verify()
		except:
			function.delete()
			raise

		return function

