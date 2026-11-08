# Scheduled private drafts runner

Generic scheduled launcher for a private draft generator. This repository contains no reservation data, customer information, draft content, shop configuration, or credentials. Standard public GitHub-hosted Linux runners only. No caches or Actions artifacts.

Customer message delivery is not implemented.

The first daily event starts at 17:03 JST and waits for 17:30 before reading the
private source. A second event at 17:43 is a safe catch-up for a delayed or lost
first event. It verifies the private manifest and both message hashes first; when
the 17:30 pair is complete, it exits without rewriting drafts or owner edits.
Recovery only replaces the private unsent draft pair and has no LINE
customer-delivery path.

Preparation requires `SOURCE_DATABASE_URL`, `LINE_SOURCE_STATUS_URL`, and
`LINE_SOURCE_STATUS_READ_KEY` in this repository's Actions secrets. The status
key is read-only and must not be replaced with the source application's general
internal API key. Missing status confirmation stops preparation and retains the
previous drafts.

Validate the result recorder locally with Python, PyYAML, and
`python -m unittest discover -s tests -v`. Invalid manual times and damaged
failure reports must still produce a private `needs_attention` record. No
credentials or network access are used by these checks.
