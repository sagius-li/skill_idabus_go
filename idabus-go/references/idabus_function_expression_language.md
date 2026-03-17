In many places in workflow specifications it is possible to enter a _function expression_, for example as the value of a workflow data expression entry. This page describes the language and the supported functions.

# General

- The language keywords are case-insensitive, so it does not make any difference whether you write `true` or `TrUe`, or `and` or `AND`.
- Parentheses are used to associate sub-expressions to be evaluated together, e.g. `true and (false or true)`.
- To quickly test an expression, use the API function `POST /api/v1/Internal/executeexpression`.

# Constants

Constant expressions can be

- Integers, e.g. `123` or `-1`
- Booleans: `true` or `false`
- Strings: `'hello world!'` or `"hello world!"`
  - Strings delimited by `'` may contain `"` and vice versa.

# The `+` operator

The `+` operator is used to concatenate strings and for integer addition. It is only interpreted as integer addition if both sides are integers, otherwise both sides are interpreted as strings. The operator is left-associative.

- `1 + 2 + 3` evaluates to 6
- `1 + 2 + 'hello world!' + 1 + 2` evaluates to the string `3hello world!12` because of left-associativity.

# Lookups

All lookups that are allowed in the context of workflows can be used.

- `'Hello' + [//requestor/displayName] + '!'` evaluates to `Hello Alice!` (assuming Alice is the display name of the requestor).
- `'Hello' + '[//requestor/displayName]' + '!'` evaluates to `Hello [//requestor/displayName]!` since the lookup is enclosed by quotes and is therefore not interpreted as a lookup but as a literal string.

# Interpolated strings

Interpolated strings are prefixed by `$` and may contain arbitrary sub-expressions that are enclosed by curly brackets.

- `$'Hello {[//requestor/displayName]}!'` evaluates to `Hello Alice!`(assuming Alice is the display name of the requestor).
- Double quotes can also be used: `$"1 + 2 equals {1 + 2}"` evaluates to `1 + 2 equals 3`.
- Lists (see below) are interpolated as comma-separated values: `$'/group[type = values({[1, 2, 3]})]'` evaluates to `/group[type = values(1, 2, 3)]`.
- Interpolated strings can also be arbitrarily nested.

# `$`-Variables

In the `Update Resources Activity` it is possible to specify update entries that write temporary variables whose name start with `$`. These variables can be reused in subsequent function expressions, e.g. `'Hello' +  $myName`.

# Lists

List expressions are delimited by `[` and `]` and may contain arbitrary sub-expressions:

- `[]` is the empty list.
- `[1, 2, "hello" + " world!", [3, 4]]` evaluates to a list containing 4 elements, namely 1, 2, the string `hello world!` and the list consisting of 3 and 4.

# Dictionaries

Dictionary expressions are written in a syntax similar to JavaScript objects:

```
{
  key1: <valueExpr1>,
  key2: <valueExpr2>,
  ...
}
```

The values can be arbitrary expressions, so dictionaries can also be nested. Dictionary keys are always case-insensitive. The keys can also be quoted, so `{ 'key': 123 }` is equivalent to `{ key: 123 }`.

# The `.` operator on dictionaries

**(Versions >= 4.18.0)**
Given a dictionary term `t` and a key `key`, `t.key` retrieves the value of `key` in the dictionary `t`. If `key` does not exist in `t` or `t` does not evaluate to a dictionary, `null` is returned. Note that `key` must be a string starting with a letter or `_` and only contain alphanumerical characters, `_`, and `-`. To retrieve the value of a computed key in a dictionary or of a constant key that does not conform to this pattern, use the `get` function instead.

# The `??` operator

The coalesce expression `<expr1> ?? <expr2>` returns the left value if it evaluates to a non-null value and otherwise evaluates the right hand side. The operator is lazy in the sense that the right hand side is not evaluated if the left hand side is returned. It is left-associative and can be chained together, for example

```
[//workflowData/myValue1] ?? [//workflowData/myValue2] ?? [//workflowData/myValue3]
```

The `+` operator binds more tightly than the `??` operator (but we generally advise using parentheses to avoid ambiguity).

# Equality and inequalities

The equality operator `=` and its logical negation `!=` can be used to compare arbitrary values, including lists and (possibly nested) dictionaries.

- `'Bob' = 'bob'` evaluates to true since `=` is case-insensitive for strings.
- `[1, 2, 3] = [2, 3, 1]` is false since the order matters in lists.
- `{'TWO': 1 + 1, 'ONE': 1} = {'one': 1, 'two': 2}` evaluates to true since the order does not matter in dictionaries.

The inequality operators `<`, `>`, `<=` and `>=` can be used to compare integer values.

# Boolean operators

The operators `and`, `or` and `not` can be used to combine boolean expressions. Both `and` and `or` are left-associative, and `and` binds more strongly than `or`.

- `1=1 or 1=2 and 3=3` is equivalent to `1=1 or (1=2 and 3=3)` evaluates to true
- `not(1=1 or 1=2 and 3=3`) evaluates to false

The operators `and` and `or` are _lazy_ in the sense that the right hand side is not evaluated if the left hand side evaluates to `false` in the case of `and`, and `true` in the case of `or`.

`null` values are interpreted as false, so `not(null())` is `true`, and `null() or true` is `true`.

# Functions

Functions are called by a function name followed by zero or more arguments enclosed by parentheses. Function evaluation is _by value_, in other words, the arguments are first evaluated and the resulting values are then fed into the function.

