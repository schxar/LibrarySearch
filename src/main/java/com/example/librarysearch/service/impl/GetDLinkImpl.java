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

            // Extract the href attribute of the download button
            downloadUrl = downloadButton.getAttribute("href");

            // 点击下载按钮触发下载
            Thread.sleep(4000); // 等待4秒确保页面加载完成
            System.out.println("已完成4000ms页面加载等待");
            downloadButton.click();
            
            // 初始等待，确保.crdownload文件创建
            System.out.println("等待10秒确保下载启动...");
            Thread.sleep(10000);
            
            // 提取书名前两个单词作为匹配模式
            String[] words = bookTitle.split(" ");
            String firstWord = words[0].replaceAll("[^a-zA-Z0-9]", "_");
            String secondWord = words.length > 1 ? words[1].replaceAll("[^a-zA-Z0-9]", "_") : "";
            String fileNamePattern = firstWord + (secondWord.isEmpty() ? "" : "_" + secondWord);
            System.out.println("正在查找匹配文件: " + fileNamePattern);
            
            // 检查下载目录中的文件
            fileNamePattern += "*." + getFileExtension(bookUrl);
            String downloadDir = "C:\\Users\\PC\\eclipse-workspace\\LibrarySearch\\src\\main\\resources\\static\\books";
            File dir = new File(downloadDir);
            long startTime = System.currentTimeMillis();
            long timeout = 120000; // 2分钟超时
            boolean downloadStarted = false;
            
            while (System.currentTimeMillis() - startTime < timeout) {
                boolean fileFound = false;
                File[] files = dir.listFiles();
                if (files != null) {
                    for (File file : files) {
                        // 检查.crdownload文件或匹配文件名模式
                        if (file.getName().endsWith(".crdownload") || 
                            file.getName().toLowerCase().matches(fileNamePattern.toLowerCase().replace("*", ".*"))) {
                            fileFound = true;
                            break;
                        }
                    }
                }
                
                if (fileFound) {
                    downloadStarted = true;
                    System.out.println("检测到相关文件，下载仍在进行中...");
                } else if (downloadStarted) {
                    System.out.println("下载已完成：相关文件已存在");
                    break;
                } else {
                    System.out.println("未检测到相关文件，等待5秒后重试...");
                }
                
                Thread.sleep(5000); // 每5秒检查一次
            }
            
            System.out.println("下载等待完成，总耗时: " + (System.currentTimeMillis() - startTime) + "ms");
        } catch (Exception e) {
            System.err.println("Error retrieving or clicking download URL for book: " + bookUrl + " - " + e.getMessage());
        } finally {
            // 关闭WebDriver释放资源
            System.out.println("Shutting Down Webdriver.");
            driver.quit();
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
