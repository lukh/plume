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
A project is therefore a subfolder, containing a "trunk", "releases", "tags" and "branches" subfolders

And a library is considered as a project


```
.
.
└── /
    ├── plume.yml
    ├── libraries
    │   ├── trunk
    │   │   ├── SharedPart1.FCStd
    │   │   ├── SharedPart2.FCStd
    │   │   ├── SharedPart3.FCStd
    │   │   └── GroupOfSharedObjects
    │   │       ├── SharedPart4.FCStd
    │   │       └── SharedPart5.FCStd
    │   ├── branches
    │   ├── releases
    │   │   ├── SharedPart1
    │   │   │   ├── 1.0
    │   │   │   │   └── SharedPart1.FCStd
    │   │   │   └── 1.1
    │   │   │       └── SharedPart1.FCStd
    │   │   ├── SharedPart2
    │   │   │   ├── 1.0
    │   │   │   │   └── SharedPart2.FCStd
    │   │   │   └── 1.1
    │   │   │       └── SharedPart2.FCStd
    │   │   ├── SharedPart3
    │   │   │   ├── 1.0
    │   │   │   │   └── SharedPart3.FCStd
    │   │   │   └── 1.1
    │   │   │       └── SharedPart3.FCStd
    │   │   └── GroupOfSharedObjects
    │   │       ├── SharedPart4
    │   │       │   └── 1.0
    │   │       │       └── SharedPart4.FCStd
    │   │       └── SharedPart5
    │   │           └── 1.0
    │   │               └── SharedPart5.FCStd
    │   └── tags
    └── projects
        └── project-A
            ├── trunk
            │   ├── Assembly.FCStd
            │   ├── LocalPart1.FCStd
            │   ├── LocalPart2.FCStd
            │   ├── LocalPart3.FCStd
            │   ├── LocalPart4.FCStd
            │   └── LocalPart5.FCStd
            ├── releases
            │   ├── Assembly
            │   │   ├── 1.A
            │   │   │   ├── Assembly.FCStd
            │   │   │   ├── LocalPart1.FCStd
            │   │   │   ├── LocalPart2.FCStd
            │   │   │   ├── LocalPart3.FCStd
            │   │   │   ├── LocalPart4.FCStd
            │   │   │   └── LocalPart5.FCStd
            │   │   ├── 1.B
            │   │   │   ├── Assembly.FCStd
            │   │   │   ├── LocalPart1.FCStd
            │   │   │   ├── LocalPart2.FCStd
            │   │   │   ├── LocalPart3.FCStd
            │   │   │   ├── LocalPart4.FCStd
            │   │   │   └── LocalPart5.FCStd
            │   │   └── 2.A
            │   │       ├── Assembly.FCStd
            │   │       ├── LocalPart1.FCStd
            │   │       ├── LocalPart2.FCStd
            │   │       ├── LocalPart3.FCStd
            │   │       ├── LocalPart4.FCStd
            │   │       └── LocalPart5.FCStd
            │   ├── LocalPart1
            │   │   ├── 1.A
            │   │   │   └── LocalPart1.FCStd
            │   │   ├── 1.B
            │   │   │   └── LocalPart1.FCStd
            │   │   ├── 1.C
            │   │   │   └── LocalPart1.FCStd
            │   │   └── 2.A
            │   │       └── LocalPart1.FCStd
            │   ├── LocalPart2
            │   │   ├── 1.A
            │   │   │   └── LocalPart2.FCStd
            │   │   ├── 1.B
            │   │   │   └── LocalPart2.FCStd
            │   │   ├── 2.A
            │   │   │   └── LocalPart2.FCStd
            │   │   └── 2.B
            │   │       └── LocalPart2.FCStd
            │   ├── LocalPart3
            │   │   ├── 1.A
            │   │   │   └── LocalPart3.FCStd
            │   │   ├── 1.B
            │   │   │   └── LocalPart3.FCStd
            │   │   ├── 1.C
            │   │   │   └── LocalPart3.FCStd
            │   │   └── 1.D
            │   │       └── LocalPart3.FCStd
            │   ├── LocalPart4
            │   │   ├── 1.A
            │   │   │   └── LocalPart4.FCStd
            │   │   ├── 2.A
            │   │   │   └── LocalPart4.FCStd
            │   │   ├── 2.B
            │   │   │   └── LocalPart4.FCStd
            │   │   └── 2.C
            │   │       └── LocalPart4.FCStd
            │   └── LocalPart5
            │       ├── 1.A
            │       │   └── LocalPart5.FCStd
            │       ├── 1.B
            │       │   └── LocalPart5.FCStd
            │       ├── 1.C
            │       │   └── LocalPart5.FCStd
            │       └── 2.A
            │           └── LocalPart5.FCStd
            ├── tags
            │   ├── v1.0
            │   │   ├── Assembly.FCStd
            │   │   ├── LocalPart1.FCStd
            │   │   ├── LocalPart2.FCStd
            │   │   ├── LocalPart3.FCStd
            │   │   └── LocalPart4.FCStd
            │   └── v2.0
            │       ├── Assembly.FCStd
            │       ├── LocalPart1.FCStd
            │       ├── LocalPart2.FCStd
            │       ├── LocalPart3.FCStd
            │       ├── LocalPart4.FCStd
            │       └── LocalPart5.FCStd
            └── branches
```