The list of all supported functions with explanations can be found [here](/Sammlung-von-Beiträgen-für-Documentation/IDABUS-Function-Expression-Language/Supported-functions)).

Examples:

- `startsWith('Hello World!', 'Hel')` evaluates to true.
- `multiply(3, 4)` evaluates to 12.
- `eval([//workflowData/myExpr])` evaluates to 12, assuming that `[//workflowData/myExpr]` evaluates to the string `multiply(3, 4)`.

## Fluent notation (dot notation)

All functions (including user-defined ones) with at least one argument can also be called by first writing the first argument, followed by a dot `.`, and then followed by the function name and the remaining arguments in parentheses:

- `'Hello World!'.endsWith('orld!')` is equivalent to `endsWith('Hello World!', 'orld!')` evaluates to true
- `2.multiply(3).subtract(1).multiply(4)` is equivalent to `multiply(subtract(multiply(2, 3), 1), 4)` and evaluates to 24.

# Lambda expressions

Lambda expressions are used to define new functions. A lambda expression with one parameter is of the form

```
variableName => <expression>
```

where the variable name must not be bound by any enclosing expression and must not start with `$`. For example, `x => x + 1` represents a function that takes an input `x` and returns its successor (if it is an integer). In general, lambda expressions can have 0 or more parameters:

```
() => <expression>
(var1, ..., varN) => <expression>
```

Recursive function definitions are **not** allowed to avoid infinite looping. You can use the `reduce` function in combination with `range` or `repeat` to implemented limited recursion.

For example,

- `[1, 2, 3].filter(x => x >= 2)` evaluates to `[2, 3]`.
- `[1, 2, 3].map(x => x.multiply(10))` evaluates to `[10, 20, 30]`.
- `[1, 2, 3].filter(x => x >= 2).map(x => x.multiply(10))` evalutes to `[20, 30]`.

# If-then-else expressions

Conditional expressions can be expressed with if-then-else expressions:

- `if 1=1 then 'yes' else 'no'` evaluates to `yes`
- `if 1!=1 then 'yes' else 'no'` evaluates to `no`
- `if $var=1 then 'one' else if $var=2 then 'two' else 'error'` evaluates to `error` assuming that `$var` is 3.

The if-condition may be an arbitrary expression but must evaluate to a boolean or `null` (which is interpreted as `false`) or else the evaluation fails.

Unlike the similar `IIF`-function, only the branch that is actually taken is evaluated.

# Switch expressions

Switch expressions are used to evaluate a single expression from a list of candidate expressions based on a pattern match with an input expression:

```
<inputExpression> switch {
    <candidateExpr1> => <resultExpression1>,
    <candidateExpr2> => <resultExpression2>,
    ...,
    _ => <defaultExpression>
}
```

The default expression is mandatory and is returned if none of the candidate expressions match. Only the branch actually taken is evaluated.

For example, the following expression retrieves a the department of a resource and converts it into an integer. An error is thrown if the department does not match any of the expected values. (This also uses the `throw` expression which is described further below.)

```
getResourceAttribute([//workflowData/myId], 'department') switch {
    'marketing' => 0,
    'hr' => 1,
    'IT' => 2,
    _ => throw 'unknown department'
}
```

# Let expressions

Let expressions are used to declare variables that can be used within the scope of the expression:

```
let <variableName> = <expr> in <bodyExpression>
```

This first evaluates the expression `<expr>` and associates the variable with the result. This value is then used wherever the variable occurs in the body expression (so `<expr>` is evaluated exactly once no matter how often the variable occurs in the body expression). The variable must not be bound by any other enclosing expression.

The syntax

```
let <var1> = <expr1>, <var2> = <expr2>, ... in <bodyExpression>
```

is short hand for

```
let <var1> = <expr1> in
   let <var2> = <expr2> in
    ...
    <bodyExpression>
```

For example, the following expression evaluates an XPath query (only once!) and returns a dictionary containing the count, all results, as well as only those results without the manager attribute:

```
let results = xpath('/person') in
{
  'count': results.count(),
  'resultsWithoutManager': results.filter(x => x.valueByKey('manager') = null()),
  'allResults': results
}
```

The following example shows how let expressions can be used to define new functions, including higher order functions that take functions as arguments and return other functions::

```
let applyTwice = f => x => f(f(x)),
    times10 = n => n.multiply(10),
    times100 = applyTwice(times10),
    mapTimes100 = list => list.map(times100) in
[1, 2, 3].mapTimes100()
```

This evaluates to `[100, 200, 300]`.

# Try-catch and throw

The try-catch expression can be used to catch evaluation errors and return a value instead:

```
try <expr> catch => <onErrorExpr>
```

For example, `try [//workflowData/num1].divide([//workflowData/num2]) catch => -1` returns -1 whenever `[//workflowData/num2]` is 0.

The expression `throw` simply throws an error - which can then be caught by an enclosing try-catch expression:

```
throw
```

A `throw` expression can optionally also be followed by an expression which is evaluated to be used as error message:

```
if [//requestor/manager] = null() then
    throw 'No manager found for ' + [//requestor/displayname]
else
    getResource([//requestor/manager])
```

# Comments

Comments and line breaks are treated as whitespace. A comment starts with `//` and encompasses the rest of the line.

```
// this is a comment
let x = 1 // this is another comment
in x // this is also a comment
```
