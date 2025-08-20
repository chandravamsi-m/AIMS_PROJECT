from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load models and encoder
clf = joblib.load("survey_model_clf.pkl")   # classification
reg = joblib.load("survey_model_reg.pkl")   # regression
label_encoder = joblib.load("label_encoder.pkl")

required_fields = [
    "facialMuscles", "lipsPerioral", "jaw", "tongue",
    "upperExtremities", "lowerExtremities", "neckShouldersHips",
    "severityOfMovements", "incapacitationDueToMovements", "patientAwareness",
    "emotionalDistress", "globalRating"
]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        input_data = [int(data[field]) for field in required_fields]
        input_array = np.array(input_data).reshape(1, -1)

        # ML prediction
        prediction_encoded = clf.predict(input_array)[0]
        prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]

        # === Dynamic suggestions (trigger only when rating == 5) ===
        suggestions = []

        # 1. Face-related
        if (data["facialMuscles"] == 5 or data["lipsPerioral"] == 5 or 
            data["jaw"] == 5 or data["tongue"] == 5):
            suggestions.append(
                "Severe facial motor issues — urgent speech/swallowing evaluation needed."
            )

        # 2. Mobility-related (bones/joints)
        if (data["neckShouldersHips"] == 5 or data["severityOfMovements"] == 5 or
            data["upperExtremities"] == 5 or data["lowerExtremities"] == 5):
            suggestions.append(
                "Severe mobility impairment — urgent physiotherapy/neurology review."
            )

        # 3. Awareness / psychological
        if data["patientAwareness"] == 5:
            suggestions.append(
                "Complete loss of awareness — requires continuous supervision."
            )
        if data["emotionalDistress"] == 5:
            suggestions.append(
                "Severe emotional distress — immediate psychiatric support advised."
            )

        # 4. Global rating / incapacitation
        if data["incapacitationDueToMovements"] == 5:
            suggestions.append(
                "Fully incapacitated by movements — emergency care required."
            )
        if data["globalRating"] == 5:
            suggestions.append(
                "Critical overall condition — hospital admission advised."
            )

        # Default if no critical red flags
        if not suggestions:
            suggestions.append("No urgent issues detected — continue routine monitoring.")

        # === FIX: use regression model for severity score ===
        severity_score = round(float(reg.predict(input_array)[0]), 2)

        return jsonify({
            "assessment": prediction_label,
            "severityScore": severity_score,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
