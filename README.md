# Plume PDM

## Goals

The idea behind Plume is to get a tool and ecosystem to manage FreeCAD projects in a more collaborative way.
I think it is a PDM but I am not sure.

## State of the Art:

Several open source projects exists already;

- OpenPLM
- NanoPLM
- Taack https://github.com/Taack/taack-plm-freecad
- EasyPDM
- 
I need to dive into into it.

## Preliminars Ideas:

What I get in mind.

1. Manage source project files via CVS
    - zippey + fcinfo to be able to make commit from FreeCAD files
    - I need to check it is possible to merge / handle conflicts.
        - xmldiff to handle structural diff and not line to line.
        - Allows to open Diff in FreeCAD, highligtning diffs via xlmdiff ?
    - fcinfo + xmldiff looks like a good idea....
    - Provide a Workbench to handle control version direclty into FreeCAD.
    
    - Or Centralized SCV with Lock capability...
        - Since FreeCAD files are not exactly easy to handle textually speaking, I would find a way to lock a file when editing...
        Breezy handles distributde/centralized ?
        mekberg/boar ?
        - Git LFS wit lock ?
    - Work with a CVSC looks a good approch, allowing "libraries" of Parts, ie, wheels, etc... allowing use of FreeCAD Links capability without having multiple copies... ?

-> SVN looks like a winner for now...

2. Handles versionning, via git tags and branch.

3. Remove "LastModified" if not actually modified... less important with a Lock feature

4. Provide an integration with ERP / Inventary tool (Inventree looks a good approch !)
    - When a new version is pushed on the server, it will create/ update a project with source files, output/ std files (steps), drawings, etc
        - a build system via docker handles it?
        - Or via UID object in FreeCAD and a Dedicated Workbench
    - It creates /update parts into the inventary system.

5. Handle "locking" of Files


## First drafts of commands

Develop a workbench "Plume" that provide these tools:

- Tool : Configure/Create "PlumePart":
Add various property to the object (Part/PartDesign/etc/Assemblies)
  - UUID, immutable -> linked to the Inventree server -> Chained link to the past revisions ?
  - Version/Revision, updatable automatically or manually ?
  - Commit Hash (?)
  - Lock/Modified
    - Lock should be handle via SVN I guess, modified is flagged when modifying a Property via an observer.
- Tool : Lock/Unlock a Part - File
- Tool : Commit
  - Commit the file where the object is located
- Tool : Create/Tag a version -> Push on the Inventree server and "build" related files (STEP, DXF, PDF, ASM, BOM....)
    -> Recursivly ?


## SVN Repo layout and file organisation

In an organization (company, etc), in a FreeCAD way of organising stuff...
Every "Part" (Laser Cut, 3D, manufactured Part, internally or externally) should have its own FreeCAD file.
- A Frame (build with Frameforge) is in a single file, for instance.
- A 3D printed object too.
- An Assembly file (or more than one) handles the work of mixing all these parts together
- Screws, nut (from fasteners workbench for instance) are a specific case, they should be added in the Assembly file

It is specially true for SharedPart, that must be unique.
It allows better granularity and an easier file management.
Since everything is tagged, it will not break projects if a Shared File is modified in the "common" trunk for instance

Using a standard svn layout, with my very limited knowledge (yet) of SVN, the repositories should look like.

