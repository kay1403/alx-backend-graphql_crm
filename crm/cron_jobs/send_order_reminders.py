#!/usr/bin/env python3
import requests
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=False)

seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()
query = gql("""
query {
  orders(orderDate_Gte: "%s") {
    id
    customer {
      email
    }
  }
}
""" % seven_days_ago)

response = client.execute(query)
with open("/tmp/order_reminders_log.txt", "a") as log:
    for order in response["orders"]:
        log.write(f"{datetime.datetime.now()} - Order {order['id']} - Email: {order['customer']['email']}\n")

print("Order reminders processed!")
