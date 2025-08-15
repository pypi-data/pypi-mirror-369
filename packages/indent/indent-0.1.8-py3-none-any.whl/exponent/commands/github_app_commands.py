import asyncio
import json
import subprocess
import sys
import webbrowser
from pathlib import Path
from uuid import uuid4

import click
from git import GitCommandError, Repo

from exponent.commands.common import (
    redirect_to_login,
    verify_gh_app_installation,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.core.config import Settings
from exponent.core.remote_execution.git import get_git_info


@exponent_cli_group()
def github_app_cli() -> None:
    """Run AI-powered chat sessions."""
    pass


@github_app_cli.command()
@use_settings
def install_github_app(
    settings: Settings,
) -> None:
    """Start or reconnect to an Exponent session."""
    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    api_key = settings.api_key
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    git_info = asyncio.run(get_git_info("."))
    if not git_info:
        raise RuntimeError("Not running inside of valid git repository")

    install_url = "https://github.com/apps/indent/installations/new"
    webbrowser.open(install_url)

    click.confirm(
        "Press enter once you've installed the github app.",
        default=True,
        abort=True,
        prompt_suffix="",
    )

    click.secho("Verifying installation...", fg="yellow")
    verified = loop.run_until_complete(
        verify_gh_app_installation(api_key, base_api_url, base_ws_url, git_info)
    )

    if verified:
        click.secho("Verified!", fg="green")
    else:
        click.secho("No verification found :(", fg="red")
        sys.exit(1)

    click.secho("Creating workflow file...", fg="yellow")
    _create_workflow_yaml()


WORKFLOW_YAML = """
name: Indent Action

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]

jobs:
  indent:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@indent')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@indent')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@indent')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@indent') || contains(github.event.issue.title, '@indent')))
    runs-on: ubuntu-latest

    steps:
      - name: Generate token for Indent app
        id: generate_token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.INDENT_APP_ID }}
          private-key: ${{ secrets.INDENT_APP_PRIVATE_KEY }}

      - name: Respond to mention
        uses: actions/github-script@v7
        with:
          github-token: ${{ steps.generate_token.outputs.token }}
          script: |
            const issue_number = context.payload.issue?.number || 
                               context.payload.pull_request?.number ||
                               context.payload.review?.pull_request?.number;

            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issue_number,
              body: 'Hi it\'s me, Indent'
            });
""".lstrip()


def _create_workflow_yaml() -> None:
    git_branch = f"indent-workflow-{uuid4()}"
    workflow_file = "indent-review.yml"

    # 1. Locate the repository (searches upward until it finds .git).
    repo = Repo(Path.cwd(), search_parent_directories=True)
    if repo.bare or not repo.working_tree_dir:
        sys.exit("Error: cannot operate inside a bare repository.")

    original_branch = repo.active_branch.name if not repo.head.is_detached else None

    # 2. Create or reuse the branch, then check it out.
    try:
        branch_ref = repo.create_head(git_branch)
    except GitCommandError:
        branch_ref = repo.heads[git_branch]
    branch_ref.checkout()

    # 3. Ensure workflow directory exists.
    wf_dir = Path(repo.working_tree_dir) / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)

    yml = wf_dir / workflow_file
    if not yml.exists():
        yml.write_text(WORKFLOW_YAML)
        # 5. Stage & commit.
        repo.index.add([str(yml)])
        repo.index.commit("Add Indent workflow template")
        print(
            f"Created {yml.relative_to(repo.working_tree_dir)} "
            f"on branch '{git_branch}'."
        )
    else:
        print(
            f"{yml.relative_to(repo.working_tree_dir)} already exists; nothing to do."
        )

    subprocess.run(
        ["git", "push", "-u", "origin", git_branch],
        cwd=repo.working_tree_dir,
        check=True,
        capture_output=False,
        text=True,
    )

    pr_url: str | None = None
    pr_title = f"Add Indent workflow ({workflow_file})"
    pr_body = "This PR introduces an Indent github action workflow"

    def run_gh(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["gh", *cmd],
            cwd=repo.working_tree_dir,
            check=True,
            capture_output=True,
            text=True,
        )

    try:
        # Does a PR already exist for this head branch?
        result = run_gh(["pr", "view", git_branch, "--json", "url"])
        pr_url = json.loads(result.stdout)["url"]
    except subprocess.CalledProcessError:
        # No PR yet → create one
        base = original_branch or repo.remotes.origin.refs[0].name.split("/")[-1]
        run_gh(
            [
                "pr",
                "create",
                "--head",
                git_branch,
                "--base",
                base,
                "--title",
                pr_title,
                "--body",
                pr_body,
            ]
        )
        # Fetch the newly created URL
        result = run_gh(["pr", "view", git_branch, "--json", "url"])
        pr_url = json.loads(result.stdout)["url"]

    if pr_url:
        click.secho(f"PR: {pr_url}", fg="green")
        webbrowser.open(pr_url)
    else:
        click.secho("Failed to create PR!", fg="red")

    if original_branch:
        repo.git.checkout(original_branch)
