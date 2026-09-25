#!/usr/bin/env python3
"""
Pushes a local folder to a GitHub repo using a personal access token.

Usage (run in Termux or any terminal with git + python installed):
    python push_to_github.py

Requirements:
    - git installed (Termux: pkg install git)
    - A file with ONLY your token inside, e.g. /storage/emulated/0/Download/github_token.txt
"""
# git config --global --add safe.directory /storage/emulated/0/Download/genzchat-push-server/

# git branch -m master main                                      git push -u origin main --force
import subprocess
import os
import sys

# ---- EDIT THESE THREE LINES ----
LOCAL_FOLDER = "/storage/emulated/0/Download/genzchat-push-server/"
TOKEN_FILE = "/storage/emulated/0/Download/github_token.txt"
REPO_URL = "https://github.com/Mrlivetv/genzchat-push-server.git"
BRANCH = "main"
# ---------------------------------

GITHUB_USER = "Mrlivetv"


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)


def main():
    if not os.path.isdir(LOCAL_FOLDER):
        print(f"Folder not found: {LOCAL_FOLDER}")
        sys.exit(1)

    if not os.path.isfile(TOKEN_FILE):
        print(f"Token file not found: {TOKEN_FILE}")
        sys.exit(1)

    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()

    if not token:
        print("Token file is empty.")
        sys.exit(1)

    # Build an authenticated remote URL (token is used only in-memory, never printed)
    auth_url = REPO_URL.replace(
        "https://", f"https://{GITHUB_USER}:{token}@"
    )

    git_dir = os.path.join(LOCAL_FOLDER, ".git")
    if not os.path.isdir(git_dir):
        run(["git", "init"], cwd=LOCAL_FOLDER)
        run(["git", "checkout", "-b", BRANCH], cwd=LOCAL_FOLDER)

    run(["git", "config", "user.email", "mostak@genzchat.local"], cwd=LOCAL_FOLDER)
    run(["git", "config", "user.name", "Mostak"], cwd=LOCAL_FOLDER)

    # Set or update the remote (with token embedded only for this push)
    remotes = subprocess.run(
        ["git", "remote"], cwd=LOCAL_FOLDER, capture_output=True, text=True
    ).stdout.split()
    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", auth_url], cwd=LOCAL_FOLDER)
    else:
        run(["git", "remote", "add", "origin", auth_url], cwd=LOCAL_FOLDER)

    run(["git", "add", "-A"], cwd=LOCAL_FOLDER)

    # Commit only if there are changes
    diff_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=LOCAL_FOLDER
    )
    if diff_check.returncode != 0:
        run(["git", "commit", "-m", "Update GenZChat"], cwd=LOCAL_FOLDER)
    else:
        print("Nothing to commit.")

    run(["git", "push", "-u", "origin", BRANCH, "--force"], cwd=LOCAL_FOLDER)

    # Reset the remote URL back to a clean (token-free) one, so it's not saved on disk
    run(["git", "remote", "set-url", "origin", REPO_URL], cwd=LOCAL_FOLDER)

    print("\nDone. Pushed to:", REPO_URL)


if __name__ == "__main__":
    main()
