# Get a CSV list of the 5 oldest admins as mail

Create a workflow with a "send mail workflow activity" and paste the following code in `attachment`.

```
createMailAttachment('data.csv',
  convertStringToBase64(
    toCsv(
      xpath("/person[isadmin=true]", {
        'pageSize': 5,
        'attributes': ['firstname', 'lastname', 'displayname', 'employeestartdate', 'azureid', 'email', 'age'],
        'orderBy': {
            'attribute': 'age',
            'order': 'Descending'
        }
      }),
      ['firstname', 'lastname', 'displayname', 'employeestartdate', 'azureid', 'email', 'age'],
      {
        "delimiter": ";",
        "includeHeader": true,
        "headers":
          {
            "displayname": "Rufname"
          }
      }
    ), true
  )
)
```

# Get a CSV list of all admins as mail

Create a workflow with a "send mail workflow activity" and paste the following code in `attachment`.

```
createMailAttachment('data.csv',
  convertStringToBase64(
    xPathToCsv("/person[isadmin=true]",
      ['firstname', 'lastname', 'displayname', 'employeestartdate', 'azureid', 'email'],
      {
        "delimiter": ";",
        "includeHeader": true,
        "headers":
          {
            "firstname": getDisplayName('firstname'),
            "lastname": getDisplayName('lastname'),
            "displayname": getDisplayName('displayname'),
            "employeestartdate": getDisplayName('employeestartdate'),
            "azureid": getDisplayName('azureid'),
            "email": getDisplayName('email')
          }
      }
    ), true
  )
)
```

# Performance optimization: group membership report

The following code lists the members of a multiple groups for a report:

```
let myGroups = xpath("/group[owner = '00951ec7-757d-4294-84c2-973e03d4da62']",
    { attributes: ['displayname', 'owner', 'explicitmember', 'computedmember'] })
in
setUnion(
    myGroups.map(group =>
        setUnion(group.explicitMember, group.computedMember)
            .map(memberId => memberId.getResource({attributes: ['displayName', 'jobTitle']}))
            .map(member => {
                groupId: group.objectId,
                groupName: group.displayName,
                groupOwner: group.owner,
                memberId: member.objectId,
                memberName: member.displayName,
                memberJobTitle: member.jobTitle

            })))
```

**Question**
Why is the code extremely inefficient (potentially taking several hours to run)? Write an optimized version of the code that produces the same results.

**Solution**

The code is inefficient because

1. `getResource` is called for each member of each group individually and sequentially;
2. the outermost `setUnion` is inefficient because it is
   - unnecessary since all list elements are distinct anyway, and
   - it acts on complex objects (dictionaries) which it needs to recurse through for comparing for distinctness.

Here is an efficient version:

```
let myGroups = xpath("/group[owner = '00951ec7-757d-4294-84c2-973e03d4da62']",
    { attributes: ['displayName', 'owner', 'explicitMember', 'computedMember'],
      resolveReferences: [
        {
          reference: 'explicitMember',
          attributes: ['displayName', 'jobTitle']
        },
        {
          reference: 'computedMember',
          attributes: ['displayName', 'jobTitle']
        }
      ]
    })
in
myGroups.flatMap(group =>
    group.explicitMember
        .append(group.computedMember)
        .distinctBy(member => member.objectId)
        .map(member => {
            groupId: group.objectId,
            groupName: group.displayName,
            groupOwner: group.owner,
            memberId: member.objectId,
            memberName: member.displayName,
            memberJobTitle: member.jobTitle
        }))
```

Note the use of `append` and `distinctBy` instead of `setUnion` to avoid expensive distinctness checks on complex objects (`group.explicitMember` and `group.computedMember` are dictionaries because of the `resolveReferences` options!).

Here is an alternative solution that is also efficient, using the versatile `resolveObjectIds` function which recurses through arbitrary objects and arrays to resolve object IDs:

```
let myGroups = xpath("/group[owner = '00951ec7-757d-4294-84c2-973e03d4da62']",
    { attributes: ['displayname', 'owner', 'explicitmember', 'computedmember'] })
        .resolveObjectIds({
            restrictToKeys: ['explicitmember', 'computedmember'],
            resolvedAttributes: ['displayName', 'jobTitle']
        })
in
... // as above
```

# Search within system configuration objects

Write a function that searches through all system configuration objects (workflows, templates, triggers, etc.) and returns those objects where a specific search string appears within an attribute value - but only if the attribute is not on a blacklist.

**Requirements:**

- The search string should be defined in a variable named `searchString`.
- Attribute names on the blacklist (e.g., "displayname", "description") should be ignored.
- The search should cover the following object types:
  `xpathtemplate`, `workflow`, `permissionrule`, `workflowtemplate`, `requestbasedworkflowtrigger`, `systempermissionrule`, `timedworkflowtrigger`, `functionexpressiontemplate`, `emailtemplate`, `dataflowrule`

- If an attribute value (after JSON serialization) contains the search string, the object should be returned with the following attributes: `objectid`, `objecttype`, and `displayname`.

**Solution**

```
let searchString = "hello",
    blacklistedAttributes = ["displayname", "description"],
    objectTypesToSearchIn = [
        "xpathtemplate", "workflow", "permissionrule", "workflowtemplate",
        "requestbasedworkflowtrigger", "systempermissionrule",
        "timedworkflowtrigger", "functionexpressiontemplate", "emailtemplate", "dataflowrule"
    ]
in
    // Determines if any value (excluding blacklisted keys) contains the search string when serialized
let containsInValues = dict =>
        dict
            .excludeKeys(blacklistedAttributes)
            .getDictionaryValues()
            .map(value => value.toJson())
            .find(json => json.contains(searchString)) != null(),

    // Gets all matching resources for a given object type
    getMatchingResources = objectType =>
        xpath($"/{objectType}") // fetch all attributes
            .filter(containsInValues)
            .map(resource => resource.includeOnlyKeys(['objectid', 'objecttype', 'displayname'])),

    result = objectTypesToSearchIn
        .flatMap(getMatchingResources)

in result
```

# Recursive group member resolution

Write a function that takes an object ID of a group and recursively resolves the display names of all explicit members (`explicitmember`) (i.e., if the members are themselves groups, resolve them in turn, etc.), up to a maximum recursion depth of 100.

**Solution**

Recursion is not supported, so we must use the `reduce` function to simulate finite recursion. The trick generally consists of:

1. designing a state object that contains both the results and auxiliary data, and
2. writing a function that transforms a state object into the next state object,

so that after a finite number of applications of this function to an initial state object, the result is fully computed.

```
let findNestedGroupMembers = groupId =>
    let maxDepth = 100,

        isGroup = id => id.startsWith('00b'), // group object ids start with 00b

        initialState = {
            next: [groupId], // the next group IDs to resolve
            results: [groupId]  // accumulated results (use [] if the initial group should not be included)
        },

        // transforms a state object into the next state object
        processLevel = (state, __) =>
            let nextMembers =
                if state.next.count() > 0 then
                    // get all explicitmembers of all current groups
                    xpathObjectIds($"/group[objectid = values({state.next.singleQuote().joinStrings(', ')})]/explicitmember")
                else [] // we are finished!
            in {
                // next stage: only consider members that are groups AND have not yet been seen
                next: nextMembers.filter(x => isGroup(x) and not(state.results.contains(x))),
                // add the members to the result list
                results: state.results.append(nextMembers).distinct()
            }
    in
    repeat(1, maxDepth)
        .reduce(processLevel, initialState) // apply processLevel iteratively to initialState
        .results
in
findNestedGroupMembers('00b428d3-f115-488e-8b12-c8bd5bc1a30b').resolveObjectIds() // we're just interested in display names
```

# Object type statistics

Write a function (e.g., for a report) that returns the "displayName" and "name" as well as the count of resources for each existing object type, sorted in descending order by count.

Tip: Starting from version 4.18.0, you can write `myDictionary.myKey` instead of `myDictionary.get('myKey')` or `myDictionary.valueByKey('myKey')`.

**Solution**

```
xpath("/objectTypeDescription", {attributes: ['displayName', 'name']})
    .map(x => x.mergeDictionaries({ count: xpathCount($"/{x.name}") }))
    .orderByDescending(row => row.count)
```

# Resolving and filtering group members

**STEP 1**

Write a function that takes a list of strings (display names) and returns all groups with these display names, with the attributes `displayname` and `explicitmember`.

**STEP 2**
Write a function that takes the list of groups from step 1 and returns a list with the same groups, but where `explicitmember` only contains the members that are themselves groups.

**STEP 3**
Write a function that takes a list of groups (e.g., from step 2) and returns a list that contains an object for each group and each explicit member of that group with the following properties:

- `group`: an object that contains only `objectid`, `objecttype` and `displayname` of the group
- `member`: an object that contains `objectid`, `objecttype` and `displayname` of the member.

**Solution**

```

// STEP 1
let getGroups = displayNames =>
        xpath($"/group[displayName = values({displayNames.singleQuote().joinStrings(', ')})]",
        {
            attributes: ['displayname', 'explicitmember']
        })
in
// STEP 2
let filterExplicitmembers = members => members
        .filter(objectId => objectId.startsWith('00b')), // group object IDs start with '00b'
    filterGroup = group => group
        .mergeDictionaries({
            explicitmember: group
                .get('explicitmember')
                .filterExplicitmembers()
        }),
    getFilteredGroups = displayNames => getGroups(displayNames)
        .map(filterGroup)
in
// STEP 3
let createRowsFromGroup = group => group
        .get('explicitmember')
        .map(member => {
            group: group.excludeKeys(['explicitmember']),
            member: member
        }),
    getResult = displayNames => getFilteredGroups(displayNames)
        .flatMap(createRowsFromGroup)
        // recursively resolve 'member' throughout the list:
        .resolveObjectIds({
            restrictToKeys: ['member'],
            resolvedAttributes: [ 'displayName' ]
        })
in getResult(['Group 1', 'Group 2'])

```

# Basic programming exercises

**BEGINNER LEVEL**

Write a function that returns the number sequence 10, 20, 30, ... up to 1000 as a list.

**Solution**

```
let numbers = range(1,100)
        .map(x => x.multiply(10)) // 8 characters indented!
in numbers
```

**INTERMEDIATE LEVEL**
Write a function with parameter n that returns as efficiently as possible all numbers between 1 and n as a list, but only those that are divisible by 17 and not divisible by 5.

**Solution**

A naive solution would be to take all numbers from 1 to n and see which ones are divisible by 17 but not by 5:

```
let result = n => range(1, n)
        .filter(i => i.mod(17) = 0 and i.mod(5) != 0)
in result(100)
```

But the task asks for the most efficient solution possible, and the naive solution simply throws away most numbers because most numbers are _not_ divisible by 17.

We can instead directly compute the (correct number of) multiples of 17 and then filter out those divisible by 5:

```
let result = n => range(1, n.divide(17)) // divide always rounds down!
        .map(i => i.multiply(17))
        .filter(i => i.mod(5) != 0)
in result(100)
```

It's also possible to do it completely without filtering and thus slightly more efficiently, but this is barely comprehensible:

```
let result = n => range(1, n.divide(17).subtract(n.divide(85)))
        .map(i => (i + (i.subtract(1)).divide(4)).multiply(17))
in result(100)
```

**ADVANCED LEVEL**

Write a function with parameter n that returns the first n Fibonacci numbers (1, 1, 2, 3, 5, 8, 13, ...) as a list.

**Solution**

The key here is to use the `reduce` function (aka `fold` or `aggregate`) and append the next value to the accumulated values using `append`. There are many equivalent ways to write this, and here's one (though not the most compact):

```
let fibonacciNumbers = n =>
        let getNextValue = accu => accu.count() switch {
            0 => 1,
            1 => 1,
            _ => accu.valueByIndex(accu.count().subtract(1)) +
                 accu.valueByIndex(accu.count().subtract(2))
        }
        in
        1.repeat(n)
            .reduce((accu, elem) => accu.append(accu.getNextValue()), [])
in
fibonacciNumbers(10)
```
