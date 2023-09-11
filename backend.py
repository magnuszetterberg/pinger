from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
import requests
from requests.exceptions import RequestException
import time
import threading
import os
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to ping a server and return its status with a timeout
def ping_server(url, timeout=0.5):
    response_dict = {
        "status": "",
        "url": url
    }
    try:
        response = requests.get(url, timeout=timeout)
        print(response)
        if response.status_code == 200:
            response_dict["status"] = "Online"
            return response_dict
        else:
            response_dict["status"] = "Error"
            return response_dict # Status when the service responds with an unexpected status code 
    except RequestException as e:
        print(e)
        response_dict["status"] = "Unreachable"
        return response_dict  # Status when the service couldn't be reached

# Function to load and return server statuses
def load_server_statuses():
    if not os.path.isfile("server_statuses.json"):
        # Create the file with an empty dictionary if it doesn't exist
        with open("server_statuses.json", "w") as file:
            json.dump({}, file)

    with open("server_statuses.json", "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}  # Return an empty dictionary if the file is not valid JSON

# Function to load server URLs from servers.json
def load_server_urls():
    with open("containers.json", "r") as file:
        data = json.load(file)
        return [container["localUrl"] for container in data["containers"]]

# Function to update server statuses and store them in the JSON file
def update_server_statuses():
    while True:
        server_urls = load_server_urls()  # Load server URLs from containers.json

        # Load existing server statuses
        server_statuses = load_server_statuses()

        # with ThreadPoolExecutor(max_workers=20) as executor:
        #     future = executor.map(ping_server, server_urls)
        #     result = future.result()
        #     url = result["url"]
        #     status = result["status"]
        #     server_statuses[url] = status
        #     with open("server_statuses.json", "w") as file:
        #         json.dump(server_statuses, file, indent=4)


        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            # Submit tasks to the executor and collect the futures
            futures = [executor.submit(ping_server, url) for url in server_urls]

            # Wait for all futures to complete
            concurrent.futures.wait(futures)

            # Retrieve the results from the completed futures
            for future in futures:
                try:
                    result = future.result()
                    print(result)
                    url = result["url"]
                    status = result["status"]
                    server_statuses[url] = status
                except Exception as e:
                    print(f"Error occurred: {e}")

        with open("server_statuses.json", "w") as file:
            json.dump(server_statuses, file, indent=4)

        # for url in server_urls:
        #     print(f"Pinging {url}...")
        #     status = ping_server(url)
        #     print(f"Status of {url}: {status}")
        #     server_statuses[url] = status
        #     with open("server_statuses.json", "w") as file:
        #         json.dump(server_statuses, file, indent=4)

        # Store server_statuses in a local store (e.g., a JSON file)
        time.sleep(10)  # Poll servers every 15 seconds

# Start the polling thread
if __name__ == '__main__':
    polling_thread = threading.Thread(target=update_server_statuses)
    polling_thread.daemon = True
    polling_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    server_statuses = load_server_statuses()
    return jsonify(server_statuses)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
