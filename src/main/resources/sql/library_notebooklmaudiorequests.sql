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
-- Table structure for table `notebooklmaudiorequests`
--

DROP TABLE IF EXISTS `notebooklmaudiorequests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notebooklmaudiorequests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_title` varchar(255) NOT NULL,
  `book_hash` varchar(64) NOT NULL,
  `request_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `clerk_user_email` varchar(255) NOT NULL,
  `status` enum('pending','processing','completed') DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notebooklmaudiorequests`
--

LOCK TABLES `notebooklmaudiorequests` WRITE;
/*!40000 ALTER TABLE `notebooklmaudiorequests` DISABLE KEYS */;
INSERT INTO `notebooklmaudiorequests` VALUES (1,'Coffee Isn’t Rocket Science A Quick and Easy Guide to Buying, Brewing, Serving, Roasting, and Tasting Coffee ','774671f40f3ce02f58ac013d1d494eeda216ad1a7aa94f72f92934f26cd3401c','2025-01-13 21:48:39','tschxar@gmail.com','pending'),(2,'Microservices with Docker, Flask, and React (Michael Herman) (Z-Library).pdf','7f8c4ea09f272cccbc75adaae9243bf3cab3ee959c7cb88f61ee0460471b4ed1','2025-01-15 20:06:05','user@example.com','completed'),(3,'Blender 3D Noob to Pro (David Millet, Arthur Tombs, Louie Monday etc.) (Z-Library).pdf','95ab8fdeb413318449cc315dbdfc863fb04e424288057c6444693e1e37bd302e','2025-01-15 20:10:18','','pending'),(4,'The Big Book of Small House Designs 75 Award-Winning Plans for Your Dream House, All 1,250 Square Feet or Less (Don Metz, Catherine Tredway) (Z-Library).pdf','392f8600e72ad036caa807050518c39d5f12d596e036f748dbd3de600fbf3228','2025-01-15 20:28:23','user@example.com','pending'),(5,'Blender 3D Noob to Pro (David Millet, Arthur Tombs, Louie Monday etc.) (Z-Library).pdf','95ab8fdeb413318449cc315dbdfc863fb04e424288057c6444693e1e37bd302e','2025-01-17 21:40:45','tschxar@gmail.com','pending'),(6,'新疆风暴七十年（第2册） (张大军) (Z-Library).pdf','a61cb1c966dd01ba289e8d579e80c3f12bd1d3783e28619bf94bdac652cb866e','2025-05-08 16:22:29','tschxar@gmail.com','processing'),(7,'Blender (Søren Ejlersen, Ditte Ingemann Thuesen) (Z-Library).epub','d2c1db5f0228bab7cd19493ddf074ea6d2c6caa170f2bbada64e645e8a02b05e','2025-05-09 14:13:10','tschxar@gmail.com','pending'),(8,'Blender 3D保姆级基础入门教程 (张楚阳) (Z-Library).pdf','3c36bd18bd9150852ad58293e29e7ab887d1b8dffaca5f54310ebf53560b0696','2025-05-10 02:02:41','tschxar@gmail.com','pending'),(9,'Blender 3D保姆级基础入门教程 (张楚阳) (Z-Library).pdf','3c36bd18bd9150852ad58293e29e7ab887d1b8dffaca5f54310ebf53560b0696','2025-05-10 02:02:48','tschxar@gmail.com','pending'),(10,'Blender (Søren Ejlersen, Ditte Ingemann Thuesen) (Z-Library).epub','d2c1db5f0228bab7cd19493ddf074ea6d2c6caa170f2bbada64e645e8a02b05e','2025-05-10 04:38:45','tschxar@gmail.com','pending');
/*!40000 ALTER TABLE `notebooklmaudiorequests` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-15  5:52:13
