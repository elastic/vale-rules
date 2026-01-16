---
title: Ingest for search use cases
description: Search use cases usually focus on general content, typically text-heavy data that does not have a timestamp. This could be data like knowledge bases,...
url: https://www.elastic.co/docs/solutions/search/ingest-for-search
products:
  - Elastic Cloud Serverless
  - Elasticsearch
applies_to:
  - Elastic Cloud Serverless: Generally available
  - Elastic Stack: Generally available in 9.0+
---

# Ingest for search use cases
<note>
  This page covers ingest methods specifically for search use cases. If you're working with a different use case, refer to the [ingestion overview](https://www.elastic.co/docs/manage-data/ingest) for more options.
</note>

Search use cases usually focus on general **content**, typically text-heavy data that does not have a timestamp. This could be data like knowledge bases, website content, product catalogs, and more.
Once you've decided how to [deploy Elastic](https://www.elastic.co/docs/deploy-manage), the next step is getting your content into Elasticsearch. Your choice of ingestion method depends on where your content lives and how you need to access it.
There are several methods to ingest data into Elasticsearch for search use cases.
Choose one or more based on your requirements:
- [Native APIs and language clients](#es-ingestion-overview-apis): Index any JSON document directly using the Elasticsearch REST API or the official clients for languages like Python, Java, Go, and more.
- **Web crawler:** Ingest content from public or private websites to make it searchable.
- **Enterprise connectors:** Use pre-built connectors to sync data from external content sources like SharePoint, Confluence, Jira, and databases like MongoDB or PostgreSQL into Elasticsearch.

<tip>
  If you just want to do a quick test, you can load [sample data](https://www.elastic.co/docs/manage-data/ingest/sample-data) into your Elasticsearch cluster using the UI.
</tip>


## Use APIs

You can use the [`_bulk` API](https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-document) to add data to your Elasticsearch indices, using any HTTP client, including the [Elasticsearch client libraries](https://www.elastic.co/docs/solutions/search/site-or-app/clients).
<tip>
  To connect to an Elasticsearch Serverless project, you must [find the connection details](https://www.elastic.co/docs/solutions/search/search-connection-details).
</tip>

While the Elasticsearch APIs can be used for any data type, Elastic provides specialized tools that optimize ingestion for specific use cases.

## Use specialized tools

You can use these specialized tools to add general content to Elasticsearch indices.

| Method                                                                              | Description                                                                                                  | Notes                                                                                                             |
|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| [**Elastic Open Web Crawler**](https://github.com/elastic/crawler)                  | Programmatically discover and index content from websites and knowledge bases                                | Crawl public-facing web content or internal sites accessible via HTTP proxy                                       |
| [**Content connectors**](https://www.elastic.co/docs/reference/search-connectors)   | Third-party integrations to popular content sources like databases, cloud storage, and business applications | Choose from a range of Elastic-built connectors or build your own in Python using the Elastic connector framework |
| [**File upload**](https://www.elastic.co/docs/manage-data/ingest/upload-data-files) | One-off manual uploads through the UI                                                                        | Useful for testing or very small-scale use cases, but not recommended for production workflows                    |


### Process data at ingest time

You can also transform and enrich your content at ingest time using [ingest pipelines](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines).
The Elastic UI has a set of tools for creating and managing indices optimized for search use cases. You can also manage your ingest pipelines in this UI. Learn more in [Ingest pipelines for search use cases](https://www.elastic.co/docs/solutions/search/search-pipelines).