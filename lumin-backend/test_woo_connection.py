"""
Quick script to test WooCommerce connection
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.integrations.models import WooCommerceConnection
from woocommerce import API

# Get connection
try:
    connection = WooCommerceConnection.objects.first()
    if not connection:
        print("[X] No WooCommerce connection found")
        exit()

    print(f"[OK] Found connection: {connection.store_url}")
    print(f"     Consumer Key: {connection.consumer_key[:20]}...")
    print(f"     Is Active: {connection.is_active}")

    # Create API instance
    wcapi = API(
        url=connection.store_url,
        consumer_key=connection.consumer_key,
        consumer_secret=connection.consumer_secret,
        version="wc/v3",
        timeout=30
    )

    print("\n[...] Fetching customers...")

    # Try to fetch customers
    response = wcapi.get("customers", params={"per_page": 10})

    print(f"     Status Code: {response.status_code}")

    if response.status_code == 200:
        customers = response.json()
        print(f"[OK] Success! Found {len(customers)} customers (first page)")
        print("\nCustomers:")
        for customer in customers[:5]:
            name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
            email = customer.get('email', 'no email')
            print(f"   - {name} ({email})")
    else:
        print(f"[X] Error: {response.status_code}")
        print(f"    Response: {response.text[:200]}")

except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
