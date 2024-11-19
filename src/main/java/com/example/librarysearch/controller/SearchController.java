package com.example.librarysearch.controller;

import com.example.librarysearch.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class SearchController {

    @Autowired
    private SearchService searchService;

    @GetMapping("/")
    public String index() {
        return "index"; // 返回 src/main/resources/templates/index.html
    }

    @GetMapping("/search")
    @ResponseBody
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
