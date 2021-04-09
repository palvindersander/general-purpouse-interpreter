# Pal - a general purpouse programming language
Interpreter written in Python for a dynamically typed, imperative language using context-free grammar and a recursive descent parser.

## Current support for:
1. variables
2. variable scoping
3. conditionals
4. print statements
5. logical operators
6. iteration

## Future Work:
1. inputs, arrays, maps, sorting 
2. different parser implementation (LR(0), LL(1))
3. functions
4. cli ide
5. compiler using modern parser generators
6. functional paradigm
7. libraries
8. generic syntax - nlp based parser
9. lambda-calculus interpreter
10. meta-programming parser

## Sample code and output:
```python
var a = 0;
var temp;

for (var b = 1; a < 100; b = temp + b) {
  print a;
  temp = a;
  a = b;
}
```
```text
VAR var None
IDENTIFIER a None
EQUAL = None
NUMBER 0 0.0
SEMICOLON ; None
VAR var None
IDENTIFIER temp None
SEMICOLON ; None
FOR for None
LEFT_PAREN ( None
VAR var None
IDENTIFIER b None
EQUAL = None
NUMBER 1 1.0
SEMICOLON ; None
IDENTIFIER a None
LESS < None
NUMBER 100 100.0
SEMICOLON ; None
IDENTIFIER b None
EQUAL = None
IDENTIFIER temp None
PLUS + None
IDENTIFIER b None
RIGHT_PAREN ) None
LEFT_BRACE { None
PRINT print None
IDENTIFIER a None
SEMICOLON ; None
IDENTIFIER temp None
EQUAL = None
IDENTIFIER a None
SEMICOLON ; None
IDENTIFIER a None
EQUAL = None
IDENTIFIER b None
SEMICOLON ; None
RIGHT_BRACE } None
EOF  None
[<__main__.variableStatement object at 0x7fcd18af73a0>, <__main__.variableStatement object at 0x7fcd18af7400>, <__main__.blockStatement object at 0x7ffcd18af7c40>]
0
1
1
2
3
5
8
13
21
34
55
89
Execution finished in 0.00897779999991144 seconds
```