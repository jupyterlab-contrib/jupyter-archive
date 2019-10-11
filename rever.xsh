$PROJECT = 'jupyter-archive'

$ACTIVITIES = ['run_tests', 'version_bump', 'tag', 'push_tag', 'pypi', 'publish_npm', 'ghrelease']

$VERSION_BUMP_PATTERNS = [('jupyter_archive/_version.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
                          ('package.json', '"version"\s*:.*,', '"version": "$VERSION",')]

$PUSH_TAG_REMOTE = 'git@github.com:hadim/jupyter-archive.git'
$GITHUB_ORG = 'hadim'
$GITHUB_REPO = 'jupyter-archive'


from rever.activity import activity

@activity
def run_tests():
    echo "Run tests"
    pytest jupyter_archive/

@activity
def publish_npm():
    echo "Publish package to NPM"
    yarn publish --access=public --new-version $VERSION
