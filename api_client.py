import requests
import websockets
import asyncio
from read_data import read_input_from_excel

excel_file_path = "input.xlsx"

url = "http://127.0.0.1:8000/"

def convert_dict_keys_to_strings(original_dict):
    return {f"{key[0]}_{key[1]}": value for key, value in original_dict.items()}

async def listen_for_notifications(websocket):
    # Empfange Nachrichten vom Server
    while True:
        message = await websocket.recv()
        print(f"Received from server: '{message}'")
        if message == "Current Status: Optimization completed":
            break

async def keep_alive(websocket, interval=30):
    while True:
        await websocket.send("ping")  # Sende alle 30 Sekunden eine Ping-Nachricht
        print("Sent ping to server.")   
        await asyncio.sleep(interval)

async def start_optimization_and_listen():
    tasks, task_times, station_type_compatibility, process_specific_costs, task_relevance, station_costs, cycle_time, same_station_pairs = read_input_from_excel(excel_file_path)

    json_station_type_compatibility = convert_dict_keys_to_strings(station_type_compatibility)
    json_task_times = convert_dict_keys_to_strings(task_times)
    json_process_specific_costs = convert_dict_keys_to_strings(process_specific_costs)

    data = {
        "tasks": {"tasks": tasks},
        "task_times": {"task_times": json_task_times},
        "station_type_compatibility": {"station_type_compatibility": json_station_type_compatibility},
        "process_specific_costs": {"process_specific_costs": json_process_specific_costs},
        "task_relevance": {"task_relevance": task_relevance},
        "station_costs": {"station_costs": station_costs},
        "cycle_time": {"cycle_time": cycle_time},
        "same_station_pairs": {"same_station_pairs": same_station_pairs},
    }
    
    print("Start uploading the data to server...")
    for endpoint, data_point in data.items():
        response = requests.post(url + f"upload-{endpoint}/", json=data_point)
        if response.status_code == 200:
            print(f"Upload of {endpoint} was successful!")
        else:
            print(f"Error while uploading {endpoint}: {response.status_code}")

    start = input("Start Optimization: [Y/N] ").strip().lower()
    if start == "y":
        await start_optimization_and_websocket() 
    elif start == "n":
        print("Optimization canceled.")
        return

async def start_optimization_and_websocket():
    uri = "ws://127.0.0.1:8000/ws"  # WebSocket-URL deines Servers
    async with websockets.connect(uri, ping_interval=30, ping_timeout=10) as websocket:
        # Erfolgreiche Verbindung
        print()
        print("WebSocket connection established!")
        print()

        # Starte das Hören auf Nachrichten in einer separaten Task
        listen_task = asyncio.create_task(listen_for_notifications(websocket))

        keep_alive_task = asyncio.create_task(keep_alive(websocket))

        # Sende eine Nachricht an den Server, um die Optimierung zu starten
        response = requests.post(url + "start-optimization/")
        print(response.json())

        # Warte, bis Nachrichten empfangen werden
        await listen_task
        await keep_alive_task

# Main-Loop
if __name__ == "__main__":
    asyncio.run(start_optimization_and_listen())
