import os
import shutil
from functools import partial
from typing import Any, Callable

from marko.element import Element

from github_index.badge import Badge
from github_index.get_repository_data import get_repositoy_data
from github_index.metadata_validation import metadata_validation
from github_index.project_pages import (
    generate_pages, generate_problems_page, generate_readme)
from github_index.readme_validation import readme_validation


def get_data(organization_name: str,
             page_path: str,
             validate_abstract_section: Callable[[list[Element], list[str], dict[str, Any]], None],
             section_validators: dict[str | tuple[str], None | Callable[[list[Element], list[str], dict[str, Any]], None]],
             metadata_validator: Callable[[dict[str, Any], list[str], dict[str, Any]], None]) -> None:
    autogenerate_path = os.path.join(page_path, "data", "auto_generated")
    repository_path = os.path.join(autogenerate_path, "repository")
    readme_path = os.path.join(autogenerate_path, "readme_information")
    metadata_path = os.path.join(autogenerate_path, "metadata_information")

    shutil.rmtree(autogenerate_path, ignore_errors=True)
    os.makedirs(repository_path, exist_ok=True)
    os.makedirs(readme_path, exist_ok=True)
    os.makedirs(metadata_path, exist_ok=True)

    get_repositoy_data(organization_name,
                       repository_path)

    readme_validation(readme_path, repository_path,
                      validate_abstract_section, section_validators)

    metadata_validation(metadata_path,
                        repository_path, metadata_validator)


def generate(organization_name: str,
             page_path: str,
             readme_preamble: str,
             group_functions: dict[str, Callable[[dict[str, dict[str, Any]]], bool]],
             badge_generator: Callable[[dict[str, dict[str, Any]]], list[Badge]] | None = None) -> None:
    data_path = os.path.join(page_path, "data")
    page_src_path = os.path.join(page_path, "page_src")
    index_path = os.path.join(page_path, "index.rst")

    try:
        shutil.rmtree(os.path.join(page_path, "page_src", "repositories"))
    except FileNotFoundError:
        pass

    toc_trees = []

    for group_name in group_functions:
        filter_function = group_functions[group_name]
        toc_tree = generate_pages(
            data_path, page_src_path, group_name, filter_function, badge_generator)
        toc_trees.append(toc_tree)

    toc_tree = "\n".join(toc_trees)
    toc_tree = f".. include:: readme_link.rst\n\n{toc_tree}"
    toc_tree = toc_tree.replace("\\", "/")

    with open(index_path, "w+", encoding="utf-8") as file:
        file.write(toc_tree)

    readme_path = generate_readme(
        readme_preamble, page_src_path, organization_name)
    with open("readme_link.rst", "w+", encoding="utf-8") as file:
        file.write(f".. mdinclude:: {readme_path}")

    generate_problems_page(data_path, page_src_path)
