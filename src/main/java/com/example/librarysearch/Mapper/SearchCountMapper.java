package com.example.librarysearch.Mapper;

import com.example.librarysearch.Entry.SearchCountEntry;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Update;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface SearchCountMapper {

    /**
     * 初始化搜索计数器
     * 向search_count表插入初始值1
     */
    @Insert("INSERT INTO search_count (count_number) VALUES (1)")
    void insertInitialCount();

    /**
     * 增加搜索计数
     * 将search_count表中的count_number字段值加1
     */
    @Update("UPDATE search_count SET count_number = count_number + 1")
    void incrementCount();

    /**
     * 获取当前搜索计数
     * @return 当前搜索计数值
     */
    @Select("SELECT count_number FROM search_count")
    Integer getCount();

}