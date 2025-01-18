"""
This module provides functions to generate various plots based on species and camera data.
"""

from typing import Counter
from datetime import datetime
from ..config.constants import DATE_TIME_FORMAT

def format_resulting_data(output_data):
    # Dictionaries for precomputed values
    cameras = {}
    species_counts = {}
    species_camera_counts = {}
    species_hourly_counts = {}
    leging_counts = {}
    species_leging_counts = {}

    for observation in output_data:
        camera = observation['metadata']['camera']
        if camera is None:
            print(f"Could not find the camera for image '{observation['target_filename']}'")
            continue
        date_time_str = f"{observation['metadata']['date']} {observation['metadata']['time']}"
        leging = observation['metadata']['leging']
        leging_counts[leging] = leging_counts.get(leging, 0) + len(observation['labels'])

        if leging not in species_leging_counts:
            species_leging_counts[leging] = {}
            
        for label in observation['labels']:
            species_leging_counts[leging][label] = species_leging_counts[leging].get(label, 0) + 1
        try:
            date_time_obj = datetime.strptime(date_time_str, DATE_TIME_FORMAT)
        except ValueError as e:
            print(f"Could not find date time for image '{observation['target_filename']}'\nError: {e}")
            continue
        hour = date_time_obj.hour

        # Update camera observation counts
        cameras[camera] = cameras.get(camera, 0) + len(observation['labels'])

        for label in observation['labels']:
            # Update total species count
            species_counts[label] = species_counts.get(label, 0) + 1
            
            # Update species per camera
            if camera not in species_camera_counts:
                species_camera_counts[camera] = {}
                
            species_camera_counts[camera][label] = species_camera_counts[camera].get(label, 0) + 1

            # Update hourly species counts
            if label not in species_hourly_counts:
                species_hourly_counts[label] = Counter()
                
            species_hourly_counts[label][hour] += 1

    return {
        'cameras': cameras,
        'species_counts': species_counts,
        'species_camera_counts': species_camera_counts,
        'species_hourly_counts': species_hourly_counts,
        'leging_counts': leging_counts,
        'species_leging_counts': species_leging_counts
    }
