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
	/**
	 * 插入或更新搜索历史记录
	 * 如果记录已存在(根据hash判断)，则更新weight和search_date字段
	 * 如果记录不存在，则插入新记录
	 * 
	 * @param entry 包含以下字段的搜索历史记录对象:
	 *              - hash: 查询内容的哈希值
	 *              - originalQuery: 原始查询字符串
	 *              - weight: 查询权重
	 *              - searchDate: 搜索日期
	 */
	@Insert("INSERT INTO search_history (hash, original_query, weight, search_date) " +
	        "VALUES (#{hash}, #{originalQuery}, #{weight}, #{searchDate}) " +
	        "ON DUPLICATE KEY UPDATE " +
	        "weight = weight + VALUES(weight), " +  // 累加而非覆盖
	        "search_date = VALUES(search_date)")
	void insertOrUpdate(SearchHistoryEntry entry);
	

	
}