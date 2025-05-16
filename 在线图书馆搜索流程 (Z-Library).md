```mermaid
graph TD
    A[搜索触发 (e.g., 来自聊天)] --> B(Flask: 调用 zlib_search 工具);
    B --> C(Flask 发送 HTTP GET /search 到 Java 后端);
    C --> D(Java 后端接收请求);
    D --> K(Java: 记录搜索查询到文件/DB); %% 并行记录
    D --> E(Java: 检查 HTML 缓存);
    E --> F{缓存有效且未过期?};
    F -- 是 --> G(Java: 从缓存加载 HTML);
    F -- 否 --> H(Java: 使用 Selenium 爬取 Z-Library);
    H --> I(Java: 保存 HTML 到缓存);
    G --> J(Java: 解析 HTML (Jsoup));
    I --> J;
    J --> L(Java: 提取书籍信息);
    L --> M(Java: 保存书籍元数据到本地 JSON);
    L --> N(Java: 准备并返回搜索结果给 Flask);
    N --> O(Flask: 接收并处理结果<br/>(可选使用模型));
    O --> P(Flask: 发送结果到浏览器);
```