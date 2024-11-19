package com.example.librarysearch.service;

import java.util.Map;

public interface SearchService {
    Map<String, Object> search(String query) throws Exception;
}
