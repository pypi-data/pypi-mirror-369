<p align="center">
    <a href="https://github.com/YisusChrist/requests-pprint/issues">
        <img src="https://img.shields.io/github/issues/YisusChrist/requests-pprint?color=171b20&label=Issues%20%20&logo=gnubash&labelColor=e05f65&logoColor=ffffff">&nbsp;&nbsp;&nbsp;
    </a>
    <a href="https://github.com/YisusChrist/requests-pprint/forks">
        <img src="https://img.shields.io/github/forks/YisusChrist/requests-pprint?color=171b20&label=Forks%20%20&logo=git&labelColor=f1cf8a&logoColor=ffffff">&nbsp;&nbsp;&nbsp;
    </a>
    <a href="https://github.com/YisusChrist/requests-pprint/stargazers">
        <img src="https://img.shields.io/github/stars/YisusChrist/requests-pprint?color=171b20&label=Stargazers&logo=octicon-star&labelColor=70a5eb">&nbsp;&nbsp;&nbsp;
    </a>
    <a href="https://github.com/YisusChrist/requests-pprint/actions">
        <img alt="Tests Passing" src="https://github.com/YisusChrist/requests-pprint/actions/workflows/github-code-scanning/codeql/badge.svg">&nbsp;&nbsp;&nbsp;
    </a>
    <a href="https://github.com/YisusChrist/requests-pprint/pulls">
        <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/YisusChrist/requests-pprint?color=0088ff">&nbsp;&nbsp;&nbsp;
    </a>
    <a href="https://opensource.org/license/gpl-3.0">
        <img alt="License" src="https://img.shields.io/github/license/YisusChrist/requests-pprint?color=0088ff">
    </a>
</p>

<br>

<p align="center">
    <a href="https://github.com/YisusChrist/requests-pprint/issues/new/choose">Report Bug</a>
    ·
    <a href="https://github.com/YisusChrist/requests-pprint/issues/new/choose">Request Feature</a>
    ·
    <a href="https://github.com/YisusChrist/requests-pprint/discussions">Ask Question</a>
    ·
    <a href="https://github.com/YisusChrist/requests-pprint/security/policy#reporting-a-vulnerability">Report security bug</a>
</p>

<br>

![Alt](https://repobeats.axiom.co/api/embed/f0abd941e547c55036eec4b15875c81929581aab.svg "Repobeats analytics image")

<br>

`requests-pprint` is a Python library that allows you to print your HTTP requests and responses in a pretty format. It is based on the `requests` library and uses the `rich` library to print the response in a more readable way.

<details>
<summary>Table of Contents</summary>

- [Requirements](#requirements)
- [Installation](#installation)
  - [From PyPI](#from-pypi)
  - [Manual installation](#manual-installation)
  - [Uninstall](#uninstall)
- [Usage](#usage)
  - [1. Pretty Print HTTP Request](#1-pretty-print-http-request)
  - [2. Pretty Print HTTP Response](#2-pretty-print-http-response)
  - [3. Print Response Summary](#3-print-response-summary)
  - [4. Pretty Print Asynchronous HTTP Response](#4-pretty-print-asynchronous-http-response)
  - [5. Pretty Print Asynchronous Response Summary](#5-pretty-print-asynchronous-response-summary)
- [Contributors](#contributors)
  - [How do I contribute to requests-pprint?](#how-do-i-contribute-to-requests-pprint)
- [License](#license)

</details>

## Requirements

Here's a breakdown of the packages needed and their versions:

- [poetry](https://pypi.org/project/poetry) >= 1.7.1 (_only for manual installation_)
- [aiohttp](https://pypi.org/project/aiohttp) >= 3.9.5
- [requests](https://pypi.org/project/requests) >= 2.31.0
- [rich](https://pypi.org/project/rich) >= 13.7.1

> [!NOTE]\
> The software has been developed and tested using Python `3.12.1`. The minimum required version to run the software is Python 3.6. Although the software may work with previous versions, it is not guaranteed.

## Installation

### From PyPI

`requests-pprint` can be installed easily as a PyPI package. Just run the following command:

```bash
pip3 install requests-pprint
```

> [!IMPORTANT]\
> For best practices and to avoid potential conflicts with your global Python environment, it is strongly recommended to install this program within a virtual environment. Avoid using the --user option for global installations. We highly recommend using [pipx](https://pypi.org/project/pipx) for a safe and isolated installation experience. Therefore, the appropriate command to install `requests-pprint` would be:
>
> ```bash
> pipx install requests-pprint
> ```

### Manual installation

If you prefer to install the program manually, follow these steps:

> [!NOTE]\
> This will install the version from the latest commit, not the latest release.

1. Download the latest version of [requests-pprint](https://github.com/YisusChrist/requests-pprint) from this repository:

   ```sh
   git clone https://github.com/YisusChrist/requests-pprint
   cd requests-pprint
   ```

2. Install the package:

   ```sh
   poetry install --only main
   ```

### Uninstall

If you installed it from PyPI, you can use the following command:

```bash
pipx uninstall requests-pprint
```

## Usage

### 1. Pretty Print HTTP Request

```python
import requests
from requests_pprint import pprint_http_request

# Prepare a sample HTTP request
url = 'https://api.example.com'
headers = {'User-Agent': 'Mozilla/5.0'}
body = {'key': 'value'}
request = requests.Request('POST', url, headers=headers, json=body)
prepared_request = request.prepare()

# Print the formatted HTTP request
pprint_http_request(prepared_request)
```

Output:

![1](https://i.imgur.com/VG7rfZq.png)

### 2. Pretty Print HTTP Response

```python
import requests
from requests_pprint import pprint_http_response

# Send a sample HTTP request
response = requests.get('https://example.com')

# Print the formatted HTTP response
pprint_http_response(response)
```

Output:

![2](https://i.imgur.com/uDF8sBk.png)

### 3. Print Response Summary

```python
import requests
from requests_pprint import print_response_summary

# Send a sample HTTP request
response = requests.get('https://example.com')

# Print a summary of the HTTP response
print_response_summary(response)
```

Output:

![3](https://i.imgur.com/eCPqCT1.png)

---

Since 2024-07-28, `requests-pprint` supports asynchronous requests from the [aiohttp](https://pypi.org/project/aiohttp) library. You can use the `pprint_async_http_request` and `pprint_async_http_response` functions to print the formatted HTTP request and response, respectively, as well as the `print_async_response_summary` function to print a summary of the HTTP response.

Here is an example of how to use these functions:

### 4. Pretty Print Asynchronous HTTP Response

```python
import asyncio
import aiohttp

from requests_pprint import pprint_async_http_response

async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://api.example.com"
        headers = {"User-Agent": "Mozilla/5.0"}
        body = {"key": "value"}
        async with session.post(url, headers=headers, json=body) as response:
            await pprint_async_http_response(response)


asyncio.run(main())
```

Output:

![4](https://i.imgur.com/uDF8sBk.png)

### 5. Pretty Print Asynchronous Response Summary

```python
import asyncio
import aiohttp

from requests_pprint import print_async_response_summary

async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://api.example.com"
        headers = {"User-Agent": "Mozilla/5.0"}
        body = {"key": "value"}
        async with session.post(url, headers=headers, json=body) as response:
            await print_async_response_summary(response)


asyncio.run(main())
```

Output:

![5](https://i.imgur.com/eCPqCT1.png)

## Contributors

<a href="https://github.com/YisusChrist/requests-pprint/graphs/contributors"><img src="https://contrib.rocks/image?repo=YisusChrist/requests-pprint" /></a>

### How do I contribute to requests-pprint?

Before you participate in our delightful community, please read the [code of conduct](https://github.com/YisusChrist/.github/blob/main/CODE_OF_CONDUCT.md).

I'm far from being an expert and suspect there are many ways to improve – if you have ideas on how to make the configuration easier to maintain (and faster), don't hesitate to fork and send pull requests!

We also need people to test out pull requests. So take a look through [the open issues](https://github.com/YisusChrist/requests-pprint/issues) and help where you can.

See [Contributing Guidelines](https://github.com/YisusChrist/.github/blob/main/CONTRIBUTING.md) for more details.

## License

`requests-pprint` is released under the [GPL-3.0 License](https://opensource.org/license/GPL-3.0).
