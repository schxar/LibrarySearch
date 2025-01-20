package com.example.librarysearch.Entry;

import java.sql.Date;

public class SearchHistoryEntry {
    private String hash;
    private String originalQuery;
    private int weight;
    private Date searchDate;

    // 完整的 Getter 和 Setter
    public String getHash() {
        return hash;
    }

    public void setHash(String hash) {
        this.hash = hash;
    }

    public String getOriginalQuery() {
        return originalQuery;
    }

    public void setOriginalQuery(String originalQuery) {
        this.originalQuery = originalQuery;
    }

    public int getWeight() {
        return weight;
    }

    public void setWeight(int weight) {
        this.weight = weight;
    }

    public Date getSearchDate() {
        return searchDate;
    }

    // 关键修改：参数类型改为 java.sql.Date
    public void setSearchDate(Date searchDate) {
        this.searchDate = searchDate;
    }
}