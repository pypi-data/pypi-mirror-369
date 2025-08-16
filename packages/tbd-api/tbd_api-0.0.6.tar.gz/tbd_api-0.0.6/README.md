# TorrentBD API

Unofficial API for TorrentBD with search and profile access.

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
  <a href="https://badge.fury.io/py/tbd-api"><img src="https://badge.fury.io/py/tbd-api.svg?nocache=1" alt="PyPI version"></a>
  <a href="https://pepy.tech/projects/tbd-api"><img src="https://static.pepy.tech/badge/tbd-api" alt="PyPI Downloads"></a>
</p>

## Overview

TorrentBD API is a Python package that provides a RESTful API wrapper for the TorrentBD website. It handles authentication, session management, and parsing of web content.

## Disclaimer

This project is not affiliated with or endorsed by TorrentBD. This is an unofficial API created for educational purposes only. Use at your own risk.

## Features

- Search torrents with pagination
- Access user profile information
- Automated login with reCAPTCHA solving
- Configurable via command line, environment variables, or config file
- Web UI for easy access

## Installation

```bash
pip install tbd-api
```

## Requirements

- Python 3.12 or later
- Chrome or Chromium browser (for login functionality)
- ChromeDriver (compatible with your Chrome/Chromium version)

## Usage

### Command Line

```bash
# Basic usage
tbd-api

# With credentials
tbd-api --username "user" --password "pass" --totp-secret "secret"

# Custom host and port
tbd-api --host "127.0.0.1" --port 8000
```

### API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/search` | GET | Search torrents | `query` (required): Search term<br>`page` (optional): Page number (default: 1) |
| `/profile` | GET | Get user profile | None |
| `/online` | GET | Get the list of online users | None |


## Configuration

### Command-Line Arguments

```
usage: tbd-api [-h] [--username USERNAME] [--password PASSWORD] [--totp-secret TOTP_SECRET]
               [--port PORT] [--host HOST] [--cookies COOKIES]

options:
  -h, --help            show this help message and exit
  --username USERNAME   TorrentBD username
  --password PASSWORD   TorrentBD password
  --totp-secret TOTP_SECRET
                        TOTP secret for 2FA
  --port PORT           Port to run the server on (default: 5000)
  --host HOST           Host to bind the server to (default: 0.0.0.0)
  --cookies COOKIES     Path to cookies file
```

### Configuration Files

All data is automatically saved in `~/.config/tbd-api/`:
- Credentials and settings: `config.json`
- Login cookies: `cookies.txt` (Netscape format)

### Cookie Management

You can use the [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) Chrome extension to export cookies from TorrentBD in Netscape format and save them to `~/.config/tbd-api/cookies.txt`. This is useful when you want to bypass the automated login process.

### Environment Variables

You can also use a `.env` file in the project folder:
```
TORRENTBD_USERNAME=username@mail.com
TORRENTBD_PASSWORD=secure_password
TORRENTBD_TOTP_SECRET=base32secret3232
```

## Docker

```bash
# Build the image
docker build -t tbd-api .

# Run the container
docker run -p 5000:5000 tbd-api --username "user" --password "pass" --totp-secret "secret"

# or with environment variables
docker run --env-file .env -p 5000:5000 tbd-api
```

## Development

```bash
# Clone the repository
git clone https://github.com/TanmoyTheBoT/torrentbd-api.git
cd torrentbd-api

# Install in development mode
make install

# Run
make run

# Run tests
make check

# Run linters
make lint
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
