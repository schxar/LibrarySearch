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
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
public class SearchServiceImpl implements SearchService {

    private static final String Z_LIBRARY_SEARCH_URL = "https://zh.z-lib.gl/s/";
    private static final String AUDIO_DIRECTORY = System.getProperty("user.dir") + "/src/main/resources/static/audio/";

    @Override
    public Map<String, Object> search(String query) throws Exception {
        // 编码搜索关键词
        String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
        // 构建完整的搜索 URL
        String searchUrl = Z_LIBRARY_SEARCH_URL + encodedQuery;

        // 设置 ChromeDriver 为无头模式
        ChromeOptions options = new ChromeOptions();
        //options.addArguments("--headless");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");

        WebDriver driver = new ChromeDriver(options);
        Map<String, Object> responseMap = new HashMap<>();

        try {
            driver.get(searchUrl);
            // 获取完整页面的 HTML 源代码
            String pageSource = driver.getPageSource();

            // 解析 HTML 页面
            Document doc = Jsoup.parse(pageSource);

            // 提取包含搜索结果的部分
            Element searchResultsBox = doc.getElementById("searchResultBox");
            List<Map<String, String>> results = new ArrayList<>();

            if (searchResultsBox != null) {
                // 向下选择每个书籍卡片
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

                    // 检查音频文件是否存在
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
                    result.put("audioExists", String.valueOf(audioExists)); // 传递音频文件存在信息

                    results.add(result);
                }
                responseMap.put("results", results);
            } else {
                System.out.println("搜索结果框未找到。");
            }

        } finally {
            // 关闭并退出浏览器
            driver.quit();
        }

        return responseMap;
    }
}
