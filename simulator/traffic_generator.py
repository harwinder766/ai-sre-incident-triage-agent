import random
import time

import requests

PAYMENT_API_URL = "http://127.0.0.1:8001/payments"

REQUEST_INTERVAL = 1.0

def generate_payment():
    """
    Generate a random payment request.
    """
    return {
        "user_id": f"USER-{random.randint(1, 20):03d}",
        "amount": round(random.uniform(100, 5000), 2),
    }

def send_payment():
    """
    Send one payment request to the simulated payment API.
    """

    payment = generate_payment()

    try:

        response = requests.post(
            PAYMENT_API_URL,
            json=payment,
            timeout=10,
        )

        print(
            f"Payment request | "
            f"user={payment['user_id']} | "
            f"amount={payment['amount']} | "
            f"status={response.status_code}"
        )

    except requests.exceptions.Timeout:

        print(
            f"Payment request timed out | "
            f"user={payment['user_id']}"
        )

    except requests.exceptions.ConnectionError:

        print(
            "Could not connect to payment-api"
        )

    except requests.exceptions.RequestException as exc:

        print(
            f"Request failed: {exc}"
        )


# Traffic generator
def main():

    print("Starting payment-api traffic generator...")
    print("Press Ctrl+C to stop.")

    while True:

        send_payment()

        time.sleep(REQUEST_INTERVAL)


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print("\nTraffic generator stopped.")