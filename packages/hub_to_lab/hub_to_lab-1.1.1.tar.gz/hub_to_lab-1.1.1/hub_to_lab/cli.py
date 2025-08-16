import os

from hub_to_lab.check import check_config_variables
from hub_to_lab.config import update_env_variable
from hub_to_lab.github import clone_github_repo
from hub_to_lab.gitlab import get_or_create_gitlab_project
from hub_to_lab.gitops import push_to_gitlab
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
import typer

app = typer.Typer()

@app.command()
def main():

    config = {
        "GITHUB_REPO": "Name of the GitHub repository (ex: torvalds/linux)",
        "GITLAB_REPO": "Name of the new project on Gitlab",
        "GITLAB_URL": "GitLab URL",
        "GITLAB_TOKEN": "GitLab TOKEN (PAT)",
        "GITLAB_USERNAME": "GitLab Username",
        "GITLAB_GROUP": "GitLab Group name (use '-' for personal namespace or leave if precedent group was your personal namespace)",
    }


    github_repo, new_repo_name, gitlab_url, gitlab_token, gitlab_user, gitlab_group = setup_config_variables(config)

    github_clone_url = f"https://github.com/{github_repo}.git"

    print("Create the Gitlab project...")

    project = get_or_create_gitlab_project(
        gitlab_url=gitlab_url,
        token=gitlab_token,
        username=gitlab_user,
        group=gitlab_group,
        name=new_repo_name
    )

    remote_url = project["http_url_to_repo"]

    remote_url = remote_url.replace("https://", f"https://oauth2:{gitlab_token}@")

    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn()
    ) as progress:
        repo = clone_github_repo(github_clone_url, progress)

        push_to_gitlab(repo, remote_url, progress)

    print("✅ Fini.")


def setup_config_variables(config: dict):
    config_variables = []
    for key, prompt in config.items():
        while True:
            variable = typer.prompt(prompt, default=os.getenv(key))
            if check_config_variables(key, variable):
                if key not in ["GITHUB_REPO", "GITLAB_REPO"]:
                    if key == "GITLAB_GROUP" and variable == "-":
                        variable = ''
                    update_env_variable(key, variable)
                config_variables.append(variable)
                break
            else:
                typer.echo(f"Error: Invalid value for {key}. Please try again.")
    return config_variables


if __name__ == "__main__":
    main()
