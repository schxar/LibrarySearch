package com.example.librarysearch.entity;

import java.time.LocalDate;

import lombok.Data;

@Data
public class SearchHistoryDaily {
    private LocalDate entryDate;
    private String hash;
    private String original;
    private Double weight;
}