-- 创建数据库
CREATE DATABASE IF NOT EXISTS wechat DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE wechat;

-- 创建文章表
CREATE TABLE IF NOT EXISTS wechat_topic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uniqueid VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    origin_title VARCHAR(255),
    read_num INT DEFAULT 0,
    like_num INT DEFAULT 0,
    publish_time VARCHAR(50),
    create_time DATETIME(6),
    update_time DATETIME(6),
    available VARCHAR(10),
    words INT DEFAULT 0,
    url VARCHAR(255),
    avatar VARCHAR(255),
    abstract TEXT,
    content TEXT,
    source VARCHAR(255),
    wechat_id INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 