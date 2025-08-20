import csv
import random

def generate_sample_for_class(label):
    if label == "Normal":
        values = [random.randint(1, 2) for _ in range(12)]
    elif label == "Moderate":
        values = [random.randint(2, 3) for _ in range(12)]
    else:  # Severe
        values = [random.randint(4, 5) for _ in range(12)]

    avg_score = sum(values) / len(values)  # severity score
    return values + [label, avg_score]

def generate_survey_data(filename='survey_data.csv', num_rows=600):
    headers = [
        "facialMuscles", "lipsPerioral", "jaw", "tongue",
        "upperExtremities", "lowerExtremities", "neckShouldersHips",
        "severityOfMovements", "incapacitationDueToMovements", "patientAwareness",
        "emotionalDistress", "globalRating", "assessment", "severityScore"
    ]

    num_per_class = num_rows // 3
    data = []

    for _ in range(num_per_class):
        data.append(generate_sample_for_class("Normal"))
        data.append(generate_sample_for_class("Moderate"))
        data.append(generate_sample_for_class("Severe"))

    random.shuffle(data)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Balanced survey data written to '{filename}' with {num_rows} rows.")

if __name__ == "__main__":
    generate_survey_data()
