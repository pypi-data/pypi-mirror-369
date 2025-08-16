from typing import Any, Callable, Self

import marko
from marko.inline import Link

from github_index.readme_validation import extract_elements


class Badge:
    def __init__(self, url_badge_image: str, url_target: str | None = None):
        self.url_badge_image = url_badge_image
        self.url_target = url_target

    def __eq__(self, other: Self) -> bool:
        return (other.url_badge_image == self.url_badge_image and
                other.url_target == self.url_target)

    def to_markdown(self) -> str:
        result = f"[![]({self.url_badge_image})]({self.url_target})"

        return result

    @classmethod
    def from_link(cls, link: Link) -> Self:
        return Badge(link.children[0].dest, link.dest)


GITHUB_BADGE_URL = "https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"


def github_badge_generator(data: dict[str, dict[str, Any]]) -> list[Badge]:
    repo_url = data["repository"]["html_url"]

    badge = Badge(GITHUB_BADGE_URL, repo_url)

    return [badge]


def generate_badges(readme: str, data: dict[str, dict[str, Any]], badge_generator: Callable[[dict[str, dict[str, Any]]], list[Badge]]) -> str:

    new_badges = badge_generator(data)

    if len(new_badges) == 0:
        return readme

    document = marko.parse(readme)

    pre_abstract = []

    for child in document.children:
        if not isinstance(child, marko.block.Heading):
            pre_abstract.append(child)
        else:
            break

    links = extract_elements(pre_abstract, marko.inline.Link)

    existing_badges = []
    for link in links:
        try:
            badge = Badge.from_link(link)
            existing_badges.append(badge)
        except:
            pass

    badges_line = ""
    for new_badge in new_badges:
        if new_badge not in existing_badges:
            badges_line += new_badge.to_markdown()

    if len(badges_line) != 0:
        readme = badges_line+"\n\n"+readme

    return readme
