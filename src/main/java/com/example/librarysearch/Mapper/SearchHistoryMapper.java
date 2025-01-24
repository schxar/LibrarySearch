package com.example.librarysearch.Mapper;

import java.util.List;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Lang;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import com.example.librarysearch.Entry.SearchHistoryEntry;
import org.mybatis.scripting.freemarker.FreeMarkerLanguageDriver;  
//注意：使用 FreeMarkerLanguageDriver 替代 SimpleDriver  

@Mapper
public interface SearchHistoryMapper {
	@Insert("INSERT INTO search_history (hash, original_query, weight, search_date) " +
	        "VALUES (#{hash}, #{originalQuery}, #{weight}, #{searchDate}) " +
	        "ON DUPLICATE KEY UPDATE " +
	        "weight = weight + VALUES(weight), " +  // 累加而非覆盖
	        "search_date = VALUES(search_date)")
	void insertOrUpdate(SearchHistoryEntry entry);
	

	
}