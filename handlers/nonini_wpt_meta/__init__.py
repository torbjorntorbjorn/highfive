from eventhandler import EventHandler

NON_INI_MSG = 'This pull request adds {0} without the .ini \
file extension to {1}. Please consider removing {2}!'


class NonINIWPTMetaFileHandler(EventHandler):
    DIRS_TO_CHECK = (
        'tests/wpt/metadata',
        'tests/wpt/mozilla/meta',
    )

    FALSE_POSITIVE_SUBSTRINGS = (
        '.ini',
        'MANIFEST.json',
        'mozilla-sync',
    )

    def _wpt_ini_dirs(self, line):
        if line.startswith('diff --git') and '.' in line \
            and not any(fp in line for fp in self.FALSE_POSITIVE_SUBSTRINGS):
            return set(directory for directory in self.DIRS_TO_CHECK if directory in line)
        else:
            return set()

    def on_pr_opened(self, api, payload):
        diff = api.get_diff()
        test_dirs_with_offending_files = set()

        for line in diff.split('\n'):
            test_dirs_with_offending_files |= self._wpt_ini_dirs(line)

        if test_dirs_with_offending_files:
            if len(test_dirs_with_offending_files) == 1:
                files = "a file"
                test_dirs_list = test_dirs_with_offending_files.pop()
                remove = "it"
            else:
                files = "files"
                test_dirs_list = '{} and {}'.format(*test_dirs_with_offending_files)
                remove = "them"

            self.warn(NON_INI_MSG.format(files, test_dirs_list, remove))


handler_interface = NonINIWPTMetaFileHandler
