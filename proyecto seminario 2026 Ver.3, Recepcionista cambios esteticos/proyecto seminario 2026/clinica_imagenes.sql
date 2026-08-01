-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: clinica_imagenes
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `citas`
--

DROP TABLE IF EXISTS `citas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `citas` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `convenio` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha` date NOT NULL,
  `hora` time(6) NOT NULL,
  `notas` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `creada_en` datetime(6) NOT NULL,
  `creada_por_id` bigint NOT NULL,
  `paciente_id` bigint NOT NULL,
  `tipo_estudio_id` bigint NOT NULL,
  `hora_llegada` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `citas_creada_por_id_e68819fa_fk_usuarios_id` (`creada_por_id`),
  KEY `citas_paciente_id_79b6833d_fk_pacientes_id` (`paciente_id`),
  KEY `citas_tipo_estudio_id_10b1026b_fk_tipos_estudio_id` (`tipo_estudio_id`),
  CONSTRAINT `citas_creada_por_id_e68819fa_fk_usuarios_id` FOREIGN KEY (`creada_por_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `citas_paciente_id_79b6833d_fk_pacientes_id` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`),
  CONSTRAINT `citas_tipo_estudio_id_10b1026b_fk_tipos_estudio_id` FOREIGN KEY (`tipo_estudio_id`) REFERENCES `tipos_estudio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citas`
--

