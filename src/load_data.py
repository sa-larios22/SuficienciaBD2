import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Obtener URI (Uniform Resource Identifier)
mongo_uri = os.getenv("MONGO_URI")

# Conexión a MongoDB
client = MongoClient(mongo_uri)
db = client["datos_f1"]

# Cargar archivos CSV
data_path = "../archive/"
files = [
    "circuits.csv", "races.csv", "results.csv", "drivers.csv", "constructors.csv",
    "constructor_results.csv", "constructor_standings.csv", "driver_standings.csv",
    "lap_times.csv", "pit_stops.csv", "qualifying.csv", "seasons.csv", "sprint_results.csv", "status.csv"
]

# Convertir CSVs a DataFrames
data = {file: pd.read_csv(f"{data_path}{file}") for file in files}

# Limpiar los datos con \N y hacer conversión de tipos
for df in data.values():
    df.replace(r"\N", None, inplace=True)
    df.fillna("", inplace=True)

# Convertir columnas numéricas a los tipos correctos
numeric_columns = {
    "circuits.csv": ["circuitId", "lat", "lng", "alt"],
    "races.csv": ["raceId", "year", "round", "circuitId"],
    "results.csv": ["resultId", "raceId", "driverId", "constructorId", "number", "grid", "positionOrder", "points", "laps", "milliseconds", "fastestLap", "rank", "statusId"],
    "constructor_results.csv": ["constructorResultsId", "raceId", "constructorId", "points"],
    "constructor_standings.csv": ["constructorStandingsId", "raceId", "constructorId", "points", "position", "wins"],
    "driver_standings.csv": ["driverStandingsId", "raceId", "driverId", "points", "position", "wins"],
    "lap_times.csv": ["raceId", "driverId", "lap", "position", "milliseconds"],
    "pit_stops.csv": ["raceId", "driverId", "stop", "lap", "milliseconds"],
    "qualifying.csv": ["qualifyId", "raceId", "driverId", "constructorId", "number", "position"],
    "sprint_results.csv": ["resultId", "raceId", "driverId", "constructorId", "number", "grid", "positionOrder", "points", "laps", "milliseconds", "fastestLap", "statusId"],
    "seasons.csv": ["year"],
    "status.csv": ["statusId"]
}
for file, cols in numeric_columns.items():
    for col in cols:
        if col in data[file].columns:
            data[file][col] = pd.to_numeric(data[file][col], errors="coerce").fillna(0)

# Crear colección de temporadas
seasons = data["seasons.csv"].to_dict("records")
for season in seasons:
    year = season["year"]
    # Obtener carreras
    races = data["races.csv"][data["races.csv"]["year"] == year].to_dict("records")
    for race in races:
        race_id = race["raceId"]
        # Datos de Circuitos
        circuit = data["circuits.csv"][data["circuits.csv"]["circuitId"] == race["circuitId"]]
        race["circuit"] = circuit[["circuitId", "name", "location", "country", "lat", "lng"]].to_dict("records")[0]
        # Resultados
        race["results"] = data["results.csv"][data["results.csv"]["raceId"] == race_id][
            ["driverId", "constructorId", "position", "points", "laps", "fastestLapTime", "statusId"]
        ].to_dict("records")
        # Tiempos
        race["qualifying"] = data["qualifying.csv"][data["qualifying.csv"]["raceId"] == race_id][
            ["driverId", "constructorId", "position", "q1", "q2", "q3"]
        ].to_dict("records")
        # Paradas de pits
        race["pit_stops"] = data["pit_stops.csv"][data["pit_stops.csv"]["raceId"] == race_id][
            ["driverId", "lap", "duration"]
        ].to_dict("records")
        # Tiempos de vuelta
        race["lap_times"] = data["lap_times.csv"][data["lap_times.csv"]["raceId"] == race_id][
            ["driverId", "lap", "time"]
        ].to_dict("records")
        # Resultados sprint
        race["sprint_results"] = data["sprint_results.csv"][data["sprint_results.csv"]["raceId"] == race_id][
            ["driverId", "constructorId", "position", "points"]
        ].to_dict("records")
    season["races"] = races
    db.seasons.insert_one(season)

# Colección de Constructores (escudería)
constructors = data["constructors.csv"].to_dict("records")
for constructor in constructors:
    constructor_id = constructor["constructorId"]
    constructor["seasons"] = []
    # Temporadas
    for year in data["seasons.csv"]["year"]:
        races = data["constructor_results.csv"][data["constructor_results.csv"]["constructorId"] == constructor_id]
        races = races[races["raceId"].isin(data["races.csv"][data["races.csv"]["year"] == year]["raceId"])]
        races_data = []
        # Carreras
        for _, race in races.iterrows():
            race_id = race["raceId"]
            race_data = {
                "raceId": race_id,
                "points": race["points"],
                # Podios
                "position": data["constructor_standings.csv"][
                    (data["constructor_standings.csv"]["raceId"] == race_id) &
                    (data["constructor_standings.csv"]["constructorId"] == constructor_id)
                ]["positionText"].iloc[0] if not data["constructor_standings.csv"][
                    (data["constructor_standings.csv"]["raceId"] == race_id) &
                    (data["constructor_standings.csv"]["constructorId"] == constructor_id)
                ].empty else None,
                # Conductores y resultados
                "drivers": data["results.csv"][
                    (data["results.csv"]["raceId"] == race_id) &
                    (data["results.csv"]["constructorId"] == constructor_id)
                ][["driverId", "position", "points"]].to_dict("records")
            }
            races_data.append(race_data)
        if races_data:
            constructor["seasons"].append({"year": year, "races": races_data})
    db.constructors.insert_one(constructor)

# Colección de pilotos
drivers = data["drivers.csv"].to_dict("records")
for driver in drivers:
    driver_id = driver["driverId"]
    driver["seasons"] = []
    # Temporadas
    for year in data["seasons.csv"]["year"]:
        # Carreras
        races = data["results.csv"][data["results.csv"]["driverId"] == driver_id]
        races = races[races["raceId"].isin(data["races.csv"][data["races.csv"]["year"] == year]["raceId"])]
        races_data = races[["raceId", "constructorId", "position", "points", "fastestLapTime"]].to_dict("records")
        if races_data:
            driver["seasons"].append({"year": year, "races": races_data})
    db.drivers.insert_one(driver)

print(f"Datos cargados exitosamente el: {datetime.now()}")