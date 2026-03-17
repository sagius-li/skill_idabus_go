This page contains a comprehensive list of all functions supported in the IDABUS Function Expression Language. Some functions have aliases, in which case the equivalent function names are separated by `/`, e.g. as in `distinct`/`removeDuplicates`.

The signature of each function is given below with parameter types and the return type, where `object` refers to any type. Function types are denoted with an arrow `->`, e.g. `(object,object) -> object` refers to the type of any lambda expression (or variable defined by a lambda expression) that takes two parameters and returns any type.

# add

```
add(int value1, int value2): int
```

Adds two integer values and returns the result.
Examples:

- `add(3, 4)` evaluates to 7
- `add(-5, 10)` evaluates to 5

# after

```
after(datetime date1, datetime date2): bool
```

Returns true if `date1` occurs after `date2`. Both parameters must be valid datetime values or `null`. If any parameter is `null`, `false` is returned.

Example:

- `after('2023-01-15', '2023-01-01')` evaluates to `true`

# and

```
and(bool condition1, bool condition2): bool
```

Returns true if both conditions are true.

Example:

- `and(true, false)` evaluates to `false`

# append

```
append(object[] list1, ..., object[] listN): object[]
```

Returns the concatenation of 0 or more lists. Null arguments are interpreted as empty lists. Non-list arguments are interpreted as singleton lists.

Example:

- `append()` evaluates to `[]`.
- `append([1, 2, 3])` evaluates to `[1, 2, 3]`.
- `[1, 2, 3].append([2, 3, 4])` evaluates to `[1, 2, 3, 2, 3, 4]`.
- `[1, 2, 3].append([2], [3, 4])` evaluates to `[1, 2, 3, 2, 3, 4]`.
- `1.append(2, 3)` evaluates to `[1, 2, 3]`.

# before

```
before(datetime date1, datetime date2): bool
```

Returns true if `date1` occurs before `date2`. Both parameters must be valid datetime values or `null`. If any parameter is `null`, `false` is returned.

Example:

- `before('2023-01-01', '2023-02-01')` evaluates to `true`

# bitAnd

```
bitAnd(int num1, int num2): int
```

Performs bitwise AND operation on two integers.

Example:

- `bitAnd(5, 3)` evaluates to `1`

# bitNot

```
bitNot(int num): int
```

Performs bitwise NOT operation on an integer.

Example:

- `bitNot(0)` evaluates to `-1`

# bitOr

```
bitOr(int num1, int num2): int
```

Performs bitwise OR operation on two integers.

Example:

- `bitOr(5, 3)` evaluates to `7`

# callTemplate

```
callTemplate(string templateNameOrId, dictionary inputParameters): object
```

Calls the [function expression template](/IDABUS-Identity-Solution/Documentation/IDABUS-Function-Expression-Language/Function-expression-templates) with the given name (not display name!) or object ID, and the given named input parameters.

Examples:

- `callTemplate('myTemplate')` calls the template with name 'myTemplate' with empty parameters. If the template has input parameters defined, the values of these are populated with `null` or the default value specified within the template.
- `callTemplate('myTemplate', {input1: 'foo', input2: 123})` calls the template with name 'myTemplate' with the given input parameters. Any input parameters of the template that are not included in the dictionary are populated with `null` or the default value specified within the template.

# concatenate

```
concatenate(string str1, string str2, ...): string
```

Joins two or more strings together.

Example:

- `concatenate('Hello', ' ', 'World')` evaluates to `'Hello World'`

# computeHashSHA256

**Versions >= 4.19.0**

```
computeHashSHA256(string source, [string encoding = 'UTF8'], [string outputFormat = 'hexLower']): string
```

Computes the SHA256 hash of the given input string `source` and returns the hash as a string. A `null` input string is interpreted as the empty string. The optional `encoding` parameter must be a valid encoding name such as `ISO-8859-1` (default value is `UTF8`). The optional `outputFormat` specifies the output format:

- `hexLower` (default): hexadecimal representation in lower case
- `hexUpper`: hexadecimal representation in upper case
- `base64`: Base64 encoding

Examples:

- `äßÜ'.computeHashSHA256()` evaluates to `'847991fdd0441fc0f1bb9fe00d95b7d2b97961dfa7889f87f62e64c63d30d38d'`.
- `'äßÜ'.computeHashSHA256('iso-8859-1')` evaluates to `'e648a5544d9f84c440a677866285db4129ea3994c2aee66da94e1055669e3184'`.

# concatenateMultivaluedString / joinStrings

```
concatenateMultivaluedString(object[] values, string separator): string
joinStrings(object[] values, string separator): string
```

Concatenates the list of the string representations of the given values, using the specified `separator` between the elements. If `values` is `null`, the empty string is returned. If `values` is not a list, the string representation of `values` is returned.

# contains

```
contains(object[] v1, object v2, [bool caseSensitive = false]): bool
contains(string v1, string v2, [bool caseSensitive = false]): bool
```

If `v1` is a list, `contains` indicates if `v2` is an element of the list. The optional third argument (default = `false`) specifies if the operation should be case-sensitive. The elements may be complex values like dictionaries or lists.

Otherwise, if `v1` and `v2` are strings (or atomic values like GUIDs, date times or numbers) `contains` indicates whether the string representation of `v1` contains the string representation of `v2` as a substring. The optional third argument (default = `false`) specifies if the operation should be case-sensitive.

This is an `O(n)` operation. Therefore, if, for a given list, you need to repeatedly check if it contains some element, consider converting the list into a dictionary and using `containsKey` instead of `contains`.

Examples:

- `contains('Hello world!', 'ELLO W')` evaluates to `true`
- `contains('Hello world!', 'ELLO W', true)` evaluates to `false`
- `'Hello 123!'.contains(100 + 20 + 3)` evaluates to true.
- `contains([{'name': 'Alice', 'age': 25 }, {'name': 'Bob', 'age': 22 }], {'name': 'BOB', 'age': 22 })` evaluates to `true`
- `contains([{'name': 'Alice', 'age': 25 }, {'name': 'Bob', 'age': 22 }], {'name': 'BOB', 'age': 22 }, true)` evaluates to `false`

# containsKey

```
containsKey(dictionary dic, string key): bool
```

Indicates if the given dictionary contains the given key (case-insensitive). This is an `O(1)` operation.

# convertStringToBase64

```
convertStringToBase64(string s): string
convertStringToBase64(string s, bool addBom): string [only available >= 4.20.0]
```

Converts a UTF8 string into a Base64 string.

**Versions >= 4.20.0**
Optional second parameter that determines whether the result should include a BOM (Byte Order Mark). Set this to `true` if the string will be used as a CSV email attachment and opened with Microsoft Excel.

Example:

```
createMailAttachment('data.csv', convertStringToBase64(xpathtoCsv('/person', ['displayname', 'description']), true))
```

# convertToBoolean

```
convertToBoolean(object value): bool
```

Converts a value to boolean. Accepts strings ('true'/'false'), numbers (0/1), or booleans.

Example:

- `convertToBoolean('true')` evaluates to `true`

# convertToNumber

```
convertToNumber(object value): int
```

Converts a value to integer. Accepts numeric strings, booleans (true=1, false=0), or numbers.

Example:

- `convertToNumber('123')` evaluates to `123`

# convertToString

```
convertToString(object value): string
```

Converts a value to its string representation. Accepts numbers, booleans, GUIDs, and strings.

Example:

- `convertToString(123)` evaluates to `'123'`

# count

```
count(list values): int
```

Returns the number of elements in a list.

Example:

- `count(['a', 'b', 'c'])` evaluates to `3`

# createMailAttachment

**Versions >= 4.20.0**
`createMailAttachment(fileName, contentBase64)`

Builds a mail attachment from a file name and base64 content for use in the Send Email workflow activity (attachment expression).

- **fileName** (string): Attachment file name, e.g. `"data.csv"` or `"photo.png"`.
- **contentBase64** (string): Attachment body as Base64 (e.g. from `convertStringToBase64(...)`). Note: It's recommended to call `convertStringToBase64(...)` with `true` as 2nd parameter if you open the attachment with Microsoft Excel.

Returns: Mail attachment object for the email workflow activity.

Example:

```
createMailAttachment('data.csv', convertStringToBase64(xpathtocsv("/person[isadmin=true]", ['firstname', 'lastname'])))

createMailAttachment('photo.png', myPerson.photo)
```

Response:

```
{ "name": "data.txt", "contentBase64": "VGhhbmsgeW91IQ==" }
```

# cr

```
cr()
```

Returns a new line character.

# crlf

```
crlf(): string
```

Returns a carriage return + line feed sequence (`\r\n`).

# dateOnly

**Versions >= 4.19.0**

```
dateOnly(datetime date): date
```

Returns only the date portion of the given datetime, removing the time component.

Example:

- `dateOnly('2023-01-01T14:30:45')` evaluates to `2023-01-01`

# datetimeAdd

```
dateTimeAdd(DateTime baseDate, TimeSpan duration): datetime
```

Adds a time span to a DateTime.

Example:

