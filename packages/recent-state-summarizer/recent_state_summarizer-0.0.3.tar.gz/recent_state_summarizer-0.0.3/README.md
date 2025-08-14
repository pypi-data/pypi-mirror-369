# recent-state-summarizer

Summarize blog article titles with the OpenAI API

a.k.a. _RSS_ 😃

## Setup

```
$ pip install recent-state-summarizer
```

⚠️ Set `OPENAI_API_KEY` environment variable.  
ref: https://platform.openai.com/account/api-keys

## Usage

```
$ omae-douyo https://nikkie-ftnext.hatenablog.com/archive/2023/4

この人物は最近、プログラミングに関することを中心にして活動しています。

（略）

最近は、株式会社はてなに入社したようです。
```

Currently support:

- はてなブログ（Hatena blog）

To see help, type `omae-douyo -h`.

## Development

### Sub commands

Fetch only:

```
python -m recent_state_summarizer.fetch -h
```

Summarize only:  
It's convenient to omit fetching in tuning the prompt.

```
python -m recent_state_summarizer.summarize -h
```

### Environment

```
$ git clone https://github.com/ftnext/recent-state-summarizer.git
$ cd recent-state-summarizer

$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.lock
(venv) $ pip install -e '.'
```
