import os

test_stats = """
{
    "observations_by_specie": {
        "duck": 1,
        "crow": 1
    },
    "observations_by_camera": {
        "UNKNOWN": 1,
        "CAMERA40": 1
    },
    "observations_by_leging": {
        "leging1": 1,
        "leging2": 1
    },
    "species_by_hour": {
        "duck": {
            "0": 1
        },
        "crow": {
            "15": 1
        }
    }
}
"""

for model in os.listdir(os.path.join("..", "results")):
    with open(os.path.join("..", "results", model, "stats.json"), 'w') as file:
        file.write(test_stats)
