-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: campus_resource_db
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `admin`
--
CREATE DATABASE IF NOT EXISTS `campus_resource_db`;
USE `campus_resource_db`;
DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `admin_id` char(4) NOT NULL,
  `admin_name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'Staff Member',
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `uq_admin_email` (`email`),
  CONSTRAINT `chk_admin_email` CHECK ((`email` like _utf8mb4'%@alueducation.com')),
  CONSTRAINT `chk_admin_role` CHECK ((`role` in (_utf8mb4'Senior Administrator',_utf8mb4'Department Manager',_utf8mb4'Staff Member')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES ('A001','Yoovin Poorun','y.poorun@alueducation.com','Department Manager'),('A002','Kwame Mensah','k.mensah@alueducation.com','Staff Member');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auditlog`
--

DROP TABLE IF EXISTS `auditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditlog` (
  `log_id` char(4) NOT NULL,
  `resource_id` char(4) NOT NULL,
  `admin_id` char(4) NOT NULL,
  `changes_made` varchar(300) NOT NULL,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`log_id`),
  KEY `fk_audit_resource` (`resource_id`),
  KEY `fk_audit_admin` (`admin_id`),
  CONSTRAINT `fk_audit_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`admin_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_audit_resource` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditlog`
--

LOCK TABLES `auditlog` WRITE;
/*!40000 ALTER TABLE `auditlog` DISABLE KEYS */;
INSERT INTO `auditlog` VALUES ('L001','R002','A001','Added 5 new books in the system','2026-05-17 09:00:00'),('L002','R004','A002','Removed 5 computers from the system','2026-05-20 11:00:00'),('L003','R001','A001','Updated HP Laptop quantity','2026-05-18 10:00:00');
/*!40000 ALTER TABLE `auditlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `borrowingtransaction`
--

DROP TABLE IF EXISTS `borrowingtransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `borrowingtransaction` (
  `transaction_id` char(4) NOT NULL,
  `student_id` char(4) NOT NULL,
  `resource_id` char(4) NOT NULL,
  `borrow_date` date NOT NULL,
  `due_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'borrowed',
  PRIMARY KEY (`transaction_id`),
  KEY `fk_trans_student` (`student_id`),
  KEY `fk_trans_resource` (`resource_id`),
  CONSTRAINT `fk_trans_resource` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_trans_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_due_after_borrow` CHECK ((`due_date` >= `borrow_date`)),
  CONSTRAINT `chk_return_after_borrow` CHECK (((`return_date` is null) or (`return_date` >= `borrow_date`))),
  CONSTRAINT `chk_status` CHECK ((`status` in (_utf8mb4'borrowed',_utf8mb4'returned')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `borrowingtransaction`
--

LOCK TABLES `borrowingtransaction` WRITE;
/*!40000 ALTER TABLE `borrowingtransaction` DISABLE KEYS */;
INSERT INTO `borrowingtransaction` VALUES ('T001','S001','R001','2026-05-01','2026-05-04','2026-05-03','returned'),('T002','S002','R002','2026-05-05','2026-05-08',NULL,'borrowed'),('T003','S003','R003','2026-05-06','2026-05-09','2026-05-08','returned'),('T004','S004','R004','2026-05-07','2026-05-10',NULL,'borrowed'),('T005','S005','R001','2026-05-08','2026-05-11',NULL,'borrowed'),('T006','S006','R005','2026-05-09','2026-05-12',NULL,'borrowed'),('T007','S007','R002','2026-05-10','2026-05-13','2026-05-12','returned');
/*!40000 ALTER TABLE `borrowingtransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource`
--

DROP TABLE IF EXISTS `resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource` (
  `resource_id` char(4) NOT NULL,
  `resource_name` varchar(100) NOT NULL,
  `resource_type` varchar(50) NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`resource_id`),
  CONSTRAINT `chk_quantity` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource`
--

LOCK TABLES `resource` WRITE;
/*!40000 ALTER TABLE `resource` DISABLE KEYS */;
INSERT INTO `resource` VALUES ('R001','HP Laptop','tech tools',5),('R002','Scientific Calculator','stationery',10),('R003','Introduction to Algorithms','books',3),('R004','USB Flash Drive','IT',20),('R005','Whiteboard Marker Set','stationery',50);
/*!40000 ALTER TABLE `resource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` char(4) NOT NULL,
  `student_name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `uq_student_email` (`email`),
  CONSTRAINT `chk_student_email` CHECK ((`email` like _utf8mb4'%@alustudent.com'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('S001','Joseph Manu','j.manu@alustudent.com'),('S002','Kwame Mensah','k.mensah@alustudent.com'),('S003','Ama Owusu','a.owusu@alustudent.com'),('S004','Kofi Boateng','k.boateng@alustudent.com'),('S005','Abena Asante','a.asante@alustudent.com'),('S006','Yaw Darko','y.darko@alustudent.com'),('S007','Efua Amponsah','e.amponsah@alustudent.com');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-25  0:58:26
