# redash_mini

A tiny Python client to run Redash queries and get fresh results.

## Example

```python
from redash_mini import RedashClient

client = RedashClient("https://redash.example.com", api_key="YOUR_API_KEY")
rows = client.get_fresh_query_result(123, {"param": "value"})
print(rows)
