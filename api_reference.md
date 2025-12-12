# Cian Parser API Reference

**Version:** 1.0.0

**Base URL:** `http://localhost:8000` (or your configured host)

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Root](#get-)
  - [Health Check](#get-health)
  - [Search Offers](#get-v1search)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

The Cian Parser API provides endpoints to search and retrieve real estate offers from Cian.ru with customizable filters for price, area, and property type.

The API is built with FastAPI and provides automatic interactive documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Endpoints

### `GET /`

Root endpoint providing basic API information.

**Response:**

```json
{
  "name": "Cian Parser API",
  "version": "1.0.0",
  "endpoints": {
    "GET /v1/search": "Search for offers with filters"
  }
}
```

**Status Codes:**
- `200 OK` - Success

---

### `GET /health`

Health check endpoint to verify API availability.

**Response:**

```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### `GET /v1/search`

Search for real estate offers with optional filters.

**Query Parameters:**

| Parameter   | Type    | Required | Description                          | Example      |
|-------------|---------|----------|--------------------------------------|--------------|
| `city`      | string  | Yes      | Search city for Cian                 | `Moscow`     |
| `price_gte` | string  | No       | Minimum price filter (in rubles)     | `1000000`    |
| `price_lte` | string  | No       | Maximum price filter (in rubles)     | `5000000`    |
| `area_gte`  | string  | No       | Minimum area in m²                   | `50`         |
| `area_lte`  | string  | No       | Maximum area in m²                   | `100`        |
| `sale`      | boolean | No       | Sale (true) or Rent (false)          | `true`       |

**Response:**

```json
{
  "query": "Moscow",
  "total_found": 42,
  "filtered_count": 42,
  "offers": [
    {
      "offer_id": 123,
      "title": "...",
      "price": "...",
      "area": "...",
      "...": "..."
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid parameters
- `500 Internal Server Error` - Server error during search

**Example Request:**

```bash
GET /v1/search?city=Moscow&price_gte=2000000&price_lte=5000000&area_gte=60&sale=true
```

---

## Data Models

### SearchResponse

Response model for the search endpoint.

| Field            | Type    | Description                           |
|------------------|---------|---------------------------------------|
| `query`          | string  | The city that was searched            |
| `total_found`    | integer | Total number of offers found          |
| `filtered_count` | integer | Number of offers after filtering      |
| `offers`         | object  | Dictionary of offers keyed by ID      |

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Status Code | Description                                      |
|-------------|--------------------------------------------------|
| `422`       | Validation error (missing or invalid parameters) |
| `500`       | Internal server error                            |

### Example Error Response

**422 Unprocessable Entity:**

```json
{
  "detail": [
    {
      "loc": ["query", "city"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**

```json
{
  "detail": "Error during search"
}
```

---

## Examples

### Example 1: Basic Search

Search for properties in Moscow:

```bash
curl -X GET "http://localhost:8000/v1/search?city=Moscow"
```

### Example 2: Search with Price Filter

Search for properties in Moscow with price between 2M and 5M rubles:

```bash
curl -X GET "http://localhost:8000/v1/search?city=Moscow&price_gte=2000000&price_lte=5000000"
```

### Example 3: Search with All Filters

Search for sale properties in Saint Petersburg with specific price and area:

```bash
curl -X GET "http://localhost:8000/v1/search?city=Saint%20Petersburg&price_gte=3000000&price_lte=6000000&area_gte=50&area_lte=80&sale=true"
```

### Example 4: Search for Rent

Search for rental properties in Moscow:

```bash
curl -X GET "http://localhost:8000/v1/search?city=Moscow&sale=false&price_lte=50000"
```

### Example 5: Using Python

```python
import requests

response = requests.get(
    "http://localhost:8000/v1/search",
    params={
        "city": "Moscow",
        "price_gte": "2000000",
        "price_lte": "5000000",
        "area_gte": "50",
        "sale": True
    }
)

data = response.json()
print(f"Found {data['total_found']} offers")
for offer_id, offer_data in data['offers'].items():
    print(f"Offer {offer_id}: {offer_data}")
```

### Example 6: Using JavaScript (fetch)

```javascript
const params = new URLSearchParams({
  city: 'Moscow',
  price_gte: '2000000',
  price_lte: '5000000',
  area_gte: '50',
  sale: 'true'
});

fetch(`http://localhost:8000/v1/search?${params}`)
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total_found} offers`);
    console.log(data.offers);
  })
  .catch(error => console.error('Error:', error));
```

---

## Notes

- The API requires a Selenium server to be running and accessible at the configured host/port (default: `localhost:4444`)
- Search operations may take some time depending on the number of results
- The `offers` object structure depends on the data scraped from Cian.ru
- Price values are in Russian rubles (RUB)
- Area values are in square meters (m²)

---

## Support

For issues or questions, please refer to the project repository or contact the development team.
