package com.example.librarysearch.service;

import java.util.List;
import java.util.Map;

public interface SearchService {
    // Existing methods
    Map<String, Object> search(String query) throws Exception;

    // New method to get top searches
    List<Map<String, Object>> getTopSearches(int top);
}
