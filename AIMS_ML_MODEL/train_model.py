import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
import joblib
import numpy as np

# Step 1: Load dataset
df = pd.read_csv("survey_data.csv")

# Step 2: Features and targets
X = df.drop(["assessment", "severityScore"], axis=1)
y_class = df["assessment"]
y_reg = df["severityScore"]

# Step 3: Encode classification labels
label_encoder = LabelEncoder()
y_class_encoded = label_encoder.fit_transform(y_class)
joblib.dump(label_encoder, "label_encoder.pkl")

# Step 4: Train/test split
X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
    X, y_class_encoded, y_reg, test_size=0.2, random_state=42
)

# Step 5: Train models
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_class_train)

reg = RandomForestRegressor(n_estimators=100, random_state=42)
reg.fit(X_train, y_reg_train)

# Step 6: Evaluate
y_class_pred = clf.predict(X_test)
print("\nClassification Report:\n", classification_report(y_class_test, y_class_pred))
print("Accuracy:", accuracy_score(y_class_test, y_class_pred))

y_reg_pred = reg.predict(X_test)
mse = mean_squared_error(y_reg_test, y_reg_pred)
print("Regression MSE:", mse)
print("Regression RMSE:", np.sqrt(mse))

# Step 7: Save models
joblib.dump(clf, "survey_model_clf.pkl")
joblib.dump(reg, "survey_model_reg.pkl")
print("Models saved: survey_model_clf.pkl, survey_model_reg.pkl")
