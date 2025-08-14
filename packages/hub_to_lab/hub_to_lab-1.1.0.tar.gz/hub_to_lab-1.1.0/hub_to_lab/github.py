import tempfile
from git import Repo


def clone_github_repo(github_url, progress):
    tmpdir = tempfile.mkdtemp()
    task = progress.add_task("[green]Clone GitHub...", total=None)

    repo = Repo.clone_from(github_url, tmpdir)
    progress.update(task, completed=1)
    progress.remove_task(task)
    return repo