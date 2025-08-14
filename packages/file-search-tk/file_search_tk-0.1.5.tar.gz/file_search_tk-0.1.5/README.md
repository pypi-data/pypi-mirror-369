## File Search TK

Simple Tkinter UI that:

- Lists files from a folder returned by an external `fetch_logs` script given a query.
- Shows selected file content.
- Highlights occurrences of the same query within the text.

### Requirements

- Python 3.9+
- A script or executable named `fetch_logs` resolvable in `PATH` that takes a single argument (query) and prints a directory path to stdout.

### Install

If using Poetry:

```bash
poetry install
```

Or via pip:

```bash
pip install -e .
```

### Run

Using the installed console script:

```bash
file-search-tk
```

Or directly:

```bash
python -m file_search_tk.app
```

### Notes

- The UI calls `fetch_logs <query>` in a background thread. The command must return a valid existing directory path on stdout and exit with code 0. Any stderr or non-zero exit code is treated as an error.
- File list shows only regular files at the top level of the returned directory, sorted by filename.
- Text area highlights case-insensitive matches of the query.