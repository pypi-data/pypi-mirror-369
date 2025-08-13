import logging
from pathlib import Path

from django.conf import settings
from dulwich.repo import Repo


FILE_NAME_REVISION = getattr(settings, 'STATIC_REVISION_VERSION_FILE', '.version')
REVISION_LENGTH = getattr(settings, 'STATIC_REVISION_STRING_LENGTH', 10)
logger = logging.getLogger(__name__)


def locate_django_manage() -> Path:
    """
    Locate project's manage.py file
    """
    folder = Path.cwd()
    # Look for manage.py in current folder or up
    for i in range(5):
        p: Path = folder / 'manage.py'
        if p.exists():
            return folder
        folder = folder.parent
    raise FileNotFoundError('Django manage.py file not found')


def get_source_revision_from_git(folder: Path) -> str:
    dot_git: Path = folder / '.git'
    # '.git' can be a folder or file, the later case is for worktree.
    if not dot_git.exists():
        raise OSError('Not a Git working copy')
    repo = Repo(folder)
    # We truncate the hash string to 7 characters,
    # that is also the way Git represents in short form.
    try:
        return repo.head()[:REVISION_LENGTH].decode()
    except KeyError:
        # Folder has just been "git init", no data yet
        return '-'


def get_source_revision_from_text_file(folder: Path) -> str:
    path = folder / FILE_NAME_REVISION
    try:
        content = path.read_text().strip()
    except IOError:
        logger.error('Failed to read {}'.format(path))
        return 'version-file-missing'
    return content[:REVISION_LENGTH]


def get_source_revision() -> str:
    folder = locate_django_manage()
    if (folder / FILE_NAME_REVISION).exists():
        return get_source_revision_from_text_file(folder)
    return get_source_revision_from_git(folder)
