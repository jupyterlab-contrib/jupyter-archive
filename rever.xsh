from rever.activities.command import command

command('run_tests', 'pytest jupyter_archive/', '')
command('publish_npm', 'yarn publish --access=public --new-version $VERSION', '')

$PROJECT = 'jupyter-archive'

$ACTIVITIES = ['version_bump', 'tag', 'push_tag', 'pypi', 'publish_npm', 'ghrelease', 'bump_to_dev', 'push_tag']

$VERSION_BUMP_PATTERNS = [('jupyter_archive/_version.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
                          ('package.json', '"version"\s*:.*,', '"version": "$VERSION",')]

$PUSH_TAG_REMOTE = 'git@github.com:hadim/jupyter-archive.git'
$GITHUB_ORG = 'hadim'
$GITHUB_REPO = 'jupyter-archive'

from rever.activity import activity
from rever.tools import eval_version, replace_in_file
from rever import vcsutils


@activity
def bump_to_dev():
    def increment_version(version):
        """Increment a version by 0.0.1"""
        version = version.split('.')
        version[2] = str(int(version[2]) + 1)
        return '.'.join(version)

    # Increment to a new version and add '-dev' flag.
    new_version = increment_version($VERSION)
    new_version += "-dev"

    for f, p, n in $VERSION_BUMP_PATTERNS:
        n = n.replace("$VERSION", new_version)
        n = eval_version(n)
        replace_in_file(p, n, f)
    vcsutils.commit('Bump to dev')
