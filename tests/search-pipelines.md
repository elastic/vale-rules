---
title: Ingest pipelines for search use cases
description: You can manage ingest pipelines through Elasticsearch APIs or Kibana UIs. The Content UI under Search has a set of tools for creating and managing indices...
url: https://www.elastic.co/docs/solutions/search/search-pipelines
products:
  - Elasticsearch
---

# Ingest pipelines for search use cases

You can manage ingest pipelines through Elasticsearch APIs or Kibana UIs.
The **Content** UI under **Search** has a set of tools for creating and managing indices optimized for search use cases (non-time series data). You can also manage your ingest pipelines in this UI.

## Find pipelines in Content UI

To work with ingest pipelines using these UI tools, you’ll be using the **Pipelines** tab on your search-optimized Elasticsearch index.
To find this tab in the Kibana UI:
1. Go to **Search > Content > Elasticsearch indices**.
2. Select the index you want to work with. For example, `search-my-index`.
3. On the index’s overview page, open the **Pipelines** tab.
4. From here, you can follow the instructions to create custom pipelines, and set up ML inference pipelines.

The tab is highlighted in this screenshot:
![ingest pipeline ent search ui](https://www.elastic.co/docs/solutions/images/elasticsearch-reference-ingest-pipeline-ent-search-ui.png)


## Overview

These tools can be particularly helpful by providing a layer of customization and post-processing of documents. For example:
- providing consistent extraction of text from binary data types
- ensuring consistent formatting
- providing consistent sanitization steps (removing PII like phone numbers or SSN’s)

It can be a lot of work to set up and manage production-ready pipelines from scratch. Considerations such as error handling, conditional execution, sequencing, versioning, and modularization must all be taken into account.
To this end, when you create indices for search use cases, (including web crawler, content connectors and API indices), each index already has a pipeline set up with several processors that optimize your content for search.
This pipeline is called `search-default-ingestion`. While it is a "managed" pipeline (meaning it should not be tampered with), you can view its details via the Kibana UI or the Elasticsearch API. You can also [read more about its contents below](#ingest-pipeline-search-details-generic-reference).
You can control whether you run some of these processors. While all features are enabled by default, they are eligible for opt-out. For [Elastic crawler](https://www.elastic.co/guide/en/enterprise-search/current/crawler.html) and [connectors](https://www.elastic.co/docs/reference/search-connectors). , you can opt out (or back in) per index, and your choices are saved. For API indices, you can opt out (or back in) by including specific fields in your documents. [See below for details](#ingest-pipeline-search-pipeline-settings-using-the-api).
At the deployment level, you can change the default settings for all new indices. This will not effect existing indices.
Each index also provides the capability to easily create index-specific ingest pipelines with customizable processing. If you need that extra flexibility, you can create a custom pipeline by going to your pipeline settings and choosing to "copy and customize". This will replace the index’s use of `search-default-ingestion` with 3 newly generated pipelines:
1. `<index-name>`
2. `<index-name>@custom`
3. `<index-name>@ml-inference`

Like `search-default-ingestion`, the first of these is "managed", but the other two can and should be modified to fit your needs. You can view these pipelines using the platform tools (Kibana UI, Elasticsearch API), and can also [read more about their content below](#ingest-pipeline-search-details-specific).

## Pipeline Settings

Aside from the pipeline itself, you have a few configuration options which control individual features of the pipelines.
- **Extract Binary Content** - This controls whether or not binary documents should be processed and any textual content should be extracted.
- **Reduce Whitespace** - This controls whether or not consecutive, leading, and trailing whitespaces should be removed. This can help to display more content in some search experiences.
- **Run ML Inference** - Only available on index-specific pipelines. This controls whether or not the optional `<index-name>@ml-inference` pipeline will be run. Enabled by default.

For Elastic web crawler and connectors, you can opt in or out per index. These settings are stored in Elasticsearch in the `.elastic-connectors` index, in the document that corresponds to the specific index. These settings can be changed there directly, or through the Kibana UI at **Search > Content > Indices > <your index> > Pipelines > Settings**.
You can also change the deployment wide defaults. These settings are stored in the Elasticsearch mapping for `.elastic-connectors` in the `_meta` section. These settings can be changed there directly, or from the Kibana UI at **Search > Content > Settings** tab. Changing the deployment wide defaults will not impact any existing indices, but will only impact any newly created indices defaults. Those defaults will still be able to be overridden by the index-specific settings.

### Using the API

These settings are not persisted for indices that "Use the API". Instead, changing these settings will, in real time, change the example cURL request displayed. Notice that the example document in the cURL request contains three underscore-prefixed fields:
```js
{
  ...
  "_extract_binary_content": true,
  "_reduce_whitespace": true,
  "_run_ml_inference": true
}
```

Omitting one of these special fields is the same as specifying it with the value `false`.
<note>
  You must also specify the pipeline in your indexing request. This is also shown in the example cURL request.
</note>

<warning>
  If the pipeline is not specified, the underscore-prefixed fields will actually be indexed, and will not impact any processing behaviors.
</warning>


## Details


### `search-default-ingestion` Reference

You can access this pipeline with the [Elasticsearch Ingest Pipelines API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-ingest-get-pipeline) or via Kibana’s [Stack Management > Ingest Pipelines](/docs/manage-data/ingest/transform-enrich/ingest-pipelines#create-manage-ingest-pipelines) UI.
<warning>
  This pipeline is a "managed" pipeline. That means that it is not intended to be edited. Editing/updating this pipeline manually could result in unintended behaviors, or difficulty in upgrading in the future. If you want to make customizations, we recommend you utilize index-specific pipelines (see below), specifically [the `<index-name>@custom` pipeline](#ingest-pipeline-search-details-specific-custom-reference).
</warning>


#### Processors

1. `attachment` - this uses the [Attachment](https://www.elastic.co/docs/reference/enrich-processor/attachment) processor to convert any binary data stored in a document’s `_attachment` field to a nested object of plain text and metadata.
2. `set_body` - this uses the [Set](https://www.elastic.co/docs/reference/enrich-processor/set-processor) processor to copy any plain text extracted from the previous step and persist it on the document in the `body` field.
3. `remove_replacement_chars` - this uses the [Gsub](https://www.elastic.co/docs/reference/enrich-processor/gsub-processor) processor to remove characters like "�" from the `body` field.
4. `remove_extra_whitespace` - this uses the [Gsub](https://www.elastic.co/docs/reference/enrich-processor/gsub-processor) processor to replace consecutive whitespace characters with single spaces in the `body` field. While not perfect for every use case (see below for how to disable), this can ensure that search experiences display more content and highlighting and less empty space for your search results.
5. `trim` - this uses the [Trim](https://www.elastic.co/docs/reference/enrich-processor/trim-processor) processor to remove any remaining leading or trailing whitespace from the `body` field.
6. `remove_meta_fields` - this final step of the pipeline uses the [Remove](https://www.elastic.co/docs/reference/enrich-processor/remove-processor) processor to remove special fields that may have been used elsewhere in the pipeline, whether as temporary storage or as control flow parameters.


#### Control flow parameters

The `search-default-ingestion` pipeline does not always run all processors. It utilizes a feature of ingest pipelines to [conditionally run processors](/docs/manage-data/ingest/transform-enrich/ingest-pipelines#conditionally-run-processor) based on the contents of each individual document.
- `_extract_binary_content` - if this field is present and has a value of `true` on a source document, the pipeline will attempt to run the `attachment`, `set_body`, and `remove_replacement_chars` processors. Note that the document will also need an `_attachment` field populated with base64-encoded binary data in order for the `attachment` processor to have any output. If the `_extract_binary_content` field is missing or `false` on a source document, these processors will be skipped.
- `_reduce_whitespace` - if this field is present and has a value of `true` on a source document, the pipeline will attempt to run the `remove_extra_whitespace` and `trim` processors. These processors only apply to the `body` field. If the `_reduce_whitespace` field is missing or `false` on a source document, these processors will be skipped.

Crawler, Native Connectors, and Connector Clients will automatically add these control flow parameters based on the settings in the index’s Pipeline tab. To control what settings any new indices will have upon creation, see the deployment wide content settings. See [Pipeline Settings](#ingest-pipeline-search-pipeline-settings).

### Index-specific ingest pipelines

In the Kibana UI for your index, by clicking on the Pipelines tab, then **Settings > Copy and customize**, you can quickly generate 3 pipelines which are specific to your index. These 3 pipelines replace `search-default-ingestion` for the index. There is nothing lost in this action, as the `<index-name>` pipeline is a superset of functionality over the `search-default-ingestion` pipeline.
<important>
  The "copy and customize" button is not available at all Elastic subscription levels. Refer to the Elastic subscriptions pages for [Elastic Cloud](https://www.elastic.co/subscriptions/cloud) and [self-managed](https://www.elastic.co/subscriptions) deployments.
</important>


#### `<index-name>` Reference

This pipeline looks and behaves a lot like the [`search-default-ingestion` pipeline](#ingest-pipeline-search-details-generic-reference), but with [two additional processors](#ingest-pipeline-search-details-specific-reference-processors).
<warning>
  You should not rename this pipeline.
</warning>

<warning>
  This pipeline is a "managed" pipeline. That means that it is not intended to be edited. Editing/updating this pipeline manually could result in unintended behaviors, or difficulty in upgrading in the future. If you want to make customizations, we recommend you utilize [the `<index-name>@custom` pipeline](#ingest-pipeline-search-details-specific-custom-reference).
</warning>


##### Processors

In addition to the processors inherited from the [`search-default-ingestion` pipeline](#ingest-pipeline-search-details-generic-reference), the index-specific pipeline also defines:
- `index_ml_inference_pipeline` - this uses the [Pipeline](https://www.elastic.co/docs/reference/enrich-processor/pipeline-processor) processor to run the `<index-name>@ml-inference` pipeline. This processor will only be run if the source document includes a `_run_ml_inference` field with the value `true`.
- `index_custom_pipeline` - this uses the [Pipeline](https://www.elastic.co/docs/reference/enrich-processor/pipeline-processor) processor to run the `<index-name>@custom` pipeline.


##### Control flow parameters

Like the `search-default-ingestion` pipeline, the `<index-name>` pipeline does not always run all processors. In addition to the `_extract_binary_content` and `_reduce_whitespace` control flow parameters, the `<index-name>` pipeline also supports:
- `_run_ml_inference` - if this field is present and has a value of `true` on a source document, the pipeline will attempt to run the `index_ml_inference_pipeline` processor. If the `_run_ml_inference` field is missing or `false` on a source document, this processor will be skipped.

Crawler, Native Connectors, and Connector Clients will automatically add these control flow parameters based on the settings in the index’s Pipeline tab. To control what settings any new indices will have upon creation, see the deployment wide content settings. See [Pipeline Settings](#ingest-pipeline-search-pipeline-settings).

#### `<index-name>@ml-inference` Reference

This pipeline is empty to start (no processors), but can be added to via the Kibana UI either through the Pipelines tab of your index, or from the **Stack Management > Ingest Pipelines** page. Unlike the `search-default-ingestion` pipeline and the `<index-name>` pipeline, this pipeline is NOT "managed".
It’s possible to add one or more ML inference pipelines to an index in the **Content** UI. This pipeline will serve as a container for all of the ML inference pipelines configured for the index. Each ML inference pipeline added to the index is referenced within `<index-name>@ml-inference` using a `pipeline` processor.
<warning>
  You should not rename this pipeline.
</warning>

<note>
  The `monitor_ml` Elasticsearch cluster permission is required in order to manage ML models and ML inference pipelines which use those models.
</note>


#### `<index-name>@custom` Reference

This pipeline is empty to start (no processors), but can be added to via the Kibana UI either through the Pipelines tab of your index, or from the **Stack Management > Ingest Pipelines** page. Unlike the `search-default-ingestion` pipeline and the `<index-name>` pipeline, this pipeline is NOT "managed".
You are encouraged to make additions and edits to this pipeline, provided its name remains the same. This provides a convenient hook from which to add custom processing and transformations for your data. Be sure to read the [docs for ingest pipelines](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines) to see what options are available.
<warning>
  You should not rename this pipeline.
</warning>


## Upgrading notes

<dropdown title="Expand to see upgrading notes">

  - `app_search_crawler` - Since 8.3, App Search web crawler has utilized this pipeline to power its binary content extraction. You can read more about this pipeline and its usage in the [App Search Guide](https://www.elastic.co/guide/en/app-search/current/web-crawler-reference.html#web-crawler-reference-binary-content-extraction). When upgrading from 8.3 to 8.5+, be sure to note any changes that you made to the `app_search_crawler` pipeline. These changes should be re-applied to each index’s `<index-name>@custom` pipeline in order to ensure a consistent data processing experience. In 8.5+, the [index setting to enable binary content](#ingest-pipeline-search-pipeline-settings) is required **in addition** to the configurations mentioned in the [App Search Guide](https://www.elastic.co/guide/en/app-search/current/web-crawler-reference.html#web-crawler-reference-binary-content-extraction).
  - `ent_search_crawler` - Since 8.4, the Elastic web crawler has utilized this pipeline to power its binary content extraction. You can read more about this pipeline and its usage in the [Elastic web crawler Guide](https://www.elastic.co/guide/en/enterprise-search/current/crawler-managing.html#crawler-managing-binary-content). When upgrading from 8.4 to 8.5+, be sure to note any changes that you made to the `ent_search_crawler` pipeline. These changes should be re-applied to each index’s `<index-name>@custom` pipeline in order to ensure a consistent data processing experience. In 8.5+, the [index setting to enable binary content](#ingest-pipeline-search-pipeline-settings) is required **in addition** to the configurations mentioned in the [Elastic web crawler Guide](https://www.elastic.co/guide/en/enterprise-search/current/crawler-managing.html#crawler-managing-binary-content).
  - `ent-search-generic-ingestion` - Since 8.5, Native Connectors, Connector Clients, and new (>8.4) Elastic web crawler indices all made use of this pipeline by default. This pipeline evolved into the `search-default-ingestion` pipeline.
  - `search-default-ingestion` - Since 9.0, Connectors have made use of this pipeline by default. You can [read more about this pipeline](#ingest-pipeline-search-details-generic-reference) above. As this pipeline is "managed", any modifications that were made to `app_search_crawler` and/or `ent_search_crawler` should NOT be made to `search-default-ingestion`. Instead, if such customizations are desired, you should utilize [Index-specific ingest pipelines](#ingest-pipeline-search-details-specific), placing all modifications in the `<index-name>@custom` pipeline(s).
</dropdown>