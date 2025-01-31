# example_tools

Example implementations of various API tools and agents, including:

- Google News search and analysis
- LinkedIn profile and company data retrieval
- Web browsing and content extraction

## Installing Python Dependencies

First, create a virtual environment:

```bash
$ uv venv
```

If you don't have `uv` installed, you can install it with:

```bash
$ brew install uv
```

Then, activate the virtual environment:

```bash
$ source .venv/bin/activate
```

Finally, install the dependencies:

```bash
$ uv pip install -e '.[dev]'
```

## Run the Examples

To run the examples, ensure you have the virutual environment activated:

```bash
$ source .venv/bin/activate
```

Then, run the tool tests:
```bash
$ python test_tools.py
```

or, you can use pytest:
```bash
$ pytest
```
