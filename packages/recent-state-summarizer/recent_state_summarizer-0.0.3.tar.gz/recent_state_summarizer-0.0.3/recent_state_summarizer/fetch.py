from __future__ import annotations

import json
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import TypedDict
from urllib.request import urlopen

from bs4 import BeautifulSoup

PARSE_HATENABLOG_KWARGS = {"name": "a", "attrs": {"class": "entry-title-link"}}


class TitleTag(TypedDict):
    title: str
    url: str


def _main(url: str, save_path: str | Path, save_as_json: bool) -> None:
    title_tags = _fetch_titles(url)
    if not save_as_json:
        contents = _as_bullet_list(
            title_tag["title"] for title_tag in title_tags
        )
    else:
        contents = _as_json(title_tags)
    _save(save_path, contents)


def _fetch_titles(url: str) -> Generator[TitleTag, None, None]:
    raw_html = _fetch(url)
    yield from _parse_titles(raw_html)

    soup = BeautifulSoup(raw_html, "html.parser")
    next_link = soup.find("a", class_="test-pager-next")
    if next_link and "href" in next_link.attrs:
        next_url = next_link["href"]
        print(f"Next page found, fetching... {next_url}")
        yield from _fetch_titles(next_url)


def _fetch(url: str) -> str:
    with urlopen(url) as res:
        return res.read()


def _parse_titles(raw_html: str) -> Generator[TitleTag, None, None]:
    soup = BeautifulSoup(raw_html, "html.parser")
    body = soup.body
    title_tags = body.find_all(**PARSE_HATENABLOG_KWARGS)
    for title_tag in title_tags:
        yield {"title": title_tag.text, "url": title_tag["href"]}


def _as_bullet_list(titles: Iterable[str]) -> str:
    return "\n".join(f"- {title}" for title in titles)


def _as_json(title_tags: Iterable[TitleTag]) -> str:
    return "\n".join(
        json.dumps(title_tag, ensure_ascii=False) for title_tag in title_tags
    )


def _save(path: str | Path, contents: str) -> None:
    with open(path, "w", encoding="utf8", newline="") as f:
        f.write(contents)


if __name__ == "__main__":
    import argparse
    import textwrap

    help_message = """
    Retrieve the titles of articles from a specified URL page
    and save them as a list.

    Support:
        - はてなブログ（Hatena blog）

    Example:
        python -m recent_state_summarizer.fetch \\
          https://awesome.hatenablog.com/archive/2023 awesome_titles.txt
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(help_message),
    )
    parser.add_argument("url", help="URL of archive page")
    parser.add_argument("save_path", help="Local file path")
    parser.add_argument(
        "--as-json",
        action="store_true",
        default=False,
        help="Save as JSON format instead of bullet list",
    )
    args = parser.parse_args()

    _main(args.url, args.save_path, args.as_json)
