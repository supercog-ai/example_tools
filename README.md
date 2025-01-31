# example_tools

Example implementations of various API tools and agents, including:

- Google News search and analysis
- LinkedIn profile and company data retrieval
- Web browsing and content extraction

## Environment Variables

To run the examples, you will need to set the following environment variables:

```bash
export RAPIDAPI_KEY=<api_key>
export OPENAI_API_KEY=<api_key>
export SCRAPINGBEE_API_KEY=<api_key>
```

If needed, you can use a tool of your choice for loading the environment variables with the provided `.env.example` file.

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
