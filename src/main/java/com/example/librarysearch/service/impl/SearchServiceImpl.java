package com.example.librarysearch.service.impl;

import com.example.librarysearch.Entry.SearchHistoryEntry;
import com.example.librarysearch.Mapper.SearchCountMapper;
import com.example.librarysearch.Mapper.SearchHistoryMapper;
import com.example.librarysearch.service.SearchService;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 搜索服务实现类
 * 提供图书搜索、搜索历史记录和缓存管理等功能
 */
@Service
@EnableScheduling
public class SearchServiceImpl implements SearchService {

    /** Z-Library搜索URL */
    public static final String Z_LIBRARY_SEARCH_URL = "https://zh.z-lib.gl/s/";
    
    /** 音频文件存储目录 */
    public static final String AUDIO_DIRECTORY = System.getProperty("user.dir") + "/src/main/resources/static/audio/";
    
    /** 缓存文件存储目录 */
    public static final String CACHE_DIRECTORY = System.getProperty("user.dir") + "/src/main/resources/static/cache/";
    
    /** 缓存最大有效期(天) */
    public static final int MAX_CACHE_AGE_DAYS = 1; // 缓存保留1天
    
    /** 搜索历史记录存储目录 */
    public static final String SEARCH_HISTORY_DIRECTORY = System.getProperty("user.dir") + "/src/main/resources/static/SearchHistory/";
    
    /** 搜索计数文件路径 */
    public static final String SEARCH_COUNT_FILE = System.getProperty("user.dir") + "/src/main/resources/static/SearchHistory/search_count.txt";
    
    @Autowired
    private SearchHistoryMapper searchHistoryMapper;
    

    
    /**
     * 执行图书搜索
     * @param query 搜索关键词
     * @return 包含搜索结果和其他信息的Map
     * @throws Exception 搜索过程中可能发生的异常
     */
    public Map<String, Object> search(String query) throws Exception {
    	 long startTime = System.currentTimeMillis();
    	
        // Encode the search query
    	// 修改后的代码
    	String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8).replace("+", "%20");
        // Construct the search URL
        String searchUrl = Z_LIBRARY_SEARCH_URL + encodedQuery;

        // Record the search query
        recordSearchQuery(query);

        // Initialize response map
        Map<String, Object> responseMap = new HashMap<>();

        // Check if a cached HTML file exists
        File cachedFile = new File(CACHE_DIRECTORY + encodedQuery + ".html");
        String pageSource;

        if (isCacheValid(cachedFile)) {
            // Load HTML from cache
            System.out.println("Loading HTML from cache: " + cachedFile.getAbsolutePath());
            pageSource = loadHtmlFromCache(cachedFile);
        } else {
            // Configure ChromeDriver in headless mode
            ChromeOptions options = new ChromeOptions();
            
            // Specify the path to the user data directory using %USERPROFILE%
            //String userProfile = System.getenv("USERPROFILE");
            //options.addArguments("user-data-dir=" + userProfile + "\\AppData\\Local\\Google\\Chrome\\User Data");
            // 替代方案：使用临时profile目录
            //String tempProfileDir = System.getProperty("java.io.tmpdir") + "chrome-profile";
            //options.addArguments("user-data-dir=" + tempProfileDir);
            // 使用项目内的持久化profile目录
            String profileDir = new File("chrome-profiles/GetDLinkImpl").getAbsolutePath();
            options.addArguments("user-data-dir=" + profileDir);
            //options.addArguments("--headless");
            options.addArguments("--disable-gpu");
            options.addArguments("--remote-debugging-port=9222");
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
                System.out.println(author);
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

        // 在返回响应前添加耗时统计
        long totalTime = System.currentTimeMillis() - startTime;
        System.out.printf("[Search Timing] Query: '%s' | Duration: %d ms%n", query, totalTime);
        
        return responseMap;
    }

    /**
     * 获取热门搜索词
     * @param topN 返回的热门搜索词数量
     * @return 包含热门搜索词信息的列表
     */
    public List<Map<String, Object>> getTopSearches(int topN) {
        try {
            // Get today's date for the file name
            String date = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
            File historyFile = new File(SEARCH_HISTORY_DIRECTORY + date + ".json");

            // Load existing data if the file exists
            if (historyFile.exists()) {
                try (FileReader reader = new FileReader(historyFile)) {
                    Map<String, Map<String, Object>> searchHistory = new Gson().fromJson(
                            reader,
                            new TypeToken<Map<String, Map<String, Object>>>() {}.getType()
                    );

                    // Convert the map to a list and sort by weight in descending order
                    List<Map.Entry<String, Map<String, Object>>> sortedEntries = new ArrayList<>(searchHistory.entrySet());
                    sortedEntries.sort((entry1, entry2) -> {
                        int weight1 = ((Number) entry1.getValue().get("weight")).intValue();
                        int weight2 = ((Number) entry2.getValue().get("weight")).intValue();
                        return Integer.compare(weight2, weight1);
                    });

                    // Limit to top N results
                    List<Map<String, Object>> topSearches = new ArrayList<>();
                    for (int i = 0; i < Math.min(topN, sortedEntries.size()); i++) {
                        Map<String, Object> entry = new HashMap<>(sortedEntries.get(i).getValue());
                        entry.put("hash", sortedEntries.get(i).getKey());
                        topSearches.add(entry);
                    }

                    return topSearches;
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading top searches: " + e.getMessage());
        }
        return Collections.emptyList();
    }


    /**
     * 检查并创建所有需要的表
     */
    private void checkTables() {
        try {
            // 确保所有需要的目录都存在
            ensureDirectoryExists(SEARCH_HISTORY_DIRECTORY);
            ensureDirectoryExists(CACHE_DIRECTORY);
            ensureDirectoryExists(AUDIO_DIRECTORY);
            
            // 表结构验证已完成
            System.out.println("所有目录结构验证完成");
        } catch (Exception e) {
            System.err.println("目录结构验证失败: " + e.getMessage());
            throw new RuntimeException("目录初始化失败", e);
        }
    }

    /**
     * 确保指定目录存在，不存在则创建
     * @param directoryPath 目录路径
     */
    private void ensureDirectoryExists(String directoryPath) {
        File dir = new File(directoryPath);
        if (!dir.exists()) {
            boolean created = dir.mkdirs();
            if (created) {
                System.out.println("Created directory: " + directoryPath);
            } else {
                System.err.println("Failed to create directory: " + directoryPath);
            }
        }
    }

    /**
     * 记录搜索查询
     * @param query 搜索关键词
     */
    private void recordSearchQuery(String query) {
        try {
            // 确保表存在
            checkTables();
            
            // 确保搜索历史目录存在
            ensureDirectoryExists(SEARCH_HISTORY_DIRECTORY);

            // Get today's date for the file name
            String date = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
            File historyFile = new File(SEARCH_HISTORY_DIRECTORY + date + ".json");

            // Initialize search history map
            Map<String, Map<String, Object>> searchHistory = new HashMap<>();

            // Load existing data if the file exists
            if (historyFile.exists()) {
                try (FileReader reader = new FileReader(historyFile)) {
                    searchHistory = new Gson().fromJson(reader, new TypeToken<Map<String, Map<String, Object>>>() {}.getType());
                    if (searchHistory == null) {
                        searchHistory = new HashMap<>();
                    }
                }
            }

            // Hash the search term using SHA-256
            String hashedQuery = hashQuery(query);

            // Update or add the hashed term in the search history
            Map<String, Object> termData = searchHistory.getOrDefault(hashedQuery, new HashMap<>());
            int weight = termData.containsKey("weight") ? ((Number) termData.get("weight")).intValue() + 1 : 1; // Safely handle type
            termData.put("original", query);
            termData.put("weight", weight);
            searchHistory.put(hashedQuery, termData);

            // Save updated history
            try (FileWriter writer = new FileWriter(historyFile)) {
                new Gson().toJson(searchHistory, writer);
            }

            // Increment search count and check if sorting is needed
            int searchCount = incrementSearchCount();
            if (searchCount % 5 == 0) {
                sortAndSaveHistory(searchHistory, historyFile);
            }
        } catch (IOException e) {
            System.err.println("Error recording search query: " + e.getMessage());
        }
    }

    /**
     * 增加搜索计数
     * @return 增加后的搜索计数
     * @throws IOException 文件读写异常
     */
    private int incrementSearchCount() throws IOException {
        // 确保表存在
        checkTables();
        File countFile = new File(SEARCH_COUNT_FILE);
        int count = 0;

        // 确保目录和文件存在
        File historyDir = new File(SEARCH_HISTORY_DIRECTORY);
        if (!historyDir.exists()) {
            historyDir.mkdirs();
        }
        
        // 如果文件不存在则创建并初始化计数为0
        if (!countFile.exists()) {
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(countFile))) {
                writer.write("0");
            }
            System.out.println("Created new search count file: " + SEARCH_COUNT_FILE);
        }

        // Read the current count from the file
        try (BufferedReader reader = new BufferedReader(new FileReader(countFile))) {
            String line = reader.readLine();
            if (line != null) {
                count = Integer.parseInt(line.trim());
            }
        }

        // Increment and write the updated count
        count++;
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(countFile))) {
            writer.write(String.valueOf(count));
        }

        System.out.println("Current search count: " + count); // 添加日志
        return count;
    }

    /**
     * 排序并保存搜索历史
     * @param searchHistory 搜索历史数据
     * @param historyFile 历史文件
     * @throws IOException 文件读写异常
     */
    private void sortAndSaveHistory(Map<String, Map<String, Object>> searchHistory, File historyFile) throws IOException {
        // Sort search history by weight in descending order
        List<Map.Entry<String, Map<String, Object>>> sortedEntries = new ArrayList<>(searchHistory.entrySet());
        sortedEntries.sort((entry1, entry2) -> {
            int weight1 = ((Number) entry1.getValue().get("weight")).intValue();
            int weight2 = ((Number) entry2.getValue().get("weight")).intValue();
            return Integer.compare(weight2, weight1);
        });

        System.out.println("Sorted Entries: " + sortedEntries); // 调试：输出排序后的结果

        // Convert sorted entries back to a map
        Map<String, Map<String, Object>> sortedHistory = new LinkedHashMap<>();
        for (Map.Entry<String, Map<String, Object>> entry : sortedEntries) {
            sortedHistory.put(entry.getKey(), entry.getValue());
        }
        
        // 保存到数据库
        for (Map.Entry<String, Map<String, Object>> entry : sortedEntries) {
            try {
                SearchHistoryEntry dbEntry = new SearchHistoryEntry();
                dbEntry.setHash(entry.getKey());
                dbEntry.setOriginalQuery((String) entry.getValue().get("original"));
                dbEntry.setWeight(((Number) entry.getValue().get("weight")).intValue());
                dbEntry.setSearchDate(new java.sql.Date(System.currentTimeMillis())); // 使用当前时间

                try {
                    // 构建并插入记录
                    searchHistoryMapper.insertOrUpdate(dbEntry);
                } catch (Exception e) {
                    System.err.println("数据库操作失败: " + e.getMessage());
                    e.printStackTrace();
                }
            
                
                System.out.println("Uploaded into MySQL: " + dbEntry.getHash());
            } catch (Exception e) {
                System.err.println("Error inserting/updating record: " + e.getMessage());
                e.printStackTrace();
            }
        }

        // Save the sorted history back to the file
        try (FileWriter writer = new FileWriter(historyFile)) {
            new Gson().toJson(sortedHistory, writer);
        }

        System.out.println("Search history sorted and saved after 5 searches.");
    }



    /**
     * 对搜索词进行哈希处理
     * @param query 搜索关键词
     * @return 哈希后的字符串
     */
    private String hashQuery(String query) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(query.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Error hashing query", e);
        }
    }


    /**
     * 从缓存加载HTML内容
     * @param cachedFile 缓存文件
     * @return HTML内容字符串
     */
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

    /**
     * 保存HTML内容到缓存
     * @param query 搜索关键词
     * @param htmlContent HTML内容
     */
    public void saveHtmlToCache(String query, String htmlContent) {
        try {
            // 确保表存在
            checkTables();
            
            // 确保缓存目录存在
            ensureDirectoryExists(CACHE_DIRECTORY);

            // Create a file for the cached HTML
            String cacheFilePath = CACHE_DIRECTORY + query + ".html";
            try (FileWriter writer = new FileWriter(cacheFilePath)) {
                writer.write(htmlContent);
            }
        } catch (IOException e) {
            System.err.println("Error saving HTML to cache: " + e.getMessage());
        }
    }

    /**
     * 检查缓存是否有效
     * @param cachedFile 缓存文件
     * @return 缓存是否有效
     */
    private boolean isCacheValid(File cachedFile) {
        if (cachedFile.exists() && cachedFile.isFile()) {
            long lastModified = cachedFile.lastModified();
            long currentTime = System.currentTimeMillis();
            long expirationTime = 3 * 24 * 60 * 60 * 1000L; // 1 day in milliseconds
            return (currentTime - lastModified) < expirationTime;
        }
        return false;
    }
    
}




