package com.example.librarysearch.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;

import com.example.librarysearch.Entry.SearchHistoryEntry;

@Mapper
public interface SearchHistoryMapper {
	@Insert("INSERT INTO search_history (hash, original_query, weight, search_date) " +
	        "VALUES (#{hash}, #{originalQuery}, #{weight}, #{searchDate}) " +
	        "ON DUPLICATE KEY UPDATE " +
	        "weight = weight + VALUES(weight), " +  // 累加而非覆盖
	        "search_date = VALUES(search_date)")
	void insertOrUpdate(SearchHistoryEntry entry);
}