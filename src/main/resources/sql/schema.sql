-- File: resources/sql/schema.sql
-- Database: library
-- Version: 1.1.0
-- Character set: utf8mb4
-- Collation: utf8mb4_unicode_ci
-- Engine: InnoDB

/*==============================================================*/
/* Table: notebook_audio_requests                               */
/* 有声书请求工单表                                             */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS `notebook_audio_requests` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `book_title` VARCHAR(255) NOT NULL COMMENT '书籍标题',
  `book_hash` CHAR(64) NOT NULL COMMENT '书籍哈希(SHA-256)',
  `request_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '请求时间',
  `clerk_user_email` VARCHAR(254) NOT NULL COMMENT '用户邮箱(RFC 5321标准)',
  `status` ENUM('pending','processing','completed') NOT NULL DEFAULT 'pending' COMMENT '工单状态',
  PRIMARY KEY (`id`),
  INDEX `idx_book_hash` (`book_hash`),
  INDEX `idx_user_email` (`clerk_user_email`),
  INDEX `idx_status` (`status`),
  INDEX `idx_request_date` (`request_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='有声书转换请求工单表'
PARTITION BY RANGE COLUMNS(request_date) (
  PARTITION p2023q4 VALUES LESS THAN ('2024-01-01'),
  PARTITION p2024q1 VALUES LESS THAN ('2024-04-01'),
  PARTITION p_future VALUES LESS THAN (MAXVALUE)
);

/*==============================================================*/
/* Table: download_history                                      */
/* 用户下载历史表                                               */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS `download_history` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `download_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下载时间',
  `user_email` VARCHAR(254) NOT NULL COMMENT '用户邮箱',
  `filename` VARCHAR(255) NOT NULL COMMENT '原始文件名',
  `email_hash` CHAR(64) GENERATED ALWAYS AS 
    (SHA2(CONCAT(user_email,'{SALT}'),256)) VIRTUAL COMMENT '带盐值哈希',
  `filename_hash` CHAR(64) GENERATED ALWAYS AS 
    (SHA2(filename,256)) VIRTUAL COMMENT '文件哈希',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_download` (`email_hash`, `filename_hash`),
  INDEX `idx_download_date` (`download_date`),
  INDEX `idx_filename` (`filename`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户下载行为记录表'
PARTITION BY HASH(id) PARTITIONS 4;

/*==============================================================*/
/* Table: search_history                                        */
/* 搜索历史记录表                                               */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS `search_history` (
  `hash` CHAR(64) NOT NULL COMMENT '查询哈希(SHA-256)',
  `original_query` VARCHAR(512) NOT NULL COMMENT '原始查询内容',
  `weight` INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '搜索权重',
  `search_date` DATE NOT NULL COMMENT '搜索日期',
  PRIMARY KEY (`hash`),
  INDEX `idx_search_date` (`search_date`),
  INDEX `idx_weight` (`weight`),
  INDEX `idx_query` (`original_query`(64))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户搜索行为分析表'
PARTITION BY RANGE (YEAR(search_date)) (
  PARTITION p2023 VALUES LESS THAN (2024),
  PARTITION p2024 VALUES LESS THAN (2025),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);

/*==============================================================*/
/* Table: search_recommendations                                */
/* 搜索推荐记录表                                               */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS `search_recommendations` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_email` VARCHAR(254) NOT NULL COMMENT '用户邮箱',
  `email_hash` CHAR(64) GENERATED ALWAYS AS 
    (SHA2(CONCAT(user_email,'{SALT}'),256)) VIRTUAL COMMENT '带盐值哈希',
  `search_terms` JSON NOT NULL COMMENT '推荐搜索词(JSON格式)',
  `generated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_user_recommend` (`email_hash`),
  INDEX `idx_generated_at` (`generated_at`),
  INDEX `idx_user_email` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='个性化搜索推荐记录表'
PARTITION BY LINEAR KEY(email_hash) PARTITIONS 4;

/*==============================================================*/
/* 系统配置表                                                   */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS `system_config` (
  `config_key` VARCHAR(64) NOT NULL COMMENT '配置键',
  `config_value` JSON NOT NULL COMMENT '配置值(JSON格式)',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='系统配置存储表';

-- 添加版本记录
INSERT INTO `system_config` (config_key, config_value) 
VALUES ('schema_version', 
  JSON_OBJECT(
    'version', '1.1.0',
    'update_time', CURRENT_TIMESTAMP,
    'changes', JSON_ARRAY(
      '优化哈希字段存储格式',
      '增加JSON类型支持',
      '统一分区策略'
    )
  )
) ON DUPLICATE KEY UPDATE 
  config_value = JSON_SET(config_value, '$.version', '1.1.0', '$.update_time', CURRENT_TIMESTAMP);