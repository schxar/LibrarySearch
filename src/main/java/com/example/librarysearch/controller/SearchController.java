package com.example.librarysearch.controller;

import com.example.librarysearch.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Map;

/**
 * Controller for handling search related requests.
 * Provides endpoints for performing searches and retrieving search statistics.
 * Note: CORS is enabled for all origins (development only).
 */
@RestController
@RequestMapping("/search")
@CrossOrigin(origins = "*") // Allow all origins (development only - restrict in production)
public class SearchController {

    @Autowired
    private SearchService searchService; // Service layer for search operations

    /**
     * Endpoint to fetch the top searches.
     *
     * @param top the number of top searches to retrieve (default is 10).
     * @return ResponseEntity containing:
     *         - 200 OK with list of top searches if successful
     *         - 204 No Content if no search data available
     *         - 500 Internal Server Error if exception occurs
     */
    @GetMapping("/top-searches")
    public ResponseEntity<List<Map<String, Object>>> getTopSearches(@RequestParam(defaultValue = "10") int top) {
        try {
            // Retrieve top searches from service layer
            List<Map<String, Object>> topSearches = searchService.getTopSearches(top);
            
            // Handle empty result case
            if (topSearches.isEmpty()) {
                return ResponseEntity.noContent().build(); // Return 204 if no data
            }
            
            // Return successful response with top searches
            return ResponseEntity.ok(topSearches);
        } catch (Exception e) {
            // Log error and return error response
            e.printStackTrace();
            return ResponseEntity.status(500).body(null); // Internal Server Error
        }
    }

    /**
     * Endpoint to perform a search.
     *
     * @param query the search keyword provided by the user.
     * @return ResponseEntity containing:
     *         - 200 OK with search results if successful
     *         - 400 Bad Request if query is empty
     *         - 204 No Content if no results found
     *         - 500 Internal Server Error if exception occurs
     */
    @GetMapping
    public ResponseEntity<?> search(@RequestParam("q") String query) {
        // Validate input query
        if (query == null || query.trim().isEmpty()) {
            return ResponseEntity.badRequest().body("Search query cannot be empty.");
        }

        try {
            // Perform search through service layer
            Map<String, Object> results = searchService.search(query);
            
            // Handle empty result case
            if (results.isEmpty()) {
                return ResponseEntity.noContent().build(); // Return 204 if no results found
            }
            
            // Return successful response with search results
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            // Log error and return error response
            e.printStackTrace();
            return ResponseEntity.status(500).body("An error occurred while performing the search.");
        }
    }
}
