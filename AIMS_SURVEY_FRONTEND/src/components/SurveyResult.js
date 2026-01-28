// src/pages/SurveyResult.jsx
import React, { useEffect, useRef, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Chart from "chart.js/auto";
import axios from "axios";
import ForecastChart from "../components/ForecastChart";
import "../styles/survey-result.css";

const SurveyResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const [predictionData, setPredictionData] = React.useState(null);
  const { patient, survey } = location.state || {};

  const handleDataUpdate = useCallback((data) => {
    setPredictionData(data);
  }, []);

  useEffect(() => {
    if (!patient || !survey) return;
    const ctx = chartRef.current.getContext("2d");

    const labels = [
      "Facial", "Lips", "Jaw", "Tongue",
      "Upper Ext", "Lower Ext", "Neck/Hips",
      "Severity", "Incapacitation", "Awareness", "Distress", "Global"
    ];
    const dataValues = [
      survey.facialMuscles, survey.lipsPerioral, survey.jaw, survey.tongue,
      survey.upperExtremities, survey.lowerExtremities, survey.neckShouldersHips,
      survey.severityOfMovements, survey.incapacitationDueToMovements, survey.patientAwareness,
      survey.emotionalDistress, survey.globalRating
    ];
    
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(16, 185, 129, 0.2)");
    gradient.addColorStop(1, "rgba(16, 185, 129, 0)");

    const chart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "AIRS Scores",
          data: dataValues,
          borderColor: "#10b981",
          backgroundColor: gradient,
          pointBackgroundColor: "#10b981",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
          pointRadius: 4,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { 
          y: { 
            min: 0, 
            max: 5, 
            ticks: { stepSize: 1, color: "#94a3b8", font: { size: 10 } },
            grid: { color: "#f1f5f9" }
          },
          x: {
            ticks: { color: "#94a3b8", font: { size: 10 } },
            grid: { display: false }
          }
        },
        plugins: { legend: { display: false } }
      }
    });
    chartInstanceRef.current = chart;
    return () => chart.destroy();
  }, [patient, survey]);

  const handleDownload = async () => {
    try {
      const canvas = chartRef.current;
      const chartImage = canvas.toDataURL("image/png");
      const response = await axios.post("http://localhost:8080/api/download-pdf", {
        patient, survey, chartImage
      }, { responseType: "blob" });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${patient.firstName}_${patient.lastName}_Survey.pdf`;
      link.click();
    } catch (e) {
      console.error(e);
    }
  };

  const getScoreStatus = (val) => {
    if (val <= 2) return { label: "Excellent", class: "status-excellent", color: "#10b981" };
    if (val === 3) return { label: "Fair", class: "status-fair", color: "#f59e0b" };
    return { label: "Poor", class: "status-poor", color: "#ef4444" };
  };

  if (!patient || !survey) {
    return (
      <div className="sr-page">
        <div className="sr-container">
          <div className="card">Missing data. Please restart the survey.</div>
        </div>
      </div>
    );
  }

  const scores = [
    { label: "Facial Muscles", val: survey.facialMuscles },
    { label: "Lips", val: survey.lipsPerioral },
    { label: "Jaw", val: survey.jaw },
    { label: "Tongue Management", val: survey.tongue },
    { label: "Physical Activity", val: survey.upperExtremities },
    { label: "Walking", val: survey.lowerExtremities },
    { label: "Neck/Hips", val: survey.neckShouldersHips },
    { label: "Mental Health", val: survey.severityOfMovements },
    { label: "Performance", val: survey.incapacitationDueToMovements },
    { label: "Self Assessment", val: survey.patientAwareness },
    { label: "Overall", val: survey.globalRating },
  ];

  return (
    <div className="sr-page">
      <div className="sr-container">
        <div className="sr-header">
          <div className="title-row">
            <span className="accent-bar"></span>
            <h2 className="sr-title">Survey Result</h2>
          </div>
          <div className="sr-subtitle">Comprehensive health and wellness assessment with AI-powered predictions</div>
        </div>

        {/* Patient card */}
        <div className="card patient-card">
          <div className="patient-header">
             👤 Patient Information
          </div>
          <div className="patient-grid">
            <div className="meta-block">
              <div className="meta-label-row"><span className="icon">👤</span> Name</div>
              <div className="meta-value">{patient.firstName} {patient.lastName}</div>
            </div>
            <div className="meta-block">
              <div className="meta-label-row"><span className="icon">#</span> Age</div>
              <div className="meta-value">{patient.age}</div>
            </div>
            <div className="meta-block">
              <div className="meta-label-row"><span className="icon">🚻</span> Gender</div>
              <div className="meta-value">
                <span className="gender-badge">{patient.gender}</span>
              </div>
            </div>
            <div className="meta-block">
              <div className="meta-label-row"><span className="icon">📅</span> Survey Date</div>
              <div className="meta-value">{patient.surveyDate}</div>
            </div>
          </div>
        </div>

        {/* AIRS Score Trends */}
        <div className="card chart-card">
          <div className="chart-section-header">
            <div className="chart-title-row">
              ✨ AIRS Score Trends
            </div>
            <div className="badge-pill">Current Assessment</div>
          </div>

          <div className="canvas-wrapper">
            <canvas className="area-canvas" ref={chartRef}></canvas>
          </div>

          <div className="score-grid">
            {scores.map((s, idx) => {
              const status = getScoreStatus(s.val);
              return (
                <div key={idx} className="score-item">
                  <div className="score-item-header">
                    <span className="score-value">{s.val}</span>
                    <span className={`score-status ${status.class}`}>{status.label}</span>
                  </div>
                  <div className="score-label">{s.label}</div>
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar-fill" 
                      style={{ 
                        width: `${(s.val / 5) * 100}%`,
                        backgroundColor: status.color
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Powered Future Prediction */}
        <div className="ai-section">
          <div className="ai-header-row">
            ✨ AI Powered Future Prediction
          </div>
          <div className="ai-description">
            Based on your current survey ratings, this section predicts how the patient's condition might evolve in 1, 3, and 6 months — along with possible disorder insights and specialist suggestions.
          </div>
          <ForecastChart 
            survey={survey} 
            apiBaseUrl="http://localhost:8080/api" 
            onDataUpdate={handleDataUpdate}
          />
        </div>

        {/* Analysis Summary */}
        <div className="card">
          <div className="analysis-title">
            📋 Analysis Summary
          </div>
          
          <div className="summary-grid">
            <div className="summary-card green">
              <div className="summary-label-row">📈 Trend</div>
              <div className="summary-value" style={{ color: "#10b981" }}>
                {predictionData?.trend ?? "Calculating..."}
              </div>
            </div>
            <div className="summary-card teal">
              <div className="summary-label-row">✨ Current Severity Score</div>
              <div className="summary-value" style={{ color: "#0d9488" }}>
                {predictionData?.currentSeverityScore ?? predictionData?.severityScore ?? "---"}
              </div>
            </div>
            <div className="summary-card orange">
              <div className="summary-label-row">🔍 Probable Disorder</div>
              <div className="summary-value" style={{ color: "#d97706" }}>
                {predictionData?.probable_disorder ?? "Orofacial / Counselor Dystonia"}
              </div>
            </div>
            <div className="summary-card purple">
              <div className="summary-label-row">🔮 6-month Severity Score</div>
              <div className="summary-value" style={{ color: "#7c3aed" }}>
                {predictionData?.predictedFutureSeverityScore ?? "---"}
              </div>
            </div>
          </div>

          <div className="specialist-banner">
             <span className="icon">👤</span>
             <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
               <span className="specialist-label">Recommended Specialist</span>
               <span className="specialist-value">
                 {predictionData?.recommended_specialist ?? "Neurologist / Speech Therapist"}
               </span>
             </div>
          </div>

          <div className="suggestions-box">
            <div className="suggestions-header">💡 Suggestions</div>
            <ul className="suggestions-list">
              <li className="suggestion-item">
                <span className="suggestion-bullet">•</span>
                Patient appears to be stable — continue monitoring, consider follow-up as needed.
              </li>
              <li className="suggestion-item">
                <span className="suggestion-bullet">•</span>
                High orofacial involvement — recommend speech/swallowing assessment and ENT if swallowing issues.
              </li>
              <li className="suggestion-item">
                <span className="suggestion-bullet">•</span>
                Significant limb involvement — physiotherapy referral recommended.
              </li>
              <li className="suggestion-item">
                <span className="suggestion-bullet">•</span>
                High emotional distress — recommend mental health evaluation (counseling/psychiatry).
              </li>
            </ul>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="footer-row">
          <div className="buttons-group">
            <button className="btn-action btn-primary" onClick={handleDownload}>
              📥 Download PDF
            </button>
            <button className="btn-action btn-outline" onClick={() => navigate("/")}>
              🔄 Take Another Survey
            </button>
            <button className="btn-action btn-outline" onClick={() => navigate("/search")}>
              🔍 Search Previous Surveys
            </button>
          </div>
        </div>

        <div className="info-disclaimer">
          ℹ️ This assessment provides insights into various health and wellness dimensions with AI-powered predictions. Please consult with a healthcare professional for personalized medical advice.
        </div>
      </div>
    </div>
  );
};

export default SurveyResult;
