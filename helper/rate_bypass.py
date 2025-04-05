import requests, time

def rate_limited_fetch(url, data, delay=0.67):
    response = requests.post(url, json=data)
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))  # Default to 60 seconds
        print(f"Rate limit reached. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)
        return rate_limited_fetch(url, data, delay)
    return response

def exponential_backoff_fetch(url, data, retries:int = 20):
    delay = 1
    for attempt in range(retries):
        response = requests.post(url, json=data)
        if response.status_code == 429:
            print(f"Rate limit reached. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2          # Double the delay for each retry
        else:
            return response
    return response