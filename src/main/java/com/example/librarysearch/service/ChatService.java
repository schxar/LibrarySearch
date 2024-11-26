package com.example.librarysearch.service;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;

@Service
public class ChatService {
	public Map<String, Object> processMessages(List<Map<String, String>> messages) {
	    // 示例逻辑，处理用户消息
	    String userMessage = messages.stream()
	                                  .filter(msg -> "user".equals(msg.get("role")))
	                                  .map(msg -> msg.get("content"))
	                                  .findFirst()
	                                  .orElse("未收到用户消息");

	    // 返回响应
	    return Map.of("response", "你发送了: " + userMessage);
	}
}
