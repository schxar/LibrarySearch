package com.example.librarysearch.Mapper;

import org.apache.ibatis.annotations.Mapper;

import com.example.librarysearch.entity.SearchHistoryDaily;

//mapper/SearchHistoryDailyMapper.java
@Mapper
public interface SearchHistoryDailyMapper {
 void insertDailySearch(SearchHistoryDaily record);
}