#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys


def run_command(command_args, cwd_path=None) -> int:
    process = subprocess.Popen(
        command_args,
        cwd=cwd_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(line)
    process.wait()
    return process.returncode


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def path_exists_and_not_empty(path: str) -> bool:
    return os.path.exists(path) and any(True for _ in os.scandir(path))


def ng_sync(master_repo_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 同步仓库: {master_repo_path}")
    rc = run_command(["krepo-ng", "sync"], cwd_path=master_repo_path)
    if rc != 0:
        print("krepo-ng sync 失败", file=sys.stderr)
        sys.exit(rc)


def ng_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["krepo-ng", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_sync(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 同步仓库: {master_repo_path}")
    rc = run_command(["git", "pull"], cwd_path=master_repo_path)
    if rc != 0:
        print("git pull 失败", file=sys.stderr)
        sys.exit(rc)


def git_branch_exists(master_repo_path: str, branch: str) -> tuple[bool, bool]:
    has_remote = run_command(["git", "ls-remote", "--exit-code", "--heads", "origin", branch], cwd_path=master_repo_path) == 0
    has_local = run_command(["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd_path=master_repo_path) == 0
    return has_local, has_remote


def git_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["git", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)
    return
    rc = run_command(["git", "worktree", "add", "-b", branch, target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_list(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] worktree list @ {master_repo_path}")
    rc = run_command(["git", "worktree", "list"], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def command_add(path_value: str, branch_value: str) -> None:
    home_dir = os.path.expanduser("~")
    # wpsmain via krepo-ng
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)

    target_root = os.path.join(home_dir, path_value)
    target_wpsmain_path = os.path.join(target_root, "wpsmain")
    if not path_exists_and_not_empty(target_wpsmain_path):
        ensure_directory(target_wpsmain_path)
        ng_sync(master_wpsmain_path)
        ng_worktree_add(master_wpsmain_path, target_wpsmain_path, branch_value)

    # wpsweb via git
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    target_wpsweb_path = os.path.join(target_root, "wpsweb")
    if not path_exists_and_not_empty(target_wpsweb_path):
        ensure_directory(target_wpsweb_path)
        git_sync(master_wpsweb_path)
        git_worktree_add(master_wpsweb_path, target_wpsweb_path, branch_value)

    print("完成。")


def command_list() -> None:
    home_dir = os.path.expanduser("~")
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")

    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    print("=== wpsmain worktrees ===")
    git_worktree_list(master_wpsmain_path)
    print("\n=== wpsweb worktrees ===")
    git_worktree_list(master_wpsweb_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="多分支 worktree 管理工具（子命令版）")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # add 子命令：添加 wpsmain 与 wpsweb 的 worktree
    add_parser = subparsers.add_parser("add", help="创建 worktree。用法: add <path> <branch>")
    add_parser.add_argument("path", help="目标路径名（对应 ~/<path>/...）")
    add_parser.add_argument("branch", help="要创建/切换的分支名")

    # list 子命令：列出 wpsmain 与 wpsweb 的 worktree
    subparsers.add_parser("list", help="列出 master 下 wpsmain 和 wpsweb 的 worktree")

    args = parser.parse_args()

    if args.command == "add":
        command_add(args.path, args.branch)
        return
    if args.command == "list":
        command_list()
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()

