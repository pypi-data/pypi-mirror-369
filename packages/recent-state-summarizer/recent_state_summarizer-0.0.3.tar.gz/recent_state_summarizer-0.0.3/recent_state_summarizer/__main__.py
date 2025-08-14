import argparse
from textwrap import dedent

from recent_state_summarizer.fetch import fetch_titles_as_bullet_list
from recent_state_summarizer.summarize import summarize_titles


def parse_args():
    help_message = """
    Summarize blog article titles with the OpenAI API.

    ⚠️ Set `OPENAI_API_KEY` environment variable.

    Example:
        omae-douyo https://awesome.hatenablog.com/archive/2023

    Retrieve the titles of articles from a specified URL.
    After summarization, prints the summary.

    Support:
        - はてなブログ（Hatena blog）
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent(help_message),
    )
    parser.add_argument("url", help="URL of archive page")
    return parser.parse_args()


def main():
    args = parse_args()

    titles = fetch_titles_as_bullet_list(args.url)
    summary = summarize_titles(titles)
    print(summary)
