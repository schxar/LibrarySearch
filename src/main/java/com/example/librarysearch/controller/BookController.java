
package com.example.librarysearch.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;
import java.util.stream.Collectors;
import java.util.Arrays;
import java.util.stream.Stream;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Controller
public class BookController {
    
    private static final String BOOKS_DIR = "src/main/resources/static/books_data/";
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    private final RestTemplate restTemplate = new RestTemplate();

    @GetMapping("/booklist")
    public String listBooks(Model model) throws IOException {
        List<Book> books = new ArrayList<>();
        scanBooksDirectory(Paths.get(BOOKS_DIR), books);
        
        // 按书名排序
        books.sort(Comparator.comparing(Book::getTitle));
        
        model.addAttribute("books", books);
        model.addAttribute("homeUrl", "/"); // 添加主页URL
        return "books";
    }

    @GetMapping("/search/books")
    public String searchBooks(
        @RequestParam String book_name,
        @RequestParam(defaultValue = "1") int page,
        Model model) throws IOException {
        
        // 1. 首先调用REST API搜索端点
       // try {
       //     ResponseEntity<?> apiResponse = restTemplate.getForEntity(
      //          "http://localhost:8080/search?q={query}", 
      //          Object.class, 
      //          book_name
       //     );
      //      // 可在此处添加API响应处理逻辑（如果需要）
       // } catch (Exception e) {
            // 静默处理API调用异常，继续执行本地搜索
     //       System.err.println("API搜索调用失败: " + e.getMessage());
     //   }
        
        // 2. 预处理：确保图书数据已入库
        preprocessBooksData();
        
        // 3. 执行本地文件搜索
        List<Book> results = new ArrayList<>();
        Path booksDir = Paths.get(BOOKS_DIR);
        scanBooksDirectory(booksDir, results);

        // 改进的搜索策略
        String searchTerm = book_name.toLowerCase();
        List<String> keywords = extractKeywords(searchTerm);
        // 动态生成核心关键词：从搜索词中提取主要部分
        List<String> coreKeywords = keywords.stream()
            .filter(word -> word.length() > 3) // 过滤掉短词
            .collect(Collectors.toList());
        
        // 为每本书计算相关性得分
        List<Book> scoredResults = results.stream()
            .map(book -> {
                String title = book.getTitle().toLowerCase();
                int score = 0;
                
                // 0. 核心关键词必须匹配
                boolean matchesCoreKeywords = coreKeywords.isEmpty() || 
                    coreKeywords.stream().anyMatch(keyword -> title.contains(keyword));
                if (!matchesCoreKeywords) {
                    return new ScoredBook(book, -1); // 不匹配核心关键词直接过滤
                }
                
                // 1. 完整匹配搜索词得分最高
                if (title.contains(searchTerm)) {
                    score += 100;
                }
                
                // 2. 匹配所有关键词得分次高
                boolean matchesAllKeywords = keywords.stream()
                    .allMatch(keyword -> title.contains(keyword.toLowerCase()));
                if (matchesAllKeywords) {
                    score += 80;
                }
                
                // 3. 匹配部分关键词得分
                long matchedKeywords = keywords.stream()
                    .filter(keyword -> title.contains(keyword.toLowerCase()))
                    .count();
                score += matchedKeywords * 20;
                
                // 4. 关键词位置加分
                for (String keyword : keywords) {
                    int index = title.indexOf(keyword.toLowerCase());
                    if (index >= 0) {
                        // 关键词出现在标题开头加分更多
                        score += (title.length() - index) * 2;
                    }
                }
                
                return new ScoredBook(book, score);
            })
            .filter(scoredBook -> scoredBook.score > 0) // 只保留有匹配的结果
            .sorted(Comparator.comparingInt(ScoredBook::getScore).reversed()) // 按得分降序排序
            .map(ScoredBook::getBook)
            .collect(Collectors.toList());
            
        List<Book> filtered = new ArrayList<>(scoredResults);
        
        // 分页处理
        int pageSize = 10; // 每页显示10条结果
        int totalItems = filtered.size();
        int totalPages = (int) Math.ceil((double) totalItems / pageSize);
        
        // 确保页码在有效范围内
        page = Math.max(1, Math.min(page, totalPages));
        
        // 获取当前页数据
        int fromIndex = (page - 1) * pageSize;
        int toIndex = Math.min(fromIndex + pageSize, totalItems);
        List<Book> pagedResults = filtered.subList(fromIndex, toIndex);
        
        // 添加模型属性
        model.addAttribute("query", book_name);
        model.addAttribute("results", pagedResults);
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", totalPages);
        
        return "search_results";
    }

    /**
     * 预处理图书数据，确保所有JSON文件已入库
     */
    private void preprocessBooksData() throws IOException {
        List<Book> allBooks = new ArrayList<>();
        Path booksDir = Paths.get(BOOKS_DIR);
        
        // 扫描整个目录获取所有图书
        scanBooksDirectory(booksDir, allBooks);
        
        // 这里可以添加额外的预处理逻辑，如：
        // - 数据校验
        // - 索引构建
        // - 缓存预热
        // 当前仅确保所有JSON文件已被扫描
    }

    private boolean isChinese(String str) {
        return str.codePoints().anyMatch(codepoint -> 
            Character.UnicodeScript.of(codepoint) == Character.UnicodeScript.HAN);
    }
    
    /**
     * 从搜索词中提取所有关键词
     */
    private List<String> extractKeywords(String searchTerm) {
        // 保留字母、数字、空格和连字符
        String cleaned = searchTerm.replaceAll("[^a-zA-Z0-9\\s-]", " ");
        // 分割并返回所有非空词
        return Arrays.stream(cleaned.split("\\s+"))
            .filter(word -> !word.isEmpty())
            // 对包含连字符的词，同时保留完整形式和拆分形式
            .flatMap(word -> {
                if (word.contains("-")) {
                    return Stream.concat(
                        Stream.of(word), // 保留原始带连字符的词
                        Arrays.stream(word.split("-")) // 同时添加拆分后的词
                    );
                }
                return Stream.of(word);
            })
            .distinct()
            .collect(Collectors.toList());
    }

    private void scanBooksDirectory(Path dir, List<Book> books) throws IOException {
        File[] files = dir.toFile().listFiles();
        if (files == null) return;

        for (File file : files) {
            if (file.isDirectory()) {
                scanBooksDirectory(file.toPath(), books);
            } else if (file.getName().endsWith(".json")) {
                try {
                    String content = new String(Files.readAllBytes(file.toPath()));
                    Book book = objectMapper.readValue(content, Book.class);
                    books.add(book);
                } catch (IOException e) {
                    System.err.println("Error reading file: " + file.getPath());
                }
            }
        }
    }

    public static class Book {
        private String id;
        private String title;
        private String bookUrl;

        // Getters and Setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getBookUrl() { return bookUrl; }
        public void setBookUrl(String bookUrl) { this.bookUrl = bookUrl; }
    }
    
    private static class ScoredBook {
        private final Book book;
        private final int score;
        
        public ScoredBook(Book book, int score) {
            this.book = book;
            this.score = score;
        }
        
        public Book getBook() { return book; }
        public int getScore() { return score; }
    }
}