LOCK TABLES `citas` WRITE;
/*!40000 ALTER TABLE `citas` DISABLE KEYS */;
INSERT INTO `citas` VALUES (1,'coex','agendada','2026-08-03','09:30:00.000000','Referida por IGSS, traer orden impresa.','2026-07-28 04:26:04.362698',3,1,3,NULL),(2,'coex','procesada','2026-07-27','13:00:00.000000','','2026-07-28 04:34:24.863014',3,2,1,NULL),(3,'coex','ausente','2026-07-28','07:00:00.000000','','2026-07-28 04:34:49.331282',3,3,1,NULL),(4,'coex','agendada','2026-07-28','10:00:00.000000','','2026-07-28 04:35:13.527580',3,4,1,'2026-07-28 05:16:02.935937'),(5,'coex','procesada','2026-07-27','07:00:00.000000','','2026-07-28 04:58:49.244949',2,5,2,'2026-07-28 04:59:11.329133'),(6,'coex','en_proceso','2026-07-27','08:00:00.000000','','2026-07-28 05:25:17.049089',3,6,1,'2026-07-28 05:25:17.053126'),(7,'coex','agendada','2026-07-30','07:00:00.000000','el paciente paqueño','2026-07-29 18:15:34.752863',3,7,1,NULL);
/*!40000 ALTER TABLE `citas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'sessions','0001_initial','2026-07-28 03:04:52.986069'),(2,'contenttypes','0001_initial','2026-07-28 03:04:53.039805'),(3,'contenttypes','0002_remove_content_type_name','2026-07-28 03:04:53.175223'),(4,'auth','0001_initial','2026-07-28 03:04:53.564959'),(5,'auth','0002_alter_permission_name_max_length','2026-07-28 03:04:53.710830'),(6,'auth','0003_alter_user_email_max_length','2026-07-28 03:04:53.715015'),(7,'auth','0004_alter_user_username_opts','2026-07-28 03:04:53.725140'),(8,'auth','0005_alter_user_last_login_null','2026-07-28 03:04:53.741102'),(9,'auth','0006_require_contenttypes_0002','2026-07-28 03:04:53.745045'),(10,'auth','0007_alter_validators_add_error_messages','2026-07-28 03:04:53.761296'),(11,'auth','0008_alter_user_username_max_length','2026-07-28 03:04:53.765039'),(12,'auth','0009_alter_user_last_name_max_length','2026-07-28 03:04:53.775198'),(13,'auth','0010_alter_group_name_max_length','2026-07-28 03:04:53.812149'),(14,'auth','0011_update_proxy_permissions','2026-07-28 03:04:53.826594'),(15,'auth','0012_alter_user_first_name_max_length','2026-07-28 03:04:53.838412'),(16,'accounts','0001_initial','2026-07-28 03:04:54.316307'),(17,'admin','0001_initial','2026-07-28 03:04:54.534938'),(18,'admin','0002_logentry_remove_auto_add','2026-07-28 03:04:54.544724'),(19,'admin','0003_logentry_add_action_flag_choices','2026-07-28 03:04:54.555409'),(20,'accounts','0002_traducir_tablas_django','2026-07-28 03:04:54.715116'),(21,'accounts','0003_usuario_rol','2026-07-28 03:29:54.883576'),(22,'pacientes','0001_initial','2026-07-28 04:22:20.866155'),(23,'pacientes','0002_seed_tipos_estudio','2026-07-28 04:22:20.889785'),(24,'pacientes','0003_alter_cita_estado','2026-07-28 04:50:40.404636'),(25,'pacientes','0004_cita_hora_llegada','2026-07-28 04:57:19.071432'),(26,'pacientes','0005_paciente_sexo_alter_cita_estado_ordentrabajo','2026-07-28 05:21:14.265555');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupos`
--

DROP TABLE IF EXISTS `grupos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupos`
--

LOCK TABLES `grupos` WRITE;
/*!40000 ALTER TABLE `grupos` DISABLE KEYS */;
/*!40000 ALTER TABLE `grupos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupos_permisos`
--

DROP TABLE IF EXISTS `grupos_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupos_permisos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `permisos` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `grupos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupos_permisos`
--

LOCK TABLES `grupos_permisos` WRITE;
/*!40000 ALTER TABLE `grupos_permisos` DISABLE KEYS */;
/*!40000 ALTER TABLE `grupos_permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_trabajo`
--

DROP TABLE IF EXISTS `ordenes_trabajo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes_trabajo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `motivo` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `creada_en` datetime(6) NOT NULL,
  `cita_id` bigint NOT NULL,
  `creada_por_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cita_id` (`cita_id`),
  KEY `ordenes_trabajo_creada_por_id_c12af009_fk_usuarios_id` (`creada_por_id`),
  CONSTRAINT `ordenes_trabajo_cita_id_aa413d53_fk_citas_id` FOREIGN KEY (`cita_id`) REFERENCES `citas` (`id`),
  CONSTRAINT `ordenes_trabajo_creada_por_id_c12af009_fk_usuarios_id` FOREIGN KEY (`creada_por_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_trabajo`
--

LOCK TABLES `ordenes_trabajo` WRITE;
/*!40000 ALTER TABLE `ordenes_trabajo` DISABLE KEYS */;
INSERT INTO `ordenes_trabajo` VALUES (1,'Paciente de 38 años, femenino, presenta lesiones graves en el brazo izquierdo tras caída.','2026-07-28 05:25:51.805024',6,3);
/*!40000 ALTER TABLE `ordenes_trabajo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pacientes`
--

DROP TABLE IF EXISTS `pacientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pacientes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `dpi` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `sexo` varchar(1) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dpi` (`dpi`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pacientes`
--

LOCK TABLES `pacientes` WRITE;
/*!40000 ALTER TABLE `pacientes` DISABLE KEYS */;
INSERT INTO `pacientes` VALUES (1,'1234567890101','Maria','Lopez','50212345678','1990-05-14','M'),(2,'1111','Paciente','Uno','','1990-01-01','M'),(3,'2222','Paciente','Dos','','1990-01-01','M'),(4,'3333','Paciente','Tres','','1990-01-01','M'),(5,'5555','Carlos','Ramirez','','1985-03-01','M'),(6,'7777','Ana','Gomez','','1988-06-15','F'),(7,'12123','pueba','jahajha','1881','2026-07-07','M');
/*!40000 ALTER TABLE `pacientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `tipos_contenido` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
INSERT INTO `permisos` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add usuario',6,'add_usuario'),(22,'Can change usuario',6,'change_usuario'),(23,'Can delete usuario',6,'delete_usuario'),(24,'Can view usuario',6,'view_usuario'),(25,'Can add paciente',7,'add_paciente'),(26,'Can change paciente',7,'change_paciente'),(27,'Can delete paciente',7,'delete_paciente'),(28,'Can view paciente',7,'view_paciente'),(29,'Can add tipo de estudio',8,'add_tipoestudio'),(30,'Can change tipo de estudio',8,'change_tipoestudio'),(31,'Can delete tipo de estudio',8,'delete_tipoestudio'),(32,'Can view tipo de estudio',8,'view_tipoestudio'),(33,'Can add cita',9,'add_cita'),(34,'Can change cita',9,'change_cita'),(35,'Can delete cita',9,'delete_cita'),(36,'Can view cita',9,'view_cita'),(37,'Can add orden de trabajo',10,'add_ordentrabajo'),(38,'Can change orden de trabajo',10,'change_ordentrabajo'),(39,'Can delete orden de trabajo',10,'delete_ordentrabajo'),(40,'Can view orden de trabajo',10,'view_ordentrabajo');
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registros_admin`
--

DROP TABLE IF EXISTS `registros_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registros_admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_usuarios_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `tipos_contenido` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_usuarios_id` FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `registros_admin_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registros_admin`
--

LOCK TABLES `registros_admin` WRITE;
/*!40000 ALTER TABLE `registros_admin` DISABLE KEYS */;
/*!40000 ALTER TABLE `registros_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesiones`
--

DROP TABLE IF EXISTS `sesiones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesiones` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesiones`
--

LOCK TABLES `sesiones` WRITE;
/*!40000 ALTER TABLE `sesiones` DISABLE KEYS */;
INSERT INTO `sesiones` VALUES ('2jbehn218h21jgpgmc02friwquvv6dgo','.eJxVjMsOwiAQRf-FtSHAFDK4dO83kBkeUjWQlHZl_Hdt0oVu7znnvkSgba1hG3kJcxJnYcTpd2OKj9x2kO7Ubl3G3tZlZrkr8qBDXnvKz8vh_h1UGvVbk-MJAexEXqNh1MVmpJSBPCjPybFBC-A4RiJvYlHFGtYOidgzK_H-AOIYOFM:1woaMf:sTIsUWyNeygWE6bFAgy5sJwCZ2iKptLCtof48NrYIOU','2026-08-11 05:28:29.644592'),('sje493wug0mpn4c362hp0uhgowcyf1yk','.eJxVjMsOgjAURP-la9PQN3Xpnm9o7qNY1JSEwsr470LCQleTzDkzb5FgW0vaWl7SxOIqjLj8dgj0zPUA_IB6nyXNdV0mlIciT9rkMHN-3U7376BAK_s662Ct7qOFQN5FZxwEBRjCHh3iyIqZetYczYhkvO58VBS9AgYPqMTnC9ZmN_w:1woaUV:fXk0rS86HpJbXkUrTv9DOvs3xnxeGsbMfJLUBTtPJQU','2026-08-11 05:36:35.426200');
/*!40000 ALTER TABLE `sesiones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_contenido`
--

DROP TABLE IF EXISTS `tipos_contenido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_contenido` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_contenido`
--

LOCK TABLES `tipos_contenido` WRITE;
/*!40000 ALTER TABLE `tipos_contenido` DISABLE KEYS */;
INSERT INTO `tipos_contenido` VALUES (6,'accounts','usuario'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(9,'pacientes','cita'),(10,'pacientes','ordentrabajo'),(7,'pacientes','paciente'),(8,'pacientes','tipoestudio'),(5,'sessions','session');
/*!40000 ALTER TABLE `tipos_contenido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_estudio`
--

DROP TABLE IF EXISTS `tipos_estudio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_estudio` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_estudio`
--

LOCK TABLES `tipos_estudio` WRITE;
/*!40000 ALTER TABLE `tipos_estudio` DISABLE KEYS */;
INSERT INTO `tipos_estudio` VALUES (1,'Rayos X'),(4,'Resonancia'),(3,'Tomografía'),(2,'Ultrasonido');
/*!40000 ALTER TABLE `tipos_estudio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `rol` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'pbkdf2_sha256$1000000$nd11OJVavwESXugykppf6m$VdCnNmZn3Jn/86ys7SPIq9XA3H1LHyWYz+ypJ8DXYmk=','2026-07-29 18:11:42.008341',1,'admin','','','admin@clinica.local',1,1,'2026-07-28 03:10:34.957321','administrador'),(2,'pbkdf2_sha256$1000000$53oUDa8RCT647VHhgb5mgn$c8foey66c6vQ/gU23buPs3YcoRrOsEeE2ZLm4r0ADYo=','2026-07-28 05:28:29.637482',0,'tecnico1','Juan','Perez','tecnico1@clinica.local',0,1,'2026-07-28 03:33:09.704979','tecnico_imagenes'),(3,'pbkdf2_sha256$1000000$OiNQ99G0nBw7Hfqqo4Wcld$ONuu1pSShhQB6TP26rYR3xxU9f1Z0ak6n+7HqXw8dnk=','2026-07-29 18:13:58.439397',0,'Elmer','Elmer Adrián','Melendrez Catalan','elmeradrianctalan@gmail.com',0,1,'2026-07-28 03:36:40.973107','recepcionista'),(4,'pbkdf2_sha256$1000000$aSFXg5keV37wGEsK1Ts1PK$ojepQqtpr8iPmK6hIMsdJVk6hElnOGAoXoSuqtnSens=','2026-07-28 03:47:35.506797',0,'marilin','Marilin Adriana','Yaque Henandez','marilin@gmail.com',0,1,'2026-07-28 03:47:09.530490','tecnico_imagenes'),(5,'pbkdf2_sha256$1000000$FLBb2pI4ahYEDIiW9UTqa0$G+6f5rB4pfAjoeo3rou/sAdx2JFCuTN0cgRxVfZEeus=','2026-07-28 05:26:44.402108',0,'tecnico_img','','','',0,1,'2026-07-28 05:24:21.937156','tecnico_imagenes');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_grupos`
--

DROP TABLE IF EXISTS `usuarios_grupos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_grupos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuarios_grupos_usuario_id_group_id_1097394d_uniq` (`usuario_id`,`group_id`),
  KEY `usuarios_grupos_group_id_f7bf68b7_fk_auth_group_id` (`group_id`),
  CONSTRAINT `usuarios_grupos_group_id_f7bf68b7_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `grupos` (`id`),
  CONSTRAINT `usuarios_grupos_usuario_id_72c46a6b_fk_usuarios_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_grupos`
--

LOCK TABLES `usuarios_grupos` WRITE;
/*!40000 ALTER TABLE `usuarios_grupos` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_grupos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_permisos`
--

DROP TABLE IF EXISTS `usuarios_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_permisos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuarios_permisos_usuario_id_permission_id_85b53a8b_uniq` (`usuario_id`,`permission_id`),
  KEY `usuarios_permisos_permission_id_6e69ac22_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `usuarios_permisos_permission_id_6e69ac22_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `permisos` (`id`),
  CONSTRAINT `usuarios_permisos_usuario_id_4cb02bdc_fk_usuarios_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_permisos`
--

LOCK TABLES `usuarios_permisos` WRITE;
/*!40000 ALTER TABLE `usuarios_permisos` DISABLE KEYS */;
INSERT INTO `usuarios_permisos` VALUES (2,2,21),(1,2,24),(3,3,1),(4,3,2),(5,3,3),(6,3,4),(7,3,5),(8,3,6),(9,3,7),(10,3,8),(11,3,9),(12,3,10),(13,3,11),(14,3,12),(15,3,13),(16,3,14),(17,3,15),(18,3,16),(19,3,17),(20,3,18),(21,3,19),(22,3,20),(23,3,21),(24,3,22),(25,3,23),(26,3,24);
/*!40000 ALTER TABLE `usuarios_permisos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-30  7:39:59