## Release / Tagging

Tagging is a repository only action. It will not update anything on the db (inventree)

This allows the devs to create tags, but without a specific meaning in the "Plume" sense.


Releasing, on the other way, is a very specific process.

### Release in subversion

In the previous tree exemple, projects and libraries folder have no specific meaning, devs can organize their repository as they want.

the important part is that you have :

In /root/path/to/project

 - trunk/[sub/path]/file.FCStd
 - releases/[sub/path]/file/[version]/file.FCStd

When an Item has dependencies (assembly) in the folder or its subfolder, the dependencies files will be released into the version too.

In /root/path/to/project

 - trunk/[sub/path]/assembly.FCStd
 - trunk/[sub/path]/subpart.FCStd
 - releases/[sub/path]/assembly/[version]/assembly.FCStd
 - releases/[sub/path]/assembly/[version]/subpart.FCStd

for external dependencies, (shared parts/files), theses parts must be released before allowing a release on Inventree
(The tools will forbid to release the top level Item if it can't find the released version)

There is a quirk for the internal dependencies.
- When a sub part is release, the stamped (released) version is in the releases subfolder.
- It would be awfully complicated to go, in the assembly, back and forth from the released version and the trunk version. It is probably possible to make freecad change from the two versions, but on a complicated assembly, it would probably explode. (and take a lot of time to be recomputed)
- An "easy" solution is to Lock the sub part in the trunk, after its release, forbidding modification, except for a wanted acces.

the internal steps for releasing items of project:

1. it is not possible to release a top level object if its children are not in a released state.
2. release a sublevel object:
   1. update internal version/revision attribute of the (ONLY) plume object in the freecad document
   2. svn copy the file in releases/[sub/path]/file/[version]/file.FCStd
   3. lock the original file (avoiding modifications)
3. release a top (intermediate) object
   1. check if all sub objects are in released state:
      - related sub files are locked (not needed for external (not in project) files ?)
      - FreeCAD Objects (links) have a valid version.rev,
      - also have a valid released path (releases exists on disk)
   2. update internal version/revision attribute of the (ONLY) plume object in the freecad document
   3. copy the file in releases/[sub/path]/file/[version]/file.FCStd
   4. Create Symlinks for all related sub files from their RELEASES folders (not needed for external (not in project) files ?)
   5. unlock the children ?

4. Alternative to release a top object 
   1. Update internal links to point to the released files of the subobject
      - How ? Moving the file will break the relative path...
   2. update internal version/revision attribute of the (ONLY) plume object in the freecad document
   3. copy the file in releases/[sub/path]/file/[version]/file.FCStd

5. Alternative to release a top object (actually same as symlink but with a copy...)
   1. check if all sub objects are in released state:
      - related sub files are locked (not needed for external (not in project) files ?)
      - FreeCAD Objects (links) have a valid version.rev,
      - also have a valid released path (releases exists on disk)
   2. Copy the released versions of subobject in the releases/[sub/path]/file/[version]/ of the top object release path
   3. update internal version/revision attribute of the (ONLY) plume object in the freecad document
   4. copy the file in releases/[sub/path]/file/[version]/file.FCStd
  
And with svn switch ? 
   
### Inventree organization

Inventree is the database that store Items and Documents.
Each Item would hold informations, such as Version/Revision, and get output files attached. (steps, pdfs, etc)
It will also hold a link to the subversion release. (source files)

## Version Control



## Attributes


Item Related
- UUID : uuid / or InventreeID : Unique, ro
- Version : Number or string (ro, read from DB/filepath-tag ? or set up at release)
- Revision : Number or string (ro, ro, read from DB/filepath-tag ? or set up at release)
- 
- Type : List [MechanicalPart, MechanicalAssembly, OtherItem] (ro, guessed from type ? or not, a MA can be bought and would need to be atomic in the DB)
  - MechanicalPart
  - an MechanicalAssembly is, well, an assembly -> it groups Parts and Manufactured Parts, and/or sub assemblies
  - OtherItem: software, stickers, cable, etc..

- Manufactured: Bool, if False, the object is bought
  - a BoughtPart is bought from a distributor (a screw, a nut, a bearing, etc..) 
    - Fasteners can be managed as SharedPart... ?(and in the SharedFasteners.FCStd, they are handle as Part, that way they are managed by inventree, but it is not mandatory)
  - a ManufacturedPart needs steps to build : 3D Prints, CNC, Metal Work, WoodWork, etc..)
    - It could need "Material", ie plastic, Profiles, etc...
    - It has documents to describe the Item

DocumentsGenerators
- ExportedTechDrawPages: the list of related techdraw pages to export
- ExportedCNCJobs: the list of related techdraw pages to export (for ManufacturedPart)
- ExportedDXFs: the list of (techdrawpage) exported as DXF for manufacturing (for ManufacturedPart)
- (ExportSTEP): Bool, but I think it is not needed, Parts/ManufacturedParts and Assemblies needs a full STEP export right ? and a Fastener doesn't.
- ExternDoc (for external datasheet, etc : )




## Plumes Tools