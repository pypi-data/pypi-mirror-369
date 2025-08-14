# sam_url_cache

A simple Python package for caching the contents of URLs using SQLite. This helps avoid repeated network requests for the same URL.

## PYPI
https://pypi.org/project/sam-url-cache/

## Features

- Caches URL responses in a local SQLite database.
- Automatically fetches and stores content on cache miss.
- Simple API for checking if a URL has been seen before.

## Installation

Install via pip

```sh
pip install sam-url-cache
```

## Usage

```python
from sam_url_cache import URLCache

cache = URLCache()  # Uses default database path 'url_cache.db'

# Fetch and cache a URL
content = cache.get_url('https://example.com')

# Check if a URL has been seen before
if cache.seen_before('https://example.com'):
    print("URL is cached!")
```

## Object

### `URLCache(databse_path: str = 'url_cache.db')`

Create a new URL cache instance. Optionally specify a custom database path.

### `get_url(url: str) -> str`

Fetch the content of the URL. Returns cached content if available, otherwise fetches from the web and caches it.

### `seen_before(url: str) -> bool`

Check if the URL is already cached.