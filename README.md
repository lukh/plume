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


## FreeCAD Integration

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
