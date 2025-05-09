package com.example.librarysearch.service.impl;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.stereotype.Service;
import java.io.File;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 实现获取电子书下载链接的服务类
 * 使用Selenium WebDriver自动化浏览器操作获取下载链接
 */
@Service
public class GetDLinkImpl {

    /**
     * 获取电子书的下载链接
     * @param bookUrl 电子书详情页URL
     * @return 下载链接URL，如果获取失败则返回null
     */
    public String getDownloadLink(String bookUrl) {
        // 配置Chrome浏览器选项
        ChromeOptions options = new ChromeOptions();

        // Specify the path to the user data directory using %USERPROFILE%
        String userProfile = System.getenv("USERPROFILE");
        options.addArguments("user-data-dir=" + userProfile + "\\AppData\\Local\\Google\\Chrome\\User Data");
        
        // Remove "--headless" if you want to see browser actions
        options.addArguments("--headless"); 
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");

        // 初始化WebDriver实例
        WebDriver driver = new ChromeDriver(options);
        String downloadUrl = null;

        try {
            // 首先访问下载页面获取限额
            driver.get("https://zh.z-lib.gl/users/downloads");
            Thread.sleep(2000); // 等待2秒确保页面加载
            
            // 获取下载限额和刷新时间信息
            try {
                // 获取下载限额
                WebElement downloadLimitElement = driver.findElement(By.cssSelector("div.m-v-auto.d-count"));
                String downloadLimitText = downloadLimitElement.getText().trim();
                
                // 获取刷新时间
                WebElement resetTimeElement = driver.findElement(By.cssSelector("div.m-v-auto.d-reset"));
                String resetTime = resetTimeElement.getText().trim();
                
                System.out.println("下载限额信息: " + downloadLimitText);
                System.out.println("下载量刷新时间: " + resetTime);
                
                // 解析下载限额格式(如"4/10"或"999/999")
                String[] limitParts = downloadLimitText.split("/");
                if (limitParts.length == 2) {
                    try {
                        int remaining = Integer.parseInt(limitParts[0].trim());
                        int total = Integer.parseInt(limitParts[1].trim());
                        
                        // 检查下载限额状态
                        if (total == 10 && remaining <= 0) {
                            System.out.println("Shutting Down Webdriver.");
                            driver.quit();
                            return "NO_QUOTA_REMAINING|COOLING";
                        } else if (total == 999 && remaining <= 0) {
                            System.out.println("Shutting Down Webdriver.");
                            driver.quit();
                            return "NO_QUOTA_REMAINING|UNLOCKED";
                        }
                    } catch (NumberFormatException e) {
                        System.out.println("无法解析下载限额: " + downloadLimitText);
                    }
                }
                
                // 获取进度条信息
                WebElement progressBar = driver.findElement(By.cssSelector("div.progress-bar"));
                String progress = progressBar.getAttribute("style");
                System.out.println("下载额度消耗进度: " + progress);
                
            } catch (Exception e) {
                System.out.println("无法获取下载信息: " + e.getMessage());
            }
            
            // 然后导航到目标书籍页面
            driver.get(bookUrl);
            Thread.sleep(2000); // 等待2秒确保页面加载

            // 检查是否需要登录
            try {
                WebElement loginElement = driver.findElement(By.cssSelector("a[data-action='login']"));
                if (loginElement != null) {
                    // Open the login window
                    loginElement.click();



                    // Wait for the page to load after login
                    Thread.sleep(2000); // Adjust this sleep time as needed
                    System.out.println("请打开Chrome进行登录操作，然后关闭窗口重启Java后端  并再次点击下载到flask文件服务器。");
                }
            } catch (Exception e) {
                System.out.println("No login required, proceeding to fetch download link.");
            }

            // 定位书籍标题元素
            WebElement bookTitleElement = driver.findElement(By.cssSelector("h1.book-title"));
            String bookTitle = bookTitleElement.getText();
            System.out.println("Book Title: " + bookTitle);
            
            // 定位下载按钮元素
            WebElement downloadButton = driver.findElement(By.cssSelector("a.btn.btn-default.addDownloadedBook"));

            // 获取文件类型信息
            String extension = "";
            try {
                WebElement fileInfo = driver.findElement(By.cssSelector("div.bookProperty.property__file div.property_value"));
                String fileText = fileInfo.getText();
                if (fileText != null && !fileText.isEmpty()) {
                    extension = fileText.split(",")[0].trim().toLowerCase();
                } else {
                    extension = getFileExtension(bookUrl);
                }
            } catch (Exception e) {
                extension = getFileExtension(bookUrl);
            }
            
            // 检查目标文件夹是否已存在同名文件（不检查扩展名）
            String downloadDir = "C:\\Users\\PC\\eclipse-workspace\\LibrarySearch\\src\\main\\resources\\static\\books";
            File dir = new File(downloadDir);
            File[] files = dir.listFiles();
            if (files != null) {
                for (File file : files) {
                    // 检测完整书名或前20个字符匹配的文件
                    String shortTitle = bookTitle.length() > 20 ? bookTitle.substring(0, 20) : bookTitle;
                    if (file.getName().startsWith(bookTitle) || file.getName().startsWith(shortTitle)) {
                        long fileSize = file.length();
                        String sizeFormatted = fileSize < 1024 ? fileSize + " B" : 
                            fileSize < 1024 * 1024 ? (fileSize / 1024) + " KB" : 
                            (fileSize / (1024 * 1024)) + " MB";
                        System.out.println("文件已存在，跳过下载: " + file.getAbsolutePath());
                        System.out.println("本地文件信息:");
                        System.out.println("  大小: " + sizeFormatted);
                        System.out.println("  格式: " + getFileExtension(file.getName()));
                        try {
                            WebElement remoteFileInfo = driver.findElement(By.cssSelector("div.bookProperty.property__file div.property_value"));
                            String remoteInfo = remoteFileInfo.getText();
                            System.out.println("远程文件信息:");
                            System.out.println("  " + remoteInfo);
                        } catch (Exception e) {
                            System.out.println("无法获取远程文件信息: " + e.getMessage());
                        }
                        // 构建与下载URL相同格式的公网URL
                        String[] titleWords = bookTitle.split("\\s+");
                        String searchQuery = titleWords.length > 1 ? 
                            titleWords[0] + " " + titleWords[1] : 
                            titleWords[0];
                        // 限制searchQuery最多20个字符
                        if (searchQuery.length() > 20) {
                            searchQuery = searchQuery.substring(0, 20);
                        }
                        return "https://schxar.picp.vip/search?book_name=" + 
                            java.net.URLEncoder.encode(searchQuery, "UTF-8");
                    }
                }
            }

            // 构建搜索URL使用书名前两个词
            String[] titleWords = bookTitle.split("\\s+");
            String searchQuery = titleWords.length > 1 ? 
                titleWords[0] + " " + titleWords[1] : 
                titleWords[0];
            // 限制searchQuery最多20个字符
            if (searchQuery.length() > 20) {
                searchQuery = searchQuery.substring(0, 20);
            }
            downloadUrl = "https://schxar.picp.vip/search?book_name=" + 
                java.net.URLEncoder.encode(searchQuery, "UTF-8");

            // 点击下载按钮触发下载
            Thread.sleep(4000); // 等待4秒确保页面加载完成
            System.out.println("已完成4000ms页面加载等待");
            downloadButton.click();
            
            // 打印文件信息
            try {
                WebElement fileInfo = driver.findElement(By.cssSelector("div.bookProperty.property__file div.property_value"));
                String fileText = fileInfo.getText();
                System.out.println("File Info: " + fileText);
            } catch (Exception e) {
                System.out.println("无法获取文件信息: " + e.getMessage());
            }
            
            // 初始等待，确保.crdownload文件创建
            System.out.println("等待10秒确保下载启动...");
            Thread.sleep(10000);
            
            // 优化下载检测逻辑
            long startTime = System.currentTimeMillis();
            long timeout = 180000; // 3分钟超时
            boolean downloadStarted = false;
            long minExpectedSize = 100 * 1024; // 最小期望文件大小100KB
            
            while (System.currentTimeMillis() - startTime < timeout) {
                File[] downloadingFiles = dir.listFiles();
                if (downloadingFiles != null) {
                    boolean shouldBreak = false;
                    for (File file : downloadingFiles) {
                        // 检测.crdownload文件
                        if (file.getName().endsWith(".crdownload")) {
                            downloadStarted = true;
                            System.out.println("检测到下载中文件: " + file.getName() + " (" + file.length() + " bytes)");
                            continue;
                        }
                        
                        // 检查文件大小是否达到最小期望值
                        if (file.length() < minExpectedSize) {
                            System.out.println("文件过小，跳过: " + file.getName() + " (" + file.length() + " bytes)");
                            continue;
                        }
                        
                        // 增强文件名匹配逻辑
                        String normalizedBookTitle = bookTitle.replaceAll("[^a-zA-Z0-9\\s\\p{L}]", "").toLowerCase();
                        String normalizedFileName = file.getName().replaceAll("[^a-zA-Z0-9\\s\\p{L}]", "").toLowerCase();
                        
                        // 1. 检测完整书名匹配（相似度>90%）
                        if (calculateSimilarity(normalizedFileName, normalizedBookTitle) > 0.9) {
                            System.out.println("检测到完整书名匹配文件: " + file.getName());
                            shouldBreak = true;
                            break;
                        }
                        
                        // 2. 检测关键特征词匹配
                        String[] keywords = extractKeywords(normalizedBookTitle);
                        boolean allKeywordsMatch = true;
                        for (String keyword : keywords) {
                            if (!normalizedFileName.contains(keyword)) {
                                allKeywordsMatch = false;
                                break;
                            }
                        }
                        if (allKeywordsMatch && keywords.length > 0) {
                            System.out.println("检测到关键特征词匹配文件: " + file.getName());
                            shouldBreak = true;
                            break;
                        }
                        
                        // 3. 检测书名前30个字符匹配（提高阈值）
                        String shortTitle = normalizedBookTitle.length() > 30 ? 
                            normalizedBookTitle.substring(0, 30) : normalizedBookTitle;
                        if (normalizedFileName.contains(shortTitle) && shortTitle.length() >= 10) {
                            System.out.println("检测到书名前30字符匹配文件: " + file.getName());
                            shouldBreak = true;
                            break;
                        }
                    }
                    if (shouldBreak) break;
                }
                
                if (!downloadStarted) {
                    System.out.println("等待下载开始...剩余时间: " + (timeout - (System.currentTimeMillis() - startTime)) + "ms");
                }
                
                Thread.sleep(3000); // 每3秒检查一次
            }
            
            System.out.println("下载检测完成，总耗时: " + (System.currentTimeMillis() - startTime) + "ms");
        } catch (Exception e) {
            System.err.println("Error retrieving or clicking download URL for book: " + bookUrl + " - " + e.getMessage());
        } finally {
            if (driver != null) {
                // 关闭WebDriver释放资源
                System.out.println("Shutting Down Webdriver.");
                driver.quit();
            }
        }

        return downloadUrl;
    }
    
    /**
     * 从URL中提取文件扩展名
     * @param url 图书URL
     * @return 文件扩展名
     */
    private String getFileExtension(String url) {
        // 尝试从URL中匹配扩展名
        Pattern pattern = Pattern.compile("\\.([a-zA-Z0-9]+)(?:\\?|$)");
        Matcher matcher = pattern.matcher(url);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return "pdf"; // 默认扩展名
    }
    
    /**
     * 计算两个字符串的相似度（Levenshtein距离）
     */
    private double calculateSimilarity(String s1, String s2) {
        int maxLength = Math.max(s1.length(), s2.length());
        if (maxLength == 0) return 1.0;
        return (maxLength - calculateLevenshteinDistance(s1, s2)) / (double) maxLength;
    }
    
    /**
     * 计算Levenshtein距离
     */
    private int calculateLevenshteinDistance(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];
        
        for (int i = 0; i <= s1.length(); i++) {
            dp[i][0] = i;
        }
        
        for (int j = 0; j <= s2.length(); j++) {
            dp[0][j] = j;
        }
        
        for (int i = 1; i <= s1.length(); i++) {
            for (int j = 1; j <= s2.length(); j++) {
                int cost = (s1.charAt(i - 1) == s2.charAt(j - 1)) ? 0 : 1;
                dp[i][j] = Math.min(
                    Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1),
                    dp[i - 1][j - 1] + cost
                );
            }
        }
        
        return dp[s1.length()][s2.length()];
    }
    
    /**
     * 从书名中提取关键特征词
     */
    private String[] extractKeywords(String title) {
        // 过滤掉常见无意义词
        String[] stopWords = {"the", "and", "of", "in", "a", "to", "for", "with", "on", "at"};
        String filtered = title;
        for (String word : stopWords) {
            filtered = filtered.replaceAll("\\b" + word + "\\b", "");
        }
        
        // 提取长度大于3的词作为关键词
        return Arrays.stream(filtered.split("\\s+"))
            .filter(word -> word.length() > 3)
            .toArray(String[]::new);
    }
}
