# LibrarySearch 项目文档

## 项目概述
集成AI聊天、图书搜索和多媒体处理的综合服务平台，包含：
- Flask Python后端服务
- Java Spring Boot图书搜索服务
- 前端交互界面

## 核心功能
1. **AI聊天服务**：支持文本/图片输入，工具自动调用
2. **图书搜索**：集成Z-Library搜索和下载
3. **多媒体处理**：图片内容分析和音频处理

## 技术架构
```mermaid
graph TD
    A[Flask后端] --> B[AI服务]
    A --> C[图书搜索]
    D[Java服务] --> C
    E[前端] --> A
    E --> D
```

```mermaid
graph TD
    %% 核心业务流程
    subgraph 用户界面
        A[用户] -->|请求| B(Flask主服务)
        A -->|聊天/搜索| C(Flask聊天服务)
    end

    subgraph 核心业务流程
        B -->|转发请求| C
        C --> D[Python工具模块]
        D --> E{Java后端}
        D --> F[豆包API]
        D --> G[谷歌搜索API]
        D --> H[Selenium]
        
        E --> H
        H --> I[浏览器]
        I --> J[Z-Library]
    end

    subgraph 数据存储
        K[MySQL数据库]
        L[文件系统]
    end

    %% 流程连接
    C -->|1.聊天处理| F
    D -->|2.在线搜索| E
    E -->|3.下载管理| H
    B -->|4.历史查询| K
    F -->|5.推荐生成| K
    B -->|6.文件服务| L
    B -->|7.工单提交| K

    %% 样式定义
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bbf,stroke:#333
    style D fill:#cfc,stroke:#333
    style E fill:#ffc,stroke:#333
    style F fill:#ccf,stroke:#333
    style G fill:#ccf,stroke:#333
    style H fill:#fcf,stroke:#333
    style K fill:#ddf,stroke:#333
    style L fill:#ddd,stroke:#333
    style I fill:#eee,stroke:#333
    style J fill:#eee,stroke:#333

    %% 流程标注
    click C "#1-聊天处理流程" _blank
    click D "#2-在线搜索流程" _blank
    click E "#3-下载管理流程" _blank
    click B "#4-历史查询流程" _blank
    click F "#5-推荐生成流程" _blank
    click B "#6-文件服务流程" _blank
    click B "#7-工单提交流程" _blank
```


```mermaid
graph TD
    %% 系统组件定义
    A[用户界面] --> |网页/表单/API调用| B{Flask主应用.端口10805};
    B --> |转发API请求| C{Flask豆包/聊天服务.端口10806};
    B <--> |下载历史.推荐数据| G[MySQL数据库];
    B --> |文件服务| H[文件系统];
    B --> |生成推荐| I[豆包API];

    C --> |工具执行| D[Python工具模块];
    C <--> |聊天历史| H;
    C <--> |大模型调用| I;

    D --> |ZLib API调用| E{Java后端.端口8080};
    D --> |大模型服务| I;
    D --> |网页搜索| J[谷歌CSE API];
    D --> |页面分析| K[Selenium];

    E --> |浏览器自动化| K;
    E --> |搜索历史| G;
    E <--> |本地数据| H;

    K --> |控制| L[浏览器实例];
    L <--> |交互| M[Z-Library网站];

    %% 数据流向
    G --> |查询结果| B;
    H --> |文件数据| B;
    H --> |配置/聊天| C;
    H --> |缓存/数据| E;
    E --> |API响应| D;
    I --> |大模型结果| D;
    I --> |推荐结果| B;
    I --> |聊天响应| C;
    J --> |搜索结果| D;
    M --> |页面数据| L;

    %% 样式定义
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bbf,stroke:#333
    style D fill:#cfc,stroke:#333
    style E fill:#ffc,stroke:#333
    style G fill:#ddf,stroke:#333
    style H fill:#ddd,stroke:#333
    style I fill:#ccf,stroke:#333
    style J fill:#ccf,stroke:#333
    style K fill:#fcf,stroke:#333
    style L fill:#eee,stroke:#333
    style M fill:#eee,stroke:#333
```



## 详细文档
- [Flask后端文档](flask_openai_backend/FLASK_BACKEND_DOC.md)
- [Java服务文档](src/main/java/com/example/librarysearch/JAVA_DOC.md)

## 快速开始
```bash
# 启动Flask服务
python flask_openai_backend/doubao_combined_service.py

# 启动Java服务
./mvnw spring-boot:run
