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

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
public class SearchServiceImpl implements SearchService {

    private static final String Z_LIBRARY_SEARCH_URL = "https://lib.opendelta.org/s/";

    @Override
    public Map<String, Object> search(String query) throws Exception {
        // 编码搜索关键词
        String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
        // 构建完整的搜索 URL
        String searchUrl = Z_LIBRARY_SEARCH_URL + encodedQuery;

        // 设置 ChromeDriver 为无头模式
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");  // 设置无头模式
        options.addArguments("--disable-gpu");  // 如果您使用的是 Windows，建议禁用 GPU
        options.addArguments("--no-sandbox");  // 解决一些 Linux 环境中的问题
        options.addArguments("--disable-dev-shm-usage"); // 应对某些资源受限问题（例如 Docker）

        WebDriver driver = new ChromeDriver(options);  // 启动无头浏览器
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
                    String bookUrl = "https://lib.opendelta.org" + item.attr("href"); // 确保完整路径

                    Map<String, String> result = new HashMap<>();
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
