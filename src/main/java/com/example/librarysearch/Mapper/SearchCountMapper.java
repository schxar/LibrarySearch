package com.example.librarysearch.Mapper;

import com.example.librarysearch.Entry.SearchCountEntry;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Update;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface SearchCountMapper {

    @Insert("INSERT INTO search_count (count_number) VALUES (1)")
    void insertInitialCount();

    @Update("UPDATE search_count SET count_number = count_number + 1")
    void incrementCount();

    @Select("SELECT count_number FROM search_count")
    Integer getCount();

}