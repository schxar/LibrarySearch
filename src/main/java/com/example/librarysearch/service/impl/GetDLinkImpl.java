package com.example.librarysearch.service.impl;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.stereotype.Service;
import java.io.File;
import java.util.HashMap;
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

            // 使用项目内的持久化profile目录
            String profileDir = new File("chrome-profiles/GetDLinkImpl").getAbsolutePath();
            options.addArguments("user-data-dir=" + profileDir);
            // Remove "--headless" if you want to see browser actions
            //options.addArguments("--headless"); 

            // 设置下载目录
            String downloadDir = new File("src/main/resources/static/books").getAbsolutePath();
            HashMap<String, Object> chromePrefs = new HashMap<>();
            chromePrefs.put("download.default_directory", downloadDir);
            chromePrefs.put("download.prompt_for_download", false);
            options.setExperimentalOption("prefs", chromePrefs);
            
            // 其他Chrome选项
            options.addArguments("--disable-gpu");
            options.addArguments("--no-sandbox");
            options.addArguments("--disable-dev-shm-usage");

        // 初始化WebDriver实例
        WebDriver driver = new ChromeDriver(options);
        String downloadUrl = null;

        try {
            // 首先访问下载页面获取限额
            driver.get("https://zh.z-lib.gl/users/downloads");
            Thread.sleep(2000);
            
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
                        
                    } catch (NumberFormatException e) {
                        System.out.println("无法解析下载限额: " + downloadLimitText);
                    }
                }
                
                // 获取进度条信息
                WebElement progressBar = driver.findElement(By.cssSelector("div.progress-bar"));
                String progress = progressBar.getAttribute("style");
                System.out.println("下载额度消耗进度: " + progress);
                
                // 解析进度百分比并检查下载限额状态
                if (progress != null && progress.contains("width:")) {
                    String widthStr = progress.split("width:")[1].split("%")[0].trim();
                    try {
                        double progressPercent = Double.parseDouble(widthStr);
                        System.out.println("解析到下载额度剩余进度百分比: " + progressPercent + "%");
                        
                        if (progressPercent >= 100) {
                            System.out.println("Shutting Down Webdriver.");
                            driver.quit();
                            return "NO_QUOTA_REMAINING|COOLING";
                        } else if (progressPercent > 90) {
                            System.out.println("Shutting Down Webdriver.");
                            driver.quit();
                            return "NO_QUOTA_REMAINING|UNLOCKED";
                        }
                    } catch (NumberFormatException e) {
                        System.out.println("无法解析进度百分比: " + progress);
                    }
                }
                
            } catch (Exception e) {
                System.out.println("无法获取下载信息: " + e.getMessage());
            }
            
            // 导航到目标书籍页面
            driver.get(bookUrl);

            // 检查是否需要登录
            try {
                WebElement loginElement = driver.findElement(By.cssSelector("a[data-action='login']"));
                if (loginElement != null) {
                    // Open the login window
                    loginElement.click();
                    Thread.sleep(600000);


                    // Wait for the page to load after login
                    Thread.sleep(2000); // Adjust this sleep time as needed
                    System.out.println("请打开Chrome进行登录操作，然后关闭窗口重启Java后端  并再次点击下载到flask文件服务器。");
                    Thread.sleep(600000);
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
            
            // 检查目标文件夹是否已存在同名文件（增加大小和格式匹配）
            File dir = new File(downloadDir);
            // 确保下载目录存在
            if (!dir.exists()) {
                boolean created = dir.mkdirs();
                if (created) {
                    System.out.println("Created download directory: " + downloadDir);
                } else {
                    System.err.println("Failed to create download directory: " + downloadDir);
                }
            }
            File[] files = dir.listFiles();
            if (files != null) {
                // 获取远程文件信息
                String remoteInfo = "";
                String remoteSize = "";
                String remoteFormat = "";
                try {
                    WebElement fileInfo = driver.findElement(By.cssSelector("div.bookProperty.property__file div.property_value"));
                    remoteInfo = fileInfo.getText();
                    System.out.println("远程文件信息: " + remoteInfo);
                    
                    // 解析远程文件大小和格式
                    String[] remoteParts = remoteInfo.split(",");
                    if (remoteParts.length >= 2) {
                        remoteFormat = remoteParts[0].trim().toLowerCase();
                        remoteSize = remoteParts[1].trim().toLowerCase().replace("mb", "").replace("kb", "").trim();
                    }
                } catch (Exception e) {
                    System.out.println("无法获取远程文件信息: " + e.getMessage());
                }
                
                for (File file : files) {
                    // 获取书名头两个字母作为额外验证条件
                    String firstTwoLetters = bookTitle.length() >= 2 ? 
                        bookTitle.substring(0, 2).toLowerCase() : bookTitle.toLowerCase();
                    
                    // 检测完整书名、前20个字符或头两个字母匹配的文件
                    String shortTitle = bookTitle.length() > 20 ? bookTitle.substring(0, 20) : bookTitle;
                    if (file.getName().toLowerCase().startsWith(bookTitle.toLowerCase()) || 
                        file.getName().toLowerCase().startsWith(shortTitle.toLowerCase()) ||
                        file.getName().toLowerCase().startsWith(firstTwoLetters)) {
                        
                        long fileSize = file.length();
                        String sizeFormatted = fileSize < 1024 ? fileSize + " B" : 
                            fileSize < 1024 * 1024 ? (fileSize / 1024) + " KB" : 
                            (fileSize / (1024 * 1024)) + " MB";
                        String fileExt = getFileExtension(file.getName()).toLowerCase();
                        
                        System.out.println("检测到可能匹配的文件: " + file.getAbsolutePath());
                        System.out.println("本地文件信息:");
                        System.out.println("  大小: " + sizeFormatted);
                        System.out.println("  格式: " + fileExt);
                        
                        // 如果获取到了远程文件信息，进行详细比较
                        if (!remoteInfo.isEmpty()) {
                            // 比较文件格式
                            boolean formatMatch = fileExt.equals(remoteFormat);
                            
                            // 比较文件大小（允许10%的误差）
                            boolean sizeMatch = false;
                            try {
                                double remoteSizeValue = Double.parseDouble(remoteSize);
                                double localSizeValue = fileSize / (1024.0 * 1024.0); // 转换为MB
                                sizeMatch = Math.abs(localSizeValue - remoteSizeValue) <= remoteSizeValue * 0.1;
                            } catch (NumberFormatException e) {
                                System.out.println("无法比较文件大小: " + e.getMessage());
                            }
                            
                            if (formatMatch && sizeMatch) {
                                System.out.println("文件大小和格式匹配，确认是同一文件，跳过下载");
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
                            } else {
                                System.out.println("文件大小或格式不匹配，继续下载流程");
                            }
                        } else {
                            System.out.println("无法获取远程文件信息，跳过详细比较");
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
            }

                    // 构建搜索URL使用书名前两个词
                    String[] titleWords = bookTitle.split("\\s+");
                    String searchQuery = "";
                    if (titleWords.length > 0) {
                        searchQuery = titleWords[0];
                        if (titleWords.length > 1) {
                            searchQuery += " " + titleWords[1];
                        }
                    }
                    // 安全限制searchQuery最多20个字符
                    if (!searchQuery.isEmpty() && searchQuery.length() > 20) {
                        searchQuery = searchQuery.substring(0, Math.min(searchQuery.length(), 20));
                    }
                    if (!searchQuery.isEmpty()) {
                        downloadUrl = "https://schxar.picp.vip/search?book_name=" + 
                            java.net.URLEncoder.encode(searchQuery, "UTF-8");
                    } else {
                        downloadUrl = "https://schxar.picp.vip/search";
                    }

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
            System.out.println("等待5秒确保下载启动...");
            Thread.sleep(5000);
            
            // 增强版下载检测逻辑
            long startTime = System.currentTimeMillis();
            long timeout = 120000; // 5分钟超时(大文件需要更长时间)
            boolean downloadStarted = false;
            long lastFileSize = 0;
            int noProgressCount = 0;
            
            while (System.currentTimeMillis() - startTime < timeout) {
                File[] downloadingFiles = dir.listFiles();
                if (downloadingFiles != null) {
                    boolean shouldBreak = false;
                    for (File file : downloadingFiles) {
                        // 检测.crdownload文件
                        if (file.getName().endsWith(".crdownload")) {
                            downloadStarted = true;
                            long currentSize = file.length();
                            if (currentSize > lastFileSize) {
                                System.out.println(String.format("下载中... 当前大小: %.2fMB", currentSize/1024.0/1024.0));
                                lastFileSize = currentSize;
                                noProgressCount = 0;
                            } else {
                                noProgressCount++;
                                if (noProgressCount > 3) {
                                    System.out.println("警告: 下载进度已停滞超过6秒");
                                }
                            }
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
                        
                        // 安全检测书名前20个字符模糊搜索
                    String shortTitle = "";
                    if (!bookTitle.isEmpty()) {
                        shortTitle = bookTitle.substring(0, Math.min(bookTitle.length(), 20));
                    }
                    if (!shortTitle.isEmpty() && file.getName().startsWith(shortTitle)) {
                        System.out.println("检测到书名前20个字符匹配文件已存在");
                        shouldBreak = true;
                        break;
                    }
                    }
                    if (shouldBreak) break;
                    
                    // 检查是否长时间无进展
                    if (noProgressCount > 10) { // 20秒无进展
                        System.out.println("下载停滞超过20秒，可能已失败");
                        break;
                    }
                }
                
                if (!downloadStarted) {
                    System.out.println("等待下载开始...");
                }
                
                Thread.sleep(2000); // 每2秒检查一次
            }
            
            if (System.currentTimeMillis() - startTime >= timeout) {
                System.out.println("下载超时，请检查网络连接或尝试重新下载");
                
                // 检查是否已有完整文件
                File[] downloadedFiles = dir.listFiles();
                if (downloadedFiles != null) {
                    for (File file : downloadedFiles) {
                        // 检查是否匹配书名且不是.crdownload文件
                        if ((file.getName().startsWith(bookTitle) || 
                             file.getName().startsWith(titleWords[0] + " " + titleWords[1])) &&
                            !file.getName().endsWith(".crdownload")) {
                            
                            long fileSize = file.length();
                            String sizeFormatted = fileSize < 1024 ? fileSize + " B" : 
                                fileSize < 1024 * 1024 ? (fileSize / 1024) + " KB" : 
                                (fileSize / (1024 * 1024)) + " MB";
                            String fileExt = getFileExtension(file.getName());
                            
                            System.out.println("检测到已下载文件: " + file.getAbsolutePath());
                            System.out.println("文件大小: " + sizeFormatted);
                            System.out.println("文件格式: " + fileExt);
                            
                            // 获取远程文件信息进行比较
                            try {
                                WebElement fileInfo = driver.findElement(By.cssSelector("div.bookProperty.property__file div.property_value"));
                                String remoteInfo = fileInfo.getText();
                                System.out.println("远程文件信息: " + remoteInfo);
                                
                                // 检查文件大小是否匹配
                                if (remoteInfo.toLowerCase().contains(fileExt.toLowerCase()) && 
                                    remoteInfo.contains(sizeFormatted.replace(" MB", "").replace(" KB", "").replace(" B", ""))) {
                                    System.out.println("文件大小和格式验证成功，下载已完成");
                                    return downloadUrl;
                                }
                            } catch (Exception e) {
                                System.out.println("无法获取远程文件信息: " + e.getMessage());
                            }
                        }
                    }
                }
            } else {
                System.out.println("下载检测完成，总耗时: " + (System.currentTimeMillis() - startTime) + "ms");
            }
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