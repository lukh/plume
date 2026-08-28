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

   They have a unique id, "PlumeIPN", version+revision number, and attributes.

   Items have links to specific Tags in the Subversion repository, 

- Documents

  Documents describe the Items for manufacturing. (BoM, Schematics, STEP file, etc)
  They are linked to a specific versionned Item.
  It can be PDF, CSV, STEP, DXF, etc.

- Versionning

  Each Item and their Documents have a numbering scheme.

  - Version

#It is a major revision. (functionnal status, when a part change completly, )
#Numbering as 1, 2, 3, etc

  - Revision
  
#A Minor revision on the part.
#Numbering A, B, C, D, etc.

- Repository
  
  A SVN root Working Copy. 

  Holds files under trunk for development, and releases/tags/branchs for releases/tags/wip

- Tags

  Tags are Subversion Tags.

  It is used to stamp a development step, that should not be released

  They can be used for internal needs, not rattached to anything special in Plume.


- Branch
  
  Subversion Branches are available, up to the engineers to create/merge.

  For instance, one needs to validate a specific feature, fix a complicated bug, etc

- FreeCAD File

The FreeCAD files are saved and tracked by the SVN Repository.
 
  Standard FreeCAD file. They can hold more than one Item, and can also hold several Document rattached to the Items

- Lock/Unlock

  Since FreeCAD files are Binary files, it is mandatory to lock others when working on a file.

  Each time a user wants to modify an item or a document, it is necessary to perform a check-out action, so that it is locked for everybody else. 
  After the changes have been made, the user performs a check-in action and the object is then free for the team to change it the same way

  A CheckOut needs two actions:

#- Update the repository
#- Lock the file

  A CheckIn needs twp actions:

#- Commit the file
#- Unlock it.


- Commit

Save Files/Folder on the main repository, in the specified place.

A Commit hold a commit message; allowing to ease development step, and hold a commit number. A Commit is on the top of a previous, in a linked way.

- Release (action) : release an Item, from a File.

The release action is launched from an Item in the file.
If possible (PlumeIPN available, files are clean, version are set-up) it will create a "tag" (copy trunk into a releases subfolder) with all related files


- Export : Taxke a release and perform :
  - Export of Documents related to Item
  - Publish to Inventree server for integration in ERP

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
├── .
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
    │   ├── exports
    │   │   └── SharedPart1
    │   │       └── 1.0
    │   │           ├── SharedPart1.step
    │   │           └── SharedPart1.pdf
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
            ├── exports
            │   └── Assembly
            │       └── 1.A
            │           ├── Assembly.step
            │           ├── Schematic.pdf
            │           └── BOM.csv
            ├── tags
            │   ├── v1.0
            │   └── v2.0
            └── branches
```


Files exists under "repositories" : A sub folder of WC/root with 
  - a trunk folder for dev work
  - a tags folder, to make a snapshot of a specific svn version.
  - a releases folder, that will be linked with Inventree items
  - and a branches folder, used for development.
  
Files holds two types of Item
  - Part Item, that doesn't depends on others (Part)
  - Assemblies Item, that depens on other Items inside the files or from other files


## Release / Tagging

Tagging is a repository only action. It will not update anything on the db (inventree)

This allows the devs to create tags, but without a specific meaning in the "Plume" sense.


Releasing, on the other way, is a very specific process.

### Release in subversion

There are two cases releasing an Item.

#### For an Part Item : 

For a file in:

  > /projects/my-project/trunk/parts/MyPart.FCStd

That hold a FreeCAD Plume Object with item name mypart :

will be released (as of version/rev 1.C)

  > /projects/my-project/releases/parts/MyPart/mypart/1.C/MyPart.FCStd

The path is then split into severals parts:

  > src: [rootpath]/trunk/[sub/path]/[filename].extension

  > dst: [rootpath]/releases/[sub/path]/[filename]/[item_name]/[ver.rev]/[filename].extension

The actual rootpath doesn't matter, it can be projects, libraries, parts, whatever.


STEPS in releasing, managed by Plume:
- Check new ver/rev number (major/minor)
- Check the file is saved and commited (clean state),
- Check that the file is not already switched
- Check that the repository is up-to-date
- Check the Plume Item is not already released (release path doesn't exists)
- svn copy the source file to the release path, with the generated (uncommited) files if svn allows it. (and the config asks for it)


#### For a file depending on others : 

The main usecase here is an assembly.

The same steps as for a single file will apply, but extra steps are mandatory to check the state of dependent Items.

for each sub item : 
  - check the path is switched to a released version
  - check the Item has the same ver/rev as the release folder
  - svn copy all the related files/link to the release folder



## Switch versions of files

For the release to work correctly, it is mandatory to be able to "svn switch" a file (Part)
from version to another version.

This is done via the svn switch command. It allows to switch from the trunk version to a specific version of the file.

Commiting a file is prohibited if it is switched, since it is gonna commit on the "release"
   


## Export

The export is the last steps to put Item in production.

### Generate Document

From a released Item in the SVN repository, it will generate all the files needed for manufacturing

- STEP file
- PDFs
- DXF
- BOM
- CNC Jobs
- etc.


### Publish to Inventree

Inventree is the database that store Items and Documents.

When Documents have been checked, the "Publish" command will :

- Commit file under "exports" folder following the same pattern of folder creation as release.
- Create a new "Part" in Inventree, linking the


Each Item would hold informations, such as Version/Revision, and get output files attached. (steps, pdfs, etc)
It will also hold a link to the subversion release. (source files)



## Plume WB Implementation

A "PlumeObject" is a standard FreeCAD object (Body, Part, Assembly, etc...)

that holds properties

## Property

Item Related
- PlumeIPN : Unique Internal Part Number, ro
- Version : Number or string (ro, read from DB/filepath-tag ? or set up at release)
- Revision : Number or string (ro, ro, read from DB/filepath-tag ? or set up at release)

- Type : List [MechanicalPart, MechanicalAssembly, OtherItem] (ro, guessed from type ? or not, a MA can be bought and would need to be atomic in the DB)
  - MechanicalPart
  - an MechanicalAssembly is, well, an assembly -> it groups Parts and Manufactured Parts, and/or sub assemblies

- Manufactured: Bool : made internally
- Purchased : Bool. a Purchased Part is bought from a distributor (a screw, a nut, a bearing, etc..) 

- Virtual : For part that must be in the BOM but doesn't have physical reality : Software Licence/Version, etc.
- DatabaseLink : For Part that have a physical reality, but doesn't needs to be released/exported: Fasteners fall into this category.

- StockMaterialIPN : when a Part must be build from raw stock, link to the Inventree IPN Material

  For Panels, Profiles, etc.... 

- StockMaterialQuantity : the Quantity needed to make (unit wise, must fit with unit in Inventree)

DocumentsGenerators
- ExportedTechDrawPages: the list of related techdraw pages to export
- ExportedCNCJobs: the list of related techdraw pages to export (for ManufacturedPart)
- ExportedDXFs: the list of (techdrawpage) exported as DXF for manufacturing (for ManufacturedPart)
- (ExportSTEP): Bool, but I think it is not needed, Parts/ManufacturedParts and Assemblies needs a full STEP export right ? and a Fastener doesn't.
- ExternDoc (for external datasheet, etc : )


