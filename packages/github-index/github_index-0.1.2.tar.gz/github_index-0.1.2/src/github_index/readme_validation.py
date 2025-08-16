import glob
import json
import os
from collections import deque
from typing import Any, Callable, Type

import marko
import marko.inline
import tqdm
from marko.element import Element


def extract_elements(tree: list[Element], element_type: Type[Element]) -> list[Element]:
    elements = []
    queue: deque[marko.block.BlockElement | str] = deque(tree)

    while len(queue) != 0:
        block = queue.popleft()

        if isinstance(block, element_type):
            elements.append(block)

        if not (isinstance(block, marko.block.BlockElement) or isinstance(block, marko.inline.Element)):
            continue

        queue.extend(block.children)

    return elements


def clean_document_tree(document: marko.block.Document) -> list[Element]:
    document_tree = document.children.copy()

    for i in range(len(document_tree)-1, -1, -1):
        if isinstance(document_tree[i],  marko.block.BlankLine):
            del document_tree[i]

    return document_tree


def separate_sections(document_tree: list[Element]) -> dict[str, list[Element]]:
    heading_indexes = []

    for i in range(len(document_tree)):
        if isinstance(document_tree[i], marko.block.Heading):
            heading_indexes.append(i)

    sections = {}

    for i in range(len(heading_indexes)):
        start = heading_indexes[i]

        if i == len(heading_indexes) - 1:
            end = len(document_tree)
        else:
            end = heading_indexes[i+1]

        children = document_tree[start].children[0]
        while not isinstance(children, str):
            children = children.children
            if isinstance(children, list):
                children = children[0]
        title = children

        sections[title] = document_tree[start:end]

    return sections


def readme_validation(output_dir: str,
                      repository_data_dir: str,
                      abstract_validator: Callable[[list[Element], list[str], dict[str, Any]], None],
                      validators: dict[str | tuple[str], None | Callable[[list[Element], list[str], dict[str, Any]], None]]) -> None:
    os.makedirs(output_dir, exist_ok=True)

    repository_paths = glob.glob(os.path.join(repository_data_dir, "*.json"))
    valids = 0

    print("Validating READMEs")
    for repository_path in tqdm.tqdm(repository_paths):
        with open(repository_path, "r") as file:
            repo_data = json.load(file)

        repository_name = repo_data["name"]
        readme = repo_data["readme"]
        errors: list[str] = []
        information: dict[str, Any] = {}

        if len(readme) == 0:
            errors.append("Empty readme")
        else:

            document = marko.parse(readme)
            document_tree = clean_document_tree(document)
            sections = separate_sections(document_tree)

            section_names = list(sections.keys())

            abstract_validator(
                sections[section_names[0]], errors, information)

            for name in validators:
                variant_name = name
                if isinstance(name, tuple):
                    for variant_name in name:
                        if variant_name in sections:
                            break

                if variant_name in sections:
                    if sections[variant_name][0].level != 2:
                        errors.append(
                            f"{variant_name} section name is not level 2 (two ##)")

                    validator = validators[name]
                    if validator is not None:
                        validator(sections[variant_name],
                                  errors, information)
                else:
                    if isinstance(name, tuple):
                        name = " or ".join(name)

                    errors.append(f"No section {name}")

        information["valid"] = len(errors) == 0
        information["errors"] = errors

        if information["valid"]:
            valids += 1
            print(repository_name)

        information_path = os.path.join(output_dir, repository_name+".json")
        with open(information_path, "w") as file:
            json.dump(information, file)

    print(f"{valids} valid READMEs")
