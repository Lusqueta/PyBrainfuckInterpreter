
import os
from time import time

class Byte():

	def __add__(self, other):

		if (type(other) == int):
			self.value = (((self.value + other) % self.__max) - 1) % self.__max + 1
			return self

		raise(f"Invalid type: {type(other)}")

	def __sub__(self, other): # Can do better

		if(type(other) == int):

			if(self.value - other < self.__min):
				self.value = (self.__max - (other % 255) + 1)
				return self
			
			self.value = self.value - other

			return self

		raise(f"Invalid type: {type(other)}")

	def __str__(self):
		return f"{self.value}"



	def __init__(self, number = 0):

		# Max = binary 11111111 -> 255
		self.__max = 255
		self.__min = 0

		self.value = number % 255



class Interpreter():

	@staticmethod
	def sanitize(fd, debug = False):

		if debug: init = time() # Get's time to debug

		sanitized = ""
		acceptable = "+-.,[]<>@#"  # Ugly.
		code = ""
		readBuffer = b'Anything' # Anything

		while(readBuffer):
			readBuffer = os.read( fd, 1024 ).decode("utf-8") # Reads and decode 1MB

			for char in readBuffer:
				if char in acceptable:
					sanitized += char

		if debug:		# Prints elapsed time and sanitezed code
			end = time()
			print(f"Sanitize finished in [{end - init}s]")
			print(f"Code:\n\t -> {sanitized}")

		return sanitized

	@staticmethod
	def checkSyntax(code): # Code needs to be text

		char = 0
		length = len(code)

		loops = []

		while(char < length):
			if(code[char] == '[' or code[char] == ']'):
				loops.append((code[char], char))
			char += 1

		keys = ''.join([l[0] for l in loops])

		while(keys != ''):
			if not "[]" in keys: break
			keys = keys.replace("[]", '', 1)
		
		if keys:
			return False
		return True

	@staticmethod
	def run(code, bufferSize = 30000, debug = False): # Can do better

		def getNext(code, count):

			code = code[count:]

			cSize = len(code)
			pChar = 0

			stack = 0

			while pChar < cSize:

				c = code[pChar]

				if c == '[':
					stack += 1

				elif c == ']':

					stack -= 1

					if stack == 0:
						return count + pChar

				pChar += 1


			raise(Exception("IDK"))

		def dump(loop, memory, pointer, dumpCount):

			memoryString = f"POINTER = {pointer}\n"
			lineBytes = 16
			memPos = 0x0
			last = 0

			lastOne = 0
			if not (len(memory) % lineBytes) == 0:
				lastOne = len(memory) % lineBytes

			toLoop = len(memory) // lineBytes

			for i in range(toLoop):

				array = [byte.value for byte in memory[last:last + lineBytes]]
				decoded = ""

				for b in array:

					if b < 32:
						decoded += '.'

					else:
						decoded += chr(b)

				memoryString += f"\t{hex(memPos)} \t"
				memoryString += f"{'	'.join(str(b) for b in array)}"
				memoryString += f"\t{decoded}"
				memoryString += '\n'

				last += lineBytes
				memPos += lineBytes

			if lastOne:

				array = [byte.value for byte in memory[last:last + lastOne]]
				decoded = ""

				for b in array:
					if b < 32:
						decoded += '.'
					else:
						decoded += chr(b)

				memoryString += f"\t{hex(memPos)} \t"
				memoryString += f"{'	'.join(str(b) for b in array)}"
				memoryString += f"\t{decoded}"
				memoryString += '\n'


			string = f'''dump_{dumpCount}
PYTHON BRAINFUCK INTERPRETER MEMORY DUMP
TIME: {time()}
LOOP: {loop}

MEMORY:
{memoryString}'''

			return string



		dumpEveryLine = False
		if code[0] == '@':		## TODO
			dumpEveryLine = True 

		loopStack = []

		byteStack = [Byte(0) for i in range(bufferSize)]

		toReturn = ""
		codeSize = len(code)
		charCount = 0
		pointer = 0
		dumps = []
		loop = 0
		dumpCount = 0

		while charCount < codeSize:

			loop += 1

			char = code[charCount]
			byte = byteStack[pointer]

			if char == '+':
				byte += 1

			elif char == '-':
				byte -= 1

			elif char == '>':
				pointer += 1

			elif char == '<':
				pointer -= 1

			elif char == '[':

				loopStack.append(charCount)

				if byte.value == 0:
					charCount = getNext(code, charCount) - 1

			elif char == ']':

				if byte.value == 0:
					loopStack.pop()

				else:
					charCount = loopStack.pop() - 1

			elif char == '.':
				print(chr(byte.value), end = '')
				toReturn += chr(byte.value)

			elif char == ',':
				byte.value = ord(input())

			elif char == '#':
				dumps.append(dump(loop, byteStack, pointer, dumpCount))
				dumpCount += 1

			charCount += 1

		if dumps:

			with open("brainfuckPyInterpreterMemoryDump.dump", "wt") as f:
				f.write('\n'.join(dumps))
				f.close()

		return toReturn

		

	def __init__(self, path = None, debug = False):

		self.path = path						# Input path

		self.fd = False
		if self.path:
			self.fd = os.open(path, os.O_RDONLY)	# File descriptor
		if not self.fd: return None

		### Need improvement
		##  = TODO
		#	= Ready / Comment

		### Sanitize
		self.code = Interpreter.sanitize(self.fd, debug = debug)
		### Check syntax
		if not Interpreter.checkSyntax(self.code):
			raise(SyntaxError()) ## Wich line?
		### Run
		self.cout = Interpreter.run(self.code, debug = debug)

		# self.cout: dumps output




Interpreter("HelloWorld.b")