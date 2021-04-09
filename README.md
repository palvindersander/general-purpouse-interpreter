# Pal - a general purpouse programming language
Interpreter written in Python for a dynamically typed, imperative language using context-free grammar and a recursive descent parser.

## Current support for:
1. variables
2. variable scoping
3. conditionals
4. print statements
5. logical operators

## Future Work:
1. input statement
2. different parser implementation (LR(0), LL(1))
3. functions
4. iteration
5. cli ide
6. compiler using modern parser generators
7. functional paradigm
8. libraries
9. generic syntax - nlp based parser
10. lambda-calculus interpreter

## Sample code and output:
```python
var v = 1;
if (v == 2 and true == true)
	print "hello";
else
	print "world";

var a = "global a";
{
	var a = "outer a";
	{
		var a = "inner a";
		print a;	
	}
	print a;
}
print a;
```
```shell
VAR var None
IDENTIFIER v None
EQUAL = None
NUMBER 1 1.0
SEMICOLON ; None
IF if None
LEFT_PAREN ( None
IDENTIFIER v None
EQUAL_EQUAL == None
NUMBER 2 2.0
AND and None
TRUE true None
EQUAL_EQUAL == None
TRUE true None
RIGHT_PAREN ) None
PRINT print None
STRING "hello" hello
SEMICOLON ; None
ELSE else None
PRINT print None
STRING "world" world
SEMICOLON ; None
VAR var None
IDENTIFIER a None
EQUAL = None
STRING "global a" global a
SEMICOLON ; None
LEFT_BRACE { None
VAR var None
IDENTIFIER a None
EQUAL = None
STRING "outer a" outer a
SEMICOLON ; None
LEFT_BRACE { None
VAR var None
IDENTIFIER a None
EQUAL = None
STRING "inner a" inner a
SEMICOLON ; None
PRINT print None
IDENTIFIER a None
SEMICOLON ; None
RIGHT_BRACE } None
PRINT print None
IDENTIFIER a None
SEMICOLON ; None
RIGHT_BRACE } None
PRINT print None
IDENTIFIER a None
SEMICOLON ; None
EOF  None
[<__main__.variableStatement object at 0x7f25d15576d0>, <__main__.ifStatement object at 0x7f25d1557b50>, <__main__.variableStatement object at 0x7f25d1557c10>, <__main__.blockStatement object at 0x7f25d1557fd0>, <__main__.printStatement object at 0x7f25d155b0d0>]
world
inner a
outer a
global a
Execution finished in 0.010862700000870973 seconds
```