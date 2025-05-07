package com.example.librarysearch.controller;

import com.example.librarysearch.service.ChatService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Controller for handling chat related requests.
 * Provides endpoint for sending messages to the chat service and receiving responses.
 * Communicates with a Flask backend for message processing.
 */
@RestController
@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    private ChatService chatService; // Service for handling chat operations

    /**
     * Endpoint for sending chat messages to the backend.
     *
     * @param message The chat message from the user
     * @return ResponseEntity containing:
     *         - 200 OK with the response message if successful
     *         - 500 Internal Server Error if an exception occurs
     */
    @PostMapping("/send")
    public ResponseEntity<String> sendMessage(@RequestBody String message) {
        try {
            // Forward message to chat service which communicates with Flask backend
            String flaskResponse = chatService.getFlaskResponse(message);
            
            // Return successful response with the processed message
            return ResponseEntity.ok(flaskResponse);
        } catch (Exception e) {
            // Return error response if any exception occurs
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }
}
