# Plume PDM

DISCLAIMER : At the moment, this project is not, in any way, ready for production.
It is a valid PoC though, and I loved to get feedback :)

I am working actively on it, but it is still a secondary project for now. (but needed for my work as [Bike Trailer Manufacturer](https://www.microforge.fr))

## Goals

The idea behind Plume is to get a tool and ecosystem to manage FreeCAD projects in a more collaborative way.

Key points :

- Allows teams to work together on projects and files
- Integrated into FreeCAD
- Use already existing tools, to ease development and leverage on great workflow
- Provide a workflow from development to production, managing parts/ipn and stock, build order, etc.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L41KKMJR)


Plume is based on Subversion and Inventree.

Subversion is a Control Version System, a "old" one, but it allows to work in Lock/Modify/Commit, which is needed to work on binary file (such as FreeCAD). It allow developpers to handle dev files.

Inventree is a Inventory Management System, Allowing to create Parts, handle storage and stock, and pass Build Order. 
It is used to release a "Project", part, tracking their version in sync with SVN.

Plume is the FreeCAD Workbench that glue these tools together.

## State of the Art:

Several open source projects exists already;

- OpenPLM
- NanoPLM
- Taack https://github.com/Taack/taack-plm-freecad
- EasyPDM
- FreePLM
  
I need to dive into into it.


## Current Work:

Check [Specifications](docs/SPECIFICATIONS.md) for getting a view of the concepts. (At the moment, the specs are out-of-date since it moved while working on the PoC)

Check [TODO](TODO.md) for getting a view of the work done, and what need to be done for a stable / fancy enough version

There is a [video](https://www.youtube.com/watch?v=fIUK7SWVy9U) as well, in French with subtitle, 


## (Chain of tought) Preliminars Ideas:

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

