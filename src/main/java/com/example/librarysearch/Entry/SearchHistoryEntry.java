package com.example.librarysearch.Entry;

import java.sql.Date;

/**
 * Entity class representing a search history entry.
 * Stores information about user search queries including:
 * - Unique hash identifier
 * - Original search query
 * - Search weight/importance
 * - Date of search
 */
public class SearchHistoryEntry {
    private String hash;          // Unique hash identifier for the search
    private String originalQuery; // Original search query text
    private int weight;          // Weight/importance of the search
    private Date searchDate;     // Date when the search was performed

    /**
     * Get the unique hash identifier of the search
     */
    public String getHash() {
        return hash;
    }

    /**
     * Set the unique hash identifier of the search
     */
    public void setHash(String hash) {
        this.hash = hash;
    }

    /**
     * Get the original search query text
     */
    public String getOriginalQuery() {
        return originalQuery;
    }

    /**
     * Set the original search query text
     */
    public void setOriginalQuery(String originalQuery) {
        this.originalQuery = originalQuery;
    }

    /**
     * Get the weight/importance of the search
     */
    public int getWeight() {
        return weight;
    }

    /**
     * Set the weight/importance of the search
     */
    public void setWeight(int weight) {
        this.weight = weight;
    }

    /**
     * Get the date when the search was performed
     */
    public Date getSearchDate() {
        return searchDate;
    }

    /**
     * Set the date when the search was performed
     * Note: Uses java.sql.Date type for database compatibility
     */
    public void setSearchDate(Date searchDate) {
        this.searchDate = searchDate;
    }
}