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

    // Endpoint to fetch top searches
    @GetMapping("/top-searches")
    public List<Map<String, Object>> getTopSearches(@RequestParam(defaultValue = "10") int top) {
        return searchService.getTopSearches(top);
    }

    // Endpoint to perform a search
    @GetMapping
    public ResponseEntity<?> search(@RequestParam("q") String query) {
        try {
            Map<String, Object> results = searchService.search(query);
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Search failed.");
        }
    }
}


