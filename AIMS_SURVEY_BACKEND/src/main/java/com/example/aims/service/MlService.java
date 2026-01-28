package com.example.aims.service;

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MlService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String FLASK_URL_CURRENT = "http://localhost:5001/predict";
    private final String FLASK_URL_FUTURE = "http://localhost:5001/predict-future";

    // ---- For current condition ----
    public Map<String, Object> getCurrentPrediction(Map<String, Object> surveyData) {
        return callFlaskModel(FLASK_URL_CURRENT, surveyData);
    }

    // ---- For future condition ----
    public Map<String, Object> getPredictionRaw(Map<String, Object> surveyData) {
        return callFlaskModel(FLASK_URL_FUTURE, surveyData);
    }

    // ---- Common reusable method ----
    private Map<String, Object> callFlaskModel(String url, Map<String, Object> surveyData) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(surveyData, headers);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            return response.getBody();
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("error", "Prediction service unreachable");
            fallback.put("trend", "N/A");
            fallback.put("suggestions", List.of("Unable to fetch AI predictions. Try again later."));
            return fallback;
        }
    }
}
