import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import numpy as np

# ==============================
# 1️⃣ Load Dataset
# ==============================
df = pd.read_csv("survey_time_data.csv")

# Display a quick overview
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

# ==============================
# 2️⃣ Prepare Features & Target
# ==============================
FEATURES = [
    "facialMuscles", "lipsPerioral", "jaw", "tongue",
    "upperExtremities", "lowerExtremities", "neckShouldersHips",
    "severityOfMovements", "incapacitationDueToMovements",
    "patientAwareness", "emotionalDistress", "globalRating", "monthsAhead"
]

TARGET = "futureSeverityScore"

X = df[FEATURES]
y = df[TARGET]

# ==============================
# 3️⃣ Split Data
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==============================
# 4️⃣ Train Model
# ==============================
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ==============================
# 5️⃣ Evaluate
# ==============================
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\nModel Evaluation:")
print(f"R² Score        : {r2:.3f}")
print(f"MAE             : {mae:.3f}")
print(f"RMSE            : {rmse:.3f}")

# ==============================
# 6️⃣ Save Model
# ==============================
joblib.dump(model, "forecast_model.pkl")
print("\n✅ Model saved as 'forecast_model.pkl'")
