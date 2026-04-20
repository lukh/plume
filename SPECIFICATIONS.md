# Plume PDM

## Definitions

- Version Control System
- PDM
- Database

- Objects
  
  Objects regroups Items and Documents

- Items

   Items represent real-work objects: parts, assemblies, puchased components, etc. 
   They are stored and saved in the Inventree system.
   They have a unique id, version+revision number, and attributes.
   Items have links to specific Tags in the Subversion repository,
   and are linked to specifics Documents 

- Documents

  Documents describe the Items for manufacturing. (BoM, Schematics, STEP file, etc)
  They are linked to a specific versionned Item.

- Versionning

  Each Item and their Documents have a numbering scheme.

  - Version

    It is a major revision. (functionnal status, when a part change completly, )
    Numbering as 1, 2, 3, etc

  - Revision
  
    A Minor revision on the part.
    Numbering A, B, C, D, etc.

  - Patch

    A Patch concerns only new minor correction of Documents like Schematic, (typo, better view, etc)

    It is used when no structural modifications is done on the Items.


- Trunk
  
  This is the working place. Modifications are done in the trunk, with commit.

- Tags

  Tags are Subversion Tags.
  They are created at every version/revision/patch change.

- Branch
  
  Subversion Branches are available, up to the engineers to create/merge.

- File / Folder
  - Project
  
  - Assembly
  - LocalPart
  - LibraryPart 
 
  Standard FreeCAD file. They can hold more than one item, and can also hold several Document rattached to the Item

- CheckIn/CheckOut

  Since FreeCAD files are Binary files, it is mandatory to lock others when working on a file.

  Each time a user wants to modify an item or a document, it is necessary to perform a check-out action, so that it is locked for everybody else. 
  After the changes have been made, the user performs a check-in action and the object is then free for the team to change it the same way

  A CheckOut will:
    - Update the repository
    - Lock the file
  A CheckIn will:
    - Commit the file
    - Unlock it.

- Lock/Unlock
- Commit
- Release (action) : release an Item, from a File.




## Data Organization

### Repository organization

The Subversion is organized as follow.

At the root of the repository, a file (YAML) describes the repository

plume.yml
```YAML

- stage_before_release: true
- include_short_fcinfo_in_commit: true

- library_folder: libraries
- projects_folder: projects

- version: number|letter
- revision: number|letter

- extra_items_attributes:
    - name: type
    - name: type
    - name: type
    - name: type

```

The complicated part here is that Items live in FreeCAD Files. 
But several parts can exists in a single file.

Also, it is mandatory to be able to use "shared file", aka libraries. They are shared across several "projects". 

## Release

The release process


### Inventree organization

## Version Control

## Attributes