
package com.example.librarysearch.task;

import com.example.librarysearch.service.impl.SearchServiceImpl;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.io.File;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;

@Component
public class CachePreloaderTask {

    @Autowired
    private SearchServiceImpl searchService;

    // 每6小时执行一次预加载
    @Scheduled(fixedRate = 6 * 60 * 60 * 1000)
    public void preloadPopularSearches() {
        // 不再每次清理缓存，由定时任务单独处理
        if (new File(SearchServiceImpl.CACHE_DIRECTORY).exists()) {
            // 如果缓存目录已存在且有文件，则跳过预加载
            if (new File(SearchServiceImpl.CACHE_DIRECTORY).list().length > 0) {
                System.out.println("缓存已存在，跳过预加载");
                return;
            }
        }
        // 获取热门搜索词（前10个）
        List<String> popularQueries = getPopularQueries(10);
        
        // 初始化无头Chrome
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        
        WebDriver driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);

        try {
            for (String query : popularQueries) {
                try {
                    // 构造搜索URL
                    String searchUrl = SearchServiceImpl.Z_LIBRARY_SEARCH_URL + 
                        java.net.URLEncoder.encode(query, "UTF-8").replace("+", "%20");
                    
                    // 访问页面获取HTML
                    driver.get(searchUrl);
                    String pageSource = driver.getPageSource();
                    
                    // 保存到缓存
                    searchService.saveHtmlToCache(query, pageSource);
                    
                    System.out.println("Preloaded cache for query: " + query);
                } catch (Exception e) {
                    System.err.println("Failed to preload query: " + query + ", error: " + e.getMessage());
                }
            }
        } finally {
            driver.quit();
        }
    }

    private List<String> getPopularQueries(int count) {
        // 从搜索历史文件获取实际热门查询
        File historyDir = new File(SearchServiceImpl.SEARCH_HISTORY_DIRECTORY);
        if (historyDir.exists()) {
            // 实现读取历史文件逻辑
            // 简化为返回固定词
            return List.of("Java", "Python", "Machine Learning", "Spring Boot", "React");
        }
        return Collections.emptyList();
    }

    // 每天清理一次过期缓存
    @Scheduled(fixedRate = 24 * 60 * 60 * 1000)
    public void cleanOldCache() {
        File cacheDir = new File(SearchServiceImpl.CACHE_DIRECTORY);
        if (cacheDir.exists()) {
            long cutoff = System.currentTimeMillis() - 
                TimeUnit.DAYS.toMillis(SearchServiceImpl.MAX_CACHE_AGE_DAYS);
            
            Arrays.stream(cacheDir.listFiles())
                .filter(file -> file.lastModified() < cutoff)
                .forEach(file -> {
                    if (file.delete()) {
                        System.out.println("Deleted old cache: " + file.getName());
                    }
                });
        }
    }
}
