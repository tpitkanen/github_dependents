import argparse
import re
import time

import bs4
import requests


class UrlError(Exception):
    """Error in URL"""


def get_all_dependents(
        url: str, repeat_delay: float = 1.5, max_pages: int = None) -> dict:
    """Get dependents (users) for a given GitHub repository

    Args:
        url: URL to repository (https://github.com/<owner>/<repository>)
        repeat_delay: seconds to wait between requests
        max_pages: maximum amount of page loads, set to None or 0 for unlimited

    Returns:
        Repositories and star counts, sorted by star count.
    """
    if not max_pages:
        # 30*100_000 = 3_000_000 results should be enough for everything
        # without the risk of getting stuck forever with unlimited pages.
        max_pages = 100_000

    url = _build_url(url)

    results = {}
    for _ in range(1, max_pages + 1):
        if not url:
            break

        start_time = time.time()

        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as ex:
            print(ex)
            print("Connection error encountered, aborting.")
            break

        if r.status_code >= 400:
            print(f"'{url}' returned status code '{r.status_code}', aborting.")
            break

        try:
            soup = bs4.BeautifulSoup(r.content, features="html.parser")
            previous_url = url
            url = parse_page(soup, results)
        except Exception as ex:
            print(ex)
            print("Error encountered while parsing page, aborting.")
            break

        if _ % 10 == 0:
            print(f"Page {_} done")

        if url == previous_url:
            break

        wait_time = repeat_delay - (time.time() - start_time)
        if wait_time > 0:
            time.sleep(wait_time)

    return results


def _build_url(url: str) -> str:
    """Build URL to dependents

    Add "/network/dependents" to URL if it is missing.

    Args:
        url: URL to build

    Raises:
        UrlError: if URL is incorrect

    Returns:
        URL to https://github.com/<owner>/<repository>/network/dependents
    """
    dependents_part = "/network/dependents"
    github_stem = "https://github.com/"

    # TODO: don't require https:// at the start
    if not url.startswith(github_stem):
        raise UrlError(f"Unsupported URL: '{url}'")

    if dependents_part not in url:
        url = url.rstrip("/") + dependents_part
    return url


# tag.prettify() is useful for planning selectors


def _is_repository_link(tag: bs4.Tag) -> bool:
    return tag.get("data-hovercard-type") == "repository"


def _is_octicon_star(tag: bs4.Tag) -> bool:
    class_ = tag.get("class")
    return class_ is not None and "octicon-star" in class_


def _is_next_button(tag: bs4.Tag) -> bool:
    return tag.text == "Next"


def parse_page(soup: bs4.BeautifulSoup, results: dict) -> str:
    """Parse dependents on a given page

    Args:
        soup: page in BeautifulSoup format
        results: results so far. New dependents are added here.

    Returns:
        Link to the next page
    """
    dependents = soup.select_one("#dependents")
    rows = dependents.select(".Box-row")

    for row in rows:
        repository_link = row.find(_is_repository_link).get("href")
        repository_link = "https://github.com" + repository_link

        octigon_star = row.find(_is_octicon_star)
        star_count = octigon_star.next_sibling
        star_count = re.sub(r"[^0-9.]", r"", str(star_count))  # Remove non-number characters
        star_count = int(star_count)

        results[repository_link] = star_count

    next_button = soup.find(_is_next_button)
    next_link = next_button.attrs.get("href")
    return next_link


def process_results(results: dict, min_stars: int = 5) -> dict:
    """Sort and filer results

    Args:
        results: results to process
        min_stars: minimum amount of stars required to include a repository in results

    Returns:
        Processed results
    """
    filtered_d = {k: v for k, v in results.items() if v >= min_stars}
    # Values in descending order
    sorted_d = dict(sorted(filtered_d.items(), key=lambda item: -item[1]))
    return sorted_d


def print_results(results: dict) -> None:
    """Print formatted results

    Args:
        results: results to print
    """
    for k, v in results.items():
        print(f"{v:7} | {k}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        Arguments
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Get the most starred GitHub repositories depending on a given repository")

    parser.add_argument(
        "url", metavar="url", type=str,
        help="URL to repository (https://github.com/<owner>/<repository>")
    parser.add_argument(
        "-d", "--repeat-delay", metavar="delay", type=float, default=1.5,
        help="seconds to wait between requests")
    parser.add_argument(
        "-p", "--pages", metavar="pages", type=int, default=20,
        help="maximum number of pages to load (30 dependents per page). Set to 0 for practically unlimited.")
    parser.add_argument(
        "-s", "--stars", metavar="stars", type=int, default=5,
        help="minimum amount of stars required to include a repository in results")

    return parser.parse_args()


def main() -> None:
    """Run the program and print results"""
    args = parse_arguments()
    results = get_all_dependents(
        args.url, repeat_delay=args.repeat_delay, max_pages=args.pages)
    results = process_results(results, min_stars=args.stars)
    print_results(results)


if __name__ == "__main__":
    main()
