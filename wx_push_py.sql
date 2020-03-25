-- MySQL dump 10.13  Distrib 8.0.16, for Win64 (x86_64)
--
-- Host: localhost    Database: wx_push_py
-- ------------------------------------------------------
-- Server version	8.0.16

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ammeters`
--

DROP TABLE IF EXISTS `ammeters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `ammeters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `ammeter_app_code` int(11) NOT NULL,
  `ammeter_addr` varchar(255) NOT NULL,
  `source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ammeters_0afd9202` (`source_id`),
  CONSTRAINT `ammeters_source_id_522c4032c5913c4c_fk_project_source_id` FOREIGN KEY (`source_id`) REFERENCES `project` (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ammeters`
--

LOCK TABLES `ammeters` WRITE;
/*!40000 ALTER TABLE `ammeters` DISABLE KEYS */;
/*!40000 ALTER TABLE `ammeters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group__permission_id_6a5a5f591a8d9425_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group__permission_id_6a5a5f591a8d9425_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permission_group_id_274d1afe6092c3d4_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  CONSTRAINT `auth_p_content_type_id_19e80c80ee1a16e_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add permission',2,'add_permission'),(5,'Can change permission',2,'change_permission'),(6,'Can delete permission',2,'delete_permission'),(7,'Can add group',3,'add_group'),(8,'Can change group',3,'change_group'),(9,'Can delete group',3,'delete_group'),(10,'Can add user',4,'add_user'),(11,'Can change user',4,'change_user'),(12,'Can delete user',4,'delete_user'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add config',7,'add_config'),(20,'Can change config',7,'change_config'),(21,'Can delete config',7,'delete_config'),(22,'Can add wx user',8,'add_wxuser'),(23,'Can change wx user',8,'change_wxuser'),(24,'Can delete wx user',8,'delete_wxuser'),(25,'Can add menu',9,'add_menu'),(26,'Can change menu',9,'change_menu'),(27,'Can delete menu',9,'delete_menu'),(28,'Can add url source',10,'add_urlsource'),(29,'Can change url source',10,'change_urlsource'),(30,'Can delete url source',10,'delete_urlsource'),(31,'Can add project',11,'add_project'),(32,'Can change project',11,'change_project'),(33,'Can delete project',11,'delete_project'),(34,'Can add ammeters',12,'add_ammeters'),(35,'Can change ammeters',12,'change_ammeters'),(36,'Can delete ammeters',12,'delete_ammeters'),(37,'Can add unconfirm user',13,'add_unconfirmuser'),(38,'Can change unconfirm user',13,'change_unconfirmuser'),(39,'Can delete unconfirm user',13,'delete_unconfirmuser'),(40,'Can add confirmed user',14,'add_confirmeduser'),(41,'Can change confirmed user',14,'change_confirmeduser'),(42,'Can delete confirmed user',14,'delete_confirmeduser'),(43,'Can add super user',15,'add_superuser'),(44,'Can change super user',15,'change_superuser'),(45,'Can delete super user',15,'delete_superuser');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'wxpushroot',NULL,1,'root','','','',0,1,'2020-03-20 22:50:16.119348'),(2,'wxpushadmin',NULL,1,'admin','','','',0,1,'2020-03-20 22:50:16.128340');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_862047c47a3a484_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_862047c47a3a484_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_20b7456d980d34d0_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_u_permission_id_709eb7cabf9b266b_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_user_u_permission_id_709eb7cabf9b266b_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissi_user_id_6fd48db2639d8366_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `config` (
  `name` varchar(255) NOT NULL,
  `textValue` longtext,
  `value` varchar(255) DEFAULT NULL,
  `valueAttached` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config`
--

LOCK TABLES `config` WRITE;
/*!40000 ALTER TABLE `config` DISABLE KEYS */;
INSERT INTO `config` VALUES ('access_token',NULL,'31_2BlQbvseNtoHOckl7Im6-aohllYOC8etmYvng0bF0NnePVs6aq3VDHfiBSxlzo0fay0pnCN4OktCfL6AuJNIWInnSLnE53NpR1FdRpGaoluwJtVkM6b59LX-vQDGXRDMcaJHt6WA94rDlwHZCIGeAGAXDB','1584723345');
/*!40000 ALTER TABLE `config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `confirmeduser`
--

DROP TABLE IF EXISTS `confirmeduser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `confirmeduser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openId` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `createTime` datetime(6) NOT NULL,
  `IDcard` varchar(255) DEFAULT NULL,
  `extraInfo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `confirmeduser`
--

LOCK TABLES `confirmeduser` WRITE;
/*!40000 ALTER TABLE `confirmeduser` DISABLE KEYS */;
/*!40000 ALTER TABLE `confirmeduser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `confirmeduser_ammeter`
--

DROP TABLE IF EXISTS `confirmeduser_ammeter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `confirmeduser_ammeter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `confirmeduser_id` int(11) NOT NULL,
  `ammeters_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `confirmeduser_id` (`confirmeduser_id`,`ammeters_id`),
  KEY `confirmedUser_ammete_ammeters_id_1aedc1d1c9846f8d_fk_ammeters_id` (`ammeters_id`),
  CONSTRAINT `confirmedU_confirmeduser_id_73631b924422214d_fk_confirmedUser_id` FOREIGN KEY (`confirmeduser_id`) REFERENCES `confirmeduser` (`id`),
  CONSTRAINT `confirmedUser_ammete_ammeters_id_1aedc1d1c9846f8d_fk_ammeters_id` FOREIGN KEY (`ammeters_id`) REFERENCES `ammeters` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `confirmeduser_ammeter`
--

LOCK TABLES `confirmeduser_ammeter` WRITE;
/*!40000 ALTER TABLE `confirmeduser_ammeter` DISABLE KEYS */;
/*!40000 ALTER TABLE `confirmeduser_ammeter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_content_type_id_4b45c0446e80947_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_30fcd591b11b9112_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_user_id_30fcd591b11b9112_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_content_type_id_4b45c0446e80947_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_2b459ee7f1b8a0b0_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(12,'app','ammeters'),(7,'app','config'),(14,'app','confirmeduser'),(9,'app','menu'),(11,'app','project'),(15,'app','superuser'),(13,'app','unconfirmuser'),(10,'app','urlsource'),(8,'app','wxuser'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2020-03-20 22:31:30.520990'),(2,'auth','0001_initial','2020-03-20 22:31:31.147617'),(3,'admin','0001_initial','2020-03-20 22:31:31.307540'),(4,'app','0001_initial','2020-03-20 22:31:32.318940'),(5,'contenttypes','0002_remove_content_type_name','2020-03-20 22:31:32.582786'),(6,'auth','0002_alter_permission_name_max_length','2020-03-20 22:31:32.720719'),(7,'auth','0003_alter_user_email_max_length','2020-03-20 22:31:33.065518'),(8,'auth','0004_alter_user_username_opts','2020-03-20 22:31:33.083498'),(9,'auth','0005_alter_user_last_login_null','2020-03-20 22:31:33.182450'),(10,'auth','0006_require_contenttypes_0002','2020-03-20 22:31:33.191437'),(11,'sessions','0001_initial','2020-03-20 22:31:33.272390');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('d0xz4lcqsartdjmhky0ir0ksq0e4mbtg','ODYyNDI4MWQ5NTdjNzQwOGE1MzkxMzBlY2M1MDViODk4ODc4NTQwNjp7InZyZiI6MTEuMTMyMTQzNjgyMzAxOTU2fQ==','2020-04-03 23:26:35.356411'),('n4julsew18cs4c19id44wrsz3oqrb1t5','ZDQyYmZlNzU5YmQyZDkyNDU0NTQxOGU5NjYyOWI2ZjUzYjFmOTQxZjp7Im9wZW5pZCI6Im8tWFNWd1JqNXVQc3V1NEMzY2tGTHBzeHFQc2MifQ==','2020-04-06 23:37:15.327320'),('w4kwjm1yf1qwn7lg0do6s2v2aal4en15','NjU2ZjEzMDA2YzRjYmEwYWEzOTk2MTYzNjA0ZGVlYTVlYmRhMjRjZTp7InZyZiI6MTQuMzg2MjkwMzc2NDI3Njc5fQ==','2020-04-03 23:26:35.355398');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `submenu_id` bigint(20) DEFAULT NULL,
  `name` varchar(60) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `key` varchar(128) DEFAULT NULL,
  `url` longtext,
  `media_id` varchar(255) DEFAULT NULL,
  `appid` varchar(100) DEFAULT NULL,
  `pagepath` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `project` (
  `source_id` int(11) NOT NULL,
  `projectname` varchar(255) NOT NULL,
  `province` varchar(100) NOT NULL,
  `city` varchar(100) NOT NULL,
  `district` varchar(100) NOT NULL,
  `extraInfo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `superuser`
--

DROP TABLE IF EXISTS `superuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `superuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openId` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `createTime` datetime(6) NOT NULL,
  `IDcard` varchar(255) DEFAULT NULL,
  `extraInfo` varchar(255) DEFAULT NULL,
  `source_id` int(11) DEFAULT NULL,
  `domain` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `superuser`
--

LOCK TABLES `superuser` WRITE;
/*!40000 ALTER TABLE `superuser` DISABLE KEYS */;
INSERT INTO `superuser` VALUES (1,'o-XSVwRj5uPsuu4C3ckFLpsxqPsc','周天宇',NULL,NULL,'2020-03-20 23:28:28.000000',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `superuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unconfirmuser`
--

DROP TABLE IF EXISTS `unconfirmuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `unconfirmuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openId` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `createTime` datetime(6) NOT NULL,
  `IDcard` varchar(255) DEFAULT NULL,
  `extraInfo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unconfirmuser`
--

LOCK TABLES `unconfirmuser` WRITE;
/*!40000 ALTER TABLE `unconfirmuser` DISABLE KEYS */;
INSERT INTO `unconfirmuser` VALUES (1,'o-XSVwRj5uPsuu4C3ckFLpsxqPsc','周天宇','15557151005','123','2020-03-21 00:27:11.732777',NULL,NULL);
/*!40000 ALTER TABLE `unconfirmuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unconfirmuser_ammeter`
--

DROP TABLE IF EXISTS `unconfirmuser_ammeter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `unconfirmuser_ammeter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unconfirmuser_id` int(11) NOT NULL,
  `ammeters_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unconfirmuser_id` (`unconfirmuser_id`,`ammeters_id`),
  KEY `unconfirmUser_ammete_ammeters_id_5f692f9541b5b132_fk_ammeters_id` (`ammeters_id`),
  CONSTRAINT `unconfirmU_unconfirmuser_id_52955f354d0c6ba8_fk_unconfirmUser_id` FOREIGN KEY (`unconfirmuser_id`) REFERENCES `unconfirmuser` (`id`),
  CONSTRAINT `unconfirmUser_ammete_ammeters_id_5f692f9541b5b132_fk_ammeters_id` FOREIGN KEY (`ammeters_id`) REFERENCES `ammeters` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unconfirmuser_ammeter`
--

LOCK TABLES `unconfirmuser_ammeter` WRITE;
/*!40000 ALTER TABLE `unconfirmuser_ammeter` DISABLE KEYS */;
/*!40000 ALTER TABLE `unconfirmuser_ammeter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `urlsource`
--

DROP TABLE IF EXISTS `urlsource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `urlsource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) DEFAULT NULL,
  `desc` varchar(100) DEFAULT NULL,
  `vaild` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `urlsource`
--

LOCK TABLES `urlsource` WRITE;
/*!40000 ALTER TABLE `urlsource` DISABLE KEYS */;
/*!40000 ALTER TABLE `urlsource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wxuser`
--

DROP TABLE IF EXISTS `wxuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `wxuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openId` varchar(255) NOT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `sex` tinyint(1) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `subscribe_time` bigint(20) NOT NULL,
  `subscribe` tinyint(1) NOT NULL,
  `subscribe_scene` varchar(50) DEFAULT NULL,
  `ammeter_id` bigint(20) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `IDcard` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `source_id` int(11) DEFAULT NULL,
  `vaild` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wxUser_e1be6330` (`openId`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wxuser`
--

LOCK TABLES `wxuser` WRITE;
/*!40000 ALTER TABLE `wxuser` DISABLE KEYS */;
INSERT INTO `wxuser` VALUES (1,'o-XSVwQPdEYOUWcq6QD9F0V9K9DU',NULL,1,NULL,NULL,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `wxuser` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-23 23:43:22
