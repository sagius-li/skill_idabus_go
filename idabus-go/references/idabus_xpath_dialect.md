# Introduction

The IDABUS XPath Dialect is a query language used in IDABUS Identity Solution for searching for resources or for specifying a set of resources. XPath queries are used in many places, including workflows, XPath templates, permission rules and various Portal configuration settings.

# Operational Rules

- Always check that the XPath syntax is correct before sending the request. For example, you can't write `/group[owner/department = 'IT']`.

- Don't forget that only reference attributes may be used as navigation attributes in multistep queries. For example, you can't write `/group/department` because `department` is not a reference attribute.

- Don't write unnecessarily complicated queries. For example, instead of `/objType[objectid = /*[...]]`, you can just write `/objType[...]`.

- Prefer request-body transport whenever the endpoint supports an XPath field in the body. Do not default to query parameters just because the endpoint also exposes something like `xPathQuery`.

- This transport choice matters for both correctness and reliability: XPath queries must not be longer than 256 kB, and request URLs may have additional length limits.

- Preferred pattern when the body supports `xPath`:

```json
{
  "xPath": "/person[starts-with(displayName, 'Eva')]",
  "attributes": ["displayname", "accountname", "description"],
  "pageSize": 10,
  "queryFormat": "IncludeNull"
}
```

- Fallback pattern only when the endpoint does not support XPath in the request body:

```text
xPathQuery=/person[starts-with(displayName, 'Eva')]
```

# Simple XPath Queries

We start off with a subset of the IDABUS XPath Dialect language, namely _simple_ XPath queries. In some places such as data flow rules or in the resource constraints for permission rules, only simple XPath queries are allowed. Simple XPath queries have the property that they can be relatively easily evaluated. More specifically, for a given resource with its attribute values at hand, it is possible to check if it satisfies a given simple XPath query without having to search for or retrieve values from any other resource.

A simple XPath query is of the form

```
/node[constraint]
```

where `node` is either `*` or an object type. The square brackets can also be omitted if `constraint` is empty, i.e., `/node` is short for `/node[]`. The query `/*[constraint]` results in all resources satisfying the constraint, whereas `/objectType[constraint]` is the set of all resources with object type `objectType` that satisfy the constraint.

The notation `/node[constraint1]...[constraintN]` is syntactic sugar for the query with a conjunctive constraint `node[constraint1 and ... and constraintN]`.

## Constraints

### Term

A _term_ is inductively defined as

- an attribute (system) name (case-insensitive), e.g. `displayName`,
- a string constant enclosed by single or double quotes, e.g. `'Alice'` or `"Alice"`,
- an integer, e.g. `123`,
- a boolean, i.e. `true` or `false`, or
- a _function application_ of the form `func(term1, ..., termN)` where `func` is the name of a supported IDABUS XPath Dialect function, `N >= 0` is the arity of the function, and the parameters `term1`, ..., `termN` have the correct parameter types for the function.

### Functions

Function names are case-insensitive.

#### Boolean functions

- `is-present(attributeName)`: the value of the attribute is `null` (i.e. undefined or empty)
- `is-not-present(attributeName)`: the value of the attribute is not `null`
- `equals-sensitive(stringTerm1, stringTerm2)`: both terms evaluate to the same string constant (case-sensitive)
- `contains(stringTerm1, stringTerm2)`: the first term evaluates to a string constant that is contained within the string constant resulting from the evaluation of the second term (case-insensitive)
- `contains-sensitive(stringTerm1, stringTerm2)`: same as above, but case-sensitive
- `contains-key(dictionary, stringConstant)`: the first term evaluates to a dictionary that contains the second argument as a (case-sensitive!) key (possibly mapping the key to `null`)
- `starts-with(stringTerm1, stringTerm2)`: the first term evaluates to a string constant that starts with the string constant resulting from the evaluation of the second term (case-insensitive)
- `starts-with-sensitive(stringTerm1, stringTerm2)`: same as above, but case-sensitive
- `ends-with(stringTerm1, stringTerm2)`: the first term evaluates to a string constant that ends with the string constant resulting from the evaluation of the second term (case-insensitive)
- `ends-with-sensitive(stringTerm1, stringTerm2)`: same as above, but case-sensitive
- `regex-match(stringTerm, regularExpression)`: the first term evaluates to a string constant that matches the constant regular expression `regularExpression` (case-insensitive)
- `regex-match-sensitive(stringTerm, regularExpression)`: same as above, but case-sensitive
- `any-starts-with-sensitive`: **(Versions >= 4.18.0.161)** indicates if any value of the multivalue attribute specified in the first argument starts with the string specified in the second argument (case-sensitive)

