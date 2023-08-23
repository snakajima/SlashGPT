.PHONY: lint
lint:
	black . --check
	isort . --check
	# Ignoring
	# - E501: max line length
	# - E203 and W203: They go against PEP8: https://black.readthedocs.io/en/stable/faq.html#why-are-flake8-s-e203-and-w503-violated
	flake8 . --ignore=E501,E203,W503

.PHONY: format
format:
	black .
	isort .