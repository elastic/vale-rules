---
title: Append processor
description: Appends one or more values to an existing array if the field already exists and it is an array. Converts a scalar to an array and appends one or more...
url: https://www.elastic.co/docs/reference/enrich-processor/append-processor
---

# Append processor
Appends one or more values to an existing array if the field already exists and it is an array. Converts a scalar to an array and appends one or more values to it if the field exists and it is a scalar. Creates an array containing the provided values if the field doesn’t exist. Accepts a single value or an array of values.


| Name                                                                                        | Required | Default            | Description                                                                                                                                                                                                                                                                         |
|---------------------------------------------------------------------------------------------|----------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `field`                                                                                     | yes      | -                  | The field to be appended to. Supports [template snippets](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines#template-snippets).                                                                                                                      |
| `value`                                                                                     | yes*     | -                  | The value to be appended. Supports [template snippets](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines#template-snippets). May specify only one of `value` or `copy_from`.                                                                         |
| `copy_from` <applies-to>Elastic Stack: Generally available since 9.2</applies-to>           | no       | -                  | The origin field which will be appended to `field`, cannot set `value` simultaneously.                                                                                                                                                                                              |
| `allow_duplicates`                                                                          | no       | true               | If `false`, the processor does not appendvalues already present in the field.                                                                                                                                                                                                       |
| `ignore_empty_values` <applies-to>Elastic Stack: Generally available since 9.2</applies-to> | no       | false              | If `true`, the processor does not append values that resolve to `null` or an empty string.                                                                                                                                                                                          |
| `media_type`                                                                                | no       | `application/json` | The media type for encoding `value`. Applies only when `value` is a [template snippet](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines#template-snippets). Must be one of `application/json`, `text/plain`, or`application/x-www-form-urlencoded`. |
| `description`                                                                               | no       | -                  | Description of the processor. Useful for describing the purpose of the processor or its configuration.                                                                                                                                                                              |
| `if`                                                                                        | no       | -                  | Conditionally execute the processor. See [Conditionally run a processor](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines#conditionally-run-processor).                                                                                             |
| `ignore_failure`                                                                            | no       | `false`            | Ignore failures for the processor. See [Handling pipeline failures](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines#handling-pipeline-failures).                                                                                                   |
| `on_failure`                                                                                | no       | -                  | Handle failures for the processor. See [Handling pipeline failures](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines#handling-pipeline-failures).                                                                                                   |
| `tag`                                                                                       | no       | -                  | Identifier for the processor. Useful for debugging and metrics.                                                                                                                                                                                                                     |


## Examples


### Simple example

Here is an `append` processor definition that adds the string `"production"` as well as the values of the `app` and `owner` fields to the `tags` field:
```js
{
  "append": {
    "field": "tags",
    "value": ["production", "{{{app}}}", "{{{owner}}}"]
  }
}
```


### Example using `allow_duplicates` and `ignore_empty_values`

<applies-to>
  - Elastic Stack: Generally available since 9.2
</applies-to>

By using `allow_duplicates` and `ignore_empty_values`, it is possible to only append the `host.name` to the `related.hosts` if the `host.name` is not empty and if the value is not already present in `related.hosts`:
```js
{
  "append": {
    "field": "related.hosts",
    "copy_from": "host.name",
    "allow_duplicates": false,
    "ignore_empty_values": true
  }
}
```