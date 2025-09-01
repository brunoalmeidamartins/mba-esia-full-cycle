.PHONY: format ingest run

# Format code using isort (imports) then black (code), both read config from pyproject.toml
format:
	isort src
	black src

# Run data ingestion script
ingest:
	python src.ingest

# Run chat application
run:
	python src.chat
