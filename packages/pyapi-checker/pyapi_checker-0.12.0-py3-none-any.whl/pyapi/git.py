"""
Copyright 2025 Palantir Technologies, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pathlib import Path

from .utils import run


def get_git_version() -> str:
    git_version = run(
        [
            "git",
            "describe",
            "--tags",
            "--always",
            "--first-parent",
            "--abbrev=7",
        ]
    ).strip()
    git_status = run(["git", "status", "--porcelain"]).strip()
    return git_version + (".dirty" if git_status else "")


def get_previous_git_tag_from_HEAD() -> str:
    return run(["git", "describe", "--tags", "--abbrev=0", "HEAD"]).strip()


def get_repo_root() -> Path:
    return Path(run(["git", "rev-parse", "--show-toplevel"]).strip())
