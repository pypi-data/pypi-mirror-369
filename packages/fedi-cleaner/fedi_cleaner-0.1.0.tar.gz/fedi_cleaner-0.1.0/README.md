# Fedi Cleaner

A tool to help you clean your Fediverse account's following/followers/lists/blocks/mutes/...

## Prerequisites

* Your Fediverse instance supports Mastodon API
* You have a good internet connection (for validating accounts)
* You know how to setup Python environment (uv for example)

## Usage

### 1. Create Configuration

Create a configuration file by running:
```bash
uvx fedi-cleaner --init-config
```

Then edit the generated `config.json` file to set your:
- `access_token`: Your Mastodon access token
- `api_base_url`: Your Mastodon instance URL (e.g., https://mastodon.social)
- Other settings as needed

Alternatively, you can set environment variables prefixed with `FEDI_CLEANER_` (for example `FEDI_CLEANER_ACCESS_TOKEN`).

### 2. Run the Tool

```bash
uvx fedi-cleaner
```

## Development

For development and contributing:

```bash
# Clone the repository
git clone https://codeberg.org/poesty/Fedi-Cleaner
cd Fedi-Cleaner

# Set up development environment
uv venv
uv sync

# Run the tool
uv run fedi-cleaner
```