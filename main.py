from fastapi import FastAPI, Depends, Query
from gps_emulator_service import GPSEmulatorService
app = FastAPI()

@app.get("/coordinates-azure-maps")
async def generate_coordinates_azure_maps(start_lat: float, start_lon: float, 
                                stop_lat: float, stop_lon: float, 
                                speed: float = Query(default = 1, description = "moving speed in meters/second"),
                                frequency: int = Query(default = 1, description= "time interval in seconds for generating coordinates"),
                                gps_service: GPSEmulatorService = Depends(GPSEmulatorService)):
    '''
    Generate GPS coordinates using Azure Maps API
    '''
    result = gps_service.generate_coordinates_azure_maps((start_lat, start_lon), (stop_lat, stop_lon),
                                              speed, frequency)
    
    return result


@app.get("/coordinates-compute")
async def generate_coordinates_compute(start_lat: float, start_lon: float, 
                                stop_lat: float, stop_lon: float, 
                                speed: float = Query(default = 1, description = "moving speed in meters/second"),
                                frequency: float = Query(default = 1, description= "time interval in seconds for generating coordinates"),
                                gps_service: GPSEmulatorService = Depends(GPSEmulatorService)):
    '''
    Generate GPS coordinates using computations
    '''
    result = gps_service.generate_coordinates_compute((start_lat, start_lon), (stop_lat, stop_lon),
                                              speed, frequency)
    
    return result