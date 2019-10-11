from rever.activities.command import command

command('run_tests', 'pytest jupyter_archive/', '')
command('publish_npm', 'yarn publish --access=public --new-version $VERSION', '')

$PROJECT = 'jupyter-archive'

$ACTIVITIES = ['run_tests', 'version_bump', 'tag', 'push_tag', 'pypi', 'publish_npm', 'ghrelease']

$VERSION_BUMP_PATTERNS = [('jupyter_archive/_version.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
                          ('package.json', '"version"\s*:.*,', '"version": "$VERSION",')]

$PUSH_TAG_REMOTE = 'git@github.com:hadim/jupyter-archive.git'
$GITHUB_ORG = 'hadim'
$GITHUB_REPO = 'jupyter-archive'

# git commit -am "Bump to dev"