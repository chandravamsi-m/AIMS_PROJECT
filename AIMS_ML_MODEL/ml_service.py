# ml_service.py
from flask import Flask, request, jsonify
import joblib
import numpy as np

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ----------------------
# Load models (ensure these exist)
# ----------------------
clf = joblib.load("survey_model_clf.pkl")         # classification model (current)
reg = joblib.load("survey_model_reg.pkl")         # regressor for current severity
label_encoder = joblib.load("label_encoder.pkl")  # label encoder for class labels
forecast_model = joblib.load("forecast_model.pkl")  # forecast model (predicts futureSeverityScore)

# ----------------------
# Required fields
# ----------------------
required_fields = [
    "facialMuscles", "lipsPerioral", "jaw", "tongue",
    "upperExtremities", "lowerExtremities", "neckShouldersHips",
    "severityOfMovements", "incapacitationDueToMovements",
    "patientAwareness", "emotionalDistress", "globalRating"
]

# ----------------------
# Analysis & Suggestion Engine
# ----------------------
def analyze_condition(data, current_score, future_score):
    """
    Return:
      {
        "trend": "Worsening"|"Stable"|"Improving",
        "probableDisorder": "string",
        "recommendedSpecialist": "string",
        "confidence": float (0-1, heuristic),
        "suggestions": [ ... ]
      }
    The logic is deterministic and explainable; can be replaced by ML later.
    """

    out = {}
    delta = float(future_score) - float(current_score)

    # Trend thresholds are tunable
    if delta >= 0.5:
        trend = "Worsening"
    elif delta <= -0.3:
        trend = "Improving"
    else:
        trend = "Stable"
    out["trend"] = trend

    # Determine probable disorder heuristically from highest-scoring domains
    # Use several rules — can output a best-guess string
    fm = int(data.get("facialMuscles", 0))
    tg = int(data.get("tongue", 0))
    ue = int(data.get("upperExtremities", 0))
    le = int(data.get("lowerExtremities", 0))
    neck = int(data.get("neckShouldersHips", 0))
    ed = int(data.get("emotionalDistress", 0))
    awareness = int(data.get("patientAwareness", 0))

    # Simple scoring
    motor_sum = ue + le + neck + int(data.get("severityOfMovements", 0))
    orofacial_sum = fm + tg + int(data.get("lipsPerioral", 0))
    mood_sum = ed + (5 - awareness)  # low awareness + high distress -> possible psychogenic

    probable = "Unspecified Motor Dysfunction"
    specialist = "General Practitioner"
    confidence = 0.5

    # Priority rules (explainable)
    if orofacial_sum >= 9 and (fm >= 4 or tg >= 4):
        probable = "Oromandibular / Oromotor Dystonia"
        specialist = "Neurologist / Speech Therapist"
        confidence = 0.8
    elif motor_sum >= 12 and (ue >= 4 or le >= 4 or neck >= 4):
        probable = "Parkinsonian-type Motor Disorder (tremor/rigidity/impaired gait)"
        specialist = "Neurologist / Movement Disorder Specialist / Physiotherapist"
        confidence = 0.82
    elif ed >= 4 and awareness <= 2:
        probable = "Functional (Psychogenic) Movement Disorder or Mood-related Motor Symptoms"
        specialist = "Psychiatrist / Psychologist"
        confidence = 0.7
    elif ed >= 4:
        probable = "High Emotional Distress - consider psychological evaluation"
        specialist = "Psychiatrist / Psychologist"
        confidence = 0.6
    elif current_score >= 4.2:
        probable = "Severe motor impairment — consider specialist review"
        specialist = "Neurologist / Physiotherapist"
        confidence = 0.7

    # If trend is worsening, increase urgency and confidence slightly
    if trend == "Worsening":
        confidence = min(0.95, confidence + 0.05)

    # Build suggestions list (actionable)
    suggestions = []
    if trend == "Worsening":
        suggestions.append("Condition is predicted to worsen — arrange specialist review within 1 month.")
    elif trend == "Improving":
        suggestions.append("Condition shows improvement — continue current management and monitor.")
    else:
        suggestions.append("Condition expected to be stable— continue monitoring, consider follow-up as needed.")

    # Domain-specific recommendations
    if orofacial_sum >= 8:
        suggestions.append("High orofacial involvement — recommend speech/swallowing assessment and ENT if swallowing issues.")
    if ue >= 4 or le >= 4:
        suggestions.append("Significant limb involvement — physiotherapy referral recommended.")
    if ed >= 4:
        suggestions.append("High emotional distress — recommend mental health evaluation (counselling/psychiatry).")

    # Safety advice (general)
    if current_score >= 4.5:
        suggestions.append("Severe score — consider immediate in-person specialist referral or emergency evaluation if symptoms dangerous.")
    if awareness <= 1:
        suggestions.append("Low patient awareness — ensure supervision and safety measures at home.")

    out["probableDisorder"] = probable
    out["recommendedSpecialist"] = specialist
    out["confidence"] = round(float(confidence), 2)
    out["suggestions"] = suggestions
    return out

# ----------------------
# ROUTE: Predict current condition (unchanged)
# ----------------------
@app.route('/predict', methods=['POST'])
def predict_current():
    data = request.json or {}
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        input_data = [int(data[field]) for field in required_fields]
        input_array = np.array(input_data).reshape(1, -1)

        encoded_pred = clf.predict(input_array)[0]
        pred_label = label_encoder.inverse_transform([encoded_pred])[0]
        severity_score = float(reg.predict(input_array)[0])

        # For current prediction we can return suggestions using analyze_condition with same current & future scores
        analyze = analyze_condition(data, severity_score, severity_score)

        result = {
            "assessment": pred_label,
            "severityScore": round(severity_score, 2),
            "suggestions": analyze.get("suggestions", [])
        }
        # include disorder/specialist for current snapshot as well
        result["probableDisorder"] = analyze.get("probableDisorder")
        result["recommendedSpecialist"] = analyze.get("recommendedSpecialist")
        result["confidence"] = analyze.get("confidence")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------
# ROUTE: Predict future condition (extended)
# ----------------------
@app.route('/predict-future', methods=['POST'])
def predict_future():
    data = request.json or {}
    # validate fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    if "monthsAhead" not in data:
        return jsonify({"error": "Missing field: monthsAhead"}), 400

    try:
        months_ahead = int(data["monthsAhead"])
        if months_ahead not in [1, 3, 6]:
            return jsonify({"error": "monthsAhead must be one of [1, 3, 6]."}), 400

        # forecast model input: features + monthsAhead
        input_data = [int(data[field]) for field in required_fields] + [months_ahead]
        input_array = np.array(input_data).reshape(1, -1)

        future_score = float(forecast_model.predict(input_array)[0])

        # compute current score for comparison
        current_input = np.array([int(data[field]) for field in required_fields]).reshape(1, -1)
        current_score = float(reg.predict(current_input)[0])

        # analysis & specialist/disorder recommendation
        analysis = analyze_condition(data, current_score, future_score)

        response = {
            "monthsAhead": months_ahead,
            "currentSeverityScore": round(current_score, 2),
            "predictedFutureSeverityScore": round(future_score, 2),
            "trend": analysis.get("trend"),
            "probableDisorder": analysis.get("probableDisorder"),
            "recommendedSpecialist": analysis.get("recommendedSpecialist"),
            "confidence": analysis.get("confidence"),
            "suggestions": analysis.get("suggestions")
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------
# Run server
# ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
