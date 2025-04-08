import requests

BASE_URL = "https://thai-agriculture-backend.onrender.com"

test_endpoints = {
    "/": lambda r: r.status_code == 200 and "message" in r.json(),
    "/healthz": lambda r: r.status_code == 200 and r.json().get("status") == "ok",
    "/docs": lambda r: r.status_code == 200,
    "/dropdowns/product-types": lambda r: r.status_code == 200 and isinstance(r.json(), list),
    "/dropdowns/product-groups?type=1": lambda r: r.status_code == 200 and isinstance(r.json(), list),
    "/dropdowns/product-names?group=ผัก": lambda r: r.status_code == 200 and isinstance(r.json(), list),
    "/prices": lambda r: r.status_code == 200 and isinstance(r.json(), list),
    "/prices?group=ผัก&start_date=2025-04-01&end_date=2025-04-04": lambda r: r.status_code == 200 and isinstance(r.json(), list),
    "/export?group=ผลไม้": lambda r: r.status_code == 200 and "text/csv" in r.headers.get("content-type", ""),
    "/export_excel?group=ผลไม้": lambda r: r.status_code == 200 and "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in r.headers.get("content-type", ""),
    "/available-dates": lambda r: r.status_code == 200 and isinstance(r.json().get("available_dates"), list),
    "/latest": lambda r: r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) <= 10,
    "/summary": lambda r: r.status_code == 200 and all(k in r.json() for k in ["total_records", "unique_product_names", "date_range"])
}

results = []
for route, check in test_endpoints.items():
    try:
        url = f"{BASE_URL}{route}"
        print(f"🔍 Testing {url} ...")
        response = requests.get(url)
        result = {
            "endpoint": route,
            "status": response.status_code,
            "success": check(response)
        }
    except Exception as e:
        result = {
            "endpoint": route,
            "status": "ERROR",
            "success": False,
            "error": str(e)
        }
    results.append(result)

# Print results
print("\n🧪 Test Results:")
for r in results:
    status = "✅ PASS" if r["success"] else "❌ FAIL"
    print(f"{status} - {r['endpoint']} (Status: {r['status']})")
    if not r["success"] and "error" in r:
        print(f"    Error: {r['error']}")
