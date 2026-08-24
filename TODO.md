TODO
====

This list is here to define what is needed for a functionnal PoC.

## Server Stack

- [x] Understand svn workflow
- [x] run on RPI
- [x] mkcert
- [x] readonlylock (svn:needs-lock)

- [ ] Validate Server Backup/Restore
- [ ] (hook) Forbid to modify files in specifics sub folder (releases/exports)

- [ ] LDAP (lldap)
- [ ] svnadmin tool
- [ ] Validate use of Lore.io

## Core / Engine

- [x?] Improve SVNFileModel
- [x?] add plume version in object

- [.?] Handle PID(FF)
- [.] Handle Fasteners objects
- [.] Handle Frameforge objects
- [.] Common/get_export_dir : define an external folder (from WC) ? uncommited ?
  - [ ] Add rules in svn to avoid commiting specifics folder (exports)
  - [ ] multiple ways of export to inventree : flat, zipped, pathinname (current implementation)
- [.] Release <> Tags ? (release / publish)

- [ ] Rework / validate full work of svn + UT
- [ ] repo housekeeping / better sourcefile management / naming
- [ ] handle stock materials object (such as frameforge or woodstock)
- [ ] add revision to external 
- [ ] Import Assembly BOM Tool to Plume

- [ ] Fix svn.commit on folder in uncommited folder
- [ ] BuildReleaseFiles : gen BOM, CSV ?
- [ ] Export CNCs Jobs / STL
- [ ] Merge PDFs
- [ ] handle multiple PlumeID in same file
  - [ ] release_name is combination of filename/objname/IPN
- [ ] Improve log / debug
  - [ ] Fix No Catch of SVN EXception
  - [ ] Add log to display svn commands 
- [ ] Add Link to svn folder in inventree part

## UI
- [ ] Improve GUI 
  - [ ] Clear Selection in tree view
  - [ ] Avoid opening Tab / add button
  - [ ] Use task panel
- [ ] model/view for inventree in FC


## Others
- [ ] LICENCES / Packaging for 
  - [ ] pysvn
  - [ ] inventree
  - [ ] pip_system_certs