```
.
└── /
    ├── __shared__
    │   ├── trunk
    │   │   ├── SharedPart1.FCStd
    │   │   ├── SharedPart2.FCStd
    │   │   ├── SharedPart3.FCStd
    │   │   └── GroupOfSharedObjects
    │   │       ├── SharedPart4.FCStd
    │   │       └── SharedPart5.FCStd
    │   ├── branches
    │   └── tags
    │       ├── SharedPart1
    │       │   ├── 1.0
    │       │   │   └── SharedPart1.FCStd
    │       │   └── 1.1
    │       │       └── SharedPart1.FCStd
    │       ├── SharedPart2
    │       │   ├── 1.0
    │       │   │   └── SharedPart2.FCStd
    │       │   └── 1.1
    │       │       └── SharedPart2.FCStd
    │       ├── SharedPart3
    │       │   ├── 1.0
    │       │   │   └── SharedPart3.FCStd
    │       │   └── 1.1
    │       │       └── SharedPart3.FCStd
    │       └── GroupOfSharedObjects
    │           ├── SharedPart4
    │           │   └── 1.0
    │           │       └── SharedPart4.FCStd
    │           └── SharedPart5
    │               └── 1.0
    │                   └── SharedPart5.FCStd
    ├── project-A
    │   ├── trunk
    │   │   ├── Assembly.FCStd
    │   │   ├── LocalPart1.FCStd
    │   │   ├── LocalPart2.FCStd
    │   │   ├── LocalPart3.FCStd
    │   │   ├── LocalPart4.FCStd
    │   │   └── LocalPart5.FCStd
    │   ├── tags
    │   │   ├── 1.0
    │   │   │   ├── Assembly.FCStd
    │   │   │   ├── LocalPart1.FCStd
    │   │   │   ├── LocalPart2.FCStd
    │   │   │   ├── LocalPart3.FCStd
    │   │   │   └── LocalPart4.FCStd
    │   │   └── 2.0
    │   │       ├── Assembly.FCStd
    │   │       ├── LocalPart1.FCStd
    │   │       ├── LocalPart2.FCStd
    │   │       ├── LocalPart3.FCStd
    │   │       ├── LocalPart4.FCStd
    │   │       └── LocalPart5.FCStd
    │   └── branches
    └── project-B
        ├── trunk
        │   ├── Assembly.FCStd
        │   ├── LocalPart1.FCStd
        │   ├── LocalPart2.FCStd
        │   ├── LocalPart3.FCStd
        │   └── LocalPart4.FCStd
        ├── tags
        │   └── 1.0
        │       ├── Assembly.FCStd
        │       ├── LocalPart1.FCStd
        │       ├── LocalPart2.FCStd
        │       ├── LocalPart3.FCStd
        │       └── LocalPart4.FCStd
        └── branches
```

Projects follows the svn convention. But common parts doesn't really, since they could be used by other projects.
They must keep tracks of all of their versions, accessible to all the others projects.

## Plume Property for any objects:

Plume will add specific data (Properties) to objects.

List of Property: (in the Plume Group)

- UUID : uuid / or InventreeID
- Version : String in the form of x.y (will name the tag)
- Revision (Subversion): the related number to the commit 
- Type : List [Part, (Fastener), ManufacturedPart, Assembly]
  - a Part is bought from a distributor (a screw, a nut, a bearing, etc..) 
  - a ManufacturedPart needs steps to build : 3D Prints, CNC, Metal Work, WoodWork, etc..)
    - It could need "Material", ie plastic, Profiles, etc...
  - an Assembly is, well, an assembly -> it groups Parts and Manufactured Parts, and/or sub assemblies
  - a Fastener (from Fastener Workbench) is linked to a Inventree Part, it is a Part but I think multiples objects should be able to exists into multiples Assemblies,
    - It will just tells the UUID to the BOM generator... ?
    - No outputs ?
    - No revision / Version ?
    - Fasteners can be managed as SharedPart... ???? (and in the SharedFasteners.FCStd, they are handle as Part, that way they are managed by inventree, but it is not mandatory)
- Reference: an internal reference

- ExportedTechDrawPages: the list of related techdraw pages to export
- ExportedCNCJobs: the list of related techdraw pages to export (for ManufacturedPart)
- ExportedDXFs: the list of (techdrawpage) exported as DXF for manufacturing (for ManufacturedPart)
- (ExportSTEP): Bool, but I think it is not needed, Parts/ManufacturedParts and Assemblies needs a full STEP export right ? and a Fastener doesn't.


## Plume Tools

1. Repository Management
   1. Connect to a repository
   2. Update/Checkout
   3. 
   
2. Project Management
   1. Lock/Unlock Project (All files related to the project (current file))
   2. Lock/Unlock a File (inside a Project or Shared)
   3. Commit a file (on related trunk /branch / forbid commit on tags)
   4. Release/Tag a Shared File
        - Create a tag
        - Create a new version in Inventree
          - And create a Inventree Part if needed
          - if a file/subfile is in a trunk, it can't be created as a version in inventree (for the top project as well, the release is cancelled )
   5. Release/Tag a Project (a project is a file and all the dependancies)
        - Create a tag
        - Create a new version in Inventree for all related files/objects (if needed, regarding their version !)
          - And create a Inventree Part if needed
          - if a file/subfile is in a trunk, it can't be created as a version in inventree (for the top project as well, the release is cancelled )

3. Links Management
   1. Update SharedObject link to a specific version.