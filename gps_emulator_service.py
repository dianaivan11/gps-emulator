import json, csv, requests

from typing import List, Tuple
from geopy.distance import geodesic

from math import sin, cos, atan2, radians, degrees, asin
from settings import GPSEmulatorConfiguration


class GPSEmulatorService:
    def __init__(self):
        self.azure_key = GPSEmulatorConfiguration.AZURE_MAPS_SUBSCRIPTION_KEY
        self.travel_mode = GPSEmulatorConfiguration.TRAVEL_MODE

    def generate_coordinates_azure_maps(self, start_point: Tuple[float, float],
                                        stop_point: Tuple[float, float],
                                        speed: float, 
                                        frequency_in_seconds: float) -> List[Tuple[float,float]]:
        url = f"https://atlas.microsoft.com/route/directions/json?subscription-key={self.azure_key}&api-version=1.0&query={start_point[0]},{start_point[1]}:{stop_point[0]},{stop_point[1]}&travelMode={self.travel_mode}&traffic=false&computeBestOrder=true&routeRepresentation=polyline"
        response = requests.get(url)

        if response.status_code != 200:
            print("Error generating GPS coordinates")
        
        json_data = json.loads(response.text)
        distance = json_data["routes"][0]["summary"]["lengthInMeters"]
        points = json_data["routes"][0]["legs"][0]["points"]

        time_in_seconds = distance / speed #speed in meters/second
        # Generate a set of coordinates every n seconds
        coordinates_count = int(time_in_seconds / frequency_in_seconds)  
        distance_per_step = distance / coordinates_count

        result = []
        result.append((points[0]["latitude"], points[0]["longitude"]))
        bearing_index = 0
        bearing_recompute = coordinates_count / len(points)
        bearing = self.calculate_bearing(points[0]["latitude"], points[0]["longitude"], points[1]["latitude"], points[1]["longitude"])

        for i in range(1, coordinates_count + 1):
            lat, lon = self.calculate_new_coordinates(result[i-1][0], result[i-1][1], bearing, distance_per_step)
            result.append((lat, lon))

            if bearing_index != int(i / bearing_recompute): 
                bearing_index = int(i / bearing_recompute)
                if bearing_index >= len(points) -1:
                    bearing_point_1 = points[len(points) -2]
                    bearing_point_2 = points[len(points) - 1]
                else:
                    bearing_point_1 = points[bearing_index]
                    bearing_point_2 = points[bearing_index + 1]

                bearing = self.calculate_bearing(bearing_point_1["latitude"], bearing_point_1["longitude"], bearing_point_2["latitude"], bearing_point_2["longitude"])

        self.save_to_csv('coordinates_azure_maps.csv', result)
        return result
    
    def generate_coordinates_compute(self, start_point: Tuple[float, float],
                                    stop_point: Tuple[float, float],
                                    speed: float, 
                                    frequency_in_seconds: float) -> List[Tuple[float,float]]:
        distance = geodesic(start_point, stop_point).m
        time_in_seconds = distance / speed
        coordinates_count = int(time_in_seconds / frequency_in_seconds)
        distance_per_step = distance / coordinates_count

        result = [start_point]
        bearing = self.calculate_bearing(start_point[0], start_point[1], stop_point[0], stop_point[1])

        for i in range(1, coordinates_count + 1):
            lat, lon = self.calculate_new_coordinates(result[i-1][0], result[i-1][1], bearing, distance_per_step)
            result.append((lat, lon))

        self.save_to_csv('coordinates_compute.csv', result)
        return result

    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        lat1 = radians(lat1)
        lat2 = radians(lat2)
        diff_lon = radians(lon2 - lon1)

        x = sin(diff_lon) * cos(lat2)
        y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(diff_lon)

        bearing = atan2(x, y)

        return (degrees(bearing) + 360) % 360
    
    def calculate_new_coordinates(self, lat, lon, bearing, distance):
        lat = radians(lat)
        lon = radians(lon)
        # Divide by the distance of the earth in meters
        distance = distance / 6371000.0
        new_lat = asin(sin(lat) * cos(distance) + cos(lat) * sin(distance) * cos(radians(bearing)))
        new_lon = lon + atan2(sin(radians(bearing)) * sin(distance) * cos(lat), cos(distance) - sin(lat) * sin(new_lat))

        new_lat = degrees(new_lat)
        new_lon = degrees(new_lon)

        return new_lat, new_lon
    
    def save_to_csv(self, filename: str, coordinates):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in coordinates:
                writer.writerow(row)
