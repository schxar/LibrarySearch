package com.example.librarysearch.service.impl;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.stereotype.Service;
import java.io.File;
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
            // 导航到目标书籍页面
            driver.get(bookUrl);

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
            long timeout = 120000; // 2分钟超时
            boolean downloadStarted = false;
            
            while (System.currentTimeMillis() - startTime < timeout) {
                File[] downloadingFiles = dir.listFiles();
                if (downloadingFiles != null) {
                    boolean shouldBreak = false;
                    for (File file : downloadingFiles) {
                        // 检测.crdownload文件
                        if (file.getName().endsWith(".crdownload")) {
                            downloadStarted = true;
                            System.out.println("检测到下载中文件...");
                            // 不立即返回，继续等待下载完成
                            continue;
                        }
                        // 检测完整书名文件
                        if (file.getName().startsWith(bookTitle)) {
                            System.out.println("检测到完整书名文件已存在");
                            shouldBreak = true;
                            break;
                        }
                        // 检测书名前两个词文件
                        
                        if (titleWords.length > 1 && file.getName().startsWith(titleWords[0] + " " + titleWords[1])) {
                            System.out.println("检测到书名关键词文件已存在");
                            shouldBreak = true;
                            break;
                        }
                        // 新增书名前20个字符模糊搜索
                        String shortTitle = bookTitle.length() > 20 ? bookTitle.substring(0, 20) : bookTitle;
                        if (file.getName().startsWith(shortTitle)) {
                            System.out.println("检测到书名前20个字符匹配文件已存在");
                            shouldBreak = true;
                            break;
                        }
                    }
                    if (shouldBreak) break;
                }
                
                if (!downloadStarted) {
                    System.out.println("等待下载开始...");
                }
                
                Thread.sleep(2000); // 每2秒检查一次
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
}
