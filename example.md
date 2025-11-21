* Adds an `applies_to` label to the logsdb message default sort setting [#137767]({{es-pull}}137767)
* Makes {{esql}} field fusion generic so it can be reused across more field types [#137382]({{es-pull}}137382)
 Check notice on line 34 in release-notes/elastic-cloud-serverless/index.md

GitHub Actions
/ vale

Elastic.Decimals: Use American-style formatting for numbers. Use commas as thousands separators (1,234) and periods as decimal points (1.23).
* Releases the {{esql}} `decay` function [#137830]({{es-pull}}137830)
 Check notice on line 35 in release-notes/elastic-cloud-serverless/index.md

GitHub Actions
/ vale

Elastic.Decimals: Use American-style formatting for numbers. Use commas as thousands separators (1,234) and periods as decimal points (1.23).
* Adds additional APM attributes to coordinator-phase duration metrics for richer tracing [#137409]({{es-pull}}137409)
* Adds telemetry to track CPS usage [#137705]({{es-pull}}137705)
 Check notice on line 37 in release-notes/elastic-cloud-serverless/index.md

GitHub Actions
/ vale

Elastic.Acronyms: 'CPS' has no definition.
* Introduces simple bulk loading for binary doc values to improve indexing throughput [#137860]({{es-pull}}137860)
 Check notice on line 38 in release-notes/elastic-cloud-serverless/index.md

GitHub Actions
/ vale

Elastic.WordChoice: Consider using 'efficient' instead of 'simple', unless the term is in the UI.
* Uses IVF_PQ for GPU-based index builds on large datasets to improve vector indexing performance [#137126]({{es-pull}}137126)
* Updates `semantic_text` documentation to link to the authoritative chunking settings guide [#137963]({{es-pull}}137963)
* Refines `semantic_text` documentation based on user feedback [#137970]({{es-pull}}137970)
* Aligns match-phase shard APM metrics with the originating search request context [#137196]({{es-pull}}137196)
* Improves {{serverless-short}} filtering behavior when creating resources from existing configurations [#137850]({{es-pull}}137850)