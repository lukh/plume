import os
import pprint
import svn.remote
import svn.local


class PlumeSvn(object):
    def __init__(self, workcopy, repo_url):
        workcopy = os.path.abspath(workcopy)
        repo_url = repo_url.rstrip("/")

        self.remote_repo = svn.remote.RemoteClient(repo_url)
        self.local_repo = svn.local.LocalClient(workcopy)

        self.working_copy = workcopy
        self.repo_url = repo_url

    def update(self, rel_filepaths=[], revision=None):
        self.local_repo.update(rel_filepaths=rel_filepaths, revision=revision)


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

    def get_abs_path(self, rel_path):
        return os.path.join(self.working_copy, rel_path)

    def get_rel_path(self, abs_path):
        """
        Returns the relative (to self.working_copy) path from an absolute path 
        """
        rp = os.path.relpath(abs_path, start=self.working_copy)

        if not os.path.exists(os.path.join(self.working_copy, rp)):
            raise ValueError(f"can't get relative path for {abs_path}")

        return rp
        
    def get_url(self, abs_path):
        """
        Returns the URL from an absolute path 
        """
        rp = self.get_rel_path(abs_path)

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

    def get_trunk_path(self, rootpath, subpath, filename):
        """
        Returns a trunk path (from self.working_copy) from rootpath, subpath, filename
        """
        return f"{self.working_copy}{os.sep}{rootpath.strip(os.sep)}{os.sep}trunk{os.sep}{subpath.strip(os.sep)}{os.sep}{filename.strip(os.sep)}"

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
        return f"{self.working_copy}{os.sep}{rootpath.strip(os.sep)}{os.sep}releases{os.sep}{subpath.strip(os.sep)}{os.sep}{release_name}{os.sep}{version}.{revision}{os.sep}{filename.strip(os.sep)}"



    def is_path_switched(self, rel_path):
        if not os.path.exists(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(self.working_copy, rel_path)):
            raise ValueError(f"{rel_path} is not a file")

        l = list(self.local_repo.status(rel_path))
        if len(l) != 1:
            raise ValueError("Can't execute status")
        status = l[0]

        return status.switched

    def switch(self, rel_trunk_path, release_name, version, revision):
        if not self.is_trunk_path(rel_trunk_path):
            raise ValueError(f"{rel_path} is not in a trunk")

        rootpath, subpath, filename = self.split_trunk_path(rel_path)

        dest_path = self.get_release_path(rootpath, subpath, release_name, version, revision, filename)

        if not self.is_release_path(dest_path):
            raise ValueError(f"{dest_path} is not a release")

    def unswitch(self, rel_path):
        pass



    def initialize_repo():
        """
        initialize a repository for use with plume
        """
        pass


    def create_project(rel_proj_path, commit=True):
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

        self.local_repo.add(f"{rel_proj_path}")
        if commit:
            self.local_repo.commit(f"adding {rel_proj_path} structure")


    def release(root_path, tag_name, sub_paths=[]):
        """
        Release files or folder (project)
        :root_path : path to root folder (containing trunk, tags, releases and branches)
        :tag_name : the name of the release
        :subpaths : a list of path (from the current trunk) to be released (file or folder/project)
          or empty list (default) to release the folder

        Solution to release partial...
            cd repo_wc/tags

            mkdir release_1.0
            cd release_1.0

            svn copy ^/trunk/myfile myfile

            mkdir parts

            svn copy ^/trunk/parts/file2 parts/file2
            svn copy ^/trunk/parts/file3 parts/file3

            svn commit -m "Create partial tag release_1.0"
        """
    #     self.working_copy_trunk_path = os.path.join(root_path, "trunk")
    #     # check existence of file
    #     if not os.path.exists(os.path.join(self.working_copy, self.working_copy_trunk_path)):
    #         raise ValueError(f"{root_path=} doesn't exist")

    #     trunk_files = [os.path.join(self.working_copy_trunk_path, sp) for sp in sub_paths]
    #     for tf in trunk_files:
    #         # check existence of file
    #         if not os.path.exists(os.path.join(self.working_copy, tf)):
    #             raise ValueError(f"{tf} doesn't exist")

    #         # check file is up-to-date with the server
    #         status = [s for s in self.local_repo.status(tf)]
    #         if len(status) > 0:
    #             raise Exception(f"{tf} is not up-to-date on the server: {status[0].type_raw_name}")

        

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