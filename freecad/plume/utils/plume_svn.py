import os
import pprint
import svn.remote
import svn.local


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
            raise ValueError(f'file {path} is switched')

        self.local_repo.add(rel_path=path)

    def commit(self, message, paths=[]):
        for rf in paths:
            if self.is_path_switched(rf):
                raise ValueError(f'file {rf} is switched')

        self.local_repo.commit(message, rel_filepaths=paths)

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

    def is_path_unversioned(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} is not a file")

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

        
    def get_url(self, path):
        """
        Returns the URL from an absolute or relative path 
        """
        rp = self.get_rel_path(path)

        return self.repo_url + "/" + rp

    def is_trunk_path(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} is not a file")

        return os.sep + 'trunk' in rel_path

    def split_trunk_path(self, rel_path):
        """
        Split a path (from self.working_copy) to
        [root_path]/trunk/[subpath]/[filename]
        :ret : (rootpath, subpath, filename)
        """
        if not self.is_trunk_path(rel_path):
            raise ValueError(f"{rel_path} is not in a trunk")


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
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} is not a file")

        return os.sep + 'releases' in rel_path

    def split_release_path(self, rel_path):
        if not self.is_release_path(rel_path):
            raise ValueError(f"{rel_path} is not in a release")

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



    def is_path_switched(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} is not a file")

        l = list(self.local_repo.status(rel_path))
        if len(l) != 1:
            return False
        status = l[0]

        return status.switched

    def get_switched_path(self, rel_path):
        if not self.is_path_switched(rel_path):
            raise ValueError(f"{rel_path} is not switched")

        l = list(self.local_repo.info(rel_path))
        if len(l) != 1:
            raise ValueError("more info than able to process")

        info = l[0]

        return os.path.relpath(info.url, self.repo_url)

    def switch(self, rel_trunk_path, release_name, version, revision):
        if not self.is_trunk_path(rel_trunk_path):
            raise ValueError(f"{rel_trunk_path} is not in a trunk")
            
        if not self.is_path_clean(rel_trunk_path):
            raise ValueError(f"Can't switch, {rel_trunk_path} is not clean")

        rootpath, subpath, filename = self.split_trunk_path(rel_trunk_path)

        dest_path = self.get_release_path(rootpath, subpath, release_name, version, revision, filename)

        if not self.is_release_path(dest_path):
            raise ValueError(f"{dest_path} is not a release")

        dest_url = self.get_url(dest_path)
        
        self.local_repo.switch(dest_url, rel_trunk_path)

    def unswitch(self, rel_trunk_path):
        if not self.is_trunk_path(rel_trunk_path):
            raise ValueError(f"{rel_trunk_path} is not in a trunk")

        if not self.is_path_clean(rel_trunk_path):
            raise ValueError(f"Can't unswitch, {rel_trunk_path} is not clean")

        dest_url = self.get_url(rel_trunk_path)

        self.local_repo.switch(dest_url, rel_trunk_path)




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
            raise Exception(f"{rel_proj_path=} aldready exsist in {self.working_copy}")

        os.makedirs(os.path.join(self.working_copy, rel_proj_path))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "trunk"))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "releases"))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "tags"))
        os.makedirs(os.path.join(self.working_copy, rel_proj_path, "branches"))

        self.local_repo.add(f"{rel_proj_path}", do_include_parents=True)
        if commit:
            self.local_repo.commit(f"adding {rel_proj_path} structure")


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
            raise ValueError(f"{rootpath} is not clean")

        filepaths = []

        # check files are in order : first one is unswitched, others are
        for idx, (sp, filename) in enumerate(sub_paths):
            trunk_path = self.get_trunk_path(rootpath, sp, filename)
            release_path = self.get_release_path(rootpath, sp, release_name, version, revision, filename)
            print(sp, filename , trunk_path , release_path)

            if not os.path.isfile(self.get_abs_path(trunk_path)):
                raise ValueError(f"{trunk_path} doesn't exist")
            if os.path.isfile(self.get_abs_path(release_path)):
                raise ValueError(f"{release_path} already exists")

            swp = self.is_path_switched(trunk_path)
            
            if (idx == 0) ^ swp:
                filepaths.append((trunk_path, release_path))
            else:
                if idx == 0:
                    raise ValueError(f"release: problem on file {trunk_path} : the main file is switched")
                else:
                    raise ValueError(f"release: problem on file {trunk_path} : sub file not switched")


        for tp, rel_p in filepaths:
            t_url = self.get_url(tp)
            self.local_repo.copy(t_url, rel_p, make_parents=True)

        if commit_msg is None:
            commit_msg = f"Release {release_name}:{version}.{revision}"

        self.local_repo.commit(commit_msg)



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