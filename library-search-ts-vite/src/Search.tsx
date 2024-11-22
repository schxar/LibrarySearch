import React, { useState, KeyboardEvent } from 'react';
import axios from 'axios';

interface Book {
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
  book_url: string;
  cover_url?: string;
  id: string;
  audioExists?: string;
}

interface SearchResult {
  results: Book[];
}

const Search: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('请输入搜索关键词');
      return;
    }

    try {
      const response = await axios.get<SearchResult>('/search', {
        params: { q: query },
      });
      setResults(JSON.stringify(response.data.results, null, 2)); // 使用 JSON.stringify 格式化结果
    } catch (error) {
      alert('搜索失败，请稍后再试');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="container mt-5">
      <h1>OpenDelta Z Library 搜索</h1>
      <div className="input-group mb-3">
        <input
          type="text"
          id="searchQuery"
          className="form-control"
          placeholder="请输入搜索关键词"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button id="searchButton" className="btn btn-primary" onClick={handleSearch}>
          搜索
        </button>
      </div>

      <div id="results">
        {results ? (
          <pre>{results}</pre>
        ) : (
          <div className="alert alert-warning" role="alert">
            无搜索结果
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;
