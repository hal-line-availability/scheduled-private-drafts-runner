# Scheduled private drafts runner

Generic scheduled launcher for a private draft generator. This repository contains no reservation data, customer information, draft content, shop configuration, or credentials. Standard public GitHub-hosted Linux runners only. No caches or Actions artifacts.

Customer message delivery is not implemented.

The first daily event starts at 17:03 JST and waits for 17:30 before reading the
private source. A second event at 17:43 is a safe catch-up for a delayed or lost
first event. Repeating preparation only replaces the private unsent draft pair;
it has no LINE customer-delivery path.
