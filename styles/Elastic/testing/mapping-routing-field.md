# _routing field
A document is routed to a particular shard in an index using the following formulas:
```
routing_factor = num_routing_shards / num_primary_shards
shard_num = (hash(_routing) % num_routing_shards) / routing_factor
```

`num_routing_shards` is the value of the [`index.number_of_routing_shards`](/docs/reference/elasticsearch/index-settings/index-modules#index-number-of-routing-shards) index setting. `num_primary_shards` is the value of the [`index.number_of_shards`](/docs/reference/elasticsearch/index-settings/index-modules#index-number-of-shards) index setting.
The default `_routing` value is the document’s [`_id`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/mapping-id-field). Custom routing patterns can be implemented by specifying a custom `routing` value per document. For instance:
```json

{
  "title": "This is a document"
}
```

The value of the `_routing` field is accessible in queries:
```json

{
  "query": {
    "terms": {
      "_routing": [ "user1" ] <1>
    }
  }
}
```

<note>
  Data streams do not support custom routing unless they were created with the [`allow_custom_routing`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-put-index-template) setting enabled in the template.
</note>


## Searching with custom routing

Custom routing can reduce the impact of searches. Instead of having to fan out a search request to all the shards in an index, the request can be sent to just the shard that matches the specific routing value (or values):
```json

{
  "query": {
    "match": {
      "title": "document"
    }
  }
}
```


## Making a routing value required

When using custom routing, it is important to provide the routing value whenever [indexing](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-create), [getting](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-get), [deleting](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-delete), or [updating](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-update) a document.
Forgetting the routing value can lead to a document being indexed on more than one shard. As a safeguard, the `_routing` field can be configured to make a custom `routing` value required for all CRUD operations:
```json

{
  "mappings": {
    "_routing": {
      "required": true <1>
    }
  }
}


{
  "text": "No routing value provided"
}
```


## Unique IDs with custom routing

When indexing documents specifying a custom `_routing`, the uniqueness of the `_id` is not guaranteed across all of the shards in the index. In fact, documents with the same `_id` might end up on different shards if indexed with different `_routing` values.
It is up to the user to ensure that IDs are unique across the index.

## Routing to an index partition

An index can be configured such that custom routing values will go to a subset of the shards rather than a single shard. This helps mitigate the risk of ending up with an imbalanced cluster while still reducing the impact of searches.
This is done by providing the index level setting [`index.routing_partition_size`](/docs/reference/elasticsearch/index-settings/index-modules#routing-partition-size) at index creation. As the partition size increases, the more evenly distributed the data will become at the expense of having to search more shards per request.
When this setting is present, the formulas for calculating the shard become:
```
routing_value = hash(_routing) + hash(_id) % routing_partition_size
shard_num = (routing_value % num_routing_shards) / routing_factor
```

That is, the `_routing` field is used to calculate a set of shards within the index and then the `_id` is used to pick a shard within that set.
To enable this feature, the `index.routing_partition_size` should have a value greater than 1 and less than `index.number_of_shards`.
Once enabled, the partitioned index will have the following limitations:
- Mappings with [`join` field](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/parent-join) relationships cannot be created within it.
- All mappings within the index must have the `_routing` field marked as required.