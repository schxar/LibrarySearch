package com.example.librarysearch.controller;

import com.example.librarysearch.service.impl.GetDLinkImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/getdlink")
public class GetDLinkController {

    @Autowired
    private GetDLinkImpl getDLinkService;

    @PostMapping
    public Map<String, String> getDownloadLink(@RequestBody Map<String, String> requestBody) {
        String bookUrl = requestBody.get("bookUrl");
        Map<String, String> response = new HashMap<>();

        if (bookUrl == null || bookUrl.isEmpty()) {
            response.put("error", "Invalid bookUrl");
            return response;
        }

        try {
            String downloadLink = getDLinkService.getDownloadLink(bookUrl);
            if (downloadLink != null) {
                response.put("downloadLink", downloadLink);
            } else {
                response.put("error", "Download link not found");
            }
        } catch (Exception e) {
            response.put("error", "Failed to retrieve download link: " + e.getMessage());
        }

        return response;
    }
}