- `dateTimeAdd('2023-01-01', '1.00:00:00')` evaluates to `2023-01-02`

# datetimeDifference

**Versions >= 4.19.0**

```
datetimeDifference(datetime date1, datetime date2): string
```

Calculates the difference between two datetime values and returns the string representation of the timespan. The result represents `date1 - date2`.

Examples

- `datetimeDifference('2023-01-02', '2023-01-01')` evaluates to `'1.00:00:00'`

# datetimeFormat

```
dateTimeFormat(DateTime date, string format): string
```

Formats a DateTime using specified format string.

Example:

- `dateTimeFormat("2023-01-01", 'yyyy-MM')` evaluates to `'2023-01'`

# datetimeFromFileTimeUtc

```
dateTimeFromFileTimeUtc(int fileTime): datetime
```

Converts a Windows file time (UTC) to datetime.

Example:

- `dateTimeFromFileTimeUtc(133312345678900000)` evaluates to corresponding datetime `2023-06-14T16:42:47.8900000Z`.

# datetimeFromString

```
dateTimeFromString(string dateString): datetime
```

Parses a string to datetime.

Example:

- `dateTimeFromString('2023-01-01')` evaluates to the corresponding datetime.

# datetimeNow

```
dateTimeNow(): DateTime
```

Returns current UTC datetime.

# datetimeSubtract

```
dateTimeSubtract(DateTime baseDate, TimeSpan duration): DateTime
```

Subtracts a time span from a datetime.

Example:

- `dateTimeSubtract('2023-01-02', '1.00:00:00')` evaluates to `2023-01-01`

# datetimeToFileTimeUtc

```
dateTimeToFileTimeUtc(datetime date): long
```

Converts a datetime to Windows file time (UTC).

Example:

- `dateTimeToFileTimeUtc('2023-01-01')` evaluates to corresponding file time 133170048000000000.

# dateTimeUtcToLocalTime

```
dateTimeUtcToLocalTime(datetime utcTime, [string timeZonId=null]): datetime
```

