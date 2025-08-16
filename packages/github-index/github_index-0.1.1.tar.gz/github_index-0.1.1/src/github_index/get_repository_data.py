import base64
import json
import os
import time
import warnings

import requests
import tqdm


def get_github_token() -> str | None:
    token = None

    if "GITHUB_TOKEN" in os.environ:
        token = os.environ["GITHUB_TOKEN"]

    return token


def http_get(url: str, session: requests.Session | None = None,
             parameters: dict | None = None,
             token: str | None = None) -> requests.Response:

    while True:
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        if session is None:
            response = requests.get(url, params=parameters, headers=headers)
        else:
            response = session.get(url, params=parameters, headers=headers)

        if response.status_code == 403:
            time_to_wait = 0

            if "retry-after" in response.headers:
                time_to_wait = float(response.headers["retry_after"])

            elif ("x-ratelimit-remaining" in response.headers and
                  response.headers["x-ratelimit-remaining"] == 0 and
                  "x-ratelimit-reset" in response.headers):

                time_to_wait = float(
                    response.headers["x-ratelimit-reset"]) - time.time()

            else:
                time_to_wait = 60

            time_to_wait = min(time_to_wait, 0)

            print(
                f"Rate limit error. Waiting {time_to_wait} seconds before retry.")
            time.sleep(time_to_wait)

        else:
            break

    return response


def get_repositoy_data(organization_name: str,
                       output_dir: str,
                       token: str | None = None) -> None:
    os.makedirs(output_dir, exist_ok=True)

    if token is None:
        token = get_github_token()
    if token is None:
        warnings.warn("No Github Token. Requests may fail or be slow.")

    session = requests.Session()

    print("Getting repositories metadata.")

    all_repos: list[dict] = []

    response = http_get(f"https://api.github.com/orgs/{organization_name}/repos",
                        session,
                        parameters={"type": "public"},
                        token=token)

    response_json = response.json()
    all_repos += response_json

    while "next" in response.headers.get("link"):
        response = http_get(
            response.links["next"]["url"], session, token=token)
        response_json = response.json()
        all_repos += response_json

    print("Getting additional data.")
    # Get additional data
    for repo in tqdm.tqdm(all_repos):

        # Contributors
        response_contributors = http_get(
            repo["contributors_url"], session, token=token)
        repo["contributors"] = response_contributors.json()

        # README
        repo_full_name = repo["full_name"]
        response_readme = http_get(
            f"https://api.github.com/repos/{repo_full_name}/readme", session, token=token)

        if "download_url" in response_readme.json():
            download_url = response_readme.json()["download_url"]

            response_content = http_get(download_url, session, token=token)
            readme = response_content.content.decode()
        else:
            readme = ""

        repo["readme"] = readme

        # CFF
        response_cff = http_get(
            f"https://api.github.com/repos/{repo["full_name"]}/contents/CITATION.cff", session, token=token)

        if response_cff.status_code == 404:
            cff = ""
        else:
            cff = base64.b64decode(response_cff.json()["content"]).decode()

        repo["cff"] = cff

    print("Saving data.")

    # Save
    for repo in tqdm.tqdm(all_repos):
        repo_clean = {key: repo[key] for key in ["name", "full_name", "html_url", "description",
                                                 "created_at", "updated_at", "license", "topics", "readme", "cff", "contributors"]}

        name = repo["name"]
        path = os.path.join(output_dir, name+".json")

        with open(path, "w") as file:
            json.dump(repo_clean, file)
