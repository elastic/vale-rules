---
title: Get started with Query DSL search and filters
description: This is a hands-on introduction to the basics of full-text search with Elasticsearch, also known as lexical search, using the _search API and Query DSL...
url: https://www.elastic.co/docs/reference/query-languages/query-dsl/full-text-filter-tutorial
products:
  - Elasticsearch
---

% URL: https://www.elastic.co/docs/reference/query-languages/query-dsl/full-text-filter-tutorial

# Get started with Query DSL search and filters

This is a hands-on introduction to the basics of full-text search with Elasticsearch, also known as *lexical search*, using the `_search` API and Query DSL.
In this tutorial, you'll implement a search function for a cooking blog and learn how to filter data to narrow down search results based on exact criteria.
The blog contains recipes with various attributes including textual content, categorical data, and numerical ratings.
The goal is to create search queries to:
- Find recipes based on preferred or avoided ingredients
- Explore dishes that meet specific dietary needs
- Find top-rated recipes in specific categories
- Find the latest recipes from favorite authors

To achieve these goals, you'll use different Elasticsearch queries to perform full-text search, apply filters, and combine multiple search criteria.
<tip>
  The code examples are in [Console](https://www.elastic.co/docs/explore-analyze/query-filter/tools/console) syntax by default.
  You can [convert into other programming languages](https://www.elastic.co/docs/explore-analyze/query-filter/tools/console#import-export-console-requests) in the Console UI.
</tip>


## Requirements

You can follow these steps in any type of Elasticsearch deployment.
To see all deployment options, refer to [Choosing your deployment type](https://www.elastic.co/docs/deploy-manage/deploy#choosing-your-deployment-type).
To get started quickly, set up a [single-node local cluster in Docker](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart).

## Create an index

Create the `cooking_blog` index to get started:
```json
```

Next, define the mappings for the index:
```json

{
  "properties": {
    "title": {
      "type": "text",
      "analyzer": "standard", 
      "fields": { 
        "keyword": {
          "type": "keyword",
          "ignore_above": 256 
        }
      }
    },
    "description": { 
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "author": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "date": {
      "type": "date",
      "format": "yyyy-MM-dd"
    },
    "category": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "tags": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "rating": {
      "type": "float"
    }
  }
}
```

<tip>
  Full-text search is powered by [text analysis](https://www.elastic.co/docs/solutions/search/full-text/text-analysis-during-search). Text analysis normalizes and standardizes text data so it can be efficiently stored in an inverted index and searched in near real-time. Analysis happens at both [index and search time](https://www.elastic.co/docs/manage-data/data-store/text-analysis/index-search-analysis). This tutorial won't cover analysis in detail, but it's important to understand how text is processed to create effective search queries.
</tip>


## Add sample blog posts to your index

Next, index some example blog posts using the [bulk API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk). Note that `text` fields are analyzed and multi-fields are generated at index time.
```json

{"index":{"_id":"1"}}
{"title":"Perfect Pancakes: A Fluffy Breakfast Delight","description":"Learn the secrets to making the fluffiest pancakes, so amazing you won't believe your tastebuds. This recipe uses buttermilk and a special folding technique to create light, airy pancakes that are perfect for lazy Sunday mornings.","author":"Maria Rodriguez","date":"2023-05-01","category":"Breakfast","tags":["pancakes","breakfast","easy recipes"],"rating":4.8}
{"index":{"_id":"2"}}
{"title":"Spicy Thai Green Curry: A Vegetarian Adventure","description":"Dive into the flavors of Thailand with this vibrant green curry. Packed with vegetables and aromatic herbs, this dish is both healthy and satisfying. Don't worry about the heat - you can easily adjust the spice level to your liking.","author":"Liam Chen","date":"2023-05-05","category":"Main Course","tags":["thai","vegetarian","curry","spicy"],"rating":4.6}
{"index":{"_id":"3"}}
{"title":"Classic Beef Stroganoff: A Creamy Comfort Food","description":"Indulge in this rich and creamy beef stroganoff. Tender strips of beef in a savory mushroom sauce, served over a bed of egg noodles. It's the ultimate comfort food for chilly evenings.","author":"Emma Watson","date":"2023-05-10","category":"Main Course","tags":["beef","pasta","comfort food"],"rating":4.7}
{"index":{"_id":"4"}}
{"title":"Vegan Chocolate Avocado Mousse","description":"Discover the magic of avocado in this rich, vegan chocolate mousse. Creamy, indulgent, and secretly healthy, it's the perfect guilt-free dessert for chocolate lovers.","author":"Alex Green","date":"2023-05-15","category":"Dessert","tags":["vegan","chocolate","avocado","healthy dessert"],"rating":4.5}
{"index":{"_id":"5"}}
{"title":"Crispy Oven-Fried Chicken","description":"Get that perfect crunch without the deep fryer! This oven-fried chicken recipe delivers crispy, juicy results every time. A healthier take on the classic comfort food.","author":"Maria Rodriguez","date":"2023-05-20","category":"Main Course","tags":["chicken","oven-fried","healthy"],"rating":4.9}
```


## Perform basic full-text searches

Full-text search involves executing text-based queries across one or more document fields. These queries calculate a relevance score for each matching document, based on how closely the document's content aligns with the search terms. Elasticsearch offers various query types, each with its own method for matching text and [relevance scoring](https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl#relevance-scores).

### Use `match` query

The [`match`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query) query is the standard query for full-text search. The query text will be analyzed according to the analyzer configuration specified on each field (or at query time).
First, search the `description` field for "fluffy pancakes":
```json

{
  "query": {
    "match": {
      "description": {
        "query": "fluffy pancakes" 
      }
    }
  }
}
```

At search time, Elasticsearch defaults to the analyzer defined in the field mapping. This example uses the `standard` analyzer. Using a different analyzer at search time is an [advanced use case](https://www.elastic.co/docs/manage-data/data-store/text-analysis/index-search-analysis#different-analyzers).
<dropdown title="Example response">

  ```json
  {
    "took": 0,
    "timed_out": false,
    "_shards": {
      "total": 1,
      "successful": 1,
      "skipped": 0,
      "failed": 0
    },
    "hits": { 
      "total": {
        "value": 1,
        "relation": "eq"
      },
      "max_score": 1.8378843, 
      "hits": [
        {
          "_index": "cooking_blog",
          "_id": "1",
          "_score": 1.8378843, 
          "_source": {
            "title": "Perfect Pancakes: A Fluffy Breakfast Delight", 
            "description": "Learn the secrets to making the fluffiest pancakes, so amazing you won't believe your tastebuds. This recipe uses buttermilk and a special folding technique to create light, airy pancakes that are perfect for lazy Sunday mornings.", 
            "author": "Maria Rodriguez",
            "date": "2023-05-01",
            "category": "Breakfast",
            "tags": [
              "pancakes",
              "breakfast",
              "easy recipes"
            ],
            "rating": 4.8
          }
        }
      ]
    }
  }
  ```
</dropdown>


### Include all terms match in a query

Specify the `and` operator to include both terms in the `description` field.
This stricter search returns *zero hits* on the sample data because no documents contain both "fluffy" and "pancakes" in the description.
```json

{
  "query": {
    "match": {
      "description": {
        "query": "fluffy pancakes",
        "operator": "and"
      }
    }
  }
}
```

<dropdown title="Example response">

  ```json
  {
    "took": 0,
    "timed_out": false,
    "_shards": {
      "total": 1,
      "successful": 1,
      "skipped": 0,
      "failed": 0
    },
    "hits": {
      "total": {
        "value": 0,
        "relation": "eq"
      },
      "max_score": null,
      "hits": []
    }
  }
  ```
</dropdown>


### Specify a minimum number of terms to match

Use the [`minimum_should_match`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-minimum-should-match) parameter to specify the minimum number of terms a document should have to be included in the search results.
Search the title field to match at least 2 of the 3 terms: "fluffy", "pancakes", or "breakfast". This is useful for improving relevance while allowing some flexibility.
```json

{
  "query": {
    "match": {
      "title": {
        "query": "fluffy pancakes breakfast",
        "minimum_should_match": 2
      }
    }
  }
}
```


## Search across multiple fields

When you enter a search query, you might not know whether the search terms appear in a specific field.
A [`multi_match`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query) query enables you to search across multiple fields simultaneously.
Start with a basic `multi_match` query:
```json

{
  "query": {
    "multi_match": {
      "query": "vegetarian curry",
      "fields": ["title", "description", "tags"]
    }
  }
}
```

This query searches for "vegetarian curry" across the title, description, and tags fields. Each field is treated with equal importance.
However, in many cases, matches in certain fields (like the title) might be more relevant than others.
You can adjust the importance of each field using field boosting:
```json

{
  "query": {
    "multi_match": {
      "query": "vegetarian curry",
      "fields": ["title^3", "description^2", "tags"] 
    }
  }
}
```

- `title^3`: The title field is 3 times more important than an unboosted field.
- `description^2`: The description is 2 times more important.
- `tags`: No boost applied (equivalent to `^1`).

These boosts help tune relevance, prioritizing matches in the title over the description and matches in the description over tags.
Learn more about fields and per-field boosting in the [`multi_match` query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query) reference.
<dropdown title="Example response">

  ```json
  {
    "took": 0,
    "timed_out": false,
    "_shards": {
      "total": 1,
      "successful": 1,
      "skipped": 0,
      "failed": 0
    },
    "hits": {
      "total": {
        "value": 1,
        "relation": "eq"
      },
      "max_score": 7.546015,
      "hits": [
        {
          "_index": "cooking_blog",
          "_id": "2",
          "_score": 7.546015,
          "_source": {
            "title": "Spicy Thai Green Curry: A Vegetarian Adventure", 
            "description": "Dive into the flavors of Thailand with this vibrant green curry. Packed with vegetables and aromatic herbs, this dish is both healthy and satisfying. Don't worry about the heat - you can easily adjust the spice level to your liking.", 
            "author": "Liam Chen",
            "date": "2023-05-05",
            "category": "Main Course",
            "tags": [
              "thai",
              "vegetarian",
              "curry",
              "spicy"
            ], 
            "rating": 4.6
          }
        }
      ]
    }
  }
  ```
  This result demonstrates how the `multi_match` query with field boosts helps you find relevant recipes across multiple fields.
  Even though the exact phrase "vegetarian curry" doesn't appear in any single field, the combination of matches across fields produces a highly relevant result.
</dropdown>

<tip>
  The `multi_match` query is often recommended over a single `match` query for most text search use cases because it provides more flexibility and better matches user expectations.
</tip>


## Filter and find exact matches

[Filtering](https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl#filter-context) enables you to narrow down your search results based on exact criteria. Unlike full-text searches, filters are binary (yes or no) and do not affect the relevance score. Filters run faster than queries because excluded results don't need to be scored.
The following [`bool`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query) query will return blog posts only in the "Breakfast" category.
```json

{
  "query": {
    "bool": {
      "filter": [
        { "term": { "category.keyword": "Breakfast" } }  
      ]
    }
  }
}
```

<tip>
  The `.keyword` suffix accesses the unanalyzed version of a field, enabling exact, case-sensitive matching. This works in two scenarios:
  1. When using dynamic mapping for text fields. Elasticsearch automatically creates a `.keyword` sub-field.
  2. When text fields are explicitly mapped with a `.keyword` sub-field. For example, you explicitly mapped the `category` field when you defined the mappings for the `cooking_blog` index.
</tip>


### Search within a date range

To find content published within a specific time frame, use a [`range`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-range-query) query.
It finds documents that fall within numeric or date ranges.
```json

{
  "query": {
    "range": {
      "date": {
        "gte": "2023-05-01", 
        "lte": "2023-05-31" 
      }
    }
  }
}
```


### Find exact matches

Sometimes you might want to search for exact terms to eliminate ambiguity in the search results. A [`term`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-term-query) query searches for an exact term in a field without analyzing it. Exact, case-sensitive matches on specific terms are often referred to as "keyword" searches.
In the following example, you'll search for the author "Maria Rodriguez" in the `author.keyword` field.
```json

{
  "query": {
    "term": {
      "author.keyword": "Maria Rodriguez" 
    }
  }
}
```

<tip>
  Avoid using the `term` query for `text` fields because they are transformed by the analysis process.
</tip>


## Combine multiple search criteria

You can use a [`bool`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query) query to combine multiple query clauses and create sophisticated searches.
For example, create a query that addresses the following requirements:
- Must be a vegetarian recipe
- Should contain "curry" or "spicy" in the title or description
- Should be a main course
- Must not be a dessert
- Must have a rating of at least 4.5
- Should prefer recipes published in the last month

```json

{
  "query": {
    "bool": {
      "must": [
        { "term": { "tags": "vegetarian" } },
        {
          "range": {
            "rating": {
              "gte": 4.5
            }
          }
        }
      ],
      "should": [
        {
          "term": {
            "category": "Main Course"
          }
        },
        {
          "multi_match": {
            "query": "curry spicy",
            "fields": [
              "title^2",
              "description"
            ]
          }
        },
        {
          "range": {
            "date": {
              "gte": "now-1M/d"
            }
          }
        }
      ],
      "must_not": [ 
        {
          "term": {
            "category.keyword": "Dessert"
          }
        }
      ]
    }
  }
}
```

<dropdown title="Example response">

  ```json
  {
    "took": 1,
    "timed_out": false,
    "_shards": {
      "total": 1,
      "successful": 1,
      "skipped": 0,
      "failed": 0
    },
    "hits": {
      "total": {
        "value": 1,
        "relation": "eq"
      },
      "max_score": 7.444513,
      "hits": [
        {
          "_index": "cooking_blog",
          "_id": "2",
          "_score": 7.444513,
          "_source": {
            "title": "Spicy Thai Green Curry: A Vegetarian Adventure", 
            "description": "Dive into the flavors of Thailand with this vibrant green curry. Packed with vegetables and aromatic herbs, this dish is both healthy and satisfying. Don't worry about the heat - you can easily adjust the spice level to your liking.", 
            "author": "Liam Chen",
            "date": "2023-05-05",
            "category": "Main Course", 
            "tags": [ 
              "thai",
              "vegetarian", 
              "curry",
              "spicy"
            ],
            "rating": 4.6 
          }
        }
      ]
    }
  }
  ```
</dropdown>


## Learn more

This tutorial introduced the basics of full-text search and filtering in Elasticsearch.
Building a real-world search experience requires understanding many more advanced concepts and techniques.
The following resources will help you dive deeper:
- [Full-text search](https://www.elastic.co/docs/solutions/search/full-text): Learn about the core components of full-text search in Elasticsearch.
- [Elasticsearch basics — Search and analyze data](https://www.elastic.co/docs/explore-analyze/query-filter): Understand all your options for searching and analyzing data in Elasticsearch.
- [Text analysis](https://www.elastic.co/docs/solutions/search/full-text/text-analysis-during-search): Understand how text is processed for full-text search.
- [Search your data](https://www.elastic.co/docs/solutions/search): Learn about more advanced search techniques using the `_search` API, including semantic search.