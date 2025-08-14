from pathlib import Path

import openai

MODEL = "gpt-3.5-turbo"


def _main(titles_path: str | Path) -> str:
    titles = _read_titles(titles_path)
    return summarize_titles(titles)


def summarize_titles(titles: str) -> str:
    prompts = _build_prompts(titles)
    response = _complete_chat(prompts)
    return _parse_response(response)


def _build_prompts(titles: str):
    prompts = [
        {"role": "user", "content": _build_summarize_prompt_text(titles)}
    ]
    return prompts


def _build_summarize_prompt_text(titles_as_list: str) -> str:
    return f"""\
3つのバッククォートで囲まれた以下は、同一人物が最近書いたブログ記事のタイトルの一覧です。
それを読み、この人物が最近何をやっているかを詳しく教えてください。
応答は文ごとに改行して区切ってください。

```
{titles_as_list}
```
"""


def _complete_chat(prompts, temperature=0.0):
    return openai.ChatCompletion.create(
        model=MODEL, messages=prompts, temperature=temperature
    )


def _parse_response(response) -> str:
    return response["choices"][0]["message"]["content"]


def _read_titles(titles_path: str | Path) -> str:
    with open(titles_path, encoding="utf8", newline="") as f:
        return f.read()


if __name__ == "__main__":
    import argparse
    import textwrap

    help_message = f"""
    Summarize a list of blog article titles using the OpenAI API ({MODEL}).
    This command prints the summary.

    ⚠️ Set `OPENAI_API_KEY` environment variable.

    Example:
        python -m recent_state_summarizer.summarize awesome_titles.txt
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(help_message),
    )
    parser.add_argument(
        "titles_path",
        help="Local file path where the list of titles is saved",
    )
    args = parser.parse_args()

    print(_main(args.titles_path))
