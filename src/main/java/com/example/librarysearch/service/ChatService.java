package com.example.librarysearch.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.HashMap;
import java.util.Map;

@Service
public class ChatService {

    private static final String FLASK_URL = "http://127.0.0.1:10803/generate";

    public String getFlaskResponse(String message) {
        // Create a RestTemplate instance
        RestTemplate restTemplate = new RestTemplate();

        // Prepare the request payload
        Map<String, String> payload = new HashMap<>();
        payload.put("message", message);

        // Set HTTP headers
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        // Create an HTTP entity with headers and body
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(payload, headers);

        // Send POST request to Flask API
        ResponseEntity<String> response = restTemplate.exchange(
            FLASK_URL,
            HttpMethod.POST,
            entity,
            String.class
        );

        // Return Flask's response body
        return response.getBody();
    }
}
