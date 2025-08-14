# Python SDK Documentation

## Overview
The Python SDK for Spartera API provides a convenient way to interact with the Spartera platform from Python applications.

**Install:** `pip install spartera-api-sdk`

## Requirements
- Python 3.8 or higher
- pip package manager

## 🚀 Sell Your First Data Product in 4 API Calls

Transform your data into revenue in under 5 minutes! Here's how to create and sell a data product on the Spartera marketplace:

```python
import os
import json
from spartera_api_sdk import ApiClient, Configuration
from spartera_api_sdk.api import cloud_providers_api, connections_api, assets_api, asset_price_history_api

# Configure client
config = Configuration()
config.host = "https://api.spartera.com"
config.api_key = {'X-API-Key': 'your-api-key-here'}
client = ApiClient(config)

COMPANY_ID = "your-company-id"
USER_ID = "your-user-id"

# Step 1: Discover available data platforms
print("🔍 Step 1: Discovering available platforms...")
storage_api = cloud_providers_api.CloudProvidersApi(client)
engines = storage_api.cloud_providers_get()
bigquery_engine_id = 1  # BigQuery engine ID
print(f"✅ Found {len(engines)} supported platforms")

# Step 2: Create a data connection (with credentials in one call!)
print("🔗 Step 2: Creating BigQuery connection...")
connections_instance = connections_api.ConnectionsApi(client)

# Your BigQuery service account JSON (replace with your actual credentials)
service_account_json = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "your-service@your-project.iam.gserviceaccount.com",
    "client_id": "client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
}

connection_data = {
    "company_id": COMPANY_ID,
    "user_id": USER_ID,
    "engine_id": bigquery_engine_id,
    "name": "My BigQuery Data Warehouse",
    "description": "Connection to our company's analytics data",
    "visibility": "PRIVATE",
    "credential_type": "SERVICE_ACCOUNT",
    "credentials": json.dumps(service_account_json),
    "verified_usage_ability": True  # Legal compliance - you have rights to this data
}

connection = connections_instance.companies_company_id_connections_post(COMPANY_ID, connection_data)
connection_id = connection.connection_id
print(f"✅ Created connection: {connection_id}")

# Step 3: Create a marketplace asset
print("📊 Step 3: Creating marketplace asset...")
assets_instance = assets_api.AssetsApi(client)

asset_data = {
    "name": "Average Temperature Analytics",
    "description": "Real-time weather temperature analytics from our IoT sensors across major cities",
    "company_id": COMPANY_ID,
    "connection_id": connection_id,
    "asset_type": "CALCULATION",
    "sql_logic": "SELECT AVERAGE(temperature) AS avg_temp, city, COUNT(*) AS readings FROM `your-project.weather.sensor_data` WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR) GROUP BY city ORDER BY avg_temp DESC",
    "sell_in_marketplace": True,  # 🔥 This makes it available for purchase!
    "source": "MANUAL",
    "visibility": "PUBLIC"
}

asset = assets_instance.companies_company_id_assets_post(COMPANY_ID, asset_data)
asset_id = asset.asset_id
print(f"✅ Created marketplace asset: {asset_id}")

# Step 4: Set your price and start earning!
print("💰 Step 4: Setting price...")
pricing_instance = asset_price_history_api.AssetPriceHistoryApi(client)

price_data = {
    "price_usd": 2.00  # $2.00 per analysis (credits calculated automatically)
}

price = pricing_instance.companies_company_id_assets_asset_id_prices_post(COMPANY_ID, asset_id, price_data)
print(f"✅ Price set: ${price.price_usd} (≈{price.price_credits} credits)")

print("\n🎉 SUCCESS! Your data product is now live on the Spartera marketplace!")
print(f"📈 Asset URL: https://marketplace.spartera.com/assets/{asset_id}")
print("💡 Customers can now discover and purchase your analytics!")
```

**That's it!** You're now selling data analytics. Every time someone runs your analysis, you earn money! 

### 🎯 What You Just Built
- **Data Connection**: Secure link to your BigQuery warehouse
- **Analytics Product**: Temperature analysis that buyers can purchase
- **Marketplace Listing**: Your product is discoverable by thousands of potential customers
- **Automated Pricing**: Credits are calculated automatically based on your USD price

### 💰 Revenue Model
- You set the price ($2.00 in this example)
- Customers pay in credits (auto-converted)
- You earn revenue each time someone uses your analytics
- Spartera handles billing, payments, and customer support

---

## 📚 Detailed Documentation

### Authentication

Get your API key from the [Spartera Dashboard](https://app.spartera.com/settings/api-keys):

```python
import os
from spartera_api_sdk import ApiClient, Configuration

# Option 1: Direct configuration
config = Configuration()
config.host = "https://api.spartera.com"
config.api_key = {'X-API-Key': 'your-api-key-here'}

# Option 2: Environment variables (recommended)
os.environ['SPARTERA_API_KEY'] = "your-api-key"
os.environ['SPARTERA_COMPANY_ID'] = "your-company-id"

config = Configuration()
config.host = "https://api.spartera.com"
config.api_key = {'X-API-Key': os.getenv('SPARTERA_API_KEY')}

client = ApiClient(config)
```

### Environment Variables

```bash
export SPARTERA_API_KEY="your-api-key"
export SPARTERA_COMPANY_ID="your-company-id"
export SPARTERA_API_BASE_URL="https://api.spartera.com"
```

### Connection Types

Create connections to different data platforms:

```python
# BigQuery
bigquery_credentials = {
    "type": "service_account",
    "project_id": "your-project",
    # ... your service account JSON
}

# Snowflake
snowflake_connection = {
    "credential_type": "USERNAME_PASSWORD",
    "username": "your-username",
    "password": "your-password"
}

# API Data Source
api_connection = {
    "credential_type": "API_KEY",
    "api_endpoint": "https://api.yourcompany.com/data",
    "api_key_param": "x-api-key",
    "credentials": "your-api-key-value"
}
```

### Asset Types

Create different types of marketplace products:

```python
# SQL-based Analytics
calculation_asset = {
    "asset_type": "CALCULATION",
    "sql_logic": "SELECT COUNT(*) as total_sales, AVG(amount) as avg_order FROM sales WHERE date >= CURRENT_DATE()"
}

# Visualization/Dashboard
visualization_asset = {
    "asset_type": "VISUALIZATION", 
    "viz_chart_type": "BAR",
    "viz_dep_var_col_name": "sales_amount",
    "viz_indep_var_col_name": "month"
}
```

### Pricing Strategies

Set different pricing models:

```python
# Fixed price per analysis
basic_pricing = {"price_usd": 1.50}

# Premium analytics
premium_pricing = {"price_usd": 10.00}

# Bulk discount with sales
sale_pricing = {
    "price_usd": 5.00,
    "discount_percentage": 20.0,
    "sale_start_date": "2024-01-01T00:00:00Z",
    "sale_end_date": "2024-01-31T23:59:59Z"
}
```

### Marketplace Management

Manage your products after launch:

```python
# Update asset details
assets_instance.companies_company_id_assets_asset_id_patch(
    COMPANY_ID, 
    asset_id,
    {"description": "Updated description with new features"}
)

# Change pricing
new_price = {"price_usd": 3.00}
pricing_instance.companies_company_id_assets_asset_id_prices_post(
    COMPANY_ID, asset_id, new_price
)

# Remove from marketplace (but keep private)
assets_instance.companies_company_id_assets_asset_id_patch(
    COMPANY_ID,
    asset_id, 
    {"sell_in_marketplace": False}
)

# Get sales analytics
analytics = companies_instance.companies_company_id_analytics_sales_get(COMPANY_ID)
print(f"Total revenue: ${analytics.total_revenue}")
```

### Error Handling

```python
from spartera_api_sdk.exceptions import ApiException

try:
    asset = assets_instance.companies_company_id_assets_post(COMPANY_ID, asset_data)
except ApiException as e:
    print(f"API Error: {e}")
    print(f"Status: {e.status}")
    print(f"Reason: {e.reason}")
    
    # Handle specific errors
    if e.status == 400:
        print("Check your asset data format")
    elif e.status == 401:
        print("Check your API key")
    elif e.status == 403:
        print("Check your permissions")
```

### Advanced Features

```python
# Batch operations
connection_ids = []
for platform in ['bigquery', 'snowflake', 'redshift']:
    conn = connections_instance.companies_company_id_connections_post(COMPANY_ID, platform_config)
    connection_ids.append(conn.connection_id)

# Asset recommendations  
recommendations = assets_instance.companies_company_id_assets_asset_id_recommendations_get(
    COMPANY_ID, asset_id, limit=10
)

# Performance analytics
performance = companies_instance.companies_company_id_analytics_assets_get(
    COMPANY_ID, 
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Package Manager
- **Platform**: PyPI
- **Install**: `pip install spartera-api-sdk`
- **Import**: `from spartera_api_sdk import ApiClient`

## Publishing
1. Build: `python setup.py sdist bdist_wheel`
2. Upload: `twine upload dist/*`
3. Install: `pip install spartera-api-sdk`