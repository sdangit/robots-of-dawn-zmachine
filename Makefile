.PHONY: test audit

test:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v

audit:
	python3 scripts/audit_publication.py
