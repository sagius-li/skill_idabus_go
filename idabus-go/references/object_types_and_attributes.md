# Common object types

- person (user objects)
- group (group objects)
- event (event objects)
- ocgassignment (encapsulates 1:1 relations between objects, e.g. org unit memberships)
- ocgorgunit (organizational units (OU))
- ocgrole (roles)
- ocgpermission (permission objects)
- ocgsod (separation of duty rules)

# Common attributes

Here is a list of common attributes that you may come across in the queries. You may also use these in your examples.

## Implicit attributes (belong to all object types)

- objectid (reference, internal (i.e. cannot be changed by the user))
- objecttype (string, internal)
- displayname (string)
- description (string)
- creator (reference, internal)
- lastupdatetime (datetime, internal)
- createdtime (datetime, internal)

## Person attributes

- firstname (string)
- lastname (string)
- accountname (string)
- department (string)
- jobtitle (string)
- azureid (string)
- employeestartdate (datetime)
- employeeenddate (datetime)
- manager (reference)
- ocgdirectrolerefs (multivalued reference, contains the directly assigned roles)
- ocginheritedrolerefs (multivalued reference, contains the roles inherited from the person's org units)
- ocgresultantrolerefs (multivalued reference, union of direct and inherited roles)

## Group attributes

- explicitmember (multivalued large reference, contains the explicitly specified members)
- memberxpath (string, optionally specifies an XPath query for populating `computedmember`)
- computedmember (multivalued large XPath-based reference)
- grouptype (string)

## OCG Assignment (ocgassignment) attributes

- displayname (string)
  - use this format to build display name: 'display name of the role' -> 'display name of the resource, the role is assigned to'.
- ocgobjecttype (string)
  - Has value `RoleAssignment` when used to assign an `ocgrole` to a `person` or `ocgorgunit`.
  - Has value `OUAssignment` when used to assign an `ocgorgunit` to a `person`.
- ocgobjectscope (string)
  - Has value `Person` when used to assign an `ocgrole` to a `person`
  - Has value `Person` when used to assign a `person` to an `ocgorgunit`
  - Has value `OU` when used to assign an `ocgrole` to a `ocgorgunit`
- ocglinksourceref (reference)
  - For role assignments, this is a reference to the role.
  - For OU assignments, this is a reference to the org unit.
- ocglinktargetref (reference)
  - For role assignments, this is a reference to the person or OU.
  - For OU assignments, this is a reference to the person.

## OCG Org Units (ocgorgunit)

- ocgparentref (reference, points to the parent OU)
- ocgdirectrolerefs (multivalued reference, contains the directly assigned roles)
- ocginheritedrolerefs (multivalued reference, contains the roles inherited from the person's org units)

## OCG Segregation of Duties (ocgsod)

Define a conflict between `ocgconflictingobject1` and `ocgconflictingobject2`, both are reference attributes.

A conflict check applies only for `person` object. It should check the values saved in the attbite `ocgresultantrolerefs` for two references, which are defined as a conflict in an `ocgsod` object.

- displayname (string)
  - use this format to build the display name: 'display name of ocgconflictingobject1' <-> 'display name of ocgconflictingobject2'.
- ocgconflictingobject1 (reference, points to any resource)
- ocgconflictingobject2 (reference, points to any resource)
