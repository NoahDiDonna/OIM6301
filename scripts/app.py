import bmi

people = [
    {"name": "Alice", "height": 1.65, "weight": 60},
    {"name": "Ben", "height": 1.80, "weight": 85},
    {"name": "Carla", "height": 1.70, "weight": 68},
    {"name": "David", "height": 1.75, "weight": 90},
    {"name": "Elena", "height": 1.60, "weight": 55},
    {"name": "Frank", "height": 1.85, "weight": 95},
    {"name": "Grace", "height": 1.68, "weight": 62},
    {"name": "Henry", "height": 1.78, "weight": 80},
]

for person in people:
    print(person)
#result = bmi.compute_bmi(1.75, 78)
#print(f"Computed BMI: {result:.2f}")