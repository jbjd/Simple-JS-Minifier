from re import sub, findall
from string import ascii_letters
from itertools import combinations

# recieves a string of javascript code and returns it with redundant var and let delarations removed
def removeRedundantDeclarations(text):
	
	splitText = text.split(';')
	length = len(splitText)-1
	toReturn = ''
	i = 0
	while i < length:
		startOfLine = splitText[i][:4]
		if startOfLine != 'var ' and  startOfLine != 'let ':
			toReturn += splitText[i]+';'
			i += 1
			continue
		startOfNext = splitText[i+1][:4]
		if startOfNext != 'var ' and  startOfNext != 'let ':
			toReturn += splitText[i]+';'
			toReturn += splitText[i+1]+';'
			i += 2
			continue
		if startOfLine != startOfNext:
			toReturn += splitText[i]+';'
			i += 1
			continue
		toReturn += splitText[i]+','+splitText[i+1][4:]
		i += 2
		while i < length and splitText[i][:4] == startOfLine:
			toReturn += ','+splitText[i][4:]
			i += 1
		toReturn += ';'
	return toReturn

def replaceTrueFalse(parsedText):
	# only replace if true/false not within a var or function name 
	parsedText = sub('(?<=[^a-zA-Z0-9])true(?=[^a-zA-Z0-9]?)', '!0', parsedText)
	parsedText = sub('(?<=[^a-zA-Z0-9])false(?=[^a-zA-Z0-9]?)', '!1', parsedText)
	return parsedText

# takes a js file as string and returns the string minified
def minifyFunction(text):
	unicodePlaceholder = u"\u200b"
	parsedText = text.replace(unicodePlaceholder, '').strip()
	# first things first, remove strings since they might get messed up by these edits, I will add them back later
	listOfStrings = ["".join(x) for x in findall('(".+?")|(\'.+?\')', parsedText)]
	parsedText = sub('(".+?")|(\'.+?\')', unicodePlaceholder, parsedText)

	# remove comments. single line = (\/\/.*) or multi-line = (\/\*(.|\n)*\*\/) 
	# sorry that the regex is impossible to read
	parsedText = sub('(\/\/.*)|(\/\*(.|\n)*\*\/)', '', parsedText).strip()
	# only leave single spaces at most (for example var a = 7; needs a space after var)
	parsedText = sub('[ \t]+', ' ', parsedText)
	# remove all trailing and indentend white space
	parsedText = sub(' ?\n+[ \n]*', '\n', parsedText)
	# remove white space before ; or ,
	parsedText = sub('[ \n]?;[ \n]?', ';', parsedText)
	parsedText = sub('[ \n]?,[ \n]?', ',', parsedText)
	# remove white space at ends of comparisons
	parsedText = sub(' ?= ?', '=', parsedText)
	parsedText = sub(' ?== ?', '==', parsedText)
	parsedText = sub(' ?=== ?', '===', parsedText)
	parsedText = sub(' ?!= ?', '!=', parsedText)
	parsedText = sub(' ?!== ?', '!==', parsedText)
	parsedText = sub(' ?!=== ?', '!===', parsedText)
	parsedText = sub(' ?> ?', '>', parsedText)
	parsedText = sub(' ?=> ?', '=>', parsedText)
	parsedText = sub(' ?< ?', '<', parsedText)
	parsedText = sub(' ?<= ?', '<=', parsedText)
	# remove white space with brackets
	parsedText = sub('[ \n]?{[ \n]?', '{', parsedText)
	parsedText = sub('[ \n]?}[ \n]?', '}', parsedText)

	parsedText = fixParentheses(parsedText)

	# special case for :
	parsedText = sub('[ \n]?:[ \n]?', ':', parsedText)
	# optimize true/false
	parsedText = replaceTrueFalse(parsedText)
	# replace redundant var/let with commas
	parsedText = removeRedundantDeclarations(parsedText)
	# check if functions are declared in this file, shorten variables if so
	parsedText = editFuncVars(parsedText)

	# at the very end, add back in the strings
	for stringToAdd in listOfStrings:
		parsedText = sub(unicodePlaceholder, stringToAdd, parsedText, count=1)
	return parsedText

def fixParentheses(parsedText):
	# spaces around function parameters
	parsedText = sub('[ \n]?\([ \n]?', '(', parsedText)
	parsedText = sub('[ \n]?\)', ')', parsedText)
	# for ) characters, I found they need a new line or semicolon after a function, but not an if statement for some reason.
	# we can exploit that for some more minifying
	listOfPossibleEdits = findall('.*\)\n', parsedText)
	listOfPossibleEdits = [line for line in listOfPossibleEdits if 'if(' in line]
	for line in listOfPossibleEdits:
		parsedLine = line[line.rfind('if(')+3:]
		depthCount = 1
		# check that the if( open paranthese is closed at very end of line, if not it must be something line e.g. if(true)console.log('foo') where we can not delete the new line!
		for char in parsedLine:
			if depthCount == 0 and char == '\n':
				# then it is OK to edit
				parsedText = parsedText.replace(line, line[:-1], 1)
			elif depthCount == 0:
				break
			if char == ')':
				depthCount -= 1
			elif char == '(':
				depthCount += 1
			

	return parsedText

# shortens local variables if they exist, will not edit globals for safety.
# This program is assuming that it will run on a single file so theres no great way to fix global variables' names
def editFuncVars(parsedText):
	funcNames = findall('[^a-zA-Z0-9]function .+\(', parsedText)
	if not funcNames:
		return parsedText
	for name in funcNames:
		# find the function and snip it out so we can edit it
		thisFunc = parsedText[parsedText.find(name):]
		print(thisFunc)  # WIP

	return parsedText
	

# takes a function as a string (everything within first and last bracket { })
def shortenVarNames(text):
	varNames = findall('(?<=var )[a-zA-Z0-9]+(?==)', text)
	newNames = list(combinations(ascii_letters, 1))
	curChar = newNames[0][0]
	for i, name in enumerate(varNames):
		text = sub(f'(?<=[^a-zA-Z0-9]){name}(?=[^a-zA-Z0-9])', curChar, text)
		if(i > 50):
			break
		curChar = newNames[i+1][0]
		
	return text

def readFileAsString(filePath):
	with open(filePath, "r") as fp:
		return fp.read()


if __name__ == "__main__":
	from pyperclip import copy as copToClipboard
	example = '''//This does great stuff
	/* this is an exampe of a 
	multiline comment */
	console.log("string with a //comment looking thingy")

			function hastrueInName(   getsh )
	{var abcd = 9;
	if(false)console.log('This has no new line after the if');else console.log('what?')
		console.log()
		var basd 	  		 	  = 8   ;
		var jklg = 99;
		
		exampleGlobal = 9;
	    console.log('asdf');
		if( true )
		var y = 0;
		else if (false) var y = 1;		else var y = 6;
		if( false ){
			var yhf = 99;
		}
		if (true)
			console.log( "I love it!" );
			console.log( "doube log!" );
		}
		'''
	output = shortenVarNames("var asdf=6;console.log('fun')\nvar asdfasdf=28;if(!0){var test=9}console.log(asdf)\nasdfasdf=99;")
	#realExample = readFileAsString(r"C:\Users\jimde\OneDrive\Desktop\main.js")
	output = minifyFunction(example)
	#output = minifyFunction(realExample)
	#copToClipboard(output)
	print('====')
	print(output)
