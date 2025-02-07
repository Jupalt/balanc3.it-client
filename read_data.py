import pandas as pd
import openpyxl

def read_input_from_excel(file_path):
    print("Start reading input data from Excel file...")
    task_relevance = read_task_relevance(file_path)
    tasks, task_times, station_type_compatibility = read_task_times(file_path, task_relevance)
    process_specific_costs = read_process_specific_costs(file_path)
    station_costs = read_station_costs(file_path)
    cycle_time = read_cycle_time(file_path)
    same_station_pairs = read_same_station_pairs(file_path, task_relevance)
    
    return tasks, task_times, station_type_compatibility, process_specific_costs, task_relevance, station_costs, cycle_time, same_station_pairs
    
def read_task_times(file_path, task_relevance):
    cols = ["tasks", "manual_times", "automatic_times"]
    df_task_times = pd.read_excel(file_path, sheet_name='task_overview', usecols=cols)

    # Liste der Aufgaben
    tasks = df_task_times['tasks'].tolist()

    # tasks = [task for i, task in enumerate(all_tasks) if task_relevance.get(task, 0) == 1]

    station_type_compatibility = {}

    # Dictionary für Task-Zeiten mit Handhabung von 'n'
    task_times = {}

    for _, row in df_task_times.iterrows():
        task_id = row["tasks"]

        for time_type in ["manual", "automatic"]:
            value = row[f"{time_type}_times"]

            # Falls 'n' in der Zelle steht, speichere 0
            if value == "n":
                task_times[(row["tasks"], time_type)] = 0
                station_type_compatibility[(task_id, time_type)] = 0
            else:
                task_times[(row["tasks"], time_type)] = int(value)  # Zahl als int speichern
                station_type_compatibility[(task_id, time_type)] = 1

    return tasks, task_times, station_type_compatibility

def read_process_specific_costs(file_path):
    cols = ["tasks", "manual_costs", "automatic_costs"]

    df_task_costs = pd.read_excel(file_path, sheet_name='task_overview', usecols=cols)

    def to_int(value):
        """Konvertiert einen Wert in int, falls möglich. Andernfalls gibt es 0 zurück."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    process_specific_costs = {
        (row['tasks'], 'manual'): to_int(row['manual_costs'])
        for _, row in df_task_costs.iterrows()
    }

    process_specific_costs.update({
        (row['tasks'], 'automatic'): to_int(row['automatic_costs'])
        for _, row in df_task_costs.iterrows()
    })

    return process_specific_costs

def read_task_relevance(file_path):
    cols = ["tasks", "relevance"]

    df_task_relevance = pd.read_excel(file_path, sheet_name='task_overview', usecols=cols)

    task_relevance = {
        int(row['tasks']): int(row['relevance'])
        for _, row in df_task_relevance.iterrows()
    }

    return task_relevance

def read_station_costs(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb["general"]
    manual_station_cost = sheet['B1'].value
    automatic_station_cost = sheet['B2'].value

    station_costs = {
        'manual': manual_station_cost,
        'automatic': automatic_station_cost
    }

    return station_costs

def read_cycle_time(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb["general"]
    cycle_time = sheet['B3'].value

    return cycle_time

def read_same_station_pairs(file_path, task_relevance):
    cols = ["tasks", "compatibility"]
    same_station_pairs = []
    df_task_comp = pd.read_excel(file_path, sheet_name='task_overview', usecols=cols)

    for _, row in df_task_comp.iterrows():
        task = row['tasks']
        compatibility = row['compatibility']
        
        # Überprüfen, ob sowohl task als auch compatibility im Dictionary den Wert 1 haben
        if pd.notna(compatibility) and task_relevance.get(task, 0) == 1 and task_relevance.get(compatibility, 0) == 1:
            same_station_pairs.append((compatibility, task))

    return same_station_pairs
