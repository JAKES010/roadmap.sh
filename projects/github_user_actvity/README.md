# GitHub User Activity

A small command-line program that fetches a user's recent public GitHub events and prints readable summaries.

## Requirements

- Python 3
- Internet access to the GitHub REST API

## Usage

From this directory, run:

```bash
python3 main.py <github_username>
```

For example:

```bash
python3 main.py torvalds
```

The tool reports recent public events such as pushes, issues, pull requests, stars, and forks. GitHub may return an empty list when a user has no recent public activity. Unauthenticated API rate limits apply.

## Run tests

From the repository root:

```bash
python3 -m unittest discover -s tests
```
