# Code blocks

The docs say "do not modify the file", then continue.

Example `app_mention` body:

```json
{
  "type": "event_callback",
  "event": {
    "type": "app_mention",
    "text": "hello there"
  }
}
```

Set `"type": "event_callback",` in the request body.

::::{dropdown} Create this chart using the API
:applies_to: { stack: "ga 9.5+, preview =9.4", serverless: ga }

Set to `0` to skip the recovering phase.
::::
