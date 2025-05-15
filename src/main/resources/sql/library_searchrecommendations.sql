-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: library
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `searchrecommendations`
--

DROP TABLE IF EXISTS `searchrecommendations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `searchrecommendations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_email` varchar(255) NOT NULL,
  `email_hash` varchar(64) NOT NULL,
  `search_terms` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `searchrecommendations`
--

LOCK TABLES `searchrecommendations` WRITE;
/*!40000 ALTER TABLE `searchrecommendations` DISABLE KEYS */;
INSERT INTO `searchrecommendations` VALUES (1,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,包括技术,艺术,文学','2025-01-31 18:13:28'),(2,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,包括音乐制作,编程,建模,烹饪','2025-01-31 19:28:38'),(3,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,包括文学,音乐制作,技术,烹饪','2025-01-31 20:25:52'),(4,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,音乐制作,编程技术,建模,宠物百科','2025-03-29 16:09:31'),(5,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,编程,机器学习教程,基于的重复下载,科学知识速成指南','2025-05-08 20:32:54'),(6,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,动画与建模,推荐关键词,建模教程,用户多次下载相关书籍','2025-05-10 04:30:35'),(7,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,科学学习,生活实用技能,特殊兴趣如军事','2025-05-10 04:59:14'),(8,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','科学学习,生活实用技能,建模教程,多次下载相关书籍','2025-05-10 05:01:02'),(9,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据下载记录分析,教程多次下载相关书籍,涵盖动画,建模等','2025-05-10 05:04:58'),(10,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','根据用户的下载记录,动画与建模,推荐关键词,动画教程,用户多次下载相关书籍','2025-05-10 05:05:39'),(11,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','推荐关键词,空气炸锅烹饪,MachineLearningMadeEasyUsingPython','2025-05-10 10:16:54'),(12,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','特别是儿童版,Blender3DCharactersMachinesandScenesforArtistsGaintheinsightsandtechniquesyouneedtogivelifetoyourown,SolarPowerDIYHandbookSoYouWantToConnectYourOffGridSolarPaneltoa12VoltsBattery','2025-05-12 14:47:33'),(13,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','儿童犬类百科全书,空气炸锅食谱,教程,科学学习资料,人体穴位按摩','2025-05-12 15:05:07'),(14,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','宠物百科,空气炸锅食谱,教程,科学学习资料,烹饪书籍','2025-05-12 15:12:28'),(15,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','犬百科全书,用户之前下载过,TheDogEncyclopediaTheDefinitiveVisualGuide','2025-05-12 15:16:38'),(16,'tschxar@gmail.com','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','犬百科全书,TheDogEncyclopediaTheDefinitiveVisualGuide,TheCatEncyclopediaTheDefinitiveVisualGuide','2025-05-12 15:23:57');
/*!40000 ALTER TABLE `searchrecommendations` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-15  5:52:14
