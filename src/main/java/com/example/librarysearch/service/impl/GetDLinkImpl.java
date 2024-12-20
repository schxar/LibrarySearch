package com.example.librarysearch.service.impl;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.springframework.stereotype.Service;

@Service
public class GetDLinkImpl {

    public String getDownloadLink(String bookUrl) {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");

        WebDriver driver = new ChromeDriver(options);
        String downloadUrl = null;

        try {
            driver.get(bookUrl);

            // Locate the download button
            WebElement downloadButton = driver.findElement(By.cssSelector("a.btn.btn-default.addDownloadedBook"));

            // Extract the href attribute of the download button
            downloadUrl = downloadButton.getAttribute("href");
        } catch (Exception e) {
            System.err.println("Error retrieving download URL for book: " + bookUrl + " - " + e.getMessage());
        } finally {
            driver.quit();
        }

        return downloadUrl;
    }
}
