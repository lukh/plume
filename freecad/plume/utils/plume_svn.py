import os
import pprint
import svn.remote
import svn.local

WC = './temp_wc/'
REPO = 'https://svn.naboo/Sandbox'
PROJECTS_ROOT = "projects"
LIBRARIES_ROOT = "libraries"


info = self.local_repo.info()
# pprint.pprint(info)

self.local_repo.update()

class PlumeSvn(object):
    def __init__(self, workcopy, repo_url):
        self.remote_repo = svn.remote.RemoteClient(repo_url)
        self.local_repo = svn.local.LocalClient(workcopy)

    def is_in_repository(self, abs_path):
        """
        check the file is in the repository
        """
        pass

    def get_rel_path(self, abs_path):
        """
        Returns the relative (wc) path from an absolute path 
        """
        pass

    def get_url(self, abs_path):
        """
        Returns the URL from an absolute path 
        """
        pass

    def initialize_repo():
        """
        initialize a repository for use with plume
        """
        if os.path.exists(os.path.join(WC, PROJECTS_ROOT)):
            raise Exception(f"{PROJECTS_ROOT=} aldready exsist in {WC}")
        if os.path.exists(os.path.join(WC, LIBRARIES_ROOT)):
            raise Exception(f"{LIBRARIES_ROOT=} aldready exsist in {WC}")

        os.makedirs(os.path.join(WC, PROJECTS_ROOT))
        os.makedirs(os.path.join(WC, LIBRARIES_ROOT))
        os.makedirs(os.path.join(WC, LIBRARIES_ROOT, "branches"))
        os.makedirs(os.path.join(WC, LIBRARIES_ROOT, "tags"))
        os.makedirs(os.path.join(WC, LIBRARIES_ROOT, "trunk"))

        self.local_repo.add(PROJECTS_ROOT)
        self.local_repo.add(LIBRARIES_ROOT)

        self.local_repo.commit(f"adding Plume repository structure")


    def create_project(rel_proj_path, commit=True):
        """
        Create a project in PROJECTS_ROOT/rel_proj_path.
        Add trunk, tags and branches subfolders into the above path
        Commit the changes if commit arg
        """
        if os.path.exists(os.path.join(WC, PROJECTS_ROOT, rel_proj_path)):
            raise Exception(f"{rel_proj_path=} aldready exsist in {WC}/{PROJECTS_ROOT}")

        os.makedirs(os.path.join(WC, PROJECTS_ROOT, rel_proj_path))
        os.makedirs(os.path.join(WC, PROJECTS_ROOT, rel_proj_path, "trunk"))
        os.makedirs(os.path.join(WC, PROJECTS_ROOT, rel_proj_path, "tags"))
        os.makedirs(os.path.join(WC, PROJECTS_ROOT, rel_proj_path, "branches"))

        self.local_repo.add(f"{PROJECTS_ROOT}/{rel_proj_path}")
        if commit:
            self.local_repo.commit(f"adding {rel_proj_path} structure")


    def tag_library_file(rel_path, tag_name, commit_msg=None):
        """
        Create a tag for a file in a subfolder (or in) 
        LIBRARIES_ROOT/trunk

        The tag will be in 
        LIBRARIES_TOOT/tags/{rel_path without ext}/{tag_name}/{filename}
        """
        wc_trunk_path = os.path.join(LIBRARIES_ROOT, "trunk", rel_path)

        # check existence of file
        if not os.path.exists(os.path.join(WC, wc_trunk_path)):
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isfile(os.path.join(WC, wc_trunk_path)):
            raise ValueError(f"{rel_path} is not a file")

        # check file is up-to-date with the server
        status = [s for s in self.local_repo.status(wc_trunk_path)]
        if len(status) > 0:
            raise Exception(f"{rel_path} is not up-to-date on the server: {status[0].type_raw_name}")

        src_url = wc_trunk_path
        # if not os.path.isfile(src_url):
        #     raise Exception(f"{src_url} must be a file")

        filename = os.path.basename(rel_path)
        basename = os.path.splitext(filename)[0]
        dirname = os.path.dirname(rel_path)
        
        tag_url = os.path.join(LIBRARIES_ROOT, "tags", dirname, basename, tag_name, filename)

        if os.path.exists(os.path.join(WC, tag_url)):
            raise Exception(f"{tag_url} already exists")

        if not commit_msg:
            commit_msg = f"Tagging project {rel_path}/{tag_name}"

        self.remote_repo.copy(src_url, tag_url, commit_msg, make_parents=True)


    def tag_project(rel_path, tag_name, commit_msg=None):
        """
        Create a tag for a folder like 
        PROJECTS_ROOT/rel_path/trunk

        The tag will be in 
        PROJECTS_ROOT/{rel_path}/tags/{tag_name}
        """
        wc_trunk_path = os.path.join(PROJECTS_ROOT, rel_path, "trunk")
        print(wc_trunk_path)

        # check existence of file
        if not os.path.exists(os.path.join(WC, wc_trunk_path)):
            raise ValueError(f"{rel_path} doesn't exist")

        if not os.path.isdir(os.path.join(WC, wc_trunk_path)):
            raise ValueError(f"{rel_path} is not a directory")

        # check file is up-to-date with the server
        status = [s for s in self.local_repo.status(wc_trunk_path)]
        if len(status) > 0:
            raise Exception(f"{rel_path} is not up-to-date on the server: {status[0].type_raw_name}")

        src_url = wc_trunk_path
        tag_url = os.path.join(PROJECTS_ROOT, rel_path, "tags", tag_name)
        print(tag_url)

        if os.path.exists(os.path.join(WC, tag_url)):
            raise Exception(f"{tag_url} already exists")

        if not commit_msg:
            commit_msg = f"Tagging project {rel_path}/{tag_name}"

        self.remote_repo.copy(src_url, tag_url, commit_msg, make_parents=True)



# initialize_repo()

# create_project("MyAweSomeProject")
# tag_project("MyAweSomeProject", "0.2")
# tag_library_file("fasteners/MyFastener.FCStd", "0.2")

# self.remote_repo.lock("projects/MyAweSomeProject/trunk/README.md")
# self.remote_repo.unlock("projects/MyAweSomeProject/trunk/README.md")
# self.local_repo.lock("projects/MyAweSomeProject/trunk/README.md")
# self.local_repo.unlock("projects/MyAweSomeProject/trunk/README.md")