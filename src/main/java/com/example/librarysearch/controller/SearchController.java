package com.example.librarysearch.controller;

import com.example.librarysearch.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/search")
@CrossOrigin(origins = "*") // Allow all origins (use with caution in production)
public class SearchController {

    @Autowired
    private SearchService searchService;

    /**
     * Endpoint to fetch the top searches.
     *
     * @param top the number of top searches to retrieve (default is 10).
     * @return a list of top searches.
     */
    @GetMapping("/top-searches")
    public ResponseEntity<List<Map<String, Object>>> getTopSearches(@RequestParam(defaultValue = "10") int top) {
        try {
            List<Map<String, Object>> topSearches = searchService.getTopSearches(top);
            if (topSearches.isEmpty()) {
                return ResponseEntity.noContent().build(); // Return 204 if no data
            }
            return ResponseEntity.ok(topSearches);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(null); // Internal Server Error
        }
    }

    /**
     * Endpoint to perform a search.
     *
     * @param query the search keyword provided by the user.
     * @return search results or an error message.
     */
    @GetMapping
    public ResponseEntity<?> search(@RequestParam("q") String query) {
        if (query == null || query.trim().isEmpty()) {
            return ResponseEntity.badRequest().body("Search query cannot be empty.");
        }

        try {
            Map<String, Object> results = searchService.search(query);
            if (results.isEmpty()) {
                return ResponseEntity.noContent().build(); // Return 204 if no results found
            }
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("An error occurred while performing the search.");
        }
    }
}
