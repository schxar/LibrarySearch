package com.example.librarysearch.service.impl;

import com.example.librarysearch.service.SearchService;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
public class SearchServiceImpl implements SearchService {

    private static final String Z_LIBRARY_SEARCH_URL = "https://zh.z-lib.gl/s/";
    private static final String AUDIO_DIRECTORY = System.getProperty("user.dir") + "/src/main/resources/static/audio/";
    private static final String CACHE_DIRECTORY = System.getProperty("user.dir") + "/src/main/resources/static/cache/";

    @Override
    public Map<String, Object> search(String query) throws Exception {
        // Encode the search query
        String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
        // Construct the search URL
        String searchUrl = Z_LIBRARY_SEARCH_URL + encodedQuery;

        // Initialize response map
        Map<String, Object> responseMap = new HashMap<>();

        // Check if a cached HTML file exists
        File cachedFile = new File(CACHE_DIRECTORY + encodedQuery + ".html");
        String pageSource;

        if (cachedFile.exists() && cachedFile.isFile()) {
            // Load HTML from cache
            System.out.println("Loading HTML from cache: " + cachedFile.getAbsolutePath());
            pageSource = loadHtmlFromCache(cachedFile);
        } else {
            // Configure ChromeDriver in headless mode
            ChromeOptions options = new ChromeOptions();
            options.addArguments("--headless");
            options.addArguments("--disable-gpu");
            options.addArguments("--no-sandbox");
            options.addArguments("--disable-dev-shm-usage");

            WebDriver driver = new ChromeDriver(options);

            try {
                driver.get(searchUrl);

                // Retrieve the full page HTML source code
                pageSource = driver.getPageSource();

                // Save the HTML to a cache file
                saveHtmlToCache(encodedQuery, pageSource);
            } finally {
                // Close and exit the browser
                driver.quit();
            }
        }

        // Parse the HTML page
        Document doc = Jsoup.parse(pageSource);

        // Extract the search results section
        Element searchResultsBox = doc.getElementById("searchResultBox");
        List<Map<String, String>> results = new ArrayList<>();

        if (searchResultsBox != null) {
            // Select each book card
            Elements items = searchResultsBox.select("z-bookcard");
            for (Element item : items) {
                String id = item.attr("id");
                String title = item.select("[slot=title]").text();
                String author = item.select("[slot=author]").text();
                String isbn = item.attr("isbn");
                String publisher = item.attr("publisher");
                String language = item.attr("language");
                String year = item.attr("year");
                String extension = item.attr("extension");
                String filesize = item.attr("filesize");
                String rating = item.attr("rating");
                String quality = item.attr("quality");
                String coverUrl = item.select("img").attr("data-src");
                String bookUrl = "https://zh.z-lib.gl" + item.attr("href");

                // Check if the audio file exists
                String audioFilePath = AUDIO_DIRECTORY + id + ".wav";
                boolean audioExists = new File(audioFilePath).exists();

                Map<String, String> result = new HashMap<>();
                result.put("id", id);
                result.put("title", title);
                result.put("author", author);
                result.put("isbn", isbn);
                result.put("publisher", publisher);
                result.put("language", language);
                result.put("year", year);
                result.put("extension", extension);
                result.put("filesize", filesize);
                result.put("rating", rating);
                result.put("quality", quality);
                result.put("cover_url", coverUrl);
                result.put("book_url", bookUrl);
                result.put("audioExists", String.valueOf(audioExists)); // Include audio existence info

                results.add(result);
            }
            responseMap.put("results", results);
        } else {
            System.out.println("Search results box not found.");
        }

        return responseMap;
    }

    private String loadHtmlFromCache(File cachedFile) {
        try (FileReader reader = new FileReader(cachedFile)) {
            StringBuilder sb = new StringBuilder();
            char[] buffer = new char[1024];
            int length;
            while ((length = reader.read(buffer)) > 0) {
                sb.append(buffer, 0, length);
            }
            return sb.toString();
        } catch (IOException e) {
            System.err.println("Error loading HTML from cache: " + e.getMessage());
            return null;
        }
    }

    private void saveHtmlToCache(String query, String htmlContent) {
        try {
            // Ensure the cache directory exists
            File cacheDir = new File(CACHE_DIRECTORY);
            if (!cacheDir.exists()) {
                cacheDir.mkdirs();
            }

            // Create a file for the cached HTML
            String cacheFilePath = CACHE_DIRECTORY + query + ".html";
            try (FileWriter writer = new FileWriter(cacheFilePath)) {
                writer.write(htmlContent);
            }
        } catch (IOException e) {
            System.err.println("Error saving HTML to cache: " + e.getMessage());
        }
    }
}
