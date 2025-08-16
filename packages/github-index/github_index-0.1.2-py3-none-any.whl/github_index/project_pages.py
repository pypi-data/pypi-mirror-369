import glob
import json
import os
import urllib
from typing import Any, Callable

import tqdm

from github_index import Badge
from github_index.badge import generate_badges


def get_repository_paths(data_path: str) -> list[str]:
    return glob.glob(os.path.join(
        data_path, "auto_generated", "repository", "*.json"))


def get_repository_data(data_path: str, repository_path: str) -> dict[str, dict[str, Any]]:
    with open(repository_path, "r") as file:
        repo_data = json.load(file)

    paths = {}
    repository_name = repo_data["name"]

    for name in ["metadata", "readme"]:
        paths[name] = os.path.join(
            data_path, "auto_generated", f"{name}_information", repository_name+".json")

    data = {"repository": repo_data}
    for name in paths:
        with open(paths[name], "r") as file:
            data[name] = json.load(file)

    return data


def is_repository_valid(data: dict[str, dict[str, Any]]) -> bool:
    return data["metadata"]["valid"] and data["readme"]["valid"]


def generate_pages(data_path: str,
                   page_src_path: str,
                   group_name: str,
                   filter_function: Callable[[dict[str, dict[str, Any]]], bool],
                   badge_generator: Callable[[dict[str, dict[str, Any]]], list[Badge]] | None = None) -> str:
    toc_tree = f".. toctree::\n\t:maxdepth: 1\n\t:caption: {group_name}\n\t:hidden:\n\n"

    generated_dir = os.path.join(page_src_path, "repositories", group_name)
    os.makedirs(generated_dir, exist_ok=True)

    repository_paths = get_repository_paths(data_path)
    for repository_path in tqdm.tqdm(repository_paths):
        data = get_repository_data(data_path, repository_path)

        repository_name = data["repository"]["name"]

        if is_repository_valid(data) and filter_function(data):
            page = data["repository"]["readme"]

            if badge_generator is not None:
                page = generate_badges(page, data, badge_generator)

            page_path = os.path.join(
                generated_dir, f"{repository_name}.md")
            with open(page_path, "w", encoding="utf-8") as file:
                file.write(page)

            toc_tree += "\t"+page_path+"\n"

    return toc_tree


def generate_problems_page(data_path: str, page_src_path: str) -> None:

    page = "# Problems\n\n"

    repository_paths = get_repository_paths(data_path)
    for repository_path in tqdm.tqdm(repository_paths):
        data = get_repository_data(data_path, repository_path)

        if not is_repository_valid(data):
            repository_name = data["repository"]["name"]
            page += f"## {repository_name}\n\n"

            for name in ["metadata", "readme"]:
                if len(data[name]["errors"]) > 0:
                    page += f"### {name}\n"
                    errors = ["- "+error for error in data[name]["errors"]]
                    page += "\n".join(errors)
                    page += "\n\n"

    page_dir = os.path.join(page_src_path, "hidden")
    os.makedirs(page_dir, exist_ok=True)
    page_path = os.path.join(page_dir, "Problems.md")

    with open(page_path, "w+", encoding="utf-8") as file:
        file.write(page)


def generate_readme(preamble: str, page_src_path: str, org_name: str) -> str:
    page = preamble

    paths = glob.glob(os.path.join(
        page_src_path, "repositories", "*", "*.md"), recursive=True)
    groups = {}
    for path in paths:
        group = path.split("\\")[-2]

        if group not in groups:
            groups[group] = []

        path_in_readme = os.path.relpath(path, os.path.commonprefix(
            ["page_src", path])).replace(".md", ".html").replace("\\", "/")
        repo_name = os.path.basename(path).removesuffix(".md")

        path_in_readme = urllib.parse.quote(path_in_readme)

        groups[group].append(
            f"[![](https://gh-card.dev/repos/{org_name}/{repo_name}.svg)]({path_in_readme})")

    for group in groups:
        page += f"\n\n## {group}\n"
        page += " ".join(groups[group])

    readme_path = os.path.join(page_src_path, "README.md")
    with open(readme_path, "w+", encoding="utf-8") as file:
        file.write(page)

    return readme_path
