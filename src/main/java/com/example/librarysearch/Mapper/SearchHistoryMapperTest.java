package com.example.librarysearch.Mapper;

import static org.assertj.core;

import java.sql.Date;
import java.util.Arrays;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import com.example.librarysearch.Entry.SearchHistoryEntry;

@SpringBootTest
@Transactional  // 测试后自动回滚
@ActiveProfiles("test")  // 激活测试配置文件
public class SearchHistoryMapperTest {

    @Autowired
    private SearchHistoryMapper searchHistoryMapper;

    @Test
    public void testBatchInsertWithConflict() {
        // 构造测试数据（注意时间戳参数）
        List<SearchHistoryEntry> entries = Arrays.asList(
            new SearchHistoryEntry(
                "hash1", 
                "Java Programming", 
                3, 
                new Date(System.currentTimeMillis())  // 使用java.sql.Date
            ),
            new SearchHistoryEntry(
                "hash1",  // 相同哈希触发冲突
                "Java Programming", 
                2, 
                new Date(System.currentTimeMillis() + 1000)  // 模拟稍后时间
            )
        );

        // 执行批量插入
        searchHistoryMapper.batchInsert(entries);

        // 验证结果（需定义select方法）
        SearchHistoryEntry result = searchHistoryMapper.selectByHash("hash1");
        assertThat(result.getWeight()).isEqualTo(5);  // 3 + 2 = 5
        assertThat(result.getOriginalQuery()).isEqualTo("Java Programming");
    }
}