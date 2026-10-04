from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import httpx

URL = "http://localhost:8005/orders"


def create_order(i: int):
    response = httpx.post(URL, headers={
        "Content-Type": "application/json",
        "Idempotency-Key": f"order-{i}"
    }, json={"sku": "SKU-1", "qty": 1}, timeout=1)


def main():
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(create_order, range(50)))
        statuses = Counter(result["status"] for result in results)
        print(statuses)


if __name__ == "__main__":
    main()