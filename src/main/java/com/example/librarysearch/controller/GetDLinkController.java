package com.example.librarysearch.controller;

import com.example.librarysearch.service.impl.GetDLinkImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Controller for handling download link requests.
 * Provides endpoint to retrieve download links for books.
 */
@RestController
@RequestMapping("/getdlink")
public class GetDLinkController {

    @Autowired
    private GetDLinkImpl getDLinkService;

    /**
     * Retrieves download link for a given book URL.
     *
     * @param requestBody Request body containing book URL
     * @return Map containing either:
     *         - "downloadLink": valid download link if successful
     *         - "error": error message if failed
     */
    @PostMapping
    public Map<String, String> getDownloadLink(@RequestBody Map<String, String> requestBody) {
        // Extract book URL from request
        String bookUrl = requestBody.get("bookUrl");
        Map<String, String> response = new HashMap<>();

        // Validate book URL
        if (bookUrl == null || bookUrl.isEmpty()) {
            response.put("error", "Invalid bookUrl");
            return response;
        }

        try {
            // Attempt to get download link from service
            String downloadLink = getDLinkService.getDownloadLink(bookUrl);
            
            if (downloadLink != null) {
                // Return successful response with download link
                response.put("downloadLink", downloadLink);
            } else {
                // Return error if no download link found
                response.put("error", "Download link not found");
            }
        } catch (Exception e) {
            // Handle any exceptions and return error message
            response.put("error", "Failed to retrieve download link: " + e.getMessage());
        }

        return response;
    }
}
