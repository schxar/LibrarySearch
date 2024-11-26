package com.example.librarysearch.controller;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.librarysearch.service.ChatService; // 假设有一个服务类处理聊天逻辑

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*") // 允许所有来源（请根据需要谨慎使用）
public class ChatController {

    @Autowired
    private ChatService chatService;

    @PostMapping("/chat")
    public ResponseEntity<?> chat(@RequestBody Map<String, Object> request) {
        try {
            // 获取消息列表
            List<Map<String, String>> messages = (List<Map<String, String>>) request.get("messages");

            // 调用服务处理逻辑
            Map<String, Object> response = chatService.processMessages(messages);

            // 返回成功响应
            HttpHeaders headers = new HttpHeaders();
            headers.add("Content-Type", "application/json");
            return ResponseEntity.ok().headers(headers).body(response);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("处理失败");
        }
    }
}
