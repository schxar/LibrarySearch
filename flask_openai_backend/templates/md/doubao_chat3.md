# doubao_chat3.html 说明文档

## 文件功能
主聊天界面，提供以下功能：
- 文本消息发送
- 图片文件上传
- 聊天历史展示
- 响应式布局

## 核心代码结构

### HTML结构
```html
<div class="chat-container">
    <div id="chatHistory"><!-- 消息展示区 --></div>
    <div class="input-area">
        <textarea id="userInput"></textarea>
        <input type="file" id="imageUpload">
    </div>
</div>
```

### JavaScript功能
```javascript
// 消息发送处理
document.getElementById('sendButton').addEventListener('click', async () => {
    const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({message: input.value})
    });
    // 更新消息展示
});
```

## 相关文件
- 样式文件：`static/css/chat.css`
- 后端接口：`flask_openai_backend/app.py`
