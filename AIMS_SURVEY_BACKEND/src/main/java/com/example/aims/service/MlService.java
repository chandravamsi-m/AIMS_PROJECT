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
    private final String FLASK_URL = "http://localhost:5001/predict";

    public Map<String, Object> getPredictionRaw(Map<String, Integer> surveyData) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Integer>> request = new HttpEntity<>(surveyData, headers);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(FLASK_URL, request, Map.class);
            return response.getBody(); // contains assessment, severityScore, suggestions
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("assessment", "Unavailable");
            fallback.put("severityScore", "N/A");
            fallback.put("suggestions", List.of("Prediction service is currently unreachable."));
            return fallback;
        }
    }

}
