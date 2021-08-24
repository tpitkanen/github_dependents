import pprint
import re
import time

from bs4 import BeautifulSoup, Tag
import requests


def get_all_dependents(
        url: str, repeat_delay: float = 1.5, min_stars: int = 5, max_pages: int = None) -> dict:
    """Get all dependents (users) for a given GitHub repository

    Args:
        url: URL to dependents (https://github.com/<owner>/<repository>/network/dependents)
        repeat_delay: seconds to wait after each request
        min_stars: minimum amount of stars required to include a repository in results
        max_pages: maximum amount of page loads, set to None for unlimited

    Returns:
        Repositories and star counts, sorted by star count.
    """
    if max_pages is None:
        # A big number is close enough to unlimited
        max_pages = 100_000

    results = {}
    for _ in range(1, max_pages + 1):
        if not url:
            break

        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as ex:
            print(ex)
            print("Connection error encountered, aborting.")
            break

        if r.status_code == 404:
            print(f"'{url}' returned a 404 error, aborting.")
            break

        soup = BeautifulSoup(r.content, features="html.parser")

        previous_url = url
        url = find_dependents(soup, results)

        if _ % 10 == 0:
            print(f"Page {_} done")

        if url == previous_url:
            break

        time.sleep(repeat_delay)

    def process_results(d: dict) -> dict:
        filtered_d = {k: v for k, v in d.items() if v >= min_stars}
        # Values in descending order
        sorted_d = sorted(filtered_d.items(), key=lambda item: -item[1])
        return dict(sorted_d)

    return process_results(results)


# tag.prettify() is useful for planning selectors


def _is_repository_link(tag: Tag) -> bool:
    return tag.get("data-hovercard-type") == "repository"


def _is_octicon_star(tag: Tag) -> bool:
    class_ = tag.get("class")
    return class_ is not None and "octicon-star" in class_


def _is_next_button(tag: Tag) -> bool:
    return tag.text == "Next"


def find_dependents(soup: BeautifulSoup, results: dict) -> str:
    """Find dependents on a given page

    Args:
        soup: page in BeautifulSoup format
        results: results so far

    Returns:
        Link to the next page
    """
    dependents = soup.select_one("#dependents")
    rows = dependents.select(".Box-row")

    for row in rows:
        repository_link = row.find(_is_repository_link).get("href")

        octigon_star = row.find(_is_octicon_star)
        star_count = octigon_star.next_sibling
        star_count = re.sub(r"[^0-9.]", r"", str(star_count))  # Remove non-number characters
        star_count = int(star_count)

        results[repository_link] = star_count

    next_button = soup.find(_is_next_button)
    next_link = next_button.attrs.get("href")
    return next_link


def main() -> None:
    # Add target URL here:
    dependents_url = "https://github.com/<owner>/<repository>/network/dependents"
    results = get_all_dependents(dependents_url)
    pprint.pprint(results, sort_dicts=False)


if __name__ == "__main__":
    main()
