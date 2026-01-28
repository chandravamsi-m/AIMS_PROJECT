import csv
import random
import uuid
import math

# ==========================
# CONFIGURATION
# ==========================

FEATURES = [
    "facialMuscles", "lipsPerioral", "jaw", "tongue",
    "upperExtremities", "lowerExtremities", "neckShouldersHips",
    "severityOfMovements", "incapacitationDueToMovements",
    "patientAwareness", "emotionalDistress", "globalRating"
]

TIMEPOINTS = [0, 1, 3, 6]  # months

# ==========================
# UTILITY FUNCTIONS
# ==========================

def generate_patient_baseline():
    """Generate a random baseline (current) survey for a patient."""
    baseline_values = [random.randint(1, 5) for _ in FEATURES]
    avg_score = sum(baseline_values) / len(baseline_values)

    if avg_score < 2:
        assessment = "Normal"
    elif avg_score < 4:
        assessment = "Moderate"
    else:
        assessment = "Severe"

    return baseline_values, assessment, round(avg_score, 2)


def simulate_future_progression(previous_values, months_ahead, patient_trend):
    """
    Simulate how a patient's condition changes naturally over time.
    patient_trend: 'worsen', 'improve', or 'stable'
    """
    new_values = []

    for val in previous_values:
        # Random adjustment strength based on months
        base_change = 0
        if patient_trend == "worsen":
            base_change = random.choices([-1, 0, 1, 1, 1], [0.05, 0.15, 0.25, 0.3, 0.25])[0]
        elif patient_trend == "improve":
            base_change = random.choices([-1, -1, 0, 0, 1], [0.3, 0.25, 0.3, 0.1, 0.05])[0]
        else:  # stable
            base_change = random.choices([-1, 0, 1], [0.2, 0.6, 0.2])[0]

        # Adjust intensity depending on how far in the future
        multiplier = 1 + (months_ahead / 12) * random.uniform(0.5, 1.2)
        adjusted = val + math.copysign(min(abs(base_change) * multiplier, 1), base_change)

        new_val = int(max(1, min(5, round(adjusted))))
        new_values.append(new_val)

    # Calculate severity
    avg_score = sum(new_values) / len(new_values)
    if avg_score < 2:
        assessment = "Normal"
    elif avg_score < 4:
        assessment = "Moderate"
    else:
        assessment = "Severe"

    # Future score estimate (simulate gradual risk increase)
    trend_bias = {
        "worsen": random.uniform(0.2, 0.6),
        "improve": random.uniform(-0.3, 0.1),
        "stable": random.uniform(-0.1, 0.2),
    }[patient_trend]

    future_score = min(5.0, max(1.0, round(avg_score + trend_bias * (months_ahead / 6), 2)))

    return new_values, assessment, round(avg_score, 2), future_score


def generate_time_series_data(filename='survey_time_data.csv', num_patients=200):
    headers = ["patientId", "monthsAhead"] + FEATURES + [
        "assessment", "severityScore", "futureSeverityScore"
    ]
    rows = []

    for _ in range(num_patients):
        patient_id = str(uuid.uuid4())[:8]
        baseline_values, base_assess, base_score = generate_patient_baseline()

        # Each patient randomly assigned a trend type
        patient_trend = random.choices(
            ["worsen", "stable", "improve"], [0.5, 0.3, 0.2]
        )[0]

        previous_values = baseline_values
        for months in TIMEPOINTS:
            if months == 0:
                # Baseline record
                rows.append(
                    [patient_id, 0] + previous_values + [base_assess, base_score, base_score]
                )
            else:
                new_vals, assess, score, fscore = simulate_future_progression(
                    previous_values, months, patient_trend
                )
                rows.append(
                    [patient_id, months] + new_vals + [assess, score, fscore]
                )
                previous_values = new_vals  # next round continues from here

    # Write all rows
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    print(
        f"✅ Generated realistic time-series dataset: {filename} with {len(rows)} records for {num_patients} patients."
    )


if __name__ == "__main__":
    generate_time_series_data()
