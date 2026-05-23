import os
import collections

import xml.etree

import svn.constants
import svn.common

_STATUS_ENTRY = \
    collections.namedtuple(
        '_STATUS_ENTRY', [
            'name',
            'type_raw_name',
            'type',
            'revision',
            'switched'
        ])

_INFO_ENTRY = \
    collections.namedtuple(
        '_INFO_ENTRY', [
            'name',
            'url',
            'revision',
        ])

class LocalClient(svn.common.CommonClient):
    def __init__(self, path_, *args, **kwargs):
        if os.path.exists(path_) is False:
            raise EnvironmentError("Path does not exist: %s" % path_)

        super(LocalClient, self).__init__(
            path_,
            svn.constants.LT_PATH,
            *args, **kwargs)

    def __repr__(self):
        return '<SVN(LOCAL) %s>' % self.path

    def add(self, rel_path, do_include_parents=False):
        args = [rel_path]

        if do_include_parents is True:
            args.append('--parents')

        self.run_command(
            'add',
            args,
            wd=self.path)

    def commit(self, message, rel_filepaths=[]):
        args = ['-m', message] + rel_filepaths

        output = self.run_command(
            'commit',
            args,
            wd=self.path)

    def copy(self, src, dst, make_parents=False):
        args = [src, dst]
        if make_parents:
            args.append('--parents')

        output = self.run_command(
            'copy',
            args,
            wd=self.path)

    def update(self, rel_filepaths=[], revision=None):
        cmd = []
        if revision is not None:
            cmd += ['-r', str(revision)]
        cmd += rel_filepaths
        self.run_command(
            'update',
            cmd,
            wd=self.path)

    def cleanup(self):
        self.run_command(
            'cleanup',
            [],
            wd=self.path)

    def status(self, rel_path=None):
        path = self.path
        if rel_path is not None:
            path += '/' + rel_path

        raw = self.run_command(
            'status',
            ['--xml', path],
            do_combine=True)

        root = xml.etree.ElementTree.fromstring(raw)

        list_ = root.findall('target/entry')
        for entry in list_:
            entry_attr = entry.attrib
            name = entry_attr['path']

            wcstatus = entry.find('wc-status')
            wcstatus_attr = wcstatus.attrib

            change_type_raw = wcstatus_attr['item']
            change_type = svn.constants.STATUS_TYPE_LOOKUP[change_type_raw]

            # This will be absent if the file is "unversioned". It'll be "-1"
            # if added but not committed.
            revision = wcstatus_attr.get('revision')

            SWICTHED_LUT = {"true":True, "false":False, None:None}
            switched = SWICTHED_LUT[wcstatus_attr.get('switched')]
            if revision is not None:
                revision = int(revision)

            yield _STATUS_ENTRY(
                name=name,
                type_raw_name=change_type_raw,
                type=change_type,
                revision=revision,
                switched=switched
            )


    def info(self, rel_path=None):
        path = self.path
        if rel_path is not None:
            path += '/' + rel_path

        raw = self.run_command(
            'info',
            ['--xml', path],
            do_combine=True)

        root = xml.etree.ElementTree.fromstring(raw)

        list_ = root.findall('entry')
        for entry in list_:
            entry_attr = entry.attrib
            name = entry_attr['path']
            revision = entry_attr.get('revision')
            if revision is not None:
                revision = int(revision)
            url = entry.find('url').text

            yield _INFO_ENTRY(
                name=name,
                url=url,
                revision=revision
            )

    def remove(self, rel_path, do_keep_local=False, do_force=False):
        args = []

        if do_keep_local is True:
            args.append('--keep-local')

        if do_force is True:
            args.append('--force')

        args += [
            rel_path
        ]

        self.run_command(
            'rm',
            args)

    def lock(self, rel_path, msg=None, do_force=False):
        args = []

        if msg:
            args += ["-m", f'"{msg}"']

        if do_force is True:
            args.append('--force')

        args.append(rel_path)

        self.run_command(
            'lock',
            args,
            wd=self.path)

    def unlock(self, rel_path, do_force=False):
        args = []

        if do_force is True:
            args.append('--force')

        args.append(rel_path)

        self.run_command(
            'unlock',
            args,
            wd=self.path)

    def switch(self, url, rel_path):
        """
        svn switch URL[@PEGREV] [PATH]
        """
        args = [url, rel_path]

        self.run_command(
            'switch',
            args,
            wd=self.path)

