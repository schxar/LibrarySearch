import React, { useState } from 'react';
import './App.css';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';

interface Result {
  extension: string;
  cover_url: string;
  year: string;
  author: string;
  isbn: string;
  rating: string;
  language: string;
  filesize: string;
  title: string;
  quality: string;
  book_url: string;
  publisher: string;
  id: string;
  audioExists: string;
}

const App: React.FC = () => {
  const [url, setUrl] = useState<string>('');
  const [results, setResults] = useState<Result[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadedAudios, setLoadedAudios] = useState<Record<string, boolean>>({}); // 记录已加载音频的状态

  const handleTestApi = async () => {
    if (!url.trim()) {
      alert("请输入测试的 URL");
      return;
    }
    
    try {
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setResults(data.results || []);
      setError(null);
      setLoadedAudios({}); // 重置已加载音频的状态
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setResults([]);
    }
  };

  const handleLoadAudio = (id: string) => {
    setLoadedAudios((prev) => ({ ...prev, [id]: true })); // 更新已加载音频的状态
  };

  return (
    <div className="container mt-5">
      <h1>http://127.0.0.1:8080/search?q=dog</h1>
      
      <header>
        <SignedOut>
          <SignInButton />
        </SignedOut>
        <SignedIn>
          <UserButton />
          <div className="input-group mb-3">
            <input
              type="text"
              className="form-control"
              placeholder="输入需要搜索的内容 如http://127.0.0.1:8080/search?q=dog"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button 
              className="btn btn-primary" 
              onClick={handleTestApi} 
              disabled={!url.trim()}
            >
              发送请求
            </button>
          </div>
        </SignedIn>
      </header>

      {error && <div className="alert alert-danger">Error: {error}</div>}
      {results.length > 0 ? (
        <div className="alert alert-success">
          <h5>Response:</h5>
          <ul className="list-group">
            {results.map((item) => (
              <li className="list-group-item" key={item.id}>
                {item.cover_url && (
                  <img
                    src={item.cover_url}
                    alt="封面"
                    className="img-thumbnail"
                    style={{ maxWidth: '100px', float: 'left', marginRight: '10px' }}
                  />
                )}
                <h5>
                  <strong>{item.title}</strong>
                </h5>
                <p><strong>Author:</strong> {item.author}</p>
                <p><strong>ISBN:</strong> {item.isbn}</p>
                <p><strong>Publisher:</strong> {item.publisher}</p>
                <p><strong>Language:</strong> {item.language}</p>
                <p><strong>Year:</strong> {item.year}</p>
                <p><strong>File Type:</strong> {item.extension}</p>
                <p><strong>File Size:</strong> {item.filesize}</p>
                <p><strong>Rating:</strong> {item.rating}</p>
                <p><strong>Quality:</strong> {item.quality}</p>
                <a href={item.book_url} target="_blank" rel="noopener noreferrer">
                  查看详情
                </a>
                {item.audioExists === 'true' && (
                  <div>
                    {!loadedAudios[item.id] ? (
                      <button 
                        className="btn btn-secondary" 
                        onClick={() => handleLoadAudio(item.id)}
                      >
                        播放音频
                      </button>
                    ) : (
                      <audio controls>
                        <source src={`http://127.0.0.1:8080/audio/${item.id}.wav`} type="audio/wav" />
                        您的浏览器不支持音频播放器。
                      </audio>
                    )}
                  </div>
                )}
                <div style={{ clear: 'both' }}></div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        !error && <div className="alert alert-warning" role="alert">无搜索结果</div>
      )}
    </div>
  );
}

export default App;
