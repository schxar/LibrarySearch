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
-- Table structure for table `downloadhistory`
--

DROP TABLE IF EXISTS `downloadhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `downloadhistory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `download_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `user_email` varchar(255) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `email_hash` varchar(64) NOT NULL,
  `filename_hash` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_hash` (`email_hash`),
  KEY `filename_hash` (`filename_hash`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `downloadhistory`
--

LOCK TABLES `downloadhistory` WRITE;
/*!40000 ALTER TABLE `downloadhistory` DISABLE KEYS */;
INSERT INTO `downloadhistory` VALUES (1,'2025-01-22 14:54:00','tschxar@gmail.com','Solar Power DIY Handbook So, You Want To Connect Your Off-Grid Solar Panel to a 12 Volts Battery (Baiano Reeves) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','6252630d5d0a041080afcb8069d7a8184a662f22fb33f0debfc52835c7f87474'),(2,'2025-01-22 14:55:41','tschxar@gmail.com','The Basics A Really Useful Cook Book (Anthony Telford) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','0afc4c335e030771025fa985fc33ca78dedfaf87f0bdeb038c14d6e7f9ed2524'),(3,'2025-01-22 15:17:42','tschxar@gmail.com','格洛克手枪制造图纸__GLOCK_17 (无) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','5503cffaebd84f01eff2ba1d34484f9babb2573ee5e4eb06b599783f0b6d0cbd'),(4,'2025-01-22 15:17:50','tschxar@gmail.com','The Cat Encyclopedia The Definitive Visual Guide (DK, Miezan Van Zyl) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','b0ac4206e1453b1ac0c32786705521114ae8cf6266bd75d2b7dcce53f619f94e'),(5,'2025-01-22 15:18:23','tschxar@gmail.com','The Dog Encyclopedia The Definitive Visual Guide (DK) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','6bfa3b18f2b5156ef246f74ce73d711957d977eed0b458399bd3c377c07f0d17'),(6,'2025-01-22 20:46:18','tschxar@gmail.com','Blender 3D Noob to Pro (David Millet, Arthur Tombs, Louie Monday etc.) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','95ab8fdeb413318449cc315dbdfc863fb04e424288057c6444693e1e37bd302e'),(7,'2025-01-22 20:46:57','tschxar@gmail.com','Microservices with Docker, Flask, and React (Michael Herman) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','7f8c4ea09f272cccbc75adaae9243bf3cab3ee959c7cb88f61ee0460471b4ed1'),(8,'2025-01-22 20:51:30','tschxar@gmail.com','If He Had Been with Me (Laura Nowlin) (Z-Library).epub','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','28f9c48b0e9b418c43fe062cf5b5d2a7ddd434b04955dac407359f58ff3adc0f'),(9,'2025-01-23 20:27:20','tschxar@gmail.com','Music Production, 2020 Edition (Tommy Swindali) (Z-Library).epub','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','d0ca08554b14074e727983b14f504afcc8b8b4aaaafbbbd4700d902d5b9aadf1'),(10,'2025-01-23 20:30:17','tschxar@gmail.com','Cyka Blyat (or Suka Blyat) Everyday Russian Slang and Curse Words (Alexander Evstafiev) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','2cbb615360ad47267f9334ee8acac58c41bf86f9bd81bc662b8b7e973e512961'),(11,'2025-01-31 19:28:07','tschxar@gmail.com','Music Production, 2020 Edition (Tommy Swindali) (Z-Library).epub','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','d0ca08554b14074e727983b14f504afcc8b8b4aaaafbbbd4700d902d5b9aadf1'),(12,'2025-01-31 20:25:37','tschxar@gmail.com','O fabricante de lágrimas (Erin Doom) (Z-Library).epub','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','99eeefa6d06b76b94c98602710bd3e400c9392fba0f4909f14761e76d60a629f'),(13,'2025-03-27 20:25:38','tschxar@gmail.com','Everything You Need to Ace Science in One Big Fat Notebook (Workman Publishing) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a5b61bd4ffd625deae2c3770a5e126c49d2e1dfdd6a6fa1c4100d7cb0ea16a8d'),(14,'2025-03-27 20:25:50','tschxar@gmail.com','Everything You Need to Ace Science in One Big Fat Notebook (Workman Publishing) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a5b61bd4ffd625deae2c3770a5e126c49d2e1dfdd6a6fa1c4100d7cb0ea16a8d'),(15,'2025-03-27 20:25:52','tschxar@gmail.com','Everything You Need to Ace Science in One Big Fat Notebook (Workman Publishing) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a5b61bd4ffd625deae2c3770a5e126c49d2e1dfdd6a6fa1c4100d7cb0ea16a8d'),(16,'2025-03-27 20:25:53','tschxar@gmail.com','Everything You Need to Ace Science in One Big Fat Notebook (Workman Publishing) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a5b61bd4ffd625deae2c3770a5e126c49d2e1dfdd6a6fa1c4100d7cb0ea16a8d'),(17,'2025-03-27 20:25:55','tschxar@gmail.com','Everything You Need to Ace Science in One Big Fat Notebook (Workman Publishing) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a5b61bd4ffd625deae2c3770a5e126c49d2e1dfdd6a6fa1c4100d7cb0ea16a8d'),(18,'2025-05-07 16:50:20','tschxar@gmail.com','Machine_Learning_Made_Easy_Using_Python (Rahul Mula) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','d505c4f2445a10fcc1d599623ec9b7c66c37b77ec17de256f6f8c967abaa4fcf'),(19,'2025-05-08 20:50:04','tschxar@gmail.com','新疆风暴七十年（第2册） (张大军) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a61cb1c966dd01ba289e8d579e80c3f12bd1d3783e28619bf94bdac652cb866e'),(20,'2025-05-08 20:50:18','tschxar@gmail.com','Air Fryer Cookbook for Beginners 2020 800 Most Wanted, Easy and Healthy Recipes to Fry, Bake, Grill  Roast (Andrea Leonard) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','da59339b90909472bf4f5c07c994e35507ad4fcfd6c21eef26e10986727a3eb2'),(21,'2025-05-08 21:55:30','tschxar@gmail.com','博物学家的神秘动物图鉴 ([法] 让-巴普蒂斯特·德·帕纳菲厄, [法] 卡米耶·让维萨德) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','b0ccc4267e092bd18e38e833058ca83c5f59fb0e4a76dfac7f0307a4dc312b62'),(22,'2025-05-08 22:28:12','tschxar@gmail.com','人体穴位自助按摩图鉴.pdf (人体穴位自助按摩图鉴.pdf) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','7693ba1c93e433fd05ed7e8416c7311da1367eb14a2ca399bd68d61bad949cf6'),(23,'2025-05-09 14:10:11','tschxar@gmail.com','Blender (Søren Ejlersen, Ditte Ingemann Thuesen) (Z-Library).epub','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','d2c1db5f0228bab7cd19493ddf074ea6d2c6caa170f2bbada64e645e8a02b05e'),(24,'2025-05-09 23:43:13','tschxar@gmail.com','Blender 3D Characters, Machines, and Scenes for Artists Gain the insights and techniques you need to give life to your own... ( etc.) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','0916d21bbb5662439eab5ef1662254384bc770d7f8b744c6b6149ededac36f1e'),(25,'2025-05-10 00:32:33','tschxar@gmail.com','Blender 2D Animation The Complete Guide to the Grease Pencil (John M. Blain) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','a969dda8d521559ed5ae16354abc68b71d68e2fd49a69f753ddedddd6af5151b'),(26,'2025-05-10 10:07:00','tschxar@gmail.com','Air Fryer Cookbook for Beginners 2020 800 Most Wanted, Easy and Healthy Recipes to Fry, Bake, Grill  Roast (Andrea Leonard) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','da59339b90909472bf4f5c07c994e35507ad4fcfd6c21eef26e10986727a3eb2'),(27,'2025-05-10 10:08:34','tschxar@gmail.com','Dog Encyclopedia (Barraza Duran, Ivan) (Z-Library).epub','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','9ce5e6068bc647ddd1b7dba67284cb1b3c6795ec8d45b8ca89692395c54509f6'),(28,'2025-05-10 10:14:32','tschxar@gmail.com','Air Fryer Cookbook for Beginners 2020 800 Most Wanted, Easy and Healthy Recipes to Fry, Bake, Grill  Roast (Andrea Leonard) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','da59339b90909472bf4f5c07c994e35507ad4fcfd6c21eef26e10986727a3eb2'),(29,'2025-05-10 10:14:43','tschxar@gmail.com','The Dog Encyclopedia for Kids (Tammy Gagne) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','8a0aed99a9adf2f1fed0c8c8911343944298ea7697682232ff36c1547aaa7e2e'),(30,'2025-05-10 10:14:43','tschxar@gmail.com','The Dog Encyclopedia for Kids (Tammy Gagne) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','8a0aed99a9adf2f1fed0c8c8911343944298ea7697682232ff36c1547aaa7e2e'),(31,'2025-05-10 10:14:43','tschxar@gmail.com','The Dog Encyclopedia for Kids (Tammy Gagne) (Z-Library).pdf','faf0ed1b5cd72340474d2f5e6a08fae7c8d36ddacd1e53298a82ceef1a571a63','8a0aed99a9adf2f1fed0c8c8911343944298ea7697682232ff36c1547aaa7e2e');
/*!40000 ALTER TABLE `downloadhistory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-15  5:52:12
