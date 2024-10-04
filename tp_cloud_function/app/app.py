import json
import time
import random
import requests

# Sample log messages
sample_logs = [
    {"level": "INFO", "message": "User logged in", "user_id": 1},
    {"level": "DEBUG", "message": "Query executed", "user_id": 3},
]
error_logs = [
    {"level": "ERROR", "message": "Failed to connect to database", "user_id": 2},
    {"level": "ERROR", "message": "Permission denied", "user_id": 4},
]

# Cloud function endpoint
CLOUD_FUNCTION_ENDPOINT = "https://myfunctionprojstan.azurewebsites.net/api/store_log"

def send_log_to_cloud_function(log):
    response = requests.post(CLOUD_FUNCTION_ENDPOINT, json=log)
    if response.status_code == 200:
        print(f"Sent log: {log}")
    else:
        print(f"Failed to send log: {log}. Status code: {response.status_code}")

def simulate_log_stream():
    while True:
        if random.random() < 0.1:
            log = random.choice(error_logs)
        else:
            log = random.choice(sample_logs)

        send_log_to_cloud_function(log)
        time.sleep(random.uniform(0.5, 3))

if __name__ == "__main__":
    simulate_log_stream()