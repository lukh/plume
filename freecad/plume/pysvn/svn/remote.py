import svn.constants
import svn.common


class RemoteClient(svn.common.CommonClient):

    def __init__(self, url, *args, **kwargs):
        super(RemoteClient, self).__init__(
            url,
            svn.constants.LT_URL,
            *args, **kwargs)

    def checkout(self, path, revision=None):
        cmd = []
        if revision is not None:
            cmd += ['-r', str(revision)]

        cmd += [self.url, path]

        self.run_command('checkout', cmd)

    def remove(self, rel_path, message, do_force=False):
        args = [
            '--message', message,
        ]

        if do_force is True:
            args.append('--force')

        url = '{}/{}'.format(self.url, rel_path)

        args += [
            url
        ]

        self.run_command(
            'rm',
            args)

    def copy(self, rel_src, rel_dest, msg, make_parents=False):
        """
            URL to URL copy (tag or branch)
        """
        src = '{}/{}'.format(self.url, rel_src)
        dest = '{}/{}'.format(self.url, rel_dest)

        args = ["-m", f'"{msg}"']

        if make_parents:
            args.append("--parents")

        args += [src, dest]

        self.run_command(
            'copy',
            args)


    def lock(self, rel_path, msg=None, do_force=False):
        path = '{}/{}'.format(self.url, rel_path)

        args = []
        if msg:
            args += ["-m", f'"{msg}"']

        if do_force:
            args += "--force"

        args.append(path)

        self.run_command(
            'lock',
            args
        )

    def unlock(self, rel_path, do_force=False):
        path = '{}/{}'.format(self.url, rel_path)

        args = []

        if do_force:
            args += "--force"

        args.append(path)

        self.run_command(
            'unlock',
            args
        )


    def __repr__(self):
        return '<SVN(REMOTE) %s>' % self.url
