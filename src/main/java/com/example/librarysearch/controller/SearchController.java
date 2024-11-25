package com.example.librarysearch.controller;

import com.example.librarysearch.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.Map;

@RestController
@RequestMapping("/search")
@CrossOrigin(origins = "*") // 允许所有来源（请根据需要谨慎使用）
public class SearchController {

    @Autowired
    private SearchService searchService;

    @GetMapping
    public ResponseEntity<?> search(@RequestParam("q") String query) {
        try {
            Map<String, Object> results = searchService.search(query);
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("搜索失败");
        }
    }
}
