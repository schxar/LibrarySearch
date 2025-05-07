package com.example.librarysearch.Entry;

/**
 * Entity class representing a search count entry.
 * Tracks and stores the count/number of searches performed.
 */
public class SearchCountEntry {

    private int countNumber; // The count/number of searches

    /**
     * Default constructor
     */
    public SearchCountEntry() {
    }

    /**
     * Constructor with initial count number
     * @param countNumber initial search count value
     */
    public SearchCountEntry(int countNumber) {
        this.countNumber = countNumber;
    }


    /**
     * Get the current search count
     * @return the number of searches
     */
    public int getCountNumber() {
        return countNumber;
    }

    /**
     * Set the search count
     * @param countNumber the new search count value
     */
    public void setCountNumber(int countNumber) {
        this.countNumber = countNumber;
    }

}