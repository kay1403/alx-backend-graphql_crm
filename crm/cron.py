import datetime
import requests

def update_low_stock():
    mutation = """
    mutation {
      updateLowStockProducts {
        updatedProducts
        message
      }
    }
    """
    response = requests.post(
        "http://localhost:8000/graphql",
        json={"query": mutation},
        headers={"Content-Type": "application/json"}
    )
    data = response.json().get("data", {}).get("updateLowStockProducts", {})
    updated = data.get("updatedProducts", [])
    message = data.get("message", "No message returned")

    with open("/tmp/low_stock_updates_log.txt", "a") as log:
        log.write(f"{datetime.datetime.now()}: {message} - Updated: {', '.join(updated)}\n")
