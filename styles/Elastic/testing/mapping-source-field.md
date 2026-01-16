---
title: _source field
description: The _source field contains the original JSON document body that was passed at index time. The _source field itself is not indexed (and thus is not searchable),...
url: https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/mapping-source-field
applies_to:
  - Elastic Cloud Serverless: Generally available
  - Elastic Stack: Generally available in 9.0+
---

# _source field
The `_source` field contains the original JSON document body that was passed at index time. The `_source` field itself is not indexed (and thus is not searchable), but it is stored so that it can be returned when executing *fetch* requests, like [get](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-get) or [search](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search).
If disk usage is important to you, then consider the following options:
- Using [synthetic `_source`](#synthetic-source), which reconstructs source content at the time of retrieval instead of storing it on disk. This shrinks disk usage, at the cost of slower access to `_source` in [Get](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-get) and [Search](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search) queries.
- [Disabling the `_source` field completely](#disable-source-field). This shrinks disk usage but disables features that rely on `_source`.


## Synthetic `_source`

<note>
  This feature requires a [subscription](https://www.elastic.co/subscriptions).
</note>

Though very handy to have around, the source field takes up a significant amount of space on disk. Instead of storing source documents on disk exactly as you send them, Elasticsearch can reconstruct source content on the fly upon retrieval. To enable this feature, use the value `synthetic` for the index setting `index.mapping.source.mode`:

```json

{
  "settings": {
    "index": {
      "mapping": {
        "source": {
          "mode": "synthetic"
        }
      }
    }
  }
}
```

While this on-the-fly reconstruction is *generally* slower than saving the source documents verbatim and loading them at query time, it saves a lot of storage space. Additional latency can be avoided by not loading `_source` field in queries when it is not needed.

### Supported fields

Synthetic `_source` is supported by all field types. Depending on implementation details, field types have different properties when used with synthetic `_source`.
[Most field types](#synthetic-source-fields-native-list) construct synthetic `_source` using existing data, most commonly [`doc_values`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/doc-values) and [stored fields](/docs/reference/elasticsearch/rest-apis/retrieve-selected-fields#stored-fields). For these field types, no additional space is needed to store the contents of `_source` field. Due to the storage layout of [`doc_values`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/doc-values), the generated `_source` field undergoes [modifications](#synthetic-source-modifications) compared to the original document.
For all other field types, the original value of the field is stored as is, in the same way as the `_source` field in non-synthetic mode. In this case there are no modifications and field data in `_source` is the same as in the original document. Similarly, malformed values of fields that use [`ignore_malformed`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/ignore-malformed) or [`ignore_above`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/ignore-above) need to be stored as is. This approach is less storage efficient since data needed for `_source` reconstruction is stored in addition to other data required to index the field (like `doc_values`).

### Synthetic `_source` restrictions

Some field types have additional restrictions. These restrictions are documented in the **synthetic `_source`** section of the field type’s [documentation](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/field-data-types).
Synthetic source is not supported in [source-only](https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/source-only-repository) snapshot repositories. To store indices that use synthetic `_source`, choose a different repository type.

### Synthetic `_source` modifications

When synthetic `_source` is enabled, retrieved documents undergo some modifications compared to the original JSON.

#### Arrays moved to leaf fields

Synthetic `_source` arrays are moved to leaves. For example:

```json

{
  "foo": [
    {
      "bar": 1
    },
    {
      "bar": 2
    }
  ]
}
```

Will become:
```json
{
  "foo": {
    "bar": [1, 2]
  }
}
```

This can cause some arrays to vanish:

```json

{
  "foo": [
    {
      "bar": 1
    },
    {
      "baz": 2
    }
  ]
}
```

Will become:
```json
{
  "foo": {
    "bar": 1,
    "baz": 2
  }
}
```


#### Fields named as they are mapped

Synthetic source names fields as they are named in the mapping. When used with [dynamic mapping](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dynamic), fields with dots (`.`) in their names are, by default, interpreted as multiple objects, while dots in field names are preserved within objects that have [`subobjects`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/subobjects) disabled. For example:

```json

{
  "foo.bar.baz": 1
}
```

Will become:
```json
{
  "foo": {
    "bar": {
      "baz": 1
    }
  }
}
```

This impacts how source contents can be referenced in [scripts](https://www.elastic.co/docs/explore-analyze/scripting/modules-scripting-using). For instance, referencing a script in its original source form will return null:
```js
"script": { "source": """  emit(params._source['foo.bar.baz'])  """ }
```

Instead, source references need to be in line with the mapping structure:
```js
"script": { "source": """  emit(params._source['foo']['bar']['baz'])  """ }
```

or simply
```js
"script": { "source": """  emit(params._source.foo.bar.baz)  """ }
```

The following [field APIs](https://www.elastic.co/docs/explore-analyze/scripting/modules-scripting-fields) are preferable as, in addition to being agnostic to the mapping structure, they make use of docvalues if available and fall back to synthetic source only when needed. This reduces source synthesizing, a slow and costly operation.
```js
"script": { "source": """  emit(field('foo.bar.baz').get(null))   """ }
"script": { "source": """  emit($('foo.bar.baz', null))   """ }
```


#### Alphabetical sorting

Synthetic `_source` fields are sorted alphabetically. The [JSON RFC](https://www.rfc-editor.org/rfc/rfc7159.md) defines objects as "an unordered collection of zero or more name/value pairs" so applications shouldn’t care but without synthetic `_source` the original ordering is preserved and some applications may, counter to the spec, do something with that ordering.

#### Representation of ranges

Range field values (e.g. `long_range`) are always represented as inclusive on both sides with bounds adjusted accordingly. See [examples](/docs/reference/elasticsearch/mapping-reference/range#range-synthetic-source-inclusive).

#### Reduced precision of `geo_point` values

Values of `geo_point` fields are represented in synthetic `_source` with reduced precision. See [examples](/docs/reference/elasticsearch/mapping-reference/geo-point#geo-point-synthetic-source).

#### Minimizing source modifications

It is possible to avoid synthetic source modifications for a particular object or field, at extra storage cost. This is controlled through param `synthetic_source_keep` with the following option:
- `none`: synthetic source diverges from the original source as described above (default).
- `arrays`: arrays of the corresponding field or object preserve the original element ordering and duplicate elements. The synthetic source fragment for such arrays is not guaranteed to match the original source exactly, e.g. array `[1, 2, [5], [[4, [3]]], 5]` may appear as-is or in an equivalent format like `[1, 2, 5, 4, 3, 5]`. The exact format may change in the future, in an effort to reduce the storage overhead of this option.
- `all`: the source for both singleton instances and arrays of the corresponding field or object gets recorded. When applied to objects, the source of all sub-objects and sub-fields gets captured. Furthermore, the original source of arrays gets captured and appears in synthetic source with no modifications.

For instance:

```json

{
  "settings": {
    "index": {
      "mapping": {
        "source": {
          "mode": "synthetic"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "path": {
        "type": "object",
        "synthetic_source_keep": "all"
      },
      "ids": {
        "type": "integer",
        "synthetic_source_keep": "arrays"
      }
    }
  }
}
```


```json

{
  "path": {
    "to": [
      { "foo": [3, 2, 1] },
      { "foo": [30, 20, 10] }
    ],
    "bar": "baz"
  },
  "ids": [ 200, 100, 300, 100 ]
}
```

returns the original source, with no array deduplication and sorting:
```json
{
  "path": {
    "to": [
      { "foo": [3, 2, 1] },
      { "foo": [30, 20, 10] }
    ],
    "bar": "baz"
  },
  "ids": [ 200, 100, 300, 100 ]
}
```

The option for capturing the source of arrays can be applied at index level, by setting `index.mapping.synthetic_source_keep` to `arrays`. This applies to all objects and fields in the index, except for the ones with explicit overrides of `synthetic_source_keep` set to `none`. In this case, the storage overhead grows with the number and sizes of arrays present in source of each document, naturally.

### Field types that support synthetic source with no storage overhead

The following field types support synthetic source using data from [`doc_values`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/doc-values) or [stored fields](/docs/reference/elasticsearch/rest-apis/retrieve-selected-fields#stored-fields), and require no additional storage space to construct the `_source` field.
<note>
  If you enable the [`ignore_malformed`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/ignore-malformed) or [`ignore_above`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/ignore-above) settings, then additional storage is required to store ignored field values for these types.
</note>

- [`aggregate_metric_double`](/docs/reference/elasticsearch/mapping-reference/aggregate-metric-double#aggregate-metric-double-synthetic-source)
- [`annotated-text`](/docs/reference/elasticsearch/plugins/mapper-annotated-text-usage#annotated-text-synthetic-source)
- [`binary`](/docs/reference/elasticsearch/mapping-reference/binary#binary-synthetic-source)
- [`boolean`](/docs/reference/elasticsearch/mapping-reference/boolean#boolean-synthetic-source)
- [`byte`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`date`](/docs/reference/elasticsearch/mapping-reference/date#date-synthetic-source)
- [`date_nanos`](/docs/reference/elasticsearch/mapping-reference/date_nanos#date-nanos-synthetic-source)
- [`dense_vector`](/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-synthetic-source)
- [`double`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`flattened`](/docs/reference/elasticsearch/mapping-reference/flattened#flattened-synthetic-source)
- [`float`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`geo_point`](/docs/reference/elasticsearch/mapping-reference/geo-point#geo-point-synthetic-source)
- [`half_float`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`histogram`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/histogram)
- [`integer`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`ip`](/docs/reference/elasticsearch/mapping-reference/ip#ip-synthetic-source)
- [`keyword`](/docs/reference/elasticsearch/mapping-reference/keyword#keyword-synthetic-source)
- [`long`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`range` types](/docs/reference/elasticsearch/mapping-reference/range#range-synthetic-source)
- [`scaled_float`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`short`](/docs/reference/elasticsearch/mapping-reference/number#numeric-synthetic-source)
- [`text`](/docs/reference/elasticsearch/mapping-reference/text#text-synthetic-source)
- [`version`](/docs/reference/elasticsearch/mapping-reference/version#version-synthetic-source)
- [`wildcard`](/docs/reference/elasticsearch/mapping-reference/keyword#wildcard-synthetic-source)


## Disabling the `_source` field

Though very handy to have around, the source field does incur storage overhead within the index. For this reason, it can be disabled as follows:
```json

{
  "mappings": {
    "_source": {
      "enabled": false
    }
  }
}
```

<warning>
  Do not disable the `_source` field, unless absolutely necessary. If you disable it, the following critical features will not be supported:
  - The [`update`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-update), [`update_by_query`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-update-by-query), and [`reindex`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-reindex) APIs.
  - Display of field data in the Kibana [Discover](https://www.elastic.co/docs/explore-analyze/discover) application.
  - On the fly [highlighting](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/highlighting).
  - The ability to reindex from one Elasticsearch index to another, either to change mappings or analysis, or to upgrade an index to a new major version.
  - The ability to debug queries or aggregations by viewing the original document used at index time.
  - Potentially in the future, the ability to repair index corruption automatically.
</warning>

<note>
  You can't disable the `_source` field for indices with [`index_mode`](/docs/reference/elasticsearch/index-settings/index-modules#index-mode-setting) set to `logsdb` or `time_series`.
</note>

<tip>
  If disk space is a concern, rather increase the [compression level](/docs/reference/elasticsearch/index-settings/index-modules#index-codec) instead of disabling the `_source`.
</tip>


## Including / Excluding fields from `_source`

An expert-only feature is the ability to prune the contents of the `_source` field after the document has been indexed, but before the `_source` field is stored.
<warning>
  Removing fields from the `_source` has similar downsides to disabling `_source`, especially the fact that you cannot reindex documents from one Elasticsearch index to another. Consider using [source filtering](/docs/reference/elasticsearch/rest-apis/retrieve-selected-fields#source-filtering) instead.
</warning>

<note>
  Source pruning is not available in Serverless
</note>

The `includes`/`excludes` parameters (which also accept wildcards) can be used as follows:
```json

{
  "mappings": {
    "_source": {
      "includes": [
        "*.count",
        "meta.*"
      ],
      "excludes": [
        "meta.description",
        "meta.other.*"
      ]
    }
  }
}


{
  "requests": {
    "count": 10,
    "foo": "bar" <1>
  },
  "meta": {
    "name": "Some metric",
    "description": "Some metric description", <1>
    "other": {
      "foo": "one", <1>
      "baz": "two" <1>
    }
  }
}


{
  "query": {
    "match": {
      "meta.other.foo": "one" <2>
    }
  }
}
```