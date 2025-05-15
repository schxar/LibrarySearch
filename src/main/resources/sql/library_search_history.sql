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
-- Table structure for table `search_history`
--

DROP TABLE IF EXISTS `search_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `search_history` (
  `hash` varchar(64) NOT NULL,
  `original_query` varchar(255) NOT NULL,
  `weight` int NOT NULL,
  `search_date` date NOT NULL,
  PRIMARY KEY (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_history`
--

LOCK TABLES `search_history` WRITE;
/*!40000 ALTER TABLE `search_history` DISABLE KEYS */;
INSERT INTO `search_history` VALUES ('030ad17f79e246d20db265cb6d4014c44a6070405c2ba7f735b7ef87a7f09dd0','glock',1,'2025-01-21'),('03fb94180aa0ff2c583d97bbb1fc6d84a6ba7df5bde3c267459bb9a9b8c9841b','cook',3,'2025-01-21'),('040228846ead4a4195145fe089343cb0894d00a9380176a41a8f6c5ee70b4824','C#',3,'2025-01-24'),('04135f433e3aa1e48649c9c7e5bee02bfaaecdd636cb6e38b63cade610b55d9e','Warhammer',2,'2025-01-21'),('044f4b3501cd8e8131d40c057893f4fdff66bf4032ecae159e0c892a28cf6c8e','tommy',4,'2025-01-24'),('0b2f6712a50d22428fa17dd1b607c2a64ddad0df953f1534460c70e2428d598e','MachineLearning',3,'2025-01-24'),('11a4a60b518bf24989d481468076e5d5982884626aed9faeb35b8576fcd223e1','python',4,'2025-01-24'),('1a483835bb7f2b2c7b82d42798b5c32c568082cddd880f0542ce75fee3bf05ce','@#$%',1,'2025-01-24'),('28a3a5e81d1e89f0efc70b63bf717b921373fc7fac70bc1b7e4d466799c0c6b0','dead',2,'2025-01-21'),('35039cc4f6ca7f6bd7667a48d1810cbe39f9eec2b846bc63d1d1ade3638925e8','C# Programming',6,'2025-01-24'),('361e48d0308f20e32dba5fb56328baf18d72ef0ccb43b84f5c262d2a6a1fc6c8','end',2,'2025-01-21'),('37ff20583960759de8bb0200d21522ae79d687f6abe680e82b486bdfe490e98a','walking',2,'2025-01-21'),('3e8e40c0af5f5ea5a94837f090631379e090fdb2fcf0c65a65859ae051e2c794','blood',3,'2025-01-24'),('538d7d9fe78e7baac47a9fbd6f2c68845ecca72dbdc2b47b4c5a0f5620ab8e93','snake',2,'2025-01-21'),('59d6d61431fce7d91388d0c60374ddaadc1acd8370221e11b029621656d5ccec','meat',2,'2025-01-21'),('5b9ab83a8706f0624eb291cf85576874fa6bf751b5cde3d7f539f17b9bafc586','cleaning house',2,'2025-01-24'),('6ac3c336e4094835293a3fed8a4b5fedde1b5e2626d9838fed50693bba00af0e','fuck',1,'2025-01-21'),('7441a902d9324a19d673df4f7bca0e2de1aa6cd3c25e8357dc9c51a082b07bc1','Machine+Learning',3,'2025-01-24'),('77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e','cat',6,'2025-01-24'),('796e43a5a8cdb73b92b5f59eb50610cea3efa8ce229cd7f0557983091b2b4552','cock',2,'2025-01-21'),('7e1815a08b8d78c4ab588d9e95ec1d5f36e65333dfe68f3704ad77c9782dff64','cyka',4,'2025-01-24'),('9316cd4d881e21d7494cada328686b37ef1ffda61a93354a0370c21d6f2f2c1e','Machine Learning',8,'2025-01-24'),('c5e85eeb7f0584a0a37ebc9b8578b0dbc0a5f8b9e923d6aa053142b8a59b8b36','hgerfiefdtrijse0opighngs0ipetjha9e-0[raeswsatapjgap0etr[rjna;jkt5yeoipjwaoprijhaqigjsrjgeairjgp0ASDOIjgseto;rfoi;ryjbdfjlk;jueoairknseotj0waiehgnsaeirjnowiefjaewoingowaeJRFO;QARGHAIURHFNGVLAEW4RHTFNLAURGHERDUIFJHwrofgtriuefhawieu',1,'2025-01-24'),('cd6357efdd966de8c0cb2f876cc89ec74ce35f0968e11743987084bd42fb8944','dog',7,'2025-01-24'),('dc9f28b12dd1818ee42ffc92ecb940386214598837348d30d3c6c0b7b57e34c9','fire',2,'2025-01-21'),('e186022d0931afe9fe0690857e32f85e50165e7fbe0966d49609ef1981f920c6','nice',2,'2025-01-21');
/*!40000 ALTER TABLE `search_history` ENABLE KEYS */;
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
