graph TD
    A[User Interface] --> B{Flask Main App<br>(Port 10805)}: Requests (Web Pages, Some APIs);
    B --> C{Flask Doubao/Chat Service<br>(Port 10806)}: Forwards API Requests<br>(e.g., /api/doubao/chat) [1-3];
    B --> I[MySQL Database]: Accesses Download History [4-6]<br>and Recommendations [1, 7, 8];
    B --> J[File System]: Serves Downloaded Files [5]<br>Searches Local Book Data [9-11]<br>Manages Chat History Files [12-14]<br>Loads CSE Config [15];

    C --> D[Python Tools Module]: Calls Tool Functions [16, 17];
    C --> F[Doubao API]: Direct Chat Completions [18, 19];

    D --> F: Embeddings [20-23]<br>Evaluation [24-34]<br>Tool Search [35-37]<br>VLM Analysis [26, 38];
    D --> G[Google CSE API]: Web Search [39];
    D --> E{Java Backend<br>(Library Search & Download)}: Calls API<br>(ZLib Search /search [40, 41], Get DLink /getdlink [27, 42]);
    D --> H[Selenium WebDriver]: Page Analysis (via Google CSE) [43, 44];

    E --> H: ZLib Search Scraping [45, 46], Get DLink [47, 48];
    E --> I: Records Search History [49-52];
    E --> J: Saves Book Data (JSON) [53, 54]<br>Downloads Files [48, 55];
    E --> K[Z-Library Website]: Target for Scraping and Download [46, 56, 57];

    H --> L[Browser Instance]: Controlled by Selenium [43, 47, 58];
    L --> K: Browses and Interacts with Z-Library;

    I --> E: Search History Data (for processing/sorting) [59];
    I --> B; % Data Flow Back to Flask Main App

    J --> B; % Data Flow Back to Flask Main App (e.g., file content, search results)
    J --> E; % Load/Save Data (e.g., search history files, cache) [50, 60-63]
    J --> D: Config Files (e.g., CSE config) [15];

    F --> C; % Chat Responses
    F --> D; % Tool/Embedding/Eval Responses
    G --> D: Search Results;
    E --> D: Search & DLink Results;

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#cfc,stroke:#333,stroke-width:2px
    style E fill:#ffc,stroke:#333,stroke-width:2px
    style F fill:#ccf,stroke:#333,stroke-width:2px
    style G fill:#ccf,stroke:#333,stroke-width:2px
    style H fill:#fcf,stroke:#333,stroke-width:2px
    style I fill:#ddf,stroke:#333,stroke-width:2px
    style J fill:#ddd,stroke:#333,stroke-width:2px
    style K fill:#eee,stroke:#333,stroke-width:2px
    style L fill:#eee,stroke:#333,stroke-width:2px