#### Other functions

- `null()`: returns null
- `value-by-key(dictionary, stringConstant)`: evaluates to the single (!) constant value associated with the (case-sensitive!) key in the given dictionary, if the term `dictionary` evaluates to a dictionary. If the dictionary does not contain the key, `null` is returned.
- `values-by-key(dictionary, stringConstant)`: evaluates to the list (!) of constant values associated with the (case-sensitive) key in the given dictionary, if the term `dictionary` evaluates to a dictionary. If the dictionary does not contain the key, `null` is returned.
- `xpathTemplate(stringConstant)`: placeholder for XPath definition in the XPath template with system name or object ID equal to the given string constant. This function can only be used in the form `attribute = xpathTemplate(...)`.
- `values(stringConstant1, ..., stringConstantN)`: evaluates to the list of the zero or more given constants
- `ref-values(stringConstant1, ..., stringConstantN)`: evaluates to the list of the zero or more given string constants, with the additional restriction that the string constants are object IDs
- `lower-case(stringTerm)`: evaluates the given term and returns the resulting string constant in lower case
- `upper-case(stringTerm)`: evaluates the given term and returns the resulting string constant in upper case
- `string-length(stringTerm)`: evaluates the given term and returns the length of the resulting string constant
- `concat(stringTerm1, ..., stringTermN)`: evaluates the (at least 1) given terms and returns the concatenation of the resulting string constants
- `substring(stringTerm, integerTerm1, integerTerm2)`: evaluates the three given terms to the string constant `s` and integer constants `i1` and `i2`, respectively, and returns the substring of `s` starting from position `i1` with length `i2`
- `add(integerTerm1, ..., integerTermN)`: evaluates all given terms and returns the sum of the resulting integer constants
- `count(multivaluedAttributeName)`: evaluates to the list length of the multivalued value of the given attribute (returns 0 if not present and 1 if present and single-valued)
- `current-dateTime()`: evaluates to a string constant representing the current date time in UTC
- `add-daytimeduration-to-datetime(dateTime, duration)`: evaluates the first term, which must be either a string constant representing a date time or the function application `current-dateTime()` and adds the given `duration` to it, where `duration` is a string constant in ISO 8601 XML Schema duration format or in .NET timespan format
- `subtract-daytimeduration-from-datetime(dateTime, duration)`: evaluates the first term, which must be either a string constant representing a date time or the function application `current-dateTime()` and subtracts the given `duration` to it, where `duration` is a string constant in ISO 8601 XML Schema duration format or in .NET timespan format

### Constraint

A _constraint_ is inductively defined as:

- `term1 = term2`, and similarly for the inequalities `!=`, `<`, `>`, `<=` and `>=` (e.g. `createdTime < lastUpdateTime`)
- a function application with a bool return type (e.g. `starts-with(displayName, 'A')`)
- `constraint1 and ... and constraint N`
- `constraint1 or ... or constraint N`
- `not(constraint)`

Round parentheses are used to disambiguate associativity. The operator `and` binds more strongly than `or`.
The logical operators `and`, `or` and `not` have the expected meaning.

In other words, `term1 = term2` is satisfied if `term1` and `term2` evaluate to `v1` and v2, respectively, and

- `v1` and `v2` are (string, integer, boolean, or `null`) constants and `v1` is equal to `v2` (case-insensitively), or
- `v1` is a constant and `v2` is a list of constants and `v1` is contained in `v2`, or
- `v2` is a constant and `v1` is a list of constants and `v2` is contained in `v1`, or
- `v1` and `v2` are lists of constants and have a non-empty intersection.

If we view `v1` and `v2` as sets, interpreting a single constant as the singleton set containing that constant, then a more succinct definition of `term1 = term2` would be that `v1` and `v2` have a non-empty intersection.

`term1 != term2` is equivalent to `not(term1 = term2)`. The inequalities `<`, `>`, `<=` and `>=` can only be used when both sides evaluate to either integers or string constants representing a date time, and have the usual meaning.

For _simple_ XPath queries, constraints **must not** contain any large attributes, except in combination with `is-present`, `is-not-present`, `count`, `= null()` or `!= null()`.

### Strings with placeholders

If `term1` is a string constant and `term2` is a single-valued attribute (or vice versa), the string constant may contain placeholders `%` as a wildcard character, and the constraint `term1 = term2` is interpreted as the equivalent case-insensitive regular expression constraint. For example,

```
displayName = "A%A%B"
```

is equivalent to

```
regex-match(displayname, "^A.*A.*B$")
```

Additionally, comparisons with `=` and `starts-with` and `contains` with the constant `"%"` is interpreted as "not `null`". For example, `displayName = '%'` and `starts-with(displayName, '%')` are both equivalent to `displayName != null()`. This is somewhat inconsistent but included for backwards compatibility with MIM. We recommend you **do not use** comparisons with `"%"` and use the more idiomatic comparison with `null()` instead.

# General XPath Queries

XPath queries in general need not be _simple_.

## Large attributes

Without the restriction of _simple_ XPath queries, we allow the use of large attributes in XPath queries, except for direct comparisons of two large attributes with `=` or `!=`.

## Multistep queries

Simple XPath queries consist of a single _step_, but in general, an XPath query can have more than one _step_:

```
/node[constraint]/refAttr1[constraint1]/.../refAttrN[constraintN]
```

where `refAttr1`, ..., `refAttrN` are reference attributes. For each step `refAttrM[constraintM]`, the values of the reference attribute `refAttrM` for each of the resulting resources from the previous step are collected, and these object IDs represent the resulting resources of this step.

Note that `refAttr1`, ..., `refAttrN` must be attributes of datatype `Reference` (e.g. `manager` or `explictmember`). It is no valid to use a non-reference attribute: e.g. `/person/displayname` would be invalid.

## Union queries

A union query is of the form

```
query1 | ... | queryN
```

where the queries are non-union XPath queries. The result of a union query is the set union of the results of the individual queries.

## Nested queries

Constraints can also have the form

```
attributeName = query
```

where `query` is a non-union XPath query. This constraint is satisfied if the value of the given attribute (or one of the values, if multivalued) is contained in the result of the given query.

# XPath with Lookups

In contexts where lookups are supported (e.g. in workflows), XPath queries may also contain lookups, e.g.

```
/person[displayName = '[//workflowData/myName]']
```

Lookups in XPath queries are always interpreted as values (and never as attribute names). It does not make a difference whether a lookup is surrounded by quotation marks or not, or whether it is enclosed by the `values` or `ref-values` function or not. If it is not enclosed by `values` or `ref-values` and the lookup is multivalued, the `values` function is implicitly added. For instance, the following queries are all equivalent:

```
/person[displayName = [//workflowData/myNames]]
/person[displayName = '[//workflowData/myNames]']
/person[displayName = values([//workflowData/myNames])]
/person[displayName = values('[//workflowData/myNames]')]

```

which all after lookup resolution becomes something like

```
/person[displayName = values('A', 'B', 'C')]
```

If the lookup evaluates to an empty or null value, it is equivalent to the `null()` function.

# Limitations and caveats

- To search for events, specify the object type explicitly using `/event[...]`. A wildcard query such as `/*[displayName = 'A']` will not include any event objects.
- Some queries can be prohibitively inefficient and/or produce a huge load on the database, especially when involving large attributes or complicated nested queries
- Some queries can be too complex to be evaluated in which case the evaluation will result in an error
- Fast counting only works for simple queries and for queries where the first requested search page already contains all results. Forced counting always returns a result but may be very slow and create a huge load on the database.
- Ordering is not supported for multi-step queries (and most queries involving large attributes) unless each query step results in fewer than 1000 results. This limit can be increased (or decreased) at the expense of more RAM consumption using the Engine app setting `MultistepXPathSortedBufferSize`.
