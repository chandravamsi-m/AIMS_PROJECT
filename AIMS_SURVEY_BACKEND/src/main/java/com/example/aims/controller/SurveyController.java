package com.example.aims.controller;

import com.example.aims.model.Patient;
import com.example.aims.model.Survey;
import com.example.aims.service.PdfService;
import com.example.aims.service.SurveyService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.example.aims.service.MlService;

import javax.servlet.http.HttpServletResponse;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class SurveyController {

    private final SurveyService surveyService;
    private final PdfService pdfService;
    private final MlService mlService;

    public SurveyController(SurveyService surveyService, PdfService pdfService, MlService mlService) {
        this.surveyService = surveyService;
        this.pdfService = pdfService;
        this.mlService = mlService;
    }

    @PostMapping("/patients")
    public ResponseEntity<Patient> savePatient(@RequestBody Patient patient) {
        Patient saved = surveyService.savePatient(patient);
        return ResponseEntity.ok(saved);
    }

    @GetMapping("/patients")
    public ResponseEntity<List<Patient>> getAllPatients() {
        return ResponseEntity.ok(surveyService.getAllPatients());
    }

    @GetMapping("/patients/{id}")
    public ResponseEntity<Patient> getPatientById(@PathVariable String id) {
        Patient patient = surveyService.getPatientById(id);
        if (patient != null) {
            return ResponseEntity.ok(patient);
        }
        return ResponseEntity.notFound().build();
    }

    @PostMapping("/patients/search-results")
    public ResponseEntity<List<Patient>> searchPatients(@RequestBody Map<String, String> payload) {
        String keyword = payload.get("keyword");
        List<Patient> matched = surveyService.searchPatientsByName(keyword);
        return ResponseEntity.ok(matched);
    }

    @PostMapping("/surveys")
    public ResponseEntity<Survey> saveSurvey(@RequestBody Survey survey) {
        Survey saved = surveyService.saveSurvey(survey);
        return ResponseEntity.ok(saved);
    }

    @PostMapping("/download-pdf")
    public void downloadPdf(@RequestBody Map<String, Object> payload, HttpServletResponse response) {
        ObjectMapper mapper = new ObjectMapper();
        Patient patient = mapper.convertValue(payload.get("patient"), Patient.class);
        Survey survey = mapper.convertValue(payload.get("survey"), Survey.class);
        String chartBase64 = (String) payload.get("chartImage");

        if (patient != null && survey != null) {
            pdfService.generatePdf(patient, survey, chartBase64, response);
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    @GetMapping("/surveys/by-patient-id/{id}")
    public ResponseEntity<Survey> getSurveyByPatientId(@PathVariable String id) {
        return surveyService.getSurveyByPatientId(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/predict-future")
    public ResponseEntity<Map<String, Object>> predictFuture(@RequestBody Map<String, Object> surveyData) {
        try {
            Map<String, Object> result = mlService.getPredictionRaw(surveyData);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500)
                    .body(Map.of("error", "Prediction service failed: " + e.getMessage()));
        }
    }

    @PostMapping("/predict")
    public ResponseEntity<Map<String, Object>> predictCurrent(@RequestBody Map<String, Object> surveyData) {
        try {
            Map<String, Object> result = mlService.getCurrentPrediction(surveyData);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500)
                    .body(Map.of("error", "Current prediction failed: " + e.getMessage()));
        }
    }


}
