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


- Repository
  
  Holds files under trunk for development, and releases/tags/branchs for releases/tags/wip

- Tags

  Tags are Subversion Tags.
  They are created at every version/revision/patch change.

- Branch
  
  Subversion Branches are available, up to the engineers to create/merge.

- File / Folder
  - Assembly
  - Part
 
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
#- name: type
#- name: type
#- name: type
#- name: type

```

The repository is organised as follow :


```
.
.
.
└── /
    ├── plume.yml
    ├── parts
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
            │   └── parts
            │       ├── LocalPart1.FCStd
            │       ├── LocalPart2.FCStd
            │       ├── LocalPart3.FCStd
            │       ├── LocalPart4.FCStd
            │       ├── LocalPart5.FCStd
            │       ├── SharedPart1.FCStd -> [root://parts/releases/SharedPart1/1.1/SharedPart1.FCStd]
            │       ├── SharedPart2.FCStd -> [root://parts/releases/SharedPart2/1.1/SharedPart2.FCSt]
            │       └── SharedPart4.FCStd -> [root://parts/releases/GroupOfSharedObjects/SharedPart4/1.0/SharedPart4.FCStd]
            ├── releases
            │   ├── Assembly
            │   │   ├── 1.A
            │   │   │   ├── Assembly.FCStd
            │   │   │   └── parts
            │   │   │       ├── LocalPart1.FCStd - > [root://projects/project-A/releases/LocalPart1/1.B/LocalPart1.FCStd]
            │   │   │       ├── LocalPart2.FCStd - > [root://projects/project-A/releases/LocalPart2/2.A/LocalPart2.FCStd]
            │   │   │       ├── LocalPart3.FCStd - > [root://projects/project-A/releases/LocalPart3/1.A/LocalPart3.FCStd]
            │   │   │       ├── LocalPart4.FCStd - > [root://projects/project-A/releases/LocalPart4/2.A/LocalPart4.FCStd]
            │   │   │       ├── LocalPart5.FCStd - > [root://projects/project-A/releases/LocalPart5/2.C/LocalPart5.FCStd]
            │   │   │       ├── SharedPart1.FCStd -> [root://parts/releases/SharedPart1/1.1/SharedPart1.FCStd]
            │   │   │       ├── SharedPart2.FCStd -> [root://parts/releases/SharedPart2/1.1/SharedPart2.FCSt]
            │   │   │       └── SharedPart4.FCStd -> [root://parts/releases/GroupOfSharedObjects/SharedPart4/1.0/SharedPart4.FCStd]
            │   │   └── 1.B
            │   │       ├── Assembly.FCStd
            │   │       └── parts
            │   │           ├── LocalPart1.FCStd - > [root://projects/project-A/releases/LocalPart1/2.A/LocalPart1.FCStd]
            │   │           ├── LocalPart2.FCStd - > [root://projects/project-A/releases/LocalPart2/2.A/LocalPart2.FCStd]
            │   │           ├── LocalPart3.FCStd - > [root://projects/project-A/releases/LocalPart3/1.D/LocalPart3.FCStd]
            │   │           ├── LocalPart4.FCStd - > [root://projects/project-A/releases/LocalPart4/2.B/LocalPart4.FCStd]
            │   │           ├── LocalPart5.FCStd - > [root://projects/project-A/releases/LocalPart5/2.C/LocalPart5.FCStd]
            │   │           ├── SharedPart1.FCStd -> [root://parts/releases/SharedPart1/1.1/SharedPart1.FCStd]
            │   │           ├── SharedPart2.FCStd -> [root://parts/releases/SharedPart2/1.1/SharedPart2.FCSt]
            │   │           └── SharedPart4.FCStd -> [root://parts/releases/GroupOfSharedObjects/SharedPart4/1.0/SharedPart4.FCStd]
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
            │   └── v2.0
            └── branches
```


Files exists under "repositories" : A sub folder of WC/root with 
  - a trunk folder for dev work
  - a tags folder, to make a snapshot of a specific svn version.
  - a releases folder, that will be linked with Inventree items
  - and a branch, used for development.
  
There are two types of files:
  - Autonomous files, that doesn't depends on others (Part)
  - Assemblies, that depens on other files in specific repositories


## Release / Tagging

Tagging is a repository only action. It will not update anything on the db (inventree)

This allows the devs to create tags, but without a specific meaning in the "Plume" sense.


Releasing, on the other way, is a very specific process.

### Release in subversion

There are two cases releasing a file. Releasing a file is a substep in releasing an Item. (since an item is contained into a Freecad file)

#### For an Autonomous files : 

the release is done in the releases top folder, without any other checks :

example: for a file in:

  > /projects/my-project/trunk/parts/MyPart.FCStd

will be released (as of version/rev 1.C)

  > /projects/my-project/releases/parts/MyPart/1.C/MyPart.FCStd

The path is then split into severals parts:

  > src: [rootpath]/trunk/[sub/path]/[filename].extension

  > dst: [rootpath]/releases/[sub/path]/[filename]/[ver.rev]/[filename].extension

The actual rootpath doesn't matter, it can be projects, libraries, parts, whatever.


STEPS:
- Ask the user the new ver/rev number (major/minor)
- Check the file is saved and commited (clean state),
- Check that the file is not already switched
- Check that the repository is up-to-date
- Check that there is only one "Plume Item" ("Part") in the File (or, since it is done in FC interface, select the item...)
- Check the Plume Item is not already released (release path doesn't exists)
- Update the Plume Item with ver/rev
  - This is a valid version in the trunk (what does that mean ???)
- (Generate Related Documents (TechDraw, DXF) from the Properties)
- and commit (on trunk) (only source file...)
- svn copy the source file to the release path, with the generated (uncommited) files if svn allows it. (and the config asks for it)


#### For a file depending on others : 

The main usecase here is an assembly.

The same steps as for a single file will apply, but extra steps are mandatory to check the state of dependent Items.

for each sub item : 
  - check the path is switched to a released version
    - Either it is an internal sub part (living into the assembly folder or its subfolder) or an external part
  - check the Item has the same ver/rev as the release folder
  - svn copy all the related files/link to the release folder



## Switch versions of files

For the release to work correctly, it is mandatory to be able to "svn switch" a file (Part)
from version to another version.

This is done via the svn switch command. It allows to switch from the trunk version to a specific version of the file.

Commiting a file is prohibited if it is switched, since it is gonna commit on the "release"
   
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
#- Fasteners can be managed as SharedPart... ?(and in the SharedFasteners.FCStd, they are handle as Part, that way they are managed by inventree, but it is not mandatory)
  - a ManufacturedPart needs steps to build : 3D Prints, CNC, Metal Work, WoodWork, etc..)
#- It could need "Material", ie plastic, Profiles, etc...
#- It has documents to describe the Item

DocumentsGenerators
- ExportedTechDrawPages: the list of related techdraw pages to export
- ExportedCNCJobs: the list of related techdraw pages to export (for ManufacturedPart)
- ExportedDXFs: the list of (techdrawpage) exported as DXF for manufacturing (for ManufacturedPart)
- (ExportSTEP): Bool, but I think it is not needed, Parts/ManufacturedParts and Assemblies needs a full STEP export right ? and a Fastener doesn't.
- ExternDoc (for external datasheet, etc : )




## Plumes Tools