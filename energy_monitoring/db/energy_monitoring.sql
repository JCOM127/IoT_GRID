-- MySQL dump 10.13  Distrib 9.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: energy_monitoring
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `power_generation`
--

DROP TABLE IF EXISTS `power_generation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `power_generation` (
  `Generation_ID` bigint NOT NULL AUTO_INCREMENT,
  `Project_ID` int NOT NULL,
  `Timestamp` timestamp NOT NULL,
  `Power_Generated` float NOT NULL,
  `Aggregation_Interval` enum('30s','5min','hourly','daily') DEFAULT 'hourly',
  `Derived_From_Sensor` int DEFAULT NULL,
  PRIMARY KEY (`Generation_ID`),
  KEY `Project_ID` (`Project_ID`),
  KEY `Derived_From_Sensor` (`Derived_From_Sensor`),
  CONSTRAINT `power_generation_ibfk_1` FOREIGN KEY (`Project_ID`) REFERENCES `projects` (`Project_ID`),
  CONSTRAINT `power_generation_ibfk_2` FOREIGN KEY (`Derived_From_Sensor`) REFERENCES `sensors` (`Sensor_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `power_generation`
--

LOCK TABLES `power_generation` WRITE;
/*!40000 ALTER TABLE `power_generation` DISABLE KEYS */;
/*!40000 ALTER TABLE `power_generation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `Project_ID` int NOT NULL AUTO_INCREMENT,
  `Project_Name` varchar(100) NOT NULL,
  `Source_Type` enum('Solar','Wind','Hybrid','Other') NOT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `Description` text,
  `Created_At` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Project_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (1,'Solar Facade','Solar',NULL,NULL,'2025-06-05 07:26:44'),(2,'Solar Brick','Solar',NULL,NULL,'2025-06-05 07:26:44'),(3,'HAWT','Wind',NULL,NULL,'2025-06-05 07:26:44');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_data`
--

DROP TABLE IF EXISTS `sensor_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_data` (
  `Data_ID` bigint NOT NULL AUTO_INCREMENT,
  `Sensor_ID` int NOT NULL,
  `Timestamp` timestamp NOT NULL,
  `Value` float NOT NULL,
  PRIMARY KEY (`Data_ID`),
  KEY `idx_sensor_time` (`Sensor_ID`,`Timestamp`),
  CONSTRAINT `sensor_data_ibfk_1` FOREIGN KEY (`Sensor_ID`) REFERENCES `sensors` (`Sensor_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_data`
--

LOCK TABLES `sensor_data` WRITE;
/*!40000 ALTER TABLE `sensor_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `sensor_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensors`
--

DROP TABLE IF EXISTS `sensors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensors` (
  `Sensor_ID` int NOT NULL AUTO_INCREMENT,
  `Project_ID` int NOT NULL,
  `Sensor_Code` varchar(50) NOT NULL,
  `Sensor_Type` varchar(100) NOT NULL,
  `Unit` varchar(50) NOT NULL,
  `Created_At` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Sensor_ID`),
  KEY `Project_ID` (`Project_ID`),
  CONSTRAINT `sensors_ibfk_1` FOREIGN KEY (`Project_ID`) REFERENCES `projects` (`Project_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensors`
--

LOCK TABLES `sensors` WRITE;
/*!40000 ALTER TABLE `sensors` DISABLE KEYS */;
INSERT INTO `sensors` VALUES (1,1,'Temp_1','temperature','C','2025-06-05 07:27:18'),(2,1,'Volt_1','voltage','V','2025-06-05 07:27:18'),(3,1,'Amp_1','current','A','2025-06-05 07:27:18'),(4,1,'Wind_1','wind_speed','m/s','2025-06-05 07:27:18'),(5,1,'Irr_1','irradiance','W/m²','2025-06-05 07:27:18'),(6,1,'PressHigh_1','pressure','Pa','2025-06-05 07:27:18'),(7,1,'PressLow_1','pressure','Pa','2025-06-05 07:27:18'),(8,2,'Irr_1','irradiance','W/m²','2025-06-05 07:27:18'),(9,2,'Temp_1','temperature','C','2025-06-05 07:27:18'),(10,2,'Volt_1','voltage','V','2025-06-05 07:27:18'),(11,2,'Amp_1','current','A','2025-06-05 07:27:18'),(12,3,'Irr_1','irradiance','W/m²','2025-06-05 07:27:18'),(13,3,'WindSpeed_1','wind_speed','m/s','2025-06-05 07:27:18'),(14,3,'Wind_Direction_1','wind_direction','°','2025-06-05 07:27:18'),(15,3,'Volt_1','voltage','V','2025-06-05 07:27:18'),(16,3,'Amp_1','current','A','2025-06-05 07:27:18');
/*!40000 ALTER TABLE `sensors` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-05  2:33:57