Convert a date to the local time or specified time zone. If the first parameter is `null`, `null` is returned. If the second parameter is `null`, the date converted to the local time on the server is returned. Otherwise, the second parameter is interpreted as a [timezone ID](https://learn.microsoft.com/de-de/dotnet/api/system.timezoneinfo.findsystemtimezonebyid) such as `W. Europe Standard Time`.

# decrypt

```
decrypt(string ciphertext, string passphrase): string
```

Decrypts a ciphertext encrypted using `encrypt` with the given passphrase.

# decryptWithKeyVault

```
decryptWithKeyVault(string ciphertext, string keyVaultKeyName): string
```

Decrypts a ciphertext given a passphrase that is retrieved from Azure Key Vault using the given `keyVaultKeyName`, using 256 bit AES (Rijndael). The ciphertext should have been encrypted using `encryptWithKeyVault`.

# distinct / removeDuplicates

```
distinct(object[] values, [bool caseSensitive = false]): object[]
removeDuplicates(object[] values, [bool caseSensitive = false]): object[]
```

Returns only distinct elements of the given list of values. The elements may be complex values like dictionaries or lists. The optional second argument (default = `false`) specifies if the operation should be case-sensitive. If the argument is `null`, `null` is returned.

Example:

- `distinct([[1, 2], [2, 1], [1, 2, 3], [1, 2]])` evalutes to `[[1, 2], [2, 1], [1, 2, 3]]`.

# distinctBy

```
distinctBy(object[] values, (object->object) selector): object[]
```

Returns only distinct elements of the given list of values, using the given `selector` function to determine if an element has already been seen (case-sensitive!).

Example:

- `[{ id: 1, age: 20 }, { id: 2, age: 30 }, { id: 1, name: 'Alice' }].distinctBy(x => x.get('id'))` evaluates to `[{ id: 1, age: 20 }, { id: 2, age: 30 }]`.

# divide

```
divide(int dividend, int divisor): int
```

Divides two integers. Throws error if divisor is zero.

Example:

- `divide(10, 3)` evaluates to `3`

# doubleQuote

```
doubleQuote(string x): string
doubleQuote(object[] x): object[]
```

Surrounds the argument by double quotes if the argument is a string (or any object that is not a list). Returns the list of strings surrounded by double quotes if the argument is a list.

Example:

- `doubleQuote('hello')` evaluates to the string `"hello"`.
- `doubleQuote(['hello', 123])` evaluates to the list containing the strings `"hello"` and `"123"`.

# encrypt

```
encrypt(string cleartext, string passphrase): string
```

Encrypts a cleartext given a passphrase, using 256 bit AES (Rijndael). Use `decrypt` to decrypt the result.

# encryptWithKeyVault

```
encryptWithKeyVault(string cleartext, string keyVaultKeyName): string
```

Encrypts a cleartext given a passphrase that is retrieved from Azure Key Vault using the given `keyVaultKeyName`, using 256 bit AES (Rijndael). Use `decryptWithKeyVault` to decrypt the result.

# endsWith / ends-with

```
endsWith(string s1, string s2, [bool caseSensitive = false]): bool
ends-with(string s1, string s2, [bool caseSensitive = false]): bool
```

Indicates if the first string ends with the second string. The optional argument (default = `false`) specifies if the operation should be case-sensitive. A `null` argument is interpreted as the empty string.

# eq

```
eq(object v1, object v2, [bool caseSensitive = false]): bool
```

Indicates if the two given values are equal. The optional argument (default = `false`) specifies if the operation should be case-sensitive. The arguments may be complex values like dictionaries or lists. With the default case-insensitive option, `eq` is equivalent to the `=` operator.

Example:

- `eq('alice', 'Alice')` evaluates to `true`
- `eq('alice', 'Alice', true)` evaluates to `false`
- `[1, 2, 3].eq([3, 2, 1])` evaluates to `false`, since the order of elements in lists matter
- `[1, 2, 3].eq([1, 2, 3])` evaluates to `true`
- `['alice', { 'name': 'bob'}].eq(['Alice', { 'name': 'Bob'}])` evaluates to `true`
- `['alice', { 'name': 'bob'}].eq(['Alice', { 'name': 'Bob'}], true)` evaluates to `false`

# escapeDnComponent

```
escapeDnComponent(string dnComponent): string
```

Escapes special characters in an LDAP DN component.

Example:

- `escapeDnComponent('cn=Test,')` evaluates to `'cn=Test\,'`

# eval

```
eval(string expression, [bool ignoreErrors]): object
```

Evaluates the given string as an expression. The optional parameter specifies if parsing or evaluation errors should be ignored, in which case the first argument is returned. In other words, `eval(expr, true)` is equivalent to `try eval(expr) catch => expr`.

If the argument is `null`, `null` is returned.

Example:

- `eval("'Hello world!'")` evaluates to the string `Hello world!`.
- `eval("Hello world!")` causes an error, since `Hello world!` is not a valid expression.
- `eval("Hello world!", true)` evaluates to the string `Hello world!` because errors are ignored.
- Suppose `[//workflowData/myExpression]` evaluates to the string `if 1=1 then 2 else 3`. Then `eval([//workflowData/myExpression])` evaluates to `2`.

# excludeKeys

```
excludeKeys(dictionary dic, string[] keys): dictionary
```

Returns the given dictionary but without the keys specified. If the first argument is `null`, `null` is returned. If the second argument is `null`, `dic` is returned.

Example:

```
{ 'objectid': '00979777-4a3a-4de1-a846-4ee0d659474f', 'displayname': 'Bob' }
    .excludeKeys(['objectid', 'description'])
```

evaluates to the dictionary

```
{ 'displayname': 'Bob' }
```

# filter

```
filter(object[] values, (object->bool) predicate): object[]
```

Filters a list of values based on the given predicate. If the first argument is `null`, `null` is returned.

Example:

- `[1, 2, 3, 4, 5, 6].filter(x => x.mod(2) = 0)` evaluates to `[2, 4, 6]`.

# filterDictionaryKeys

```
filterDictionaryKeys(dictionary dic, (object->bool) predicate): dictionary
```

Returns the given dictionary with only those mappings where the key satisfies the given predicate. If the first argument is `null`, `null` is returned.

Example:

```
{
   'objectid': '00979777-4a3a-4de1-a846-4ee0d659474f',
   'displayname': 'Bob'
}.filterDictionaryValues(key => key != 'ObjectId')
```

evaluates to the dictionary

```
{ 'displayname': 'Bob' }
```

# filterDictionaryValues

```
filterDictionaryValues(dictionary dic, (object->bool) predicate): dictionary
```

Returns the given dictionary with only those mappings where the value satisfies the given predicate. If the first argument is `null`, `null` is returned.

Example:

```
{
    'objectid': '00979777-4a3a-4de1-a846-4ee0d659474f',
    'displayname': 'Bob'
}.filterDictionaryValues(value => not(value.isGuid()))
```

evaluates to the dictionary

```
{ 'displayname': 'Bob' }
```

# find

```
find(object[] values, (object->bool) predicate): object
```

Returns the first element in a list of values that satisfies the given predicate. If no such value exists, `null` is returned. If the first argument is `null`, `null` is returned. If the first argument is not a list, it is interpreted as a singleton list with this value as element.

Examples:

- `['apple', 'banana', 'banjo', 'charlie'].find(word => word.startsWith('b'))` evaluates to `banana`.
- `['apple', 'banana', 'banjo', 'charlie'].find(word => word.startsWith('x'))` evaluates to `null`.
- `[].find(x => true)` evaluates to `null`.
- `banana'.find(word => word.startsWith('b'))` evaluates to `banana`.

# findMap

**Versions >= 4.19.0**

```
findMap(object[] list, (object->object) mapper, (object->bool) predicate): object
```

Applies the mapper function to each element in sequence until the predicate function returns `true` for a mapped result. Returns the first mapped result that satisfies the predicate. Processing stops immediately when a match is found, so the mapper function is not applied to subsequent elements. If no mapped result satisfies the predicate, `null` is returned. If the first argument is `null`, `null` is returned. If the first argument is not a list, it is interpreted as a singleton list with this value as element.

Example:

- `['group1', 'group2', 'group3'].findMap(name => xpathFirst($"/group[displayName = '{name}']"), group => group != null())` evaluates to the first group object found and stops querying after the first match.

# first

```
first(list values): object
```

Returns first element of a list, or the value itself if not a list. If the list is empty, `null` is returned.

Example:

- `first(['a', 'b'])` evaluates to `'a'`

# flatMap

```
flatMap(object[] values, (object->object[]) selector, [int take = infinity]): object[]
```

Projects each element of `values` into a list, using the selector function, and merges the resulting lists into a single list. If the selector function returns a non-list, the value is interpreted as a singleton list. The optional parameter specifies the maximum number of elements to include in the result. With the optional parameter the function is _lazy_ in that it applies the selector function to the elements one by one, and stops as soon the specified number of elements has been reached.

If the first argument is `null`, `null` is returned.

Examples:

```
[10, 20, 30].flatMap(x => [x, x + 1])
```

evaluates to `[10, 11, 20, 21, 30, 31]`.

The following expression constructs a sequence of XPath queries and evaluates them one by one until a maximum of 100 results have been accumulated:

```
[//workflowData/names]
   .map(name => $"/person[displayName = '{name}']")
   .flatMap(query => xpath(query, {pageSize: 100}), 100)
```

# flatten

```
flatten(object[] lists): object[]
```

Flattens a list of lists of elements into a flat list. Non-list elements are interpreted as singleton lists. The function does not recurse down the elements if these are lists as well. If the argument is `null`, `null` is returned.

Examples:

- `flatten([1, [2, 3], [4, [5, 6]]])` evaluates to `[1, 2, 3, 4, [5, 6]]`.
- `[1, [2, 3], [4, [5, 6]]].flatten().flatten()` evaluates to `[1, 2, 3, 4, 5, 6]`.

# formatMultivaluedList

```
formatMultivaluedList(string format, object[] values1, ..., object[] valuesN]): string[]
```

Generates a list of strings from a format string with placeholders, using the given value lists to replace the placeholders.

Parameters:

- `format`: format string with placeholders `{0}` up to `{N}` where `N` is the number of given value lists.
- `values1` up to `valuesN`: The given value lists.

Key behavior:

- Shorter lists are padded with `null` values to match longest list length
- Single values are treated as list with repeating values
- `null` values are formatted as empty strings in the final output

Example:

- `formatMultivaluedList("{0}-{1}", ["A", "B"], [1, 2, 3])` evaluates to `["A-1", "B-2", "-3"]`
- `formatMultivaluedList("{0}-{1}", "A", [1, 2, 3])` evaluates to `["A-1", "A-2", "A-3"]`

# fromJson

```
fromJson(string jsonString): object
```

Deserializes a JSON string. if the string is `null`, `null` is returned.

Examples

- `fromJson('{ "name": "Alice", "age": null }')`

# generateRandomPassword

```
generateRandomPassword(int length): string
```

Generates a random password of specified length. The generated password guarantees: 

- At least one number.
- At least one special character (!@#$&).
- For passwords ≥4 characters, at least one uppercase and one lowercase character

Example:

- `generateRandomPassword(8)` evaluates to random 8-character string

# get / valueByKey

```
get(dictionary dic, string key): object
valueByKey(dictionary dic, string key): object
```

Gets the value associated with the given key in the given dictionary, or `null` if no mapping exists for the given key. If the dictionary is `null`, `null` is returned.

# getCommittedResourceEvents

**Versions >= 4.17.0.557**

```
getCommittedResourceEvents(dictionary options): dictionary[]
```

Retrieves committed resource and overflow events from the system (using admin read permissions) based on specified search criteria. Returns a list of event dictionaries containing event details and changes. The events are ordered by committed time in ascending order. The event archive is included in the search.

The `options` dictionary may specify the following search parameters:

- `requestorId` (Guid, optional): filters events by the ID of the user who requested the change
- `targetId` (Guid, optional): filters events by the ID of the target resource that was changed
- `committedTimeStart` (DateTime, optional): filters events committed after this time (inclusive)
- `committedTimeEnd` (DateTime, optional): filters events committed before this time (exclusive)
- `resourceChangedType` (string, optional): filters events by the type of change. Allowed values are: `Create` (resource creation), `Delete` (resource deletion), `Modify` (single-value update), `Add` (multi-value insertion update), `Remove` (multi-value removal update)
- `changedAttribute` (string, optional): filters events by the name of the changed attribute. Can only be specified if `resourceChangedType` is specified.
- `changedAttributeValue` (string, optional): filters events by the changed (or inserted or removed) attribute value. Can only be specified if `changedAttribute` is specified.
- `pageSize` (int, default: 100): maximum number of events to return
- `attributes` (string[], optional): list of specific event attributes to include in the results. If not specified, returns a default set of attributes including (these include the attributes needed by [`getSingleAttributeChangesFromEvents`](#getSingleAttributeChangesFromEvents)):
  - Event metadata: `displayname`, `eventtype`, `parenteventid`, `rooteventid`, `status`, `resourcechangedtype`, `resourceeventtype`
  - Requestor information: `requestorid`, `requestordisplayname`
  - Timing information: `createdtime`, `committedtime`, `starttime`, `completedtime`
  - Target information: `targetdisplayname`, `targetid`, `targetobjecttype`
  - Change details: , `attributeassignments`, `previousattributeassignments`, `fullResource`
  - Multivalue changes: `multivalueinsertions`, `multivalueremovals`
  - Overflow data: `multivalueinsertionsoverflow`, `multivalueremovalsoverflow`, `fullresourceoverflow`
- `includeOnlySpecifiedChanges` (bool, default: false): when true, the attributes `attributeassignments`, `previousattributeassignments`, `fullResource`, `multivalueinsertions`, `multivalueremovals`, `multivalueinsertionsoverflow`, `multivalueremovalsoverflow` and `fullresourceoverflow` are trimmed to contain only change entries that match the search criteria (`resourceChangedType`, `changedAttribute` and `changedAttributeValue`). Otherwise, the events contain all changes that happened during that event, even if these changes are unrelated to the search criteria.

Examples:

```
// Get the last 100 resource creation events from the last 24 hours
getCommittedResourceEvents({
    'committedTimeStart': datetimeNow().datetimeAdd('-1.00:00:00'),
    'resourceChangedType': 'Create'
})

// Get the last 10 changes (excluding resource creation/deletion) to the 'department' attribute.
// Trim down the events to only include the changes on `department`.
getCommittedResourceEvents({
    'pageSize': 10,
    'resourceChangedType': 'Modify'
    'changedAttribute': 'department',
    'includeOnlySpecifiedChanges': true
})

// Get the last 10 attribute changes where a specified user was added to `explicitmember` by
// a modify (but not a create) event.
// Trim down the events to only include the insertion of this specified user to `explicitmember`.
getCommittedResourceEvents({
    'pageSize': 10,
    'resourceChangedType': 'Add'
    'changedAttribute': 'explicitmember',
    'changedAttributeValue': '009e597a-ea7b-4f33-bd96-865939c63ce7'
    'includeOnlySpecifiedChanges': true
})

// Get the last 10 attribute changes where a specified user was removed from `explicitmember` by
// a resource delete (but not a modify) event.
// Trim down the events to only include the removal of this specified user from `explicitmember`.
getCommittedResourceEvents({
    'pageSize': 10,
    'resourceChangedType': 'Delete'
    'changedAttribute': 'explicitmember',
    'changedAttributeValue': '009e597a-ea7b-4f33-bd96-865939c63ce7'
    'includeOnlySpecifiedChanges': true
})

// For all change types (apart from 'Modify' which is not compatible with multivalued attributes)
// and target attributes 'explicitmember' and 'computedmember', get the last 10 changes to the specified target each,
// and return them in a flat list of individual attribute changes, ordered by committedTime.
['Create', 'Delete', 'Add', 'Remove']
    .flatMap(changeType =>
        ['explicitmember', 'computedmember']
            .flatMap(attr => getCommittedResourceEvents({
                targetId: '00b0fa65-bab8-44df-9730-9d33b1e96123',
                resourceChangedType: changeType,
                changedAttribute: attr,
                includeOnlySpecifiedChanges: true,
                pageSize: 10
            })))
    .orderBy(ev => ev.get('committedTime'))
    .getSingleAttributeChangesFromEvents()
```

# getDeletedResource

```
getDeletedResource(guid objectId, [dictionary getObjectSpecification = null]): dictionary
```

Gets a resource in the last recorded state before it was deleted. The optional `getObjectSpecification` specifies further options for returning the resource (see [getResource](/IDABUS-Identity-Solution/Documentation/IDABUS-Function-Expression-Language/Supported-functions#getResource) for details, but `resolveReferences` is ignored). If the resource never existed or has not been deleted, `null` is returned. The returned resource has the attribute `_deleted` set to the deletion time.

# getDictionaryKeys / getKeys

```
getDictionaryKeys(dictionary dic): string[]
```

Returns all keys of the given dictionary. A `null` argument is interpreted as an empty dictionary.

# getDictionaryValues

```
getDictionaryValues(dictionary dic): object[]
```

Returns all values of the given dictionary. A `null` argument is interpreted as an empty dictionary.

# getDisplayName

```
getDisplayName(guid objectId): string
getDisplayName(string attribute): string

```

If the argument is an existing object ID, it returns the display name of the corresponding resource.

If the argument is the system name of an attribute type description, `getDisplayName` returns the display name of that attribute. If the argument is the system name of an attribute concatenated with `/added` or `/removed` (as in multivalued insertions and removals in the `[//delta]`-lookup), the function returns the display name of that attribute concatenated with the string ` (insertions)` or ` (removals)`, respectively.

If the argument is the system name of an object type description, `getDisplayName` returns the display name of that object type.

If none of these cases apply, the argument is simply returned.

Examples:

- `getDisplayName('009a3544-3ac7-46c8-86fc-ce69c4feb666')` evaluates to `IDABUS`
- `getDisplayName('objectid')` evaluates to `Resource ID`
- `getDisplayName('explicitMember/added')` evaluates to `Explicit Member (insertions)`
- `getDisplayName('explicitMember/removed')` evaluates to `Explicit Member (removals)`
- `getDisplayName('requestbasedworkflowtrigger')` evaluates to `Request-based workflow trigger`
- `getDisplayName(null())` evaluates to`null`
- `getDisplayName(123)` evaluates to`123`
- `getDisplayName('00000000-0000-0000-0000-000000000000')` evaluates to`00000000-0000-0000-0000-000000000000`

# getHistoricalResource

```
getHistoricalResource(guid objectId, datetime datetime): dictionary
```

Gets the historical state of a resource specified by an `objectId` at the given `datetime` in the past. `null` is returned if the no resource with the given `objectId` existed at the specified time in the past.

# getManualTaskDecision

```
getManualTaskDecision(string responseKey): string
getManualTaskDecision(string responseKey, int reponseIndex): string
```

Returns the overall decision of the manual task whose responses are stored in `workflowData` under the given `responseKey`. If a `reponseIndex` is given, the decision of the response with that (0-based) index position is returned. The decision can take on the values `Approved`, `Expired` and `Aborted`.

`getManualTaskDecision('respKey')` is equivalent to `[//workflowData/respKey/$decision]`.
`getManualTaskDecision('respKey', index)` is equivalent to `[//workflowData/respKey/$taskResponses].valueByIndex(index).get('$decision')`.

# getManualTaskResponderId

```
getManualTaskResponderId(string responseKey, int reponseIndex): guid
```

Returns the object ID of the person who gave the response at the (0-based) index position `responseIndex` for the manual task whose responses are stored in `workflowData` under the given `responseKey`.

`getManualTaskResponderId('respKey', index)` is equivalent to `[//workflowData/respKey/$taskResponses].valueByIndex(index).get('responderid')`.

# getManualTaskResponderName

```
getManualTaskResponderName(string responseKey, int reponseIndex): string
```

Returns the display name of the person who gave the response at the (0-based) index position `responseIndex` for the manual task whose responses are stored in `workflowData` under the given `responseKey`.

`getManualTaskResponderName('respKey', index)` is equivalent to `[//workflowData/respKey/$taskResponses].valueByIndex(index).get('responderdisplayname')`.

# getManualTaskResponse

```
getManualTaskResponse(string responseKey, int reponseIndex): object
```

Returns the response at the (0-based) index position `responseIndex` for the manual task whose responses are stored in `workflowData` under the given `responseKey`.

`getManualTaskResponse('respKey', index)` is equivalent to `[//workflowData/respKey/$taskResponses].valueByIndex(index)`.

# getManualTaskResponseContent

```
getManualTaskResponseContent(string responseKey, int reponseIndex): object
getManualTaskResponseContent(string responseKey, int reponseIndex, string key): object
```

Returns the content object of the response at the (0-based) index position `responseIndex` for the manual task whose responses are stored in `workflowData` under the given `responseKey`. If the third argument `key` is given, the content is interpreted as a dictionary, and the value of the key is returned.

`getManualTaskResponseContent('respKey', index)` is equivalent to `[//workflowData/respKey/$taskResponses].valueByIndex(index).get('content')`.

`getManualTaskResponseContent('respKey', index, key)` is equivalent to `[//workflowData/respKey/$taskResponses].valueByIndex(index).get('content').get(key)`.

# getManualTaskResponseContents

```
getManualTaskResponseContents(string responseKey): object[]
```

Returns the list of content objects of the responses for the manual task whose responses are stored in `workflowData` under the given `responseKey`.

`getManualTaskResponseContent('respKey')` is equivalent to `[//workflowData/respKey/$taskResponses].map(x => x.get('content'))`.

# getManualTaskResponses

```
getManualTaskResponses(string responseKey): object[]
```

Returns the list of responses for the manual task whose responses are stored in `workflowData` under the given `responseKey`.

`getManualTaskResponses('respKey')` is equivalent to `[//workflowData/respKey/$taskResponses]`.

# getResource

```
getResource(guid objectId, [dictionary getObjectSpecification = null]): dictionary
```

Fetches the resource with the given object ID, specified as GUID or string. If the resource does not exist, `null` is returned. If the function is evaluated inside a simulation container or a preview, the simulated context is used.
The optional `getObjectSpecfication` may specify the following options:

- `attributes`: the list of attributes to fetch. The attributes `objectid` and `objecttype` are always included, even if `attributes` is specified as the empty list `[]`. By default (or if `attributes` is `null`), all non-computed and non-large attributes are fetched. To fetch all attributes including computed and large attributes, set `attributes` to `[ '*' ]`.

- `queryFormat`: specifies the format in which the result is returned. If `queryFormat` is `Standard` or `null` or not specified, the result contains only attributes with non-null values. If `IncludeNull` is specified, the result contains all (possibly null-valued) attributes listed in `attributes`.

- `resolveReferences`: a list of specifications for resolving reference attributes. Each such specification is a dictionary with the following two properties:
  - `reference`: the name of the reference attribute to resolve
  - `attributes`: the list of attributes to fetch when resolving the reference attribute

- `includeEventArchive` (default: false): specifies if the resource may be found in the event archive collection.

Examples

- `getResource([//requestor])` returns a dictionary representing the requestor, with all attributes apart from computed or large ones.

- `getResource([//requestor], { 'attributes': ['displayName']})` returns a dictionary representing the requestor, containing only the attributes `objectid`, `objecttype` and `displayname`.

The following expression returns a dictionary representing the requestor, with all attributes apart from computed or large ones, but the value of the reference attribute `manager` is resolved to be a dictionary representing the manager that include the manager's display name:

```
getResource([//requestor], {
    'resolveReferences': [{
        'reference': 'manager',
        'attributes': ['displayname']
    }]
})
```

# getResourceAttribute

```
getResourceAttribute(guid objectId, string attribute): object
```

Fetches the resource with the given object ID and returns only the value of the specified attribute. If the attribute is not present in the resource, `null` is returned. If the resource does not exist, an exception is thrown.

Example:

- `[//requestor/manager].getResourceAttribute('displayName')` gets the display name of the requestor's manager.

# getSingleAttributeChangesFromEvents

**Versions >= 4.17.0.557**

```
getSingleAttributeChangesFromEvents(dictionary[] events, [dictionary options = null]): dictionary[]
```

Processes a list of resource events and extracts individual attribute changes from each event, returning each change as a separate dictionary.

The first parameter is an array of event resources (e.g. obtained from [`getCommittedResourceEvents`](#getCommittedResourceEvents) or from an XPath query of the form `/event[...]`).

The optional `options` dictionary may specify:

- `resolveRootEventRequestor` (bool, default: false): when true, includes information about the root event requestor for each change

The function returns an array of dictionaries, where each dictionary represents a single attribute change with the following properties:

- `eventid` (Guid): The object ID of the event
- `committedtime`: the datetime when the change was committed
- `requestorid` (Guid): The object ID of the user who requested the change (which may be the IDABUS system user if the change was caused by e.g. a workflow)
- `requestordisplayname` (string): The display name of the user who requested the change
- `targetid` (Guid): The object ID of the resource that was changed
- `targetdisplayname` (string): The display name of the resource that was changed
- `changetype` (string): The type of change (`Create`, `Delete`, `Modify`, `Add`, `Remove`)
- `attribute` (string): The name of the attribute that was changed
- `attributevalue` (object): The new value of the changed single-value attribute, or the inserted or removed value if the attribute is multivalued.
- `rooteventid` (Guid): The object ID of the root event that triggered this change
- `rooteventrequestorid` (Guid): The object ID of the user who caused the root event (only if resolveRootEventRequestor is true)
- `rooteventrequestordisplayname` (string): The display name of the user who caused the root event (only if resolveRootEventRequestor is true)

# groupBy

```
groupBy(object[] list, (object->object) keySelector): dictionary
```

Returns a dictionary that maps each key (resulting from applying `keySelector` to an element of `list`) to the list of all elements of `list` that yield the same key. Null is returned if `list` is null.

The following example computes the list of roles that occur at least twice:

```
[ { userId: 1, role: 'Accountant' }, { userId: 1, role: 'Auditor' }, { userId: 2, role: 'Accountant' } ]
    .groupBy(x => x.get('role'))
    .filterDictionaryValues(v => v.count() >= 2)
    .getKeys()
```

evaluates to

```
['Accountant']
```

# htmlDecode

```
htmlDecode(string s): string
```

Converts a string that has been HTML-encoded into a decoded string. If the argument is `null`, `null` is returned.

Example:

- `htmlDecode('&lt;hello&gt;')` evaluates to `<hello>`.

# htmlEncode

```
htmlEncode(string s): string
```

HTML-encodes a string. If the argument is `null`, `null` is returned.

Example:

- `htmlDEnode('<hello>')` evaluates to `&lt;hello&gt;`.

# iif

```
iif(bool condition, object trueValue, object falseValue): object
```

Returns `trueValue` if condition is true, otherwise `falseValue`.

Example:

- `iif(1 < 2, 'Yes', 'No')` evaluates to `'Yes'`

# includeOnlyKeys

```
includeOnlyKeys(dictionary dic, string[] keys): dictionary
```

Returns the given dictionary but only with the specified keys. If the first argument is `null`, `null` is returned. If the second argument is `null`, the empty dictionary is returned.

Example:

```
{ 'objectid': '00979777-4a3a-4de1-a846-4ee0d659474f', 'displayname': 'Bob' }
    .includeOnlyKeys(['displayName', 'description'])
```

evaluates to the dictionary

```
{ 'displayname': 'Bob' }
```

# indexByValue

```
indexByValue(object[] list, object value): int
```

Returns the 0-based index of the first occurrence of the given value in the given list. -1 is returned if the value does not exist in the list or the list is `null`.

# insertValues

```
insertValues(object value): object
insertValues(object[] values): object
```

Returns a special object that is used exclusively in a value expression of an update instruction within an update resources workflow activity to indicate that the given value or values should be added to a multivalue attribute.

# isArray

**Versions >= 4.19.0**

```
isArray(object x): bool
```

Indicates if the given value is an array.

Example:

- `isArray([1, 2, 3])` evaluates to `true`.
- `isArray("hello")` evaluates to `false`.
- `isArray(null())` evaluates to `false`.

# isDictionary

**Versions >= 4.19.0**

```
isDictionary(object x): bool
```

Indicates if the given value is a dictionary.

Example:

- `isDictionary({name: 'Alice', age: 25})` evaluates to `true`.
- `isDictionary([1, 2, 3])` evaluates to `false`.
- `isDictionary(null())` evaluates to `false`.

# isGuid

```
isGuid(object x): bool
```

Indicates if the given value is a GUID or a string that represents a GUID.

# isInteger

**Versions >= 4.19.0**

```
isInteger(object x): bool
```

Indicates if the given value is an integer.

Example:

- `isInteger(42)` evaluates to `true`.
- `isInteger("42")` evaluates to `false`.
- `isInteger(null())` evaluates to `false`.

# isNullOrEmpty

```
isNullOrEmpty(object x): bool
```

Indicates if the given value is null or an empty string or an empty list or an empty dictionary. This function is the negation of `isPresent`.

# isPresent

```
isPresent(object x): bool
```

Indicates if the given value is not null and not an empty string, list or dictionary. This function is the negation of `isNullOrEmpty`.

# isString

**Versions >= 4.19.0**

```
isString(object x): bool
```

Indicates if the given value is a string.

Example:

- `isString("hello")` evaluates to `true`.
- `isString(42)` evaluates to `false`.
- `isString([1, 2, 3])` evaluates to `false`.
- `isString(null())` evaluates to `false`.

# isValidFunctionExpression

**Versions >= 4.19.0**

```
isValidFunctionExpression(object expression): bool
```

Returns `true` if the given string is a valid function expression that can be parsed without syntax errors, `false` otherwise. If the argument is not a string, `false` is returned.

Example:

- `isValidFunctionExpression("'hello'")` evaluates to `true`.
- `isValidFunctionExpression("hello")` evaluates to `false`.
- `isValidFunctionExpression("if true then 'yes' else 'no'")` evaluates to `true`.

# isValidSimpleXPath

**Versions >= 4.19.0**

```
isValidSimpleXPath(object xpath): bool
```

Returns `true` if the given string is a valid simple XPath query that can be parsed without syntax errors, `false` otherwise. Simple XPath queries have restrictions and can be evaluated without searching other resources. If the argument is not a string, `false` is returned.

Example:

- `isValidSimpleXPath("/person[displayName = 'Alice']")` evaluates to `true`.
- `isValidSimpleXPath("/person[manager = /group[displayName = 'Managers']]")` evaluates to `false` (not simple due to nested query).
- `isValidSimpleXPath("invalid xpath")` evaluates to `false`.
- `isValidSimpleXPath(null())` evaluates to `false`.

# isValidXPath

**Versions >= 4.19.0**

```
isValidXPath(object xpath): bool
```

Returns `true` if the given string is a valid XPath query that can be parsed without syntax errors, `false` otherwise. This includes both simple and non-simple XPath queries. If the argument is not a string, `false` is returned.

Example:

- `isValidXPath("/person[displayName = 'Alice']")` evaluates to `true`.
- `isValidXPath("/person[manager = /group[displayName = 'Managers']]")` evaluates to `true`.
- `isValidXPath("/person | /group")` evaluates to `true`.
- `isValidXPath("invalid xpath")` evaluates to `false`.
- `isValidXPath(null())` evaluates to `false`.

# last

```
last(object input): object
```

Returns the last element from a list, or returns the input itself if it's not a list.If the input is `null` or an empty list, `null` is returned.

Examples:

- `last(["a", "b", "c"])` evaluates to `"c"`
- `last("hello")` evaluates to `"hello"`
- `last([])` evaluates to `null`
- `last(null())` evaluates to `null`

# left

```
left(string input, int length): string
```

Returns leftmost `length` characters of a string.

Example:

- `left('Hello', 2)` evaluates to `'He'`

# leftPad

```

leftPad(string value, int length, string padding): string
```

Returns a new string that is equivalent to the given value, but right-aligned and padded on the left with as many padding characters as needed to create the specified length. The padding must be a string of length 1. If the value is `null`, `null` is returned.

Examples:

- `leftPad("test", 6, '*')` evaluates to `"**test"`
- `leftPad("test", 3, '*')` evaluates to `"test"`
- `leftPad(null(), 3, '!')` evaluates to `null`

# length

```
length(string input): int
```

Returns length of a string.

Example:

- `length('test')` evaluates to `4`

# lowerCase

```
lowerCase(string input): string
```

Converts the given input to lower case. If the input is `null` or not a string, the input is simply returned.

Example:

- `lowerCase('TEST')` evaluates to `'test'`

# lTrim

```

lTrim(string value, [string trimChars = ' ']): string
```

Removes leading whitespace or specified characters from a string.

Examples:

- `lTrim("  test 123)` evaluates to `"test 123"`
- `lTrim("xxxtest", "x")` evaluates to `"test"`
- `lTrim("abctesting abctesting", "cbaxt")` evaluates to `"esting abctesting"`
- `lTrim(null, "a")` evaluates to `null`

# map

```
map(object[] values, (object->object) selector): object[]
```

Maps each value of a list to another value using the selector function. If the first argument is `null`, `null` is returned.

Example

- `[1, 2, 3].map(x => {'options': [ x ]})` evaluates to `[{'options': [1]}, {'options': [2]}, {'options': [3]}]`

# mapDictionary

```
mapDictionary(dictionary dic,
              ((object, object) -> object) keySelector,
              ((object, object) -> object) valueSelector): dictionary
```

Maps each key-value pair of a dictionary to a new key, using a key selector function, and to a new value, using a value selector function. If the first argument is `null`, `null` is returned.

Example:

```
{a: 1, b: 2, c:3}
    .mapDictionary((k,v) => k + v, (k,v) => [k,v])
```

evaluates to the dictionary

```
{a1: ['a', 1], b2: ['b', 2], c3: ['c', 3]}
```

# mapDictionaryKeys

```
mapDictionaryKeys(dictionary dic, (object->object) selector): dictionary
```

Maps each key of the given dictionary to another value using the selector function and returns the resulting dictionary. If the first argument is `null`, `null` is returned.

Example:

```
{ 'objectid': '00979777-4a3a-4de1-a846-4ee0d659474f', 'displayname': 'Bob' }
    .mapDictionaryKeys(attribute => getDisplayName(attribute))
```

evaluates to the dictionary

```
{ 'Resource ID': '00979777-4a3a-4de1-a846-4ee0d659474f', 'Display Name': 'Bob' }
```

# mapDictionaryValues

```
mapDictionaryValues(dictionary dic, (object->object) selector): dictionary
```

Maps each value of the given dictionary to another value using the selector function and returns the resulting dictionary. If the first argument is `null`, `null` is returned.

Example:

```
{ 'manager': '00979777-4a3a-4de1-a846-4ee0d659474f', 'displayname': 'Alice' }
    .mapDictionaryValues(value => getDisplayName(value))
```

evaluates to the dictionary

```
{ 'manager': 'Bob', 'displayname': 'Alice' }
```

# max / maxBy

```
max(object[] list): object
maxBy(object[] list, (object->object) keySelector): object
```

Returns the maximum element of the `list`. If `keySelector` is given, the function is used on each element to determine the order.

Examples:

- `max(["apple", "zebra", "dog"])` evaluates to `"zebra"`.
- `[{id: 1}, {id: 3}, {id: 2}].maxBy(x => x.get('id'))` evaluates to `{id: 3}`.

# mergeDictionaries

```
mergeDictionaries(dictionary d1, dictionary d2): dictionary
```

Returns a new dictionary containing the key-value pairs from both dictionaries. If the second dictionary contains keys that also occur in the first dictionary, the corresponding values from the first dictionary are overwritten. A null parameter is interpreted as an empty dictionary.

For example,

```
{ name: 'Alice', age: 20 }.mergeDictionaries({ id: 1, name: 'Alice Smith' })
```

evaluates to

```
{ id: 1, name: 'Alice Smith', age: 20 }
```

# mid

```
mid(string value, int startIndex, int length): string
```

Extracts a substring from the specified position with the given length. Returns `null` for invalid indices, or if the value is `null`.

Examples:

- `mid("hello world", 6, 3)` evaluates to `"wor"`
- `mid("hello world", 6, 0)` evaluates to the empty string
- `mid("test", 5, 3)` evaluates to `null`
- `mid("example", 2, 10)` evaluates to `"ample"`
- `mid(null, 0, 1)` evaluates to `null`

# min / minBy

```
min(object[] list): object
minBy(object[] list, (object->object) keySelector): object
```

Returns the minimum element of the `list`. If `keySelector` is given, the function is used on each element to determine the order. See also `max`/`maxBy`.

# mod

```
mod(int num1, int num2): int
```

Returns remainder of division operation.

Example:

- `mod(10, 3)` evaluates to `1`

# multiply

```
multiply(int num1, int num2): int
```

Multiplies two integers.

Example:

- `multiply(3, 4)` evaluates to `12`

# newGuid

```
newGuid(): guid
```

Generates a new GUID.

# newObjectId

```
newObjectId(string objectType): guid
```

Returns a new unused object ID suitable for the given object type. This could be used in a Create Resource Activity to specify the object ID of the resource to be created upfront.

# normalizeString

```

normalizeString(string value, [string substitutions]): string
```

Normalizes text by applying character substitutions and removing diacritics. First processes substitutions, then performs Unicode normalization.

Parameters:

- `value`: string to normalize
- `substitutions`: optional colon-pipe format "old:new|old2:new2" replacements

Examples:

- `normalizeString("Mëtàl")` evaluates to `"Metal"`
- `normalizeString("ﬀßæÁÂÃÄÅ", "Å:AA|Ä:AE|ß:ss|æ:ae")`  
  evaluates to `"fssaeAAAAA"`

# null

```
null(): null
```

Returns null value.

Example:

- `null()` evaluates to `null`

# or

```
or(bool condition1, bool condition2): bool
```

Returns true if either condition is true. `null` is interpreted as `false`.

Example:

- `or(true, false)` evaluates to `true`

# order / orderBy

```
order(object[] list): object[]
orderBy(object[] list, (object->object) keySelector): object[]
```

Returns a list that contains the elements of `list` in ascending order. If `keySelector` is given, the function is used on each element to determine the order. If `list` is null, null is returned.

Examples:

- `order([1, 3, 2])` evaluates to `[1, 2, 3]`.
- `[{id: 1}, {id: 3}, {id: 2}].orderBy(x => x.get('id'))` evaluates to `[{id: 1}, {id: 2}, {id: 3}]`.

# orderDescending / orderByDescending

```
order(object[] list): object[]
orderBy(object[] list, (object->object) keySelector): object[]
```

Same as `order`/`orderBy`, but in descending order.

# properCase

```

properCase(string value): string
```

Converts the first character of each space-delimited word in the given string to upper case and all other characters to lower case. Returns `null` if the string is `null`.

Examples:

- `properCase("hello world")` evaluates to `"Hello World"`
- `properCase("HELLO_WORLD")` evaluates to `"Hello_world"`
- `properCase("john ö'conner-von")` evaluates to `"John Ö'conner-von"`

# randomNum

```
randomNum(int min, int max): int
```

Generates random integer between min (inclusive) and max (exclusive). The random numbers are generated from a cryptographic random number generator.

Examples:

- `randomNum(1, 10)` evaluates to random integer between 1-9
- `randomNum(5, 5)` evaluates to `5`
- `randomNum(-5, 0)` evaluates to random integer between -5 to -1

#range

```
range(int start, int count): int[]
```

Returns an increasing sequence of numbers starting from `start` and containing `count` many numbers.

Example:

- `range(3, 4)` evaluates to `[3, 4, 5, 6]`.

# reduce / fold / aggregate

```
reduce(object[] list, ((object,object)->object) accumulator): object
reduce(object[] list, ((object,object)->object) accumulator, object seed): object
```

Applies the `accumulator` function over the elements of the `list`, and returns the accumulated value after all elements have been iterated over. The accumulator function takes two parameters: the first parameter is the accumulated value, and the second parameter is the current element of the list. The specified `seed` value is taken as the initial accumulator value if specified. If `seed` is not specified, the first element of the list is taken as the initial accumulator value, , and the accumulator function is first called on the seed and the second element of the list (if a second element exists). If `seed` is not specified an the list is empty, an exception is thrown.

Examples

- `['a', 'b', 'c'].reduce((x,y) => x + y)` evaluates to `'abc'`.
- `['a', 'b', 'c'].reduce((x,y) => x.append(x.last() + y), [])` evaluates to `['a', 'ab', 'abc']`.
- `[1, 2, 3].reduce((x,y) => x + y, 1000)` evaluates to `1006`.
- `[].reduce((x,y) => x + y)` throws an exception.
- `[].reduce((x,y) => x + y, 0)` evaluates to `0`.

# regexMatch

```
regexMatch(string input, string pattern): bool
```

Tests if the input string contains at least one match of the given regular expression pattern. Uses .NET regex syntax. If the input is `null`, `false` is returned.

Examples:

- `regexMatch("test@contoso.com", "^\w+@\w+\.\w+$")` evaluates to `true`
- `regexMatch("hello", "ell")` evaluates to `true`
- `regexMatch("hello", "Hell")` evaluates to `false`
- `regexMatch(null(), ".*")` evaluates to `false`

# regexReplace

```
regexReplace(string input, string pattern, string replacement): string
```

Replaces all regex pattern matches in input with replacement string. Uses .NET regex syntax. If the input is `null`, `null` is returned.

Examples:

- `regexReplace("Hello123", "\d", "")` evaluates to `"Hello"`
- `regexReplace("test@contoso.com", "@.*$", "@domain.com")` evaluates to `"test@domain.com"`
- `regexReplace(null(), "a", "b")` evaluates to `null`
- `regexReplace("abc", "(a)(b)", "$2$1")` evaluates to `"bac"`

# removeValues

```
removeValues(object value): object
removeValues(object[] values): object
```

Returns a special object that is used exclusively in a value expression of an update instruction within an update resources workflow activity to indicate that the given value or values should be removed from a multivalue attribute.

# repeat

```
repeat(object value, int n): object[]
```

Returns a list containing `n` repeated occurrences of `value`.

Example:

- `'A'.repeat(3)` evaluates to `['A', 'A', 'A']`.

# replaceString

```
replaceString(string input, string oldValue, string newValue): string
```

Replaces all occurrences of a substring with another string. Case-sensitive. If the input is `null`, `null` is returned.

Examples:

- `replaceString("Hello World", "World", "Universe")` evaluates to `"Hello Universe"`
- `replaceString("Hello World", "world", "Universe")` evaluates to `"Hello World"`

# resolveLookups

```
resolveLookups(string stringWithLookups): string
```

Resolves all lookups that occur in the given string. If the first argument is `null`, `null` is returned.

Exaxmple

- If `[//workflowData/title]` evaluates to the string `Hello [//requestor/displayName]!` and the requestor's display name is `Bob`, then `resolveLookups([//workflowData/title])` evaluates to `Hello Bob!`.

# resolveObjectIds

```
resolveObjectIds(object value): object
resolveObjectIds(object value, dictionary options): object
```

Recurses through the object (which may be a complex nested object like a list or a dictionary) and replaces all valid object IDs by the corresponding display name. If the argument is `null`, `null` is returned. Dictionary _keys_ are _not_ replaced. Applying this function once on an entire object is more efficient than applying it on each sub-object individually.

Example:

```
{ manager: '00979777-4a3a-4de1-a846-4ee0d659474f', displayname: 'Alice' }
    .resolveObjectIds()
```

evaluates to the dictionary

```
{ 'manager': 'Bob', 'displayname': 'Alice' }
```

**Versions >= 4.17.0.557:** The optional argument `options` can contain the following properties:

- `restrictToKeys`: a list of dictionary keys. If specified, only object IDs inside a dictionary within a value corresponding to a key in this list are replaced.
- `resolvedAttributes`: if specified, object IDs are not replaced by the display name, but by an object containing `objectid`, `objecttype` as well as the specified attributes.

Example:

```
{ manager: '00979777-4a3a-4de1-a846-4ee0d659474f', target: '00979777-4a3a-4de1-a846-4ee0d659474f' }
    .resolveObjectIds({
        restrictToKeys: ['target'],
        resolvedAttributes: ['displayName']})
```

evaluates to the dictionary

```
{
    manager: '00979777-4a3a-4de1-a846-4ee0d659474f',
    target: {
        objectid: '00979777-4a3a-4de1-a846-4ee0d659474f',
        objecttype: 'person',
        displayname: 'Bob'
    }
}
```

# reverse

```
reverse(object[] list): object[]
```

Reverses the given list.

# setDifference / except

```
setDifference(object[] list1, object[] list2): object[]
```

Returns all non-null elements in `list` that are not in `list2. A `null` argument is interpreted as the empty set.

For example,

```
[ ['apple', 'banana'], ['banana', 'apple'], ['banana', 'cherry'] ]
    .setDifference([ ['Banana', 'Apple'], ['cherry', 'banana'] ])
```

evaluates to `[ ['apple', 'banana'], '['banana', 'cherry'] ]`.

# right

```
right(string input, int length): string
```

Returns rightmost `length` characters of a string.

Example:

- `right('Hello', 2)` evaluates to `'lo'`

# rightPad

```

rightPad(string value, int length, string padding): string
```

Returns a new string that is equivalent to the given value, but left-aligned and padded on the right with as many padding characters as needed to create the specified length. The padding must be a string of length 1. If the value is `null`, `null` is returned.

Examples:

- `rightPad("test", 6, '*')` evaluates to `"test**"`
- `rightPad("test", 3, '*')` evaluates to `"test"`
- `rightPad(null(), 3, '!')` evaluates to `null`

# rTrim

```
rTrim(string value, [string trimChars = ' ']): string
```

Removes trailing whitespace or specified characters from a string.

Examples:

- `rTrim("  test 123   ")` evaluates to `"  test 123"`
- `rTrim("xxxtestxxx", "x")` evaluates to `"xxxtest"`
- `rTrim("abctesting abctesting", "gnix")` evaluates to `"abctesting abctest"`
- `rTrim(null, "a")` evaluates to `null`

# sequenceEqual

```
sequenceEqual(object[] list1, object[] list2, [bool caseSensitive = false]): bool
```

Indicates if the two lists are equal, taking the order into account. A `null` argument is interpreted as the empty list.

Examples:

- `['apple', 'banana'].sequenceEqual(['apple', 'Banana'])` evaluates to `true`.
- `['apple', 'banana'].sequenceEqual(['apple', 'Banana'], true)` evaluates to `false`.
- `['apple', 'banana'].sequenceEqual(['apple', 'banana'], true)` evaluates to `true`.
- `sequenceequal([], null())` is `true`.

# setEqual

```
setEqual(object[] list1, object[] list2): bool
```

Indicates if the two lists are equal, regardless of ordering and number of occurrences. A `null` argument is interpreted as the empty set.

Examples:

- `['apple', 'banana'].setEqual(['banana', 'Apple', 'Banana'])` evaluates to `true`.

# setIntersection

```
setIntersection(object[] list1, object[] list2, ...): object[]
```

Computes the set intersection of up to 10 given lists. A `null` argument is interpreted as the empty set.

# setUnion

```
setUnion(object[] list1, object[] list2, ...): object[]
```

Computes the set union of up to 10 given lists. A `null` argument is interpreted as the empty set.

# singleQuote

```
singleQuote(string x): string
singleQuote(object[] x): object[]
```

Surrounds the argument by single quotes if the argument is a string (or any object that is not a list). Returns the list of strings surrounded by single quotes if the argument is a list.

Example:

- `singleQuote("hello")` evaluates to the string `'hello'`.
- `singleQuote(["hello", 123])` evaluates to the list containing the strings `'hello'` and `'123'`.

# skip

```
skip(object[] list, int n): object[]
```

Returns the given list without the first `n` elements. If the first argument is `null`, `null` is returned.

Example:

- `[1, 2, 3, 4].skip(2)` evaluates to `[3, 4]`.
- `[1, 2, 3, 4].skip(100)` evaluates to `[]`.

# splitString

```
splitString(string input, [string separator], [int count]): string[]
```

Splits string into substrings. Optional separator (default whitespace) and max count.

Example:

- `splitString('a,b,c', ',')` evaluates to `['a', 'b', 'c']`

# startsWith / starts-with

```
startsWith (string s1, string s2, [bool caseSensitive = false]): bool
starts-with(string s1, string s2, [bool caseSensitive = false]): bool
```

Indicates if the first string starts with the second string. The optional argument (default = `false`) specifies if the operation should be case-sensitive. A `null` argument is interpreted as the empty string.

# subsetEqual

```
subsetEqual(object[] list1, object[] list2): bool
```

Indicates if the first list is a subset of or equal to the second list (regardless of ordering and number of occurrences).

# substring

Version >= 4.18.0

Identical to [`mid`](#mid).

# subtract

```
subtract(int num1, int num2): int
```

Subtracts `num2` from `num1`.

Example:

- `subtract(5, 3)` evaluates to `2`

# sum

```
sum(object[] list): int
```

Computes the sum of all integers in the given list. Non-integers are skipped. If the list is `null`, `0` is returned.

# take

```
take(object[] list, int n): object[]
```

Returns the first `n` elements. If the first argument is `null`, `null` is returned.

Example:

- `[1, 2, 3, 4].take(2)` evaluates to `[1, 2]`.
- `[1, 2, 3, 4].take(100)` evaluates to `[1, 2, 3, 4]`.

# titleCase

```
titleCase(string value): string
```

Converts string to title case using invariant culture rules. Preserves uppercase acronyms while capitalizing other words. If the input is `null`, `null` is returned.

Examples:

- `titleCase("hello WoRLD")` evaluates to `"Hello World"`
- `titleCase("HELLO WORLD")` evaluates to `"HELLO WORLD"`
- `titleCase("NASA launch")` evaluates to `"NASA Launch"`

# timespanDaysComponent

**Versions >= 4.19.0**

```
timespanDaysComponent(string timespan): int
```

Parses the given timespan string and returns only the days component.

Example:

- `timespanDaysComponent('3.10:45:30.250')` evaluates to `3`

# timespanHoursComponent

**Versions >= 4.19.0**

```
timespanHoursComponent(string timespan): int
```

Parses the given timespan string and returns only the hours component.

Example:

- `timespanHoursComponent('3.10:45:30.250')` evaluates to `10`

# timespanMillisecondsComponent

**Versions >= 4.19.0**

```
timespanMillisecondsComponent(string timespan): int
```

Parses the given timespan string and returns only the milliseconds component.

Example:

- `timespanMillisecondsComponent('3.10:45:30.250')` evaluates to `250`

# timespanMinutesComponent

**Versions >= 4.19.0**

```
timespanMinutesComponent(string timespan): int
```

Parses the given timespan string and returns only the minutes component.

Example:

- `timespanMinutesComponent('3.10:45:30.250')` evaluates to `45`

# timespanSecondsComponent

**Versions >= 4.19.0**

```
timespanSecondsComponent(string timespan): int
```

Parses the given timespan string and returns only the seconds component.

Example:

- `timespanSecondsComponent('3.10:45:30.250')` evaluates to `30`

# timespanTotalMilliseconds

**Versions >= 4.19.0**

```
timespanTotalMilliseconds(string timespan): int
```

Parses the given timespan string as a timespan and returns the total milliseconds (rounded down to nearest integer value).

Example:

- `timespanTotalMilliseconds('1.10:30:45.250')` evaluates to `124245250`

# toComparisonHtmlTable

```
toComparisonHtmlTable(dictionary dic1, dictionary dic2): string
```

Returns a string representing a sequence of `<tr>`-HTML-elements that can be placed inside a `<table>` element, representing a 3-column HTML table comparing both dictionaries. A `null` argument is interpreted as an empty dictionary.

For example,

```
let prettifyDelta = delta => delta
        .resolveObjectIds()
        .mapDictionaryKeys(attr => getDisplayName(attr)),

    beforeChange = [//deltaBeforeChange].prettifyDelta(),

    afterChange = [//delta].prettifyDelta(),

    tableHtml = toComparisonHtmlTable(beforeChange, afterChange)

in

$"<table><tr><th>Attribute</th><th>Current value</th><th>Requested value</th></tr>{tableHtml}</table>"

```

may return the string

```
<table><tr><th>Attribute</th><th>Current value</th><th>Requested value</th></tr>
<tr>
<td>Display Name</td>
<td>Marketing</td>
<td>Marketing Group</td>
</tr>
<tr>
<td>Explicit Member (insertions)</td>
<td></td>
<td>Alice Smith, Bob Doe</td>
</tr>
</table>
```

# toCsv

**Versions >= 4.20.0**

```
toCsv(data, attributeNames, options?)
```

Converts an array of dictionary-like objects to a CSV string. Data source is arbitrary (e.g. result of `xpath()` or any other expression returning a list of key-value objects).

- **data** (array): List of dictionary-like objects (e.g. `xpath(...)`).
- **attributeNames** (array): Column names as array of strings, e.g. `['displayname', 'description']`.
- **options** (dictionary, optional) [same as xpathToCsv]:
  - `delimiter` (string, default `";"`),
  - `includeHeader` (bool, default true),
  - `headers` (dictionary: attribute name → header label, e.g. `{ "displayname": "My Display Name" }`).

Returns: CSV string (UTF-8). Values with delimiter, newline or `"` are quoted; `"` escaped as `""`.

Example:

```
toCsv(person, ['firstname', 'lastname', 'displayname'],
  {
     "delimiter": ";",
     "includeHeader": true,
     "headers": { "displayname": "MyAnzeigename", 'accountname': getDisplayName('accountname')
  }
})
```

# toDictionary

```
toDictionary(object[] list, (object->object) keySelector): dictionary
toDictionary(object[] list, (object->object) keySelector, (object->object) valueSelector): dictionary
```

Converts the given list into a dictionary, applying the `keySelector` function to each element to yield the keys, and (if supplied), applying the `valueSelector` function to transform the values. Null is returned if the list is null.
An exception is thrown if the `keySelector` function maps two different elements of the list to the same key.

For example,

```
[{id: 1, name: 'Alice'}, {id: 2, name: 'Bob'}].toDictionary(x => x.get('id'))
```

evaluates to

```
{
  '1': {id: 1, name: 'Alice'},
  '2': {id: 2, name: 'Bob'}
}
```

and

```
[{id: 1, name: 'Alice'}, {id: 2, name: 'Bob'}].toDictionary(x => x.get('id'), x => x.get('name'))
```

evaluates to

```
{
  '1': 'Alice',
  '2': 'Bob'
}
```

# toFriendlyString

```
toFriendlyString(object v): string
```

Returns a friendly string representation of the given value. If `v` is `null`, the empty string is returned. If `v` is a list, the friendly string representations of the elements of the list are concatenated, separated by a comma.

# toHtmlTable

```
toHtmlTable(dictionary dic): string
```

Returns a string representing a sequence of `<tr>`-HTML-elements that can be placed inside a `<table>` element, representing a 2-column HTML table representing the keys and values of the given dictionary. If the argument is `null`, the empty string is returned.

For example,

```
toHtmlTable({Name : 'Bob', Age: 20})
```

evaluates to the string

```
<tr>
<td>Name</td>
<td>Bob</td>
</tr>
<tr>
<td>Age</td>
<td>20</td>
</tr>
```

# toJson

```
toJson(object v): string
```

Serializes the given value to a JSON string.

# toList

```
toList(object o1, ...): object[]
```

Returns the list consisting of the given arguments, skipping null values. If all values are non-null, `toList(o1, ..., oN)` is equivalent to simply writing `[o1, ..., oN]`.

# trim

```
trim(string input): string
```

Removes leading and trailing whitespace from a string.

Example:

- `trim('  test  ')` evaluates to `'test'`

# upperCase

```
upperCase(string input): string
```

Converts string to uppercase using invariant culture.

Example:

- `upperCase('test')` evaluates to `'TEST'`

# urlDecode

```
urlDecode(string s): string
```

URL-decodes the given string. If the argument is `null`, `null` is returned.

# urlEncode

```
urlEncode(string s): string
```

URL-encodes the given string. If the argument is `null`, `null` is returned.

# valueByIndex

```
valueByIndex(list values, int index): object
```

Retrieves the element at the specified position in a list. Returns null for out-of-range indexes or non-list inputs.

Example:

- `valueByIndex(['a','b','c'], 1)` evaluates to `'b'`

# valueType

```
valueType(object value): string
```

Returns the fully qualified type name of the input value.

Example:

- `valueType(123)` evaluates to `'System.Int64'`

# word

```
word(string input, int index, char delimiter): string
```

Splits a string using the specified delimiter and returns the element at the given position. Returns null for invalid indexes.

Example:

- `word('a|b|c', 1, '|')` evaluates to `'b'`

# xpath

```
xpath(string query, [dictionary searchSpecification = null]): dictionary[]
```

Evaluates the given XPath query (possibly in a simulated context, if applicable) and returns the results as a list of dictionaries. The query may contain lookups.

The optional search specification is a dictionary that may specify the following options:

- `attributes`: the list of attributes to fetch. See the documentation for `getResource` for details.
- `pageSize` (default: infinity): the maximum number of results to fetch.
- `requestorId` (default: `null`): if `null`, the query is evaluated in an admin context, i.e., without any permnission checks. If specified, the query is evaluated with the read permission of the given requestor.
- `resolveReferences`: specifies which reference attributes should be resolved. See the documentation for `getResource` for details.
- `includeEventArchive` (default: false): specifies if the results may be found in the event archive collection.
- `orderBy`: specifies the order of the results. This must be a dictionary specifying two properties:
  - `attribute`: the attribute to order by.
  - `order`: either `Ascending` or `Descending`

Examples:

- `xpath('/person')` returns a list of all person objects with all attributes (apart from non-computed and large attributes).

The following expression returns a list of the first 10 person objects containing only `objectid`, `objecttype` and `displayname`, sorted in ascending order based on their display names:

```
xpath('/person', {
    'pageSize': 10,
    'attributes': [ 'displayname' ],
    'orderBy': {
        'attribute': 'displayname',
        'order': 'Ascending'
    }
})
```

# xpathCount

```
xpathCount(string query, [guid requestorId = null]): int
```

Evaluates the count of the given XPath query (possibly in a simulated context, if applicable) and returns the count. The query may contain lookups. This is more efficient than `xpath(<query>).count()`. The optional parameter specifies the requestor for evaluating the query.

# xpathExists

```
xpathExists(string query, [guid requestorId = null]): bool
```

Returns true if the query has at least one result, and otherwise false. The optional parameter specifies the requestor for evaluating the query.

# xpathFirst

```
xpathFirst(string query, [dictionary searchSpecification = null]): dictionary
```

Returns the first result of the given query, or null if the query has no results. The optional parameter is used to specify search options (see the documentation for `xpath()`).

# xpathObjectIds

```
xpathObjectIds(string query, [int maxNum = infinity], [guid requestorId = null]): guid[]
```

Evaluates the count of the given XPath query (possibly in a simulated context, if applicable) and returns only the object IDs of the results. The first optional parameter specifies the maximum number of object IDs to return. The second optional parameter specifies the requestor for evaluating the query (in which case `maxNum` must be specified as well). The query may contain lookups. This is equivalent to

```
xpath(<query>, { attributes: [], pageSize: <maxNum>, requestorId: <requestorId>})
    .map(x => x.get('objectid'))
```

# xpathToCsv

**Versions >= 4.20.0**

```
xpathToCsv(xpath, attributeNames, options?)
```

Queries data via an XPath expression and returns the result as a CSV string. Simplifies `toCsv(xpath("..."))` because attributes to query and contain in the CSV need to be specified only once.

- **xpath** (string): XPath query, e.g. `/person[isadmin=true]`. Supports dynamic lookup resolution.
- **attributeNames** (array): Column names as array of strings, e.g. `['displayname', 'accountname']`
- **options** (dictionary, optional):
  - `delimiter` (string, default `";"`),
  - `includeHeader` (bool, default true),
  - `headers` (dictionary: attribute name → header label, e.g. `{ "displayname": "My Display Name" }`).

Returns: CSV string (UTF-8). Values with delimiter, newline or `"` are quoted; `"` escaped as `""`.

Example:

```
xpathToCsv("/person[isadmin=true]",
  ["firstname", "lastname", "displayname", "employeestartdate"],
  { "delimiter": ",", "includeHeader": true, "headers": { "displayname": "Display Name" } })
```
