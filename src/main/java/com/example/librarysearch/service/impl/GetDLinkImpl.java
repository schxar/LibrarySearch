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
        // Set up ChromeOptions
        ChromeOptions options = new ChromeOptions();

        // Specify the path to the user data directory using %USERPROFILE%
        String userProfile = System.getenv("USERPROFILE");
        options.addArguments("user-data-dir=" + userProfile + "\\AppData\\Local\\Google\\Chrome\\User Data");
        
        // Remove "--headless" if you want to see browser actions
        //options.addArguments("--headless"); 
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");

        // Initialize WebDriver with options
        WebDriver driver = new ChromeDriver(options);
        String downloadUrl = null;

        try {
            driver.get(bookUrl);

            // Check if login is required
            try {
                WebElement loginElement = driver.findElement(By.cssSelector("a[data-action='login']"));
                if (loginElement != null) {
                    // Open the login window
                    loginElement.click();



                    // Wait for the page to load after login
                    Thread.sleep(2000); // Adjust this sleep time as needed
                }
            } catch (Exception e) {
                System.out.println("No login required, proceeding to fetch download link.");
            }

            // Locate the book title element
            WebElement bookTitleElement = driver.findElement(By.cssSelector("h1.book-title"));
            String bookTitle = bookTitleElement.getText();
            System.out.println("Book Title: " + bookTitle);
            
            // Locate the download button
            WebElement downloadButton = driver.findElement(By.cssSelector("a.btn.btn-default.addDownloadedBook"));

            // Extract the href attribute of the download button
            downloadUrl = downloadButton.getAttribute("href");

            // Click the download button to trigger the download
            Thread.sleep(4000); // Adjust this sleep time as needed
            downloadButton.click();
            Thread.sleep(600000); // Adjust this sleep time as needed
        } catch (Exception e) {
            System.err.println("Error retrieving or clicking download URL for book: " + bookUrl + " - " + e.getMessage());
        } finally {
            // Temporarily comment out driver.quit() for testing purposes
        	System.out.println("Shutting Down Webdriver.");
            driver.quit();
        }

        return downloadUrl;
    }
}
