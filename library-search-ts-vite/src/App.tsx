import React, { useState, ChangeEvent, KeyboardEvent } from 'react';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  publisher: string;
  language: string;
  year: string;
  extension: string;
  filesize: string;
  rating: string;
  quality: string;
  cover_url: string;
  book_url: string;
  audioExists: string;
}

const App: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<Book[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("请输入搜索关键词");
      return;
    }
    try {
      const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      alert("搜索失败，请稍后再试");
    }
  };

  return (
    <div className="container mt-5">
      <header>
        <SignedOut>
          <SignInButton />
        </SignedOut>
        <SignedIn>
          <UserButton />
        </SignedIn>
      </header>
      <h1>OpenDelta Z Library 搜索</h1>
      <div className="input-group mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="请输入搜索关键词"
          value={query}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
          onKeyPress={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSearch()}
        />
        <button className="btn btn-primary" onClick={handleSearch}>
          搜索
        </button>
      </div>
      <div id="results">
        {results.length > 0 ? (
          <ul className="list-group">
            {results.map(item => (
              <li key={item.id} className="list-group-item">
                {item.cover_url && (
                  <img
                    src={item.cover_url}
                    alt="封面"
                    className="img-thumbnail"
                    style={{ maxWidth: 100, float: 'left', marginRight: 10 }}
                  />
                )}
                <h5><strong>{item.title}</strong></h5>
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
                {item.audioExists === "true" && (
                  <div><audio controls>
                    <source src={`/audio/${item.id}.wav`} type="audio/wav" />
                    您的浏览器不支持音频播放器。
                  </audio></div>
                )}
              </li>
            ))}
          </ul>
        ) : <div className='alert alert-warning'>无搜索结果</div>}
      </div>
    </div>
  );
}

export default App;
