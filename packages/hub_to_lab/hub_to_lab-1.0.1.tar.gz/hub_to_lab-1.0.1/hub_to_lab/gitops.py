def push_to_gitlab(repo, remote_url, progress):
    task = progress.add_task("[cyan]Push to GitLab...", total=None)

    if "origin" in repo.remotes:
        repo.delete_remote("origin")
    origin = repo.create_remote("origin", remote_url)
    origin.push(all=True)
    origin.push(tags=True)

    progress.update(task, completed=1)
    progress.remove_task(task)
