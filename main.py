from re import sub, findall, split


# recieves a string of javascript code and returns it with redundant var and let delarations removed
def removeRedundantDeclarations(text):
	
	splitText = split(';', text)
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

# takes a js file as string and returns the string minified
def minifyFunction(text):
	unicodePlaceholder = u"\u200b"
	parsedText = text.replace(unicodePlaceholder, '').strip()
	# first things first, remove strings since they might get messed up by these edits
	listOfStrings = ["".join(x) for x in findall('(".+?")|(\'.+?\')', parsedText)]
	parsedText = sub('(".+?")|(\'.+?\')', unicodePlaceholder, parsedText)

	# remove comments. sinlge line = (\/\/.*) or multi-line = (\/\*(.|\n)*\*\/)
	parsedText = sub('(\/\/.*)|(\/\*(.|\n)*\*\/)', '', parsedText).strip()
	# only leave single spaces at most (for example var a = 7; needs a space after var)
	parsedText = sub('[ \t]+', ' ', parsedText)
	# remove all trailing and indentend white space
	parsedText = sub(' ?\n+[ \n]*', '\n', parsedText)
	# remove white space before ; or ,
	parsedText = sub('[ \n]?;[ \n]?', ';', parsedText)
	parsedText = sub('[ \n]?,[ \n]?', ',', parsedText)
	# remove white space at ends of some special characters
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
	# spaces around function parameters
	parsedText = sub('[ \n]?\([ \n]?', '(', parsedText)
	parsedText = sub('[ \n]?\)[ \n]?', ')', parsedText)
	# special case for :
	parsedText = sub(':[ \n]', ':', parsedText)
	#print(findall('(if\(.+?\))', parsedText))
	# replace redundant var/let with commas
	parsedText = removeRedundantDeclarations(parsedText)

	# at the very end, add back in the strings
	for stringToAdd in listOfStrings:
		parsedText = sub(unicodePlaceholder, stringToAdd, parsedText, count=1)
	return parsedText

def readFileAsString(filePath):
	with open(filePath, "r") as fp:
		return fp.read()


if __name__ == "__main__":
	from pyperclip import copy as copToClipboard
	example = '''//This does great stuff
	/* this is an exampe of a 
	multiline comment */
	console.log("string with a //comment looking thingy")

			function asdf(   getsh )
	{var abcd = 9;
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
	realExample = readFileAsString(r"C:\Users\jimde\OneDrive\Desktop\main.js")

	output = minifyFunction(realExample)
	copToClipboard(output)
	print(output)
