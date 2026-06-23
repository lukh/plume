import os
import pprint
import svn.remote
import svn.local

class PlumeSvnException(Exception):
    pass

class PlumeSvn(object):
    def __init__(self, workcopy, repo_url=None):
        workcopy = os.path.abspath(workcopy)

        self.local_repo = svn.local.LocalClient(workcopy)
        if repo_url is None:
            repo_url = self.local_repo.common_info()['url']

        repo_url = repo_url.rstrip("/")
        self.remote_repo = svn.remote.RemoteClient(repo_url)


        self.working_copy = workcopy
        self.repo_url = repo_url

    def update(self, paths=[], revision=None):
        self.local_repo.update(rel_filepaths=[self.get_rel_path(p) for p in paths], revision=revision)

    def add(self, path):
        path = self.get_rel_path(path)
        if self.is_path_switched(path): # TODO : can't be switched if not in repo ???
            raise PlumeSvnException(f'file {path} is switched')

        self.local_repo.add(rel_path=path)

    def commit(self, message, paths=[]):
        for rf in paths:
            if self.is_path_switched(rf):
                raise PlumeSvnException(f'file {rf} is switched')

        self.local_repo.commit(message, rel_filepaths=paths)

    def is_path_locked(self, rel_path):
        ret = self.path_status(rel_path)
        return ret.locked

    def lock(self, paths=[], message=None):
        for p in paths:
            self.local_repo.lock(self.get_rel_path(p), msg=message)

    def unlock(self, paths=[]):
        for p in paths:
            self.local_repo.unlock(self.get_rel_path(p))

    def get_abs_path(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.working_copy, path)

        # if not os.path.exists(path):
        #     raise ValueError(f"can't get relative path for {path}")

        return path

    def get_rel_path(self, path):
        """
        Returns the relative (to self.working_copy) path from an absolute path 
        """
        if not os.path.isabs(path):
            rp = path
        else:
            rp = os.path.relpath(path, start=self.working_copy)

        # if not os.path.exists(os.path.join(self.working_copy, rp)):
        #     raise ValueError(f"can't get relative path for {path}")

        return rp

    def is_in_repository(self, abs_path):
        """
        check the file is in the repository
        
        abs_path is an absolute path (eg. /home/user/svn_wc/my_project/trunk/myfile)
        """
        try:
            cp = os.path.commonpath([abs_path, self.working_copy])
            return os.path.samefile(cp, self.working_copy)
        except ValueError:
            return False

    def is_path_unversioned(self, path):
        rel_path = self.get_rel_path(path)
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} is not a file")

        l = list(self.local_repo.status(rel_path))
        if len(l) != 1:
            return False
        status = l[0]

        return status.type_raw_name == "unversioned"

    def is_path_clean(self, path):
        rel_path = self.get_rel_path(path)

        st_rep = list(self.local_repo.status(rel_path))

        if len(st_rep) > 0:
            for s in st_rep:
                if s.type_raw_name != "normal":
                    return False

        return True

    def path_status(self, path):
        rel_path = self.get_rel_path(path)
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        l = list(self.local_repo.status(rel_path))
        if len(l) == 0:
            return svn.local._STATUS_ENTRY(name=rel_path, type_raw_name="normal", type=None, revision=None, switched=None, locked=False, external=False)
        if len(l) > 1:
            raise PlumeSvnException(f"{rel_path} more than one entry")
        status = l[0]

        return status

    def status(self, path=""):
        rel_path = self.get_rel_path(path)
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        return list(self.local_repo.status(rel_path))

    def get_url(self, path):
        """
        Returns the URL from an absolute or relative path 
        """
        rp = self.get_rel_path(path)

        return self.repo_url + "/" + rp

    def is_trunk_path(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} is not a file")

        return os.sep + 'trunk' in rel_path

    def split_trunk_path(self, rel_path):
        """
        Split a path (from self.working_copy) to
        [root_path]/trunk/[subpath]/[filename]
        :ret : (rootpath, subpath, filename)
        """
        if not self.is_trunk_path(rel_path):
            raise PlumeSvnException(f"{rel_path} is not in a trunk")


        rootpath, after_trunk_path = rel_path.split(os.sep + "trunk")
        after_trunk_path = after_trunk_path.lstrip(os.sep)

        subpath, filename = os.path.split(after_trunk_path)

        return rootpath, subpath, filename

    def get_trunk_path(self, rootpath, subpath="", filename=""):
        """
        Returns a trunk path (from self.working_copy) from rootpath, subpath, filename
        """
        p = f"{rootpath.strip(os.sep)}{os.sep}trunk{os.sep}{subpath.strip(os.sep)}{os.sep}{filename.strip(os.sep)}"
        return os.path.normpath(p)

    def is_release_path(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} is not a file")

        return os.sep + 'releases' in rel_path

    def split_release_path(self, rel_path):
        if not self.is_release_path(rel_path):
            raise PlumeSvnException(f"{rel_path} is not in a release")

        rootpath, after_release_path = rel_path.split("releases")

        ar_split = after_release_path.lstrip(os.sep).split(os.sep)
        
        filename = ar_split.pop()
        version, revision = ar_split.pop().split(".")
        release_name = ar_split.pop()

        if len(ar_split) > 0:
            subpath = os.path.join(*ar_split)
        else:
            subpath = ""

        return (rootpath, subpath, release_name, version, revision, filename)



    def get_release_path(self, rootpath, subpath, release_name, version, revision, filename):
        p = f"{rootpath.strip(os.sep)}{os.sep}releases{os.sep}{subpath.strip(os.sep)}{os.sep}{release_name}{os.sep}{version}.{revision}{os.sep}{filename.strip(os.sep)}"
        return os.path.normpath(p)

    def get_releases_available(self, rel_trunk_path, release_name=None):
        rootpath, subpath, filename = self.split_trunk_path(rel_trunk_path)
        if release_name is None:
            release_name = os.path.splitext(filename)[0]

        p = f"{rootpath.strip(os.sep)}{os.sep}releases{os.sep}{subpath.strip(os.sep)}{os.sep}{release_name}"
        releases_path = self.get_abs_path(os.path.normpath(p))

        if not os.path.isdir(releases_path):
            raise PlumeSvnException(f"{releases_path} doesn't exist")

        return [d for d in os.listdir(releases_path) if os.path.isdir(os.path.join(releases_path, d))]

    def is_path_switched(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} is not a file")

        l = list(self.local_repo.status(rel_path))
        if len(l) != 1:
            return False
        status = l[0]

        return status.switched

    def get_switched_path(self, rel_path):
        if not self.is_path_switched(rel_path):
            raise PlumeSvnException(f"{rel_path} is not switched")

        l = list(self.local_repo.info(rel_path))
        if len(l) != 1:
            raise PlumeSvnException("more info than able to process")

        info = l[0]

        return os.path.relpath(info.url, self.repo_url)

    def switch(self, rel_trunk_path, release_name, version, revision):
        if not self.is_trunk_path(rel_trunk_path):
            raise PlumeSvnException(f"{rel_trunk_path} is not in a trunk")
            
        if not self.is_path_clean(rel_trunk_path):
            raise PlumeSvnException(f"Can't switch, {rel_trunk_path} is not clean")

        rootpath, subpath, filename = self.split_trunk_path(rel_trunk_path)

        dest_path = self.get_release_path(rootpath, subpath, release_name, version, revision, filename)

        if not self.is_release_path(dest_path):
            raise PlumeSvnException(f"{dest_path} is not a release")

        dest_url = self.get_url(dest_path)
        
        self.local_repo.switch(dest_url, rel_trunk_path)

    def unswitch(self, rel_trunk_path):
        if not self.is_trunk_path(rel_trunk_path):
            raise PlumeSvnException(f"{rel_trunk_path} is not in a trunk")

        if not self.is_path_clean(rel_trunk_path):
            raise PlumeSvnException(f"Can't unswitch, {rel_trunk_path} is not clean")

        dest_url = self.get_url(rel_trunk_path)

        self.local_repo.switch(dest_url, rel_trunk_path)


    def is_path_external(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise PlumeSvnException(f"{rel_path} is not a file")

        l = list(self.local_repo.status(rel_path))
        if len(l) != 1:
            return False
        status = l[0]
        return status.external


    def get_externals(self, rel_root_path):
        """
        returns externals of a root path in the form
        {dest:url, ...}
        dest from trunk
        """
        rel_trunk_path = os.path.join(rel_root_path, "trunk")
        if not os.path.exists(os.path.join(self.working_copy, rel_trunk_path)):
            raise PlumeSvnException(f"{rel_trunk_path} doesn't exist")

        props = self.local_repo.properties(rel_trunk_path)
        externals = {}
        for ext in props.get("svn:externals", "").strip("\n").split('\n'):
            ed = ext.split()
            if len(ed) == 2:
                url, dest = ed
                externals[dest] = url
            elif len(ed) == 0:
                print("empty svn:externals ?")
            else:
                raise PlumeSvnException(f"Can't handle externals props for {rel_trunk_path}")

        return externals
        

    def set_externals(self, rel_root_path, externals, commit_msg=None):
        """
        param externals: {dest:url, ...}
        """
        rel_trunk_path = os.path.join(rel_root_path, "trunk")
        if not os.path.exists(os.path.join(self.working_copy, rel_trunk_path)):
            raise PlumeSvnException(f"{rel_trunk_path} doesn't exist")

        self.local_repo.set_properties(
            rel_trunk_path , 
            "svn:externals", 
            "\n".join([f"{externals[des]} {des}" for des in externals])
        )

        if commit_msg is None:
            commit_msg = f"set externals for {rel_trunk_path}"
        self.local_repo.commit(commit_msg)
        self.local_repo.update([rel_trunk_path])


    def add_externals(self, rel_root_path, dest_sub_dir, rel_targets_path, commit_msg=None):
        rel_trunk_path = os.path.join(rel_root_path, "trunk")
        if not os.path.exists(os.path.join(self.working_copy, rel_trunk_path)):
            raise PlumeSvnException(f"{rel_trunk_path} doesn't exist")

        dest_dir = os.path.join(self.get_abs_path(rel_trunk_path), dest_sub_dir)

        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
            self.local_repo.add(dest_dir)
            self.local_repo.commit(f"add {dest_dir} in {rel_trunk_path}", rel_filepaths=[dest_dir])


        externals_files = []
        for rtp in rel_targets_path:
            if not self.is_release_path(rtp):
                raise PlumeSvnException(f"{rtp} not in a release path")
            if self.is_path_switched(rtp):
                raise PlumeSvnException(f"{rtp} is switched")

            externals_files.append(
                (
                    self.get_url(rtp), 
                    os.path.join(dest_sub_dir, os.path.split(rtp)[1])
                )
            )

        existing_props = self.local_repo.properties(rel_trunk_path)
        existings_externals = existing_props.get("svn:externals", "")
        self.local_repo.set_properties(
            rel_trunk_path , 
            "svn:externals", 
            existings_externals + "\n".join([" ".join(ef) for ef in externals_files])
        )

        if commit_msg is None:
            commit_msg = f"Add externals to {rel_root_path}"

        self.local_repo.commit(commit_msg)
        self.local_repo.update([rel_trunk_path])


    def initialize_repo():
        """
        initialize a repository for use with plume
        """
        pass


    def create_project(self, rel_proj_path, commit=True):
        """
        Create a project in rel_proj_path.
        Add trunk, tags, releases and branches subfolders into the above path
        Commit the changes if commit arg
        """
        if os.path.exists(os.path.join(self.working_copy, rel_proj_path)):
            raise PlumeSvnException(f"{rel_proj_path=} aldready exsist in {self.working_copy}")

        if self.path_status(os.path.split(rel_proj_path)[0]).type_raw_name != "normal":
            raise PlumeSvnException(f"{rel_proj_path=} is not in 'normal' state")


        os.makedirs(os.path.join(self.working_copy, rel_proj_path))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "trunk"))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "releases"))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "tags"))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "branches"))

        self.local_repo.add(f"{rel_proj_path}", do_include_parents=True)
        if commit:
            self.local_repo.commit(f"adding {rel_proj_path} structure", rel_filepaths=[rel_proj_path])


    def release(self, rootpath, release_name, version, revision, sub_paths=[], commit_msg=None):
        """
        Release files or folder (project)
        :root_path : path to root folder (containing trunk, tags, releases and branches)
        :tag_name : the name of the release
        :subpaths : a list of (subpath, filename) (from the current trunk) to be released (file or folder/project)
          or empty list (default) to release the folder

        the subpath is reproduced inside the releases folder.

        The first sub_paths element is the "main file", ie it must be unswitched
        The others must be switched on a specific release
        """

        # check that the WC is clean
        if not self.is_path_clean(self.get_trunk_path(rootpath)):
            raise PlumeSvnException(f"{rootpath} is not clean")

        release_root_path = self.get_release_path(rootpath, "", release_name, version, revision, "")
        abs_release_root_path = os.path.join(self.working_copy,release_root_path)
        if os.path.isdir(abs_release_root_path):
            raise PlumeSvnException(f"{rootpath} release dir already exists")

        filepaths = []
        externals_files = []

        # check files are in order : first one is unswitched, others are
        for idx, (sp, filename) in enumerate(sub_paths):
            trunk_path = self.get_trunk_path(rootpath, sp, filename)
            release_path = self.get_release_path(rootpath, sp, release_name, version, revision, filename)

            if not os.path.isfile(self.get_abs_path(trunk_path)):
                raise PlumeSvnException(f"{trunk_path} doesn't exist")
            if os.path.isfile(self.get_abs_path(release_path)):
                raise PlumeSvnException(f"{release_path} already exists")

            external = self.is_path_external(trunk_path)
            switched = self.is_path_switched(trunk_path)
            
            if not external:
                if idx == 0:
                    if switched:
                        raise PlumeSvnException(f"release: problem on file {trunk_path} : the main file is switched")

                    filepaths.append((trunk_path, release_path))
                
                else:
                    if not switched:
                        raise PlumeSvnException(f"release: problem on file {trunk_path} : sub file not switched")

                    filepaths.append((self.get_switched_path(trunk_path), release_path))
            else:
                sts = list(self.local_repo.info(trunk_path))
                if len(sts) != 1:
                    raise PlumeSvnException(f"release : error while analysing ext file {trunk_path}")

                st = sts[0]
                url = st.url

                externals_files.append((url, filename))


        release_root_parent = os.path.split(release_root_path)[0]
        if (not os.path.isdir(os.path.join(self.working_copy, release_root_parent))) or (self.path_status(release_root_parent).type_raw_name == "unversioned"):
            self.local_repo.mkdir(release_root_parent, parents=True)
            self.local_repo.commit(f"add release folder for {release_name}", rel_filepaths=[release_root_parent])

        for tp, rel_p in filepaths: # switched files, and main root file
            # print("file to add: ", tp, rel_p)
            t_url = self.get_url(tp)
            self.local_repo.copy(t_url, rel_p, make_parents=True)

        # TODO : add externals to release
        if len(externals_files) > 0:
            self.local_repo.set_properties(
                release_root_path, 
                "svn:externals", 
                "\n".join([" ".join(ef) for ef in externals_files])
            )

        if commit_msg is None:
            commit_msg = f"Release {release_name}:{version}.{revision}"

        self.local_repo.commit(commit_msg, rel_filepaths=[release_root_path])



    # def tag_library_file(rel_path, tag_name, commit_msg=None):
    #     """
    #     Create a tag for a file in a subfolder (or in) 
    #     LIBRARIES_ROOT/trunk

    #     The tag will be in 
    #     LIBRARIES_TOOT/tags/{rel_path without ext}/{tag_name}/{filename}
    #     """
    #     self.working_copy_trunk_path = os.path.join(LIBRARIES_ROOT, "trunk", rel_path)

    #     # check existence of file
    #     if not os.path.exists(os.path.join(self.working_copy, self.working_copy_trunk_path)):
    #         raise ValueError(f"{rel_path} doesn't exist")

    #     if not os.path.isfile(os.path.join(self.working_copy, self.working_copy_trunk_path)):
    #         raise ValueError(f"{rel_path} is not a file")

    #     # check file is up-to-date with the server
    #     status = [s for s in self.local_repo.status(self.working_copy_trunk_path)]
    #     if len(status) > 0:
    #         raise Exception(f"{rel_path} is not up-to-date on the server: {status[0].type_raw_name}")

    #     src_url = self.working_copy_trunk_path
    #     # if not os.path.isfile(src_url):
    #     #     raise Exception(f"{src_url} must be a file")

    #     filename = os.path.basename(rel_path)
    #     basename = os.path.splitext(filename)[0]
    #     dirname = os.path.dirname(rel_path)
        
    #     tag_url = os.path.join(LIBRARIES_ROOT, "tags", dirname, basename, tag_name, filename)

    #     if os.path.exists(os.path.join(self.working_copy, tag_url)):
    #         raise Exception(f"{tag_url} already exists")

    #     if not commit_msg:
    #         commit_msg = f"Tagging project {rel_path}/{tag_name}"

    #     self.remote_repo.copy(src_url, tag_url, commit_msg, make_parents=True)


    # def tag_project(rel_path, tag_name, commit_msg=None):
    #     """
    #     Create a tag for a folder like 
    #     PROJECTS_ROOT/rel_path/trunk

    #     The tag will be in 
    #     PROJECTS_ROOT/{rel_path}/tags/{tag_name}
    #     """
    #     self.working_copy_trunk_path = os.path.join(PROJECTS_ROOT, rel_path, "trunk")
    #     print(self.working_copy_trunk_path)

    #     # check existence of file
    #     if not os.path.exists(os.path.join(self.working_copy, self.working_copy_trunk_path)):
    #         raise ValueError(f"{rel_path} doesn't exist")

    #     if not os.path.isdir(os.path.join(self.working_copy, self.working_copy_trunk_path)):
    #         raise ValueError(f"{rel_path} is not a directory")

    #     # check file is up-to-date with the server
    #     status = [s for s in self.local_repo.status(self.working_copy_trunk_path)]
    #     if len(status) > 0:
    #         raise Exception(f"{rel_path} is not up-to-date on the server: {status[0].type_raw_name}")

    #     src_url = self.working_copy_trunk_path
    #     tag_url = os.path.join(PROJECTS_ROOT, rel_path, "tags", tag_name)
    #     print(tag_url)

    #     if os.path.exists(os.path.join(self.working_copy, tag_url)):
    #         raise Exception(f"{tag_url} already exists")

    #     if not commit_msg:
    #         commit_msg = f"Tagging project {rel_path}/{tag_name}"

    #     self.remote_repo.copy(src_url, tag_url, commit_msg, make_parents=True)



# info = self.local_repo.info()
# pprint.pprint(info)

# initialize_repo()

# create_project("MyAweSomeProject")
# tag_project("MyAweSomeProject", "0.2")
# tag_library_file("fasteners/MyFastener.FCStd", "0.2")

# self.remote_repo.lock("projects/MyAweSomeProject/trunk/README.md")
# self.remote_repo.unlock("projects/MyAweSomeProject/trunk/README.md")
# self.local_repo.lock("projects/MyAweSomeProject/trunk/README.md")
# self.local_repo.unlock("projects/MyAweSomeProject/trunk/README.md")