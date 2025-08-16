import glob
import json
import os
from typing import Any, Callable

import tqdm


def metadata_validation(output_dir: str,
                        repository_data_dir: str,
                        validator: Callable[[dict[str, Any], list[str], dict[str, Any]], None]) -> None:
    os.makedirs(output_dir, exist_ok=True)

    repository_paths = glob.glob(os.path.join(repository_data_dir, "*.json"))
    valids = 0

    print("Validating metadata")
    for repository_path in tqdm.tqdm(repository_paths):
        with open(repository_path, "r") as file:
            repo_data = json.load(file)

        repository_name = repo_data["name"]

        errors: list[str] = []
        information: dict[str, Any] = {}

        validator(repo_data, errors, information)

        information["valid"] = len(errors) == 0
        information["errors"] = errors

        if information["valid"]:
            valids += 1

        information_path = os.path.join(output_dir, repository_name+".json")
        with open(information_path, "w") as file:
            json.dump(information, file)

    print(f"{valids} valid metadata")
