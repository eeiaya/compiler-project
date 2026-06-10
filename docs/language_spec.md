# MiniCompiler Language Specification

Encoding: UTF-8

## Keywords

if
else
while
for
int
float
bool
return
true
false
void
struct
fn

## Identifier

```ebnf
identifier =
letter,
{ letter | digit | "_" };
```

Maximum length: 255

## Literals

```ebnf
integer = digit , { digit };
float = digit , { digit } , "." , digit , { digit };
string = '"' , { character } , '"';
boolean = "true" | "false";
```

## Operators

+ - * / %

== != < <= > >=

&& || !

=

## Delimiters

( ) { } ; ,

## Comments

```text
// single line

/* multi line */
```