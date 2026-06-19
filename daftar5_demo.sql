-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 19, 2026 at 11:29 AM
-- Server version: 8.4.7
-- PHP Version: 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `daftar_barnameh`
--

-- --------------------------------------------------------

--
-- Table structure for table `accesslevels`
--

DROP TABLE IF EXISTS `accesslevels`;
CREATE TABLE IF NOT EXISTS `accesslevels` (
  `AccessLevelID` int NOT NULL AUTO_INCREMENT,
  `AccessLevelName` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `Description` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`AccessLevelID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `accesslevels`
--

INSERT INTO `accesslevels` (`AccessLevelID`, `AccessLevelName`, `Description`) VALUES
(1, 'admin', 'دسترسی کامل'),
(2, 'Editor', 'مربوط به سوپروایزر'),
(3, 'Viewer', 'برای افرادی که فقط دسترسی به قسمت آمار نیاز داند'),
(4, 'any', 'هیچ کس برای باگ سیستم'),
(5, 'metron', 'دسترسی مترون'),
(6, 'modir', 'دسترسی مدیران'),
(7, 'm_fani', 'دسترسی مسئول فنی'),
(8, 'rais', 'دسترسی ریاست و مدیریت'),
(10, 'پرستار هموویژلانس', 'کنترل کمی و کیفی خون'),
(13, 'مسئول بخش', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `audittrail`
--

DROP TABLE IF EXISTS `audittrail`;
CREATE TABLE IF NOT EXISTS `audittrail` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `DateTime` datetime NOT NULL,
  `Script` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `User` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IPAddress` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `UserAgent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Action` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Table` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Field` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `KeyValue` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `OldValue` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `NewValue` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Status` enum('SUCCESS','FAILURE','PENDING') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'SUCCESS',
  `ErrorMessage` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `SessionID` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `idx_datetime` (`DateTime`),
  KEY `idx_user` (`User`),
  KEY `idx_table_action` (`Table`,`Action`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `audittrail`
--

INSERT INTO `audittrail` (`Id`, `DateTime`, `Script`, `User`, `IPAddress`, `UserAgent`, `Action`, `Table`, `Field`, `KeyValue`, `OldValue`, `NewValue`, `Status`, `ErrorMessage`, `SessionID`) VALUES
(1, '2026-06-14 09:47:41', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(2, '2026-06-14 10:24:00', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(3, '2026-06-14 10:26:49', 'app.py', 'UserID:42', NULL, NULL, 'INSERT', 'users', NULL, '42', NULL, '{\"fullname\": \"تست بخش\", \"username\": \"9999999999\"}', 'SUCCESS', NULL, NULL),
(4, '2026-06-14 10:27:40', 'app.py', 'UserID:44', NULL, NULL, 'INSERT', 'users', NULL, '44', NULL, '{\"fullname\": \"مدیر تستی\", \"username\": \"3333333333\"}', 'SUCCESS', NULL, NULL),
(5, '2026-06-14 10:31:23', 'app.py', 'UserID:1', NULL, NULL, 'UPDATE', 'onvan_shift', NULL, '6', '{\"ID_onvan_shift\": 6, \"nam_shift\": \"شب\", \"shift_code\": \"N\", \"start_time\": \"20:00:00\", \"end_time\": \"8:00:00\", \"color_code\": \"#ce09ec\", \"time_duration\": \"12:00:00\"}', '{\"code\": \"N\", \"name\": \"شب\", \"start\": \"20:00\", \"end\": \"08:00\", \"duration\": \"12:00\", \"color\": \"#ce09ec\"}', 'SUCCESS', NULL, NULL),
(6, '2026-06-14 10:32:03', 'app.py', 'UserID:1', NULL, NULL, 'UPDATE', 'onvan_shift', NULL, '4', '{\"ID_onvan_shift\": 4, \"nam_shift\": \"فول\", \"shift_code\": \"F\", \"start_time\": \"8:00:00\", \"end_time\": \"8:00:00\", \"color_code\": \"#e60a4c\", \"time_duration\": \"23:00:00\"}', '{\"code\": \"F\", \"name\": \"فول\", \"start\": \"08:00\", \"end\": \"08:00\", \"duration\": \"25:00\", \"color\": \"#e60a4c\"}', 'SUCCESS', NULL, NULL),
(7, '2026-06-14 10:33:55', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(8, '2026-06-14 10:34:03', 'app.py', 'UserID:42', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(9, '2026-06-14 10:38:14', 'app.py', 'UserID:42', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(10, '2026-06-14 10:38:23', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(11, '2026-06-14 10:38:44', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'shift_namt', NULL, '140503242', NULL, 'تاریخ:14050324, روز:یکشنبه, شیفت:صبح و عصر', 'SUCCESS', NULL, NULL),
(12, '2026-06-14 10:42:50', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '34', NULL, 'شیفت:140503242, بخش:34, تعداد حاضر:6', 'SUCCESS', NULL, NULL),
(13, '2026-06-14 10:43:37', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'users', NULL, '1', NULL, '{\"fullname\": \"امجد\", \"username\": \"2222222222\"}', 'SUCCESS', NULL, NULL),
(14, '2026-06-14 10:52:19', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(15, '2026-06-14 10:59:23', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(16, '2026-06-14 10:59:36', 'app.py', 'UserID:41', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(17, '2026-06-14 10:59:46', 'app.py', 'UserID:41', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(18, '2026-06-14 11:00:00', 'app.py', 'UserID:41', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(19, '2026-06-14 11:00:49', 'app.py', 'UserID:38', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(20, '2026-06-14 11:01:47', 'app.py', 'UserID:38', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(21, '2026-06-14 11:01:59', 'app.py', 'UserID:41', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(22, '2026-06-14 11:05:18', 'app.py', 'UserID:41', NULL, NULL, 'INSERT', 'users', NULL, '41', NULL, '{\"fullname\": \"تست کارگزینی\", \"username\": \"6666666666\"}', 'SUCCESS', NULL, NULL),
(23, '2026-06-14 11:09:02', 'app.py', 'UserID:41', NULL, NULL, 'UPDATE', 'onvan_shift', NULL, '1', '{\"ID_onvan_shift\": 1, \"nam_shift\": \"صبح\", \"shift_code\": \"M\", \"start_time\": \"8:00:00\", \"end_time\": \"14:00:00\", \"color_code\": \"#e3f2fd\", \"time_duration\": \"6:00:00\"}', '{\"code\": \"M\", \"name\": \"صبح\", \"start\": \"08:00\", \"end\": \"14:00\", \"duration\": \"06:30\", \"color\": \"#e3f2fd\"}', 'SUCCESS', NULL, NULL),
(24, '2026-06-14 11:10:14', 'app.py', 'UserID:41', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(25, '2026-06-14 11:10:20', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(26, '2026-06-14 11:10:32', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '34', NULL, 'شیفت:140503242, بخش:34, تعداد حاضر:7', 'SUCCESS', NULL, NULL),
(27, '2026-06-14 11:14:01', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_ghaybat', NULL, NULL, NULL, 'پرسنل:98, بخش:31, وضعیت:غیبت=1, تأخیر=0, تعجیل=0, پاس=0, ریزشیفت=شب', 'SUCCESS', NULL, NULL),
(28, '2026-06-14 11:22:28', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(29, '2026-06-14 11:24:12', 'app.py', 'UserID:1', NULL, NULL, 'DELETE', 'tbl_ghaybat', NULL, '1', NULL, NULL, 'SUCCESS', NULL, NULL),
(30, '2026-06-14 11:24:41', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_ghaybat', NULL, NULL, NULL, 'پرسنل:166, بخش:34, ریزشیفت:2', 'SUCCESS', NULL, NULL),
(31, '2026-06-14 11:25:15', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_ghaybat', NULL, NULL, NULL, 'پرسنل:367, بخش:30, ریزشیفت:2', 'SUCCESS', NULL, NULL),
(32, '2026-06-14 11:38:14', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(33, '2026-06-14 11:43:53', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(34, '2026-06-14 13:40:52', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(35, '2026-06-14 13:52:58', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(36, '2026-06-14 14:12:20', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(37, '2026-06-14 15:38:30', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(38, '2026-06-14 18:13:56', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(39, '2026-06-14 19:12:47', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(40, '2026-06-14 19:27:27', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(41, '2026-06-14 19:31:39', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(42, '2026-06-14 19:39:05', 'app.py', 'Unknown', NULL, NULL, 'Login Attempt', NULL, NULL, NULL, NULL, NULL, '', '⛔ نام کاربری یا رمز عبور نادرست است', NULL),
(43, '2026-06-14 19:39:10', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(44, '2026-06-14 19:45:56', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(45, '2026-06-14 22:21:10', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(46, '2026-06-14 22:28:42', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(47, '2026-06-14 22:28:47', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(48, '2026-06-14 22:47:02', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(49, '2026-06-14 22:47:08', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(50, '2026-06-14 22:47:50', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(51, '2026-06-15 08:40:53', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(52, '2026-06-15 08:43:52', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(53, '2026-06-15 08:43:59', 'app.py', 'UserID:35', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(54, '2026-06-15 08:44:47', 'app.py', 'UserID:35', NULL, NULL, 'INSERT', 'users', NULL, '35', NULL, '{\"fullname\": \"نوا نوایی\", \"username\": \"5555555555\"}', 'SUCCESS', NULL, NULL),
(55, '2026-06-15 08:45:05', 'app.py', 'UserID:35', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(56, '2026-06-15 08:45:13', 'app.py', 'UserID:35', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(57, '2026-06-15 08:47:53', 'app.py', 'UserID:35', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(58, '2026-06-15 08:48:07', 'app.py', 'UserID:38', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(59, '2026-06-15 08:49:30', 'app.py', 'UserID:38', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(60, '2026-06-15 10:18:46', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(61, '2026-06-15 10:25:03', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(62, '2026-06-15 10:40:38', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(63, '2026-06-15 10:55:56', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(64, '2026-06-15 10:57:12', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(65, '2026-06-15 10:59:00', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(66, '2026-06-15 12:01:29', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(67, '2026-06-15 12:11:40', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(68, '2026-06-15 12:14:17', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'shift_namt', NULL, '140503246', NULL, 'تاریخ:14050324, روز:یکشنبه, شیفت:شب', 'SUCCESS', NULL, NULL),
(69, '2026-06-15 12:15:07', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '30', NULL, 'شیفت:140503246, بخش:30, تعداد حاضر:4', 'SUCCESS', NULL, NULL),
(70, '2026-06-15 12:15:32', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '34', NULL, 'شیفت:140503246, بخش:34, تعداد حاضر:5', 'SUCCESS', NULL, NULL),
(71, '2026-06-15 12:27:04', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(72, '2026-06-15 12:30:06', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(73, '2026-06-15 12:37:00', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(74, '2026-06-15 12:53:41', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(75, '2026-06-15 13:42:04', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(76, '2026-06-15 13:43:13', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'shift_namt', NULL, '140503251', NULL, 'تاریخ:14050325, روز:دوشنبه, شیفت:صبح', 'SUCCESS', NULL, NULL),
(77, '2026-06-15 13:55:41', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(78, '2026-06-15 13:56:19', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '34', NULL, 'شیفت:140503251, بخش:34, تعداد حاضر:4', 'SUCCESS', NULL, NULL),
(79, '2026-06-15 13:56:40', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '30', NULL, 'شیفت:140503251, بخش:30, تعداد حاضر:6', 'SUCCESS', NULL, NULL),
(80, '2026-06-15 13:56:59', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '31', NULL, 'شیفت:140503251, بخش:31, تعداد حاضر:8', 'SUCCESS', NULL, NULL),
(81, '2026-06-15 13:57:32', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'shift_namt', NULL, '140503255', NULL, 'تاریخ:14050325, روز:دوشنبه, شیفت:عصروشب', 'SUCCESS', NULL, NULL),
(82, '2026-06-15 13:58:49', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '34', NULL, 'شیفت:140503255, بخش:34, تعداد حاضر:6', 'SUCCESS', NULL, NULL),
(83, '2026-06-15 13:59:21', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '30', NULL, 'شیفت:140503255, بخش:30, تعداد حاضر:5', 'SUCCESS', NULL, NULL),
(84, '2026-06-15 14:01:32', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'tbl_hozor', NULL, '34', NULL, 'شیفت:140503255, بخش:34, تعداد حاضر:7', 'SUCCESS', NULL, NULL),
(85, '2026-06-15 14:13:37', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(86, '2026-06-15 14:37:46', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(87, '2026-06-15 14:39:45', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(88, '2026-06-15 14:47:52', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(89, '2026-06-15 14:52:27', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(90, '2026-06-15 15:31:21', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(91, '2026-06-15 15:55:16', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(92, '2026-06-15 16:02:55', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(93, '2026-06-15 16:03:02', 'app.py', 'UserID:35', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(94, '2026-06-15 16:06:54', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(95, '2026-06-15 16:12:20', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'Unknown', NULL, NULL, '[[1, \"reports_ankal\"], [1, \"reports_attendance\"], [1, \"reports_blood\"], [1, \"reports_codes\"], [1, \"reports_crisis\"], [1, \"reports_rounds\"], [1, \"reports_stats\"], [1, \"reports_workflow\"], [2, \"reports_ankal\"], [2, \"reports_attendance\"], [2, \"reports_blood\"], [2, \"reports_codes\"], [2, \"reports_crisis\"], [2, \"reports_rounds\"], [2, \"reports_stats\"], [2, \"reports_workflow\"], [3, \"reports_ankal\"], [3, \"reports_attendance\"], [3, \"reports_blood\"], [3, \"reports_codes\"], [3, \"reports_crisis\"], [3, \"rep...', '[{\"level_id\": 1, \"form_name\": \"manager_management_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_reports\"}, {\"level_id\": 5, \"form_name\": \"manager_reports\"}, {\"level_id\": 6, \"form_name\": \"manager_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 2, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 3, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 6, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_edit\"}, {\"lev...', 'SUCCESS', NULL, NULL),
(96, '2026-06-15 16:13:49', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(97, '2026-06-15 16:13:58', 'app.py', 'UserID:35', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(98, '2026-06-15 16:14:31', 'app.py', 'UserID:35', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(99, '2026-06-15 16:14:43', 'app.py', 'UserID:38', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(100, '2026-06-15 16:28:23', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(101, '2026-06-15 16:29:48', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'Unknown', NULL, NULL, '[[1, \"manager_management_reports\"], [1, \"manager_reports\"], [1, \"manager_shift_comparison\"], [1, \"manager_shift_edit\"], [1, \"manager_shift_review\"], [1, \"manager_shifts\"], [1, \"reports_ankal\"], [1, \"reports_attendance\"], [1, \"reports_blood\"], [1, \"reports_codes\"], [1, \"reports_crisis\"], [1, \"reports_rounds\"], [1, \"reports_stats\"], [1, \"reports_workflow\"], [2, \"manager_shift_comparison\"], [2, \"manager_shift_edit\"], [2, \"reports_ankal\"], [2, \"reports_attendance\"], [2, \"reports_blood\"], [2, \"rep...', '[{\"level_id\": 1, \"form_name\": \"manager_management_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_reports\"}, {\"level_id\": 5, \"form_name\": \"manager_reports\"}, {\"level_id\": 6, \"form_name\": \"manager_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 2, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 3, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 6, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_edit\"}, {\"lev...', 'SUCCESS', NULL, NULL),
(102, '2026-06-15 16:30:19', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'Unknown', NULL, NULL, '[[1, \"manager_management_reports\"], [1, \"manager_reports\"], [1, \"manager_shift_comparison\"], [1, \"manager_shift_edit\"], [1, \"manager_shift_review\"], [1, \"manager_shifts\"], [1, \"matron_checklist\"], [1, \"matron_codes\"], [1, \"matron_personnel\"], [1, \"matron_reports\"], [1, \"reports_ankal\"], [1, \"reports_attendance\"], [1, \"reports_blood\"], [1, \"reports_codes\"], [1, \"reports_crisis\"], [1, \"reports_rounds\"], [1, \"reports_stats\"], [1, \"reports_workflow\"], [2, \"manager_shift_comparison\"], [2, \"manager...', '[{\"level_id\": 1, \"form_name\": \"manager_management_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_reports\"}, {\"level_id\": 5, \"form_name\": \"manager_reports\"}, {\"level_id\": 6, \"form_name\": \"manager_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 2, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 3, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 6, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_edit\"}, {\"lev...', 'SUCCESS', NULL, NULL),
(103, '2026-06-15 16:38:42', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(104, '2026-06-15 16:48:27', 'app.py', 'UserID:1', NULL, NULL, 'INSERT', 'Unknown', NULL, NULL, '[[1, \"manager_management_reports\"], [1, \"manager_reports\"], [1, \"manager_shift_comparison\"], [1, \"manager_shift_edit\"], [1, \"manager_shift_review\"], [1, \"manager_shifts\"], [1, \"matron_checklist\"], [1, \"matron_codes\"], [1, \"matron_personnel\"], [1, \"matron_reports\"], [1, \"reports_ankal\"], [1, \"reports_attendance\"], [1, \"reports_blood\"], [1, \"reports_codes\"], [1, \"reports_crisis\"], [1, \"reports_rounds\"], [1, \"reports_stats\"], [1, \"reports_workflow\"], [2, \"manager_shift_comparison\"], [2, \"manager...', '[{\"level_id\": 1, \"form_name\": \"manager_management_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_reports\"}, {\"level_id\": 5, \"form_name\": \"manager_reports\"}, {\"level_id\": 6, \"form_name\": \"manager_reports\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 2, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 3, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 6, \"form_name\": \"manager_shift_comparison\"}, {\"level_id\": 1, \"form_name\": \"manager_shift_edit\"}, {\"lev...', 'SUCCESS', NULL, NULL),
(105, '2026-06-15 17:27:32', 'app.py', 'Unknown', NULL, NULL, 'Login Attempt', NULL, NULL, NULL, NULL, NULL, '', '⛔ خطا در اتصال به پایگاه داده. لطفاً بعداً تلاش کنید.', NULL),
(106, '2026-06-15 17:27:46', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(107, '2026-06-15 17:31:33', 'app.py', 'Unknown', NULL, NULL, 'Login Attempt', NULL, NULL, NULL, NULL, NULL, '', '⛔ نام کاربری یا رمز عبور نادرست است', NULL),
(108, '2026-06-15 17:31:46', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(109, '2026-06-15 17:33:44', 'app.py', 'Unknown', NULL, NULL, 'Login Attempt', NULL, NULL, NULL, NULL, NULL, '', '⛔ نام کاربری یا رمز عبور نادرست است', NULL),
(110, '2026-06-15 17:34:03', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(111, '2026-06-15 17:46:27', 'app.py', 'UserID:44', NULL, NULL, 'INSERT', 'users', NULL, '44', NULL, '{\"fullname\": \"مدیر تستی\", \"username\": \"3333333333\"}', 'SUCCESS', NULL, NULL),
(112, '2026-06-15 17:49:02', 'app.py', 'UserID:44', NULL, NULL, 'INSERT', 'users', NULL, '44', NULL, '{\"fullname\": \"مدیر تستی\", \"username\": \"3333333333\"}', 'SUCCESS', NULL, NULL),
(113, '2026-06-15 17:49:33', 'app.py', 'UserID:44', NULL, NULL, 'INSERT', 'users', NULL, '44', NULL, '{\"fullname\": \"مدیر تستی\", \"username\": \"3333333333\"}', 'SUCCESS', NULL, NULL),
(114, '2026-06-15 17:50:09', 'app.py', 'UserID:44', NULL, NULL, 'INSERT', 'users', NULL, '44', NULL, '{\"fullname\": \"مدیر تستی\", \"username\": \"3333333333\"}', 'SUCCESS', NULL, NULL),
(115, '2026-06-15 18:25:14', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(116, '2026-06-15 18:26:11', 'app.py', 'UserID:41', NULL, NULL, 'INSERT', 'users', NULL, '41', NULL, '{\"fullname\": \"تست کارگزینی\", \"username\": \"6666666666\"}', 'SUCCESS', NULL, NULL),
(117, '2026-06-15 18:26:52', 'app.py', 'UserID:1', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(118, '2026-06-15 18:27:04', 'app.py', 'UserID:38', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(119, '2026-06-15 18:27:11', 'app.py', 'UserID:38', NULL, NULL, 'Logout', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(120, '2026-06-15 18:27:19', 'app.py', 'UserID:41', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(121, '2026-06-15 18:38:35', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(122, '2026-06-15 18:39:04', 'app.py', 'UserID:41', NULL, NULL, 'INSERT', 'users', NULL, '41', NULL, '{\"fullname\": \"تست کارگزینی\", \"username\": \"6666666666\"}', 'SUCCESS', NULL, NULL),
(123, '2026-06-15 18:50:31', 'app.py', 'UserID:1', NULL, NULL, 'Login', NULL, NULL, NULL, NULL, NULL, 'SUCCESS', NULL, NULL),
(124, '2026-06-15 18:51:02', 'app.py', 'UserID:41', NULL, NULL, 'INSERT', 'users', NULL, '41', NULL, '{\"fullname\": \"تست کارگزینی\", \"username\": \"6666666666\"}', 'SUCCESS', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `dashboard_content`
--

DROP TABLE IF EXISTS `dashboard_content`;
CREATE TABLE IF NOT EXISTS `dashboard_content` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content_type` enum('slider','news','quick_link','welcome_message','banner') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `link_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `link_text` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bg_color` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '#3b82f6',
  `text_color` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '#ffffff',
  `sort_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `start_date` int DEFAULT NULL,
  `expiry_date` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `exportlog`
--

DROP TABLE IF EXISTS `exportlog`;
CREATE TABLE IF NOT EXISTS `exportlog` (
  `FileId` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `DateTime` datetime NOT NULL,
  `User` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ExportType` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Table` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `KeyValue` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Filename` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Request` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`FileId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hafth_aiiam`
--

DROP TABLE IF EXISTS `hafth_aiiam`;
CREATE TABLE IF NOT EXISTS `hafth_aiiam` (
  `ID` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `hafth_aiiam`
--

INSERT INTO `hafth_aiiam` (`ID`) VALUES
('شنبه'),
('یکشنبه'),
('دوشنبه'),
('سه شنبه'),
('چهار شنبه'),
('پنج شنبه'),
('جمعه');

-- --------------------------------------------------------

--
-- Table structure for table `onvan_shift`
--

DROP TABLE IF EXISTS `onvan_shift`;
CREATE TABLE IF NOT EXISTS `onvan_shift` (
  `ID_onvan_shift` int NOT NULL AUTO_INCREMENT,
  `nam_shift` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `shift_code` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `color_code` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `time_duration` time NOT NULL,
  PRIMARY KEY (`ID_onvan_shift`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `onvan_shift`
--

INSERT INTO `onvan_shift` (`ID_onvan_shift`, `nam_shift`, `shift_code`, `start_time`, `end_time`, `color_code`, `time_duration`) VALUES
(1, 'صبح', 'M', '08:00:00', '14:00:00', '#e3f2fd', '06:30:00'),
(2, 'صبح و عصر', 'ME', '08:00:00', '20:00:00', '#3bf748', '12:00:00'),
(3, 'عصر', 'E', '14:00:00', '20:00:00', '#fff3e0', '06:00:00'),
(4, 'فول', 'F', '08:00:00', '08:00:00', '#e60a4c', '25:00:00'),
(5, 'عصروشب', 'EN', '14:00:00', '08:00:00', '#3b82f6', '18:00:00'),
(6, 'شب', 'N', '20:00:00', '08:00:00', '#ce09ec', '12:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `shift_namt`
--

DROP TABLE IF EXISTS `shift_namt`;
CREATE TABLE IF NOT EXISTS `shift_namt` (
  `CreatedDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `dat_sabt` int DEFAULT NULL,
  `ID_shift` int NOT NULL,
  `monasebat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam_shift` int DEFAULT NULL,
  `nam_super` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `roz_hafteh` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `tarkib` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `UserID` int DEFAULT '0',
  `mynewdat` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  PRIMARY KEY (`ID_shift`),
  KEY `tbl-shiftnam-shift` (`nam_shift`),
  KEY `UserID` (`UserID`),
  KEY `Usersshift_namT` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `shift_namt`
--

INSERT INTO `shift_namt` (`CreatedDate`, `dat_sabt`, `ID_shift`, `monasebat`, `nam_shift`, `nam_super`, `roz_hafteh`, `tarkib`, `UserID`, `mynewdat`) VALUES
('2026-06-14 10:38:44', 14050324, 140503242, 'خدایا به امید خودت فقط', 2, 'امجد', 'یکشنبه', 'یکشنبه 1405/03/24 صبح و عصر', 1, ''),
('2026-06-15 12:14:17', 14050324, 140503246, '', 6, 'امجد', 'یکشنبه', 'یکشنبه 1405/03/24 شب', 1, ''),
('2026-06-15 13:43:13', 14050325, 140503251, '', 1, 'امجد', 'دوشنبه', 'دوشنبه 1405/03/25 صبح', 1, ''),
('2026-06-15 13:57:32', 14050325, 140503255, '', 5, 'امجد', 'دوشنبه', 'دوشنبه 1405/03/25 عصروشب', 1, '');

-- --------------------------------------------------------

--
-- Table structure for table `site_settings`
--

DROP TABLE IF EXISTS `site_settings`;
CREATE TABLE IF NOT EXISTS `site_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `site_settings`
--

INSERT INTO `site_settings` (`id`, `setting_key`, `setting_value`) VALUES
(2, 'hospital_logo', 'uploads/logo/logo.png'),
(3, 'center_name', 'دانشگاه علوم پزشکی کرمانشاه'),
(4, 'sub_center_name', 'بیمارستان خیریه لنوا');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_amar_data`
--

DROP TABLE IF EXISTS `tbl_amar_data`;
CREATE TABLE IF NOT EXISTS `tbl_amar_data` (
  `ID_data` int NOT NULL AUTO_INCREMENT,
  `bakhsh_id` int NOT NULL,
  `item_id` int NOT NULL,
  `value` int DEFAULT '0',
  `nam_shift` varchar(50) DEFAULT NULL,
  `dat_sabt` int DEFAULT NULL,
  `zaman_sabt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `UserID` int NOT NULL,
  `tozihat` text,
  PRIMARY KEY (`ID_data`),
  KEY `bakhsh_id` (`bakhsh_id`),
  KEY `item_id` (`item_id`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_amar_items`
--

DROP TABLE IF EXISTS `tbl_amar_items`;
CREATE TABLE IF NOT EXISTS `tbl_amar_items` (
  `ID_item` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(255) NOT NULL,
  `unit` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID_item`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tbl_amar_items`
--

INSERT INTO `tbl_amar_items` (`ID_item`, `item_name`, `unit`) VALUES
(18, 'بستری', 'تعداد'),
(19, 'پذیرش', 'تعداد'),
(20, 'ترخیص', 'تعداد'),
(21, 'اعزام', 'تعداد'),
(22, 'سقوط از تخت', 'تعداد'),
(23, 'عمل شده', 'تعداد');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_amliat_kod`
--

DROP TABLE IF EXISTS `tbl_amliat_kod`;
CREATE TABLE IF NOT EXISTS `tbl_amliat_kod` (
  `dat_sabt` int DEFAULT NULL,
  `ID_kod` int NOT NULL AUTO_INCREMENT,
  `jens` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `mavred1` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam_bakhsh` int NOT NULL,
  `nam_biar` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam_pezshk_lider` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam_shift` int NOT NULL,
  `natijeh_amlit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `onvan_kod` int NOT NULL,
  `sen` int NOT NULL,
  `tashkhis_pezeshk` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `tavzih` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `time_saat_dagig_shoro` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `time_sat_dagigeh_paian` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `sen_mah` int DEFAULT NULL,
  `sen_roz` int DEFAULT NULL,
  PRIMARY KEY (`ID_kod`),
  KEY `shift_namTtbl_amliat_kod` (`nam_shift`),
  KEY `tbl_bakhshtbl_amliat_kod` (`nam_bakhsh`),
  KEY `tbl_onvan_kodtbl_amliat_kod` (`onvan_kod`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_ankal`
--

DROP TABLE IF EXISTS `tbl_ankal`;
CREATE TABLE IF NOT EXISTS `tbl_ankal` (
  `dat_sabt` int DEFAULT NULL,
  `ID_ankal` int NOT NULL AUTO_INCREMENT,
  `nam_pezshk` int NOT NULL,
  `nam_shift` int NOT NULL,
  `nam_takhasos` int NOT NULL,
  `no_rispons` tinyint(1) DEFAULT '0',
  `tozihat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_ankal`),
  UNIQUE KEY `ID` (`ID_ankal`),
  KEY `shift_namTtbl_ankal` (`nam_shift`),
  KEY `tbl_pezesktbl_ankal` (`nam_pezshk`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_arziabi_bakhsh`
--

DROP TABLE IF EXISTS `tbl_arziabi_bakhsh`;
CREATE TABLE IF NOT EXISTS `tbl_arziabi_bakhsh` (
  `dat_sabt` int DEFAULT NULL,
  `emtiaz` double DEFAULT '0',
  `ID_arziabi_bakhsh` int NOT NULL AUTO_INCREMENT,
  `id_ckeklist` int DEFAULT '0',
  `id_nam_bakhsh` int DEFAULT '0',
  `id_onvan_arziabi` int DEFAULT '0',
  `id_shift` int DEFAULT '0',
  `nokat_manfi` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nokhat_mosbat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nomreh_kol` double DEFAULT '0',
  `tozihat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `sanad` varchar(250) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`ID_arziabi_bakhsh`),
  KEY `id_ckeklist` (`id_ckeklist`),
  KEY `id_onvan_arziabi` (`id_onvan_arziabi`),
  KEY `id_shift` (`id_shift`),
  KEY `id-nam_bakhsh` (`id_nam_bakhsh`),
  KEY `shift_namTtbl_arziabi_bakhsh` (`id_shift`),
  KEY `tbl_arziabi_cheklisttbl_arziabi_bakhsh` (`id_ckeklist`),
  KEY `tbl_arzibi_onvantbl_arziabi_bakhsh` (`id_onvan_arziabi`),
  KEY `tbl_bakhshtbl_arziabi_bakhsh` (`id_nam_bakhsh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_arziabi_cheklist`
--

DROP TABLE IF EXISTS `tbl_arziabi_cheklist`;
CREATE TABLE IF NOT EXISTS `tbl_arziabi_cheklist` (
  `adres_sanjeh` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `dat_sabt` int DEFAULT NULL,
  `ID_cheklist` int NOT NULL AUTO_INCREMENT,
  `id_onvan_arziabi` int DEFAULT '0',
  `imani_chek` tinyint(1) DEFAULT '0',
  `nam_item` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `nomreh` double DEFAULT '0',
  `rahnamii` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `sath` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `vazn_sanjeh` double DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `kole_emtiaz` double NOT NULL,
  PRIMARY KEY (`ID_cheklist`),
  KEY `id_onvan_arziabi` (`id_onvan_arziabi`),
  KEY `tbl_arzibi_onvantbl_arziabi_cheklist` (`id_onvan_arziabi`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=166 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_arziabi_cheklist`
--

INSERT INTO `tbl_arziabi_cheklist` (`adres_sanjeh`, `dat_sabt`, `ID_cheklist`, `id_onvan_arziabi`, `imani_chek`, `nam_item`, `nomreh`, `rahnamii`, `sath`, `UserID`, `vazn_sanjeh`, `zaman_sabt`, `kole_emtiaz`) VALUES
('الف-1-1-1', 140501101, 1, 20, 0, 'سیاست‌های اصلی بر اساس ماموریت‌های بیمارستان و همسو با سیاست‌های بالادستی تدوین شده است.', 4, 'مبنای برنامه‌ریزی استراتژیک، مدیریت کیفیت و ارزیابی عملکرد بیمارستان است - ۱. تدوین سیاست‌های اصلی بیمارستان با رویکرد بیمار و خانواده محور ۲. تعیین سیاست‌های اصلی بر اساس نیازهای سلامت جامعه و سیاست‌های وزارت بهداشت ۳. همسویی سیاست‌های اصلی با اسناد بالادستی و قوانین ۴. تصویب سیاست‌های اصلی در تیم رهبری و مدیریت ۵. ابلاغ سیاست‌های اصلی به ذی‌نفعان کلیدی ۶. بازنگری دوره‌ای سیاست‌های اصلی و به‌روزرسانی آن ۷. آگاهی کارکنان از سیاست‌های اصلی مرتبط با حوزه کاری خود', '1', 1, 1, '2026-05-05 13:47:03', 4),
('الف-1-2-1', 140501101, 2, 20, 0, 'نمودار سازمانی با روابط و سطوح مسئولیت‌ها و اختیارات در بیمارستان تدوین و ابلاغ شده و ارتباط سازمانی بر اساس آن برقرار است.', 2, 'نمودار سازمانی باید نمایش تصویری از ساختار داخلی، سلسله مراتب دستوردهی و گزارش‌دهی باشد.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-2-2', 140501101, 3, 20, 0, 'وجود گواهی آموزش مدیران، برای پنج رده مدیریتی تعیین شده', 0, 'پنج رده مدیریتی: ۱. رئیس/مدیرعامل ۲. مدیر اجرایی/داخلی/مدیر خدمات پشتیبانی ۳. مدیر مالی ۴. مدیر پرستاری ۵. مدیر/مسئول بهبود کیفیت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-3-1', 140501101, 4, 20, 0, 'سند استراتژیک بیمارستان هماهنگ با سیاست‌های اصلی تدوین، مصوب، ابلاغ و بازنگری می‌شود.', 0, 'برنامه‌های ایمنی بیمار باید از اولویت‌های استراتژیک بیمارستان باشد.', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-5-2', 140501101, 5, 20, 0, 'کمیته‌های بیمارستانی بر اساس ساختار و عملکردی سازمان‌یافته در بیمارستان فعال هستند و به ارتقای کیفیت و حل مشکلات کمک می‌کنند.', 0, 'حداقل کمیته‌ها: بهبود کیفیت، مدیریت خطر و بلایا، کنترل عفونت، دارو و درمان، مرگ و میر، بافت و پیوند، انتقال خون، بهداشت محیط، مدارک پزشکی، احیا قلبی-ریوی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-6-1', 140501101, 6, 20, 1, 'تصمیمات و اقدامات تیم رهبری و مدیریت نشان دهنده اولویت بخشی به ارتقاء کیفیت خدمات و ایمنی بیماران است.', 0, 'تصمیمات با پیوست ایمنی: بکارگیری نیروی انسانی، عملیات ساختمانی، خرید تجهیزات پزشکی، مدیریت تدارک دارو و تجهیزات، برون‌سپاری خدمات، تنظیم قراردادها', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-8-1', 140501101, 7, 20, 0, 'مدیریت تخت‌های بیمارستانی بر اساس میزان اشغال تخت و چرخش تخت با رویکرد ارتقای کیفیت و ایمنی بیماران انجام می‌شود.', 0, 'بهینه‌سازی استفاده از تخت‌های بیمارستانی، کاهش زمان انتظار بستری و جلوگیری از بستری در راهروها', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-2-1-1', 140501101, 8, 21, 1, 'برنامه عملیاتی مدیریت خطر حوادث و بلایا منطبق بر ارزیابی خطر بیمارستان و پایش مستمر است.', 5, 'ارزیابی خطر با شاخص ایمنی بیمارستان (FHSI)، کمیته مدیریت خطر اصلی است.', '1', 1, 2, '2026-05-05 13:47:03', 10),
('ب-1-1-1', 140501101, 9, 22, 0, 'فرایند پذیرش بیمار در بخش های بستری برنامه ریزی شده و مطابق با آن اجرا می شود.', 0, 'دستورالعمل شامل مراحل پذیرش، مسئولیت‌ها، مدارک، ارزیابی اولیه، ثبت اطلاعات و اولویت‌بندی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-2-1-1', 140501101, 10, 23, 1, 'دستورالعمل تریاژ بیماران در بخش اورژانس تدوین و بر اساس آن اجرا می شود.', 0, 'حداکثر ۱۰ دقیقه از ورود تا تریاژ، سیستم ۵ سطحی ESI', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-3-1-1', 140501101, 11, 24, 1, 'برنامه جراحی ایمن مبتنی بر آخرین ویرایش چک لیست ایمنی جراحی سازمان جهانی بهداشت در اتاق عمل اجرا می شود.', 0, 'سه مرحله: قبل از القای بیهوشی، قبل از برش جراحی، قبل از خروج بیمار از اتاق عمل', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-5-1-1', 140501101, 12, 25, 1, 'برنامه جامع پیشگیری و کنترل عفونت مطابق با دستورالعمل‌های کشوری تدوین و اجرا می شود.', 0, 'ایزولاسیون، بهداشت دست، استریلیزاسیون، مدیریت پسماند، آموزش', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-6-1-1', 140501101, 13, 26, 1, 'مدیریت دارویی بیمارستان شامل انتخاب، تهیه، ذخیره، تجویز و مصرف داروها مطابق با ضوابط کشوری برنامه‌ریزی و اجرا می شود.', 0, 'خطاهای دارویی جزو وقایع ناخواسته مهم، سیستم گزارش‌دهی خطاهای دارویی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ج-1-1-1', 140501101, 14, 27, 0, 'بیمارستان دسترسی به خدمات و تسهیلات را به صورت عادلانه و بدون تبعیض برای تمامی بیماران فارغ از نژاد، قومیت، ملیت، مذهب، جنسیت، سن، توانمندی مالی یا نوع بیماری فراهم می کند.', 0, 'عدالت در سلامت و مراقبت بیمار-محور', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ج-2-1-1', 140501101, 15, 28, 1, 'منشور حقوق بیمار (ابلاغی وزارت بهداشت) در بیمارستان در معرض دید عموم نصب شده و کارکنان و بیماران از مفاد آن آگاهند.', 0, 'ارائه نسخه منشور به بیمار یا همراه در بدو پذیرش', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-4-1', 140501101, 16, 20, 0, 'تصمیم‌گیری‌های تیم رهبری و مدیریت مبتنی بر شواهد و داده‌های علمی و با مشارکت ذینفعان است.', 0, 'سنجش فرهنگ تصمیم‌گیری مبتنی بر شواهد (Evidence-Based Management)', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-4-2', 140501101, 17, 20, 0, 'تیم رهبری و مدیریت بیمارستان از تکنولوژی‌های نوین اطلاعاتی و ارتباطی در مدیریت و تصمیم‌گیری‌های خود استفاده می‌کند.', 0, 'مدیریت مبتنی بر داده', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-4-3', 140501101, 18, 20, 0, 'تیم رهبری و مدیریت به صورت مستمر رضایت و نیازهای ذینفعان کلیدی را ارزیابی می‌کند.', 0, 'ذینفعان کلیدی شامل بیماران، کارکنان، جامعه و سازمان‌های بالادستی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-4-4', 140501101, 19, 20, 0, 'مدیران و مسئوالن بیمارستان در انجام وظایف محوله متعهد و پاسخگو هستند.', 0, 'تعهد و پاسخگویی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-4-6', 140501101, 20, 20, 0, 'مستندسازی تصمیم‌های مهم مدیریتی و تحلیل داده ها توسط تیم رهبری و مدیریت بیمارستان انجام می شود.', 0, 'مستندسازی تصمیم‌های مهم', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-4-7', 140501101, 21, 20, 0, 'از نظرات و پیشنهادات ذی‌نفعان در فرایندهای تصمیم‌گیری و بهبود استفاده می‌شود.', 0, 'استفاده از خرد جمعی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-4-8', 140501101, 22, 20, 0, 'اقدامات و تصمیمات تیم رهبری و مدیریت نشانگر اهتمام و نظارت بر حسن اجرای قانون انطباق امور اداری و فنی با موازین شرع مقدس در بیمارستان است.', 0, 'سنجه اضافه شده به دوره پنجم', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-5-1', 140501101, 23, 20, 0, 'کمیته‌های بیمارستانی بر اساس آیین نامه مدون تشکیل و به صورت منظم جلسات برگزار می‌نمایند.', 0, 'حداقل کمیته‌ها: بهبود کیفیت، مدیریت خطر، کنترل عفونت، دارو و درمان، مرگ و میر، بافت و پیوند، انتقال خون، بهداشت محیط، مدارک پزشکی، احیا', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-5-2', 140501101, 24, 20, 0, 'کمیته‌های بیمارستانی بر اساس ساختار و عملکردی سازمان‌یافته در بیمارستان فعال هستند و به ارتقای کیفیت و حل مشکلات کمک می‌کنند.', 0, 'توصیه می‌شود برای اعضا و دبیران کمیته‌ها، آموزش‌های لازم برگزار شود.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-5-3', 140501101, 25, 20, 0, 'اثربخشی کمیته‌های بیمارستانی اندازه‌گیری و تحلیل شده و در صورت نیاز اقدامات اصلاحی اجرا می‌شود.', 0, 'سنجش اثربخشی کمیته‌ها', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-5-4', 140501101, 26, 20, 1, 'کمیته‌های بیمارستانی در روند ارتقاء کیفیت خدمات و ایمنی بیماران نقش مؤثر ایفا می‌نمایند.', 0, 'توصیه می‌شود پیوست ایمنی هریک از مصوبات مرتبط با بیماران و خدمات تشخیصی و درمانی پیش‌بینی شده و مد نظر قرار گیرد.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-6-1', 140501101, 27, 20, 1, 'تصمیمات و اقدامات تیم رهبری و مدیریت نشان دهنده اولویت بخشی به ارتقاء کیفیت خدمات و ایمنی بیماران است.', 0, 'برنامه‌ها و تصمیمات با پیوست ایمنی: بکارگیری نیروی انسانی، عملیات ساختمانی، خرید تجهیزات پزشکی، مدیریت تدارک دارو، برون‌سپاری خدمات، قراردادها', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-6-2', 140501101, 28, 20, 1, 'فرهنگ ایمنی بیمار به صورت کمی و کیفی ارزیابی و نتایج آن برای بهبود ایمنی بیمار استفاده می‌شود.', 0, 'سنجش فرهنگ ایمنی بیمار (Safety Culture Assessment)', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-6-3', 140501101, 29, 20, 1, 'روش و راهنمای مدونی برای شناسایی، تحلیل و اولویت‌بندی وقایع ناخواسته وجود دارد.', 0, 'روش‌های شناسایی شامل: گزارش داوطلبانه، شکایات، بازدیدها، بررسی پرونده و روش‌های بومی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-6-4', 140501101, 30, 20, 1, 'شناسایی و گزارش‌دهی کدهای وقایع ناخواسته بر اساس دستورالعمل وزارت بهداشت انجام می‌شود.', 0, 'تیم رهبری باید با اتخاذ رویکرد عاری از سرزنش نابجا، فرهنگ منصفانه را ترویج دهد. بی‌مباالتی‌ها قابل پذیرش نیست.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-6-5', 140501101, 31, 20, 1, 'اقدامات پیشگیرانه برای کاهش وقایع ناخواسته طراحی و اجرا می‌شود.', 0, 'مدیریت خطر پیشگیرانه (Proactive Risk Management)', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-6-6', 140501101, 32, 20, 1, 'اثربخشی برنامه های ارتقاء ایمنی بیمار در فواصل زمانی معین ارزیابی و در صورت لزوم اقدامات اصالحی/برنامه بهبود مؤثر اجرا می شود.', 0, 'اهداف اختصاصی اسمارت برای برنامه‌های ایمنی بیمار تعیین و اجرا شوند.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-7-3', 140501101, 33, 34, 0, 'اثربخشی آموزش‌های ارائه شده به کارکنان ارزیابی و نتایج آن در بهبود برنامه‌های آموزشی استفاده می‌شود.', 0, 'اثربخشی در سطوح واکنش، یادگیری، رفتار و نتایج', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-7-4', 140501101, 34, 34, 0, 'برنامه‌ریزی و اقدامات الزم برای ارتقای سالمت جسمی، روانی و اجتماعی کارکنان انجام می‌شود.', 0, 'شامل معاینات دوره‌ای، مشاوره روانشناسی، برنامه‌های ورزشی و تفریحی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-7-5', 140501101, 35, 34, 0, 'حوادث و بیماری‌های شغلی در بیمارستان پیشگیری و مدیریت می‌شود.', 0, 'مدیریت حوادث شغلی', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-7-6', 140501101, 36, 34, 1, 'در رعایت اصول اخالق حرفه‌ای و حقوق بیماران، کارکنان مورد حمایت تیم رهبری و مدیریت قرار می‌گیرند.', 0, 'حمایت از کارکنان', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-1-8-1', 140501101, 37, 20, 0, 'مدیریت تخت‌های بیمارستانی بر اساس میزان اشغال تخت و چرخش تخت با رویکرد ارتقای کیفیت و ایمنی بیماران انجام می‌شود.', 0, 'بهینه‌سازی استفاده از تخت، کاهش زمان انتظار بستری و جلوگیری از بستری در راهروها', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-8-2', 140501101, 38, 20, 0, 'فرآیند ترخیص بیمار از بخش‌های بستری برنامه‌ریزی و اجرا می‌شود.', 0, 'ترخیص ایمن (Safe Discharge)', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-9-1', 140501101, 39, 20, 0, 'کلیه خدمات مورد نیاز بیمارستانی با برنامه‌ریزی و به طور کارآمد تامین و ارائه می‌شود.', 0, 'مدیریت منابع و خدمات پشتیبانی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-9-2', 140501101, 40, 20, 0, 'فرایند خرید کاالها، ملزومات و تجهیزات به صورت شفاف و بر اساس قوانین و مقررات انجام می‌شود.', 0, 'خرید شفاف و قانونی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-10-1', 140501101, 41, 20, 0, 'انتخاب بیمارکناران با لحاظ معیارهای کیفی به صورت مدون برنامه‌ریزی و انجام می‌شود.', 0, 'بیمارکناران', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-10-2', 140501101, 42, 20, 0, 'برای تحقق نتایج مطلوب، نظارت مستمر بر عملکرد بیمارکناران برنامه‌ریزی و انجام می‌شود.', 0, 'نظارت بر برون‌سپاری', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-10-3', 140501101, 43, 20, 0, 'انتخاب و نظارت بر ارائه خدمات توسط برون سپاران در حیطه خدمات بالینی منطبق بر اهداف کیفی تعیین شده انجام می شود.', 0, 'برون‌سپاری بالینی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-10-4', 140501101, 44, 20, 0, 'خط مشی مدونی برای برون‌سپاری خدمات بر اساس قوانین و مقررات باالدستی و صرفه و صالح بیمارستان وجود دارد.', 0, 'خط مشی برون‌سپاری', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-11-1', 140501101, 45, 20, 0, 'بیمارستان در زمینه برنامه های ملی سلامت جامعه محور مشارکت مؤثر دارد.', 0, 'تایید توسط مراجع ذیربط وزارت بهداشت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-11-2', 140501101, 46, 20, 0, 'بیمارستان در پیاده سازی برنامه ملی ترویج زایمان طبیعی پیشگام بوده و مشارکت فعال و مؤثر دارد.', 0, 'پیشگامی در برنامه ترویج زایمان طبیعی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-11-3', 140501101, 47, 20, 0, 'بیمارستان در اجرای برنامه ملی تغذیه با شیر مادر پیشگام بوده و مشارکت فعال و مؤثر دارد.', 0, 'پیشگامی در برنامه تغذیه با شیر مادر', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-11-4', 140501101, 48, 20, 0, 'بیمارستان نسبت به استقرار برنامه ملی سلامت محیط و کار در بیمارستان اهتمام می ورزد.', 0, 'برنامه ملی سلامت محیط و کار', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-1-11-5', 140501101, 49, 20, 0, 'بیمارستان در اجرای برنامه ملی ارتقای ایمنی و بهداشت حرفه ای پرسنل مشارکت فعال دارد.', 0, 'برنامه ملی ارتقای ایمنی و بهداشت حرفه ای', '2', 1, 2, '2026-05-05 13:47:03', 0),
('ب-1-1-1', 140501101, 50, 22, 0, 'فرایند پذیرش بیمار در بخش های بستری برنامه ریزی شده و مطابق با آن اجرا می شود.', 0, 'شامل مراحل پذیرش، مسئولیت‌ها، مدارک، ارزیابی اولیه، ثبت اطلاعات و اولویت‌بندی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-2-1', 140501101, 51, 22, 0, 'ارزیابی اولیه بیماران در بخش های بستری منطبق بر دستورالعمل تدوین شده و توسط پزشک معالج انجام می شود.', 0, 'ارزیابی اولیه پزشکی باید شامل تاریخچه، معاینه فیزیکی کامل، تشخیص افتراقی و پلن درمانی باشد.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-2-1-1', 140501101, 52, 23, 1, 'دستورالعمل تریاژ بیماران در بخش اورژانس تدوین و بر اساس آن اجرا می شود.', 0, 'حداکثر ۱۰ دقیقه از ورود تا تریاژ، سیستم ۵ سطحی ESI', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-2-1', 140501101, 53, 23, 1, 'خدمات اورژانس به صورت شبانه روزی و بدون وقفه ارائه می شود و پزشک مقیم یا آنکال در دسترس است.', 0, 'بخش اورژانس باید از نظر تجهیزات و نیروی انسانی برای مدیریت بیماران بدحال و مصدومین انبوه آمادگی داشته باشد.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-2-2', 140501101, 54, 23, 1, 'بخش اورژانس دارای فضای فیزیکی مناسب، استاندارد و ایمن است.', 0, 'طراحی فضای فیزیکی اورژانس باید به گونه‌ای باشد که جریان کار بهینه و ایمنی بیماران تضمین شود.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-3-1', 140501101, 55, 23, 1, 'تجهیزات و داروهای ضروری برای احیاء قلبی-ریوی در تمام بخش های اورژانس و بستری آماده به کار است.', 0, 'ترالی احیاء باید شامل داروها، تجهیزات راه هوایی و مدیریت ریتم قلب باشد و به صورت روزانه و شیفتی کنترل شود.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-4-1', 140501101, 56, 23, 1, 'مراقبت های ویژه (ICU) مطابق با استانداردهای ملی و با تامین نیروی انسانی و تجهیزات الزم ارائه می شود.', 0, 'مراقبت های ویژه (ICU) باید دارای فضای ایزوله و سیستم تهویه مناسب باشد.', '2', 1, 2, '2026-05-05 13:47:03', 0),
('ب-3-1-1', 140501101, 57, 24, 1, 'برنامه جراحی ایمن مبتنی بر آخرین ویرایش چک لیست ایمنی جراحی سازمان جهانی بهداشت در اتاق عمل اجرا می شود.', 0, 'سه مرحله: قبل از القای بیهوشی، قبل از برش جراحی، قبل از خروج بیمار از اتاق عمل', '1', 1, 2, '2026-05-05 13:47:03', 2),
('ب-3-1-2', 140501101, 58, 24, 1, 'علامت‌گذاری محل جراحی توسط جراح و با مشارکت بیمار قبل از عمل انجام می‌شود.', 0, 'علامت‌گذاری باید در تمام اعمال جراحی که دارای قرینگی هستند انجام شود.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-3-1-3', 140501101, 59, 24, 1, 'برنامه پیشگیری از ترومبوآمبولی وریدی (VTE) در بیماران جراحی و بستری اجرا می‌شود.', 0, 'پیشگیری از ترومبوآمبولی وریدی (VTE)', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-3-2-1', 140501101, 60, 24, 1, 'خدمات بیهوشی مطابق با استانداردهای ملی و بین المللی ارائه می‌شود.', 0, 'برگه بیهوشی باید شامل تمام مراحل القا، نگهداری و خروج از بیهوشی باشد.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-4-1-1', 140501101, 61, 29, 0, 'برنامه مراقبت‌های مادر و نوزاد منطبق بر دستورالعمل‌های کشوری تدوین و اجرا می شود.', 0, 'برنامه ترویج زایمان طبیعی و تغذیه با شیر مادر از اولویت‌های این محور است.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-4-2-1', 140501101, 62, 29, 1, 'خدمات زایمان طبیعی و سزارین مطابق با دستورالعمل‌های کشوری و با رعایت ایمنی مادر و نوزاد ارائه می‌شود.', 0, 'ترویج زایمان طبیعی و خوشایندسازی زایمان', '1', 1, 2, '2026-05-05 13:47:03', 0),
('داخلی', 14041210, 63, 18, 0, 'بررسی رضایتمندی بیماران و همراهان', 0, 'مصاحبه و مشاهده ', '1', 33, 1.5, '2026-03-01 15:29:29', 1.5),
('', 14050126, 64, 18, 1, 'کنترل نظافت و تمیزی و بهداشت', 0, 'کنترل برنامه واشینگ - کنترل اجرای برنامه - بررسی قسمتهای مختلف  بخش', '1', 1, 1, '2026-04-15 13:42:23', 2),
('الف-1-1-1', 14050209, 65, 20, 1, 'سیاست‌های اصلی بر اساس ماموریت‌های بیمارستان و همسو با سیاست‌های بالادستی تدوین شده است.', 0, 'تدوین و مکتوب نمودن سیاست‌ها توسط مسئولان ارشد1', '2', 1, 2, '2026-04-29 15:57:56', 2),
('ب-5-3-1', 140501101, 66, 25, 1, 'فرایند استریلیزاسیون وسایل و تجهیزات پزشکی مطابق با استانداردهای ملی انجام می‌شود.', 0, 'استریلیزاسیون', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-5-4-1', 140501101, 67, 25, 1, 'مدیریت پسماندهای بیمارستانی مطابق با ضوابط کشوری انجام می‌شود.', 0, 'پسماندهای عفونی، تیز و برنده، شیمیایی و دارویی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-6-1-1', 140501101, 68, 26, 1, 'مدیریت دارویی بیمارستان شامل انتخاب، تهیه، ذخیره، تجویز و مصرف داروها مطابق با ضوابط کشوری برنامه‌ریزی و اجرا می شود.', 0, 'خطاهای دارویی جزو وقایع ناخواسته مهم، سیستم گزارش‌دهی خطاهای دارویی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-6-2-1', 140501101, 69, 26, 1, 'نگهداری و ذخیره‌سازی داروها در بیمارستان مطابق با ضوابط کشوری انجام می‌شود.', 0, 'نگهداری داروها', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-6-3-1', 140501101, 70, 26, 1, 'تجویز، نسخه پیچی و توزیع داروها در بیمارستان به صورت ایمن و با حداقل خطا انجام می شود.', 0, 'توزیع ایمن دارو', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-7-1-1', 140501101, 71, 30, 1, 'خدمات تصویربرداری پزشکی مطابق با استانداردهای ملی و با رعایت ایمنی پرتویی ارائه می‌شود.', 0, 'ایمنی پرتویی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-8-1-1', 140501101, 72, 31, 0, 'خدمات آزمایشگاه بالینی مطابق با استانداردهای ملی و بین‌المللی ارائه می‌شود.', 0, 'آزمایشگاه', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-9-1-1', 140501101, 73, 32, 1, 'خدمات طب انتقال خون مطابق با ضوابط کشوری و با رعایت ایمنی بیمار ارائه می‌شود.', 0, 'ایمنی انتقال خون', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-10-1-1', 140501101, 74, 33, 0, 'خدمات سرپایی به صورت برنامه‌ریزی شده، با کیفیت و ایمن ارائه می‌شود.', 0, 'خدمات سرپایی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ج-1-1-1', 140501101, 75, 27, 0, 'بیمارستان دسترسی به خدمات و تسهیلات را به صورت عادلانه و بدون تبعیض برای تمامی بیماران فارغ از نژاد، قومیت، ملیت، مذهب، جنسیت، سن، توانمندی مالی یا نوع بیماری فراهم می کند.', 0, 'عدالت در سلامت و مراقبت بیمار-محور', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ج-1-2-1', 140501101, 76, 27, 1, 'بیمارستان محیطی امن و ایمن برای بیماران، کارکنان و مراجعین فراهم می کند.', 0, 'شامل ایمنی در برابر آتش، مدیریت مواد خطرناک، ایمنی برق و گاز، و آمادگی برای تخلیه اضطراری است.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ج-2-1-1', 140501101, 77, 28, 1, 'منشور حقوق بیمار (ابلاغی وزارت بهداشت) در بیمارستان در معرض دید عموم نصب شده و کارکنان و بیماران از مفاد آن آگاهند.', 0, 'ارائه نسخه منشور به بیمار یا همراه در بدو پذیرش', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ج-2-2-1', 140501101, 78, 28, 0, 'فرایند اخذ رضایت آگاهانه از بیمار یا قیم قانونی وی قبل از انجام اقدامات تشخیصی و درمانی برنامه‌ریزی و اجرا می‌شود.', 0, 'رضایت آگاهانه باید شامل توضیح تشخیص، ماهیت اقدام، مزایا، خطرات و عوارض احتمالی، و جایگزین‌های درمانی باشد.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ج-2-3-1', 140501101, 79, 28, 0, 'بیمارستان به حریم خصوصی و محرمانگی اطلاعات بیماران احترام گذاشته و ساز و کارهای الزم را فراهم می کند.', 0, 'حریم خصوصی و محرمانگی اطلاعات', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-2-1-1', 140501101, 80, 21, 1, 'برنامه عملیاتی مدیریت خطر حوادث و بلایا منطبق بر ارزیابی خطر بیمارستان و پایش مستمر است.', 0, 'ارزیابی خطر با FHSI، کمیته مدیریت خطر اصلی است', '1', 1, 2, '2026-05-05 13:47:03', 2),
('الف-2-1-2', 140501101, 81, 21, 1, 'بیمارستان دارای برنامه مدون برای تداوم فعالیت (Business Continuity) در شرایط بحران و حوادث است.', 0, 'تداوم فعالیت در بحران', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-1', 140501101, 82, 21, 1, 'برنامه ایمنی بیمارستان در برابر آتش سوزی مطابق با ضوابط ملی تدوین و اجرا می شود.', 0, 'ایمنی در برابر آتش', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-2', 140501101, 83, 21, 1, 'ایمن‌سازی سطوح، دیوارها و محیط فیزیکی بیمارستان برنامه‌ریزی و اجرا می‌شود.', 0, 'شامل نصب دستگیره، نرده، کف‌پوش ضد لغزش، ثابت‌سازی لوازم و حفاظت از لبه‌های تیز', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-3', 140501101, 84, 21, 1, 'نصب و نگهداری سیستم‌های اطفاء حریق و اعلام حریق مطابق استانداردهای ملی انجام می‌شود.', 0, 'خاموش‌کننده‌ها بر اساس نوع حریق (A,B,C,D,E) انتخاب شوند.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-4', 140501101, 85, 21, 1, 'برنامه بازدیدهای دوره‌ای ایمنی تجهیزات و تأسیسات بیمارستان تدوین و اجرا می‌شود.', 0, 'بازدیدهای ایمنی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-5', 140501101, 86, 21, 0, 'تجهیزات و تأسیسات بیمارستان دارای برنامه نگهداری پیشگیرانه هستند.', 0, 'نگهداری پیشگیرانه تأسیسات', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-2-2-6', 140501101, 87, 21, 1, 'ارزیابی خطر حوادث و بالیا در سطح بیمارستان انجام شده و برنامه‌های کاهش خطر مبتنی بر آن تدوین می‌شود.', 0, 'ارزیابی خطر با شاخص ایمنی بیمارستان (FHSI)', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-7', 140501101, 88, 21, 1, 'بیمارستان برنامه مدون برای تخلیه اضطراری در زمان حوادث دارد و کارکنان از آن آگاهند.', 0, 'تخلیه می‌تواند افقی، عمودی یا کامل باشد.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-2-8', 140501101, 89, 21, 1, 'بیمارستان از نظر سازه‌ای و غیرسازه‌ای در برابر حوادث و بالیا مقاوم‌سازی شده است.', 0, 'مقاوم‌سازی', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-3-1', 140501101, 90, 21, 0, 'تأسیسات بیمارستان شامل سیستم‌های برق، آب، گاز و تهویه مطابق با استانداردها نگهداری می‌شوند.', 0, 'تأسیسات حیاتی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-2-4-1', 140501101, 91, 21, 1, 'بیمارستان دارای برنامه مدون مدیریت بحران و سامانه فرماندهی حادثه (HICS) است.', 0, 'سامانه فرماندهی حادثه بیمارستان (HICS)', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-4-2', 140501101, 92, 21, 1, 'برنامه عملیاتی تداوم مراقبت و خدمات بیمارستان در شرایط بحران تدوین و اجرا می‌شود.', 0, 'تداوم خدمات در بحران', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-4-3', 140501101, 93, 21, 1, 'برنامه‌ریزی برای مدیریت مصدومین انبوه (Mass Casualty) در بیمارستان انجام شده است.', 0, 'مدیریت مصدومین انبوه', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-4-4', 140501101, 94, 21, 0, 'آموزش‌های عمومی و تخصصی مدیریت خطر حوادث و بالیا برای کارکنان برنامه‌ریزی و اجرا می‌شود.', 0, 'آموزش حوادث و بالیا', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-2-4-5', 140501101, 95, 21, 0, 'تمرین‌های شبیه‌سازی شده حوادث و بالیا با تدوین سناریو، برنامه‌ریزی و انجام می‌شود.', 0, 'تمرین‌ها شامل تریاژ، فعال‌سازی سامانه فرماندهی، استفاده از وسایل حفاظت فردی، آلودگی‌زدایی و تخلیه اضطراری است.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-2-4-6', 140501101, 96, 21, 1, 'دستورالعمل تخلیه بیمارستان در زمان حادثه تدوین و ابلاغ شده و کارکنان از آن آگاهند.', 0, 'تخلیه می‌تواند افقی، عمودی و یا کامل صورت گیرد.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-5-1', 140501101, 97, 21, 1, 'بیمارستان دارای برنامه مدون و عملیاتی برای تأمین منابع و تجهیزات حیاتی در شرایط بحران است.', 0, 'منابع حیاتی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-5-2', 140501101, 98, 21, 1, 'برنامه مدون برای کاهش آسیب‌پذیری و ارتقای ایمنی بیماران، کارکنان و مراجعین در برابر حوادث و بالیا وجود دارد.', 0, 'کاهش آسیب‌پذیری', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-2-5-3', 140501101, 99, 21, 1, 'منابع و تجهیزات الزم برای تخلیه اضطراری بیماران و کارکنان در زمان حوادث تامین شده و در دسترس است.', 0, 'تجهیزات تخلیه', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-1-1', 140501101, 100, 34, 0, 'برنامه مدون و مکتوبی برای تأمین نیروی انسانی بر اساس نیاز سنجی و برنامه ریزی جامع وجود داشته و اجرا می شود.', 0, 'برنامه جامع تأمین نیروی انسانی باید شامل جذب، به‌کارگیری، آموزش و بهسازی، نگهداشت و ارتقای کارکنان باشد و به تأیید تیم رهبری برسد.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-2-1', 140501101, 101, 34, 0, 'شرح وظایف کلیه پست‌های سازمانی مکتوب شده و در دسترس کارکنان است.', 0, 'شرح وظایف', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-2-2', 140501101, 102, 34, 0, 'فرایند جذب و استخدام کارکنان بر اساس ضوابط و مقررات و به صورت شفاف انجام می‌شود.', 0, 'جذب شفاف', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-2-3', 140501101, 103, 34, 0, 'برنامه جامع آموزش و توانمندسازی کارکنان بر اساس نیازسنجی آموزشی تدوین و اجرا می‌شود.', 0, 'آموزش و توانمندسازی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-2-4', 140501101, 104, 34, 0, 'ارزشیابی عملکرد کارکنان بر اساس شرح وظایف و اهداف تعیین شده به صورت عادالنه و شفاف انجام می‌شود.', 0, 'ارزشیابی عملکرد', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-2-5', 140501101, 105, 34, 0, 'سالمت جسمی و روانی کارکنان به صورت دوره ای پایش و برای حفظ و ارتقای آن برنامه ریزی می‌شود.', 0, 'پایش سلامت کارکنان', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-2-6', 140501101, 106, 34, 1, 'اقدامات الزم برای پیشگیری از حوادث شغلی و مدیریت آنها در بیمارستان انجام می‌شود.', 0, 'پیشگیری از حوادث شغلی', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-3-1', 140501101, 107, 34, 0, 'برنامه‌ریزی و اقدامات لازم برای ارتقای سلامت روانی کارکنان انجام می‌شود.', 0, 'سلامت روانی کارکنان', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-3-2', 140501101, 108, 34, 0, 'برنامه‌ریزی و اقدامات لازم برای ارتقای سلامت جسمی کارکنان انجام می‌شود.', 0, 'سلامت جسمی کارکنان', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-3-3', 140501101, 109, 34, 1, 'مدیریت خطرات شغلی (فیزیکی، شیمیایی، بیولوژیکی، ارگونومیکی و روانی) در بیمارستان اجرا می‌شود.', 0, 'خطرات شغلی: فیزیکی (صدا، نور، پرتو)، شیمیایی (مواد ضدعفونی، گازهای بیهوشی)، بیولوژیکی (خون و ترشحات)، ارگونومیکی (جابجایی بیمار)، روانی (استرس)', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-3-4', 140501101, 110, 34, 1, 'وسایل حفاظت فردی (PPE) متناسب با خطرات شغلی تامین و استفاده می‌شود.', 0, 'وسایل حفاظت فردی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-3-5', 140501101, 111, 34, 1, 'برنامه ایمنی بیولوژیکی (Biosafety) در بخش‌های آزمایشگاه و عفونی اجرا می‌شود.', 0, 'ایمنی بیولوژیکی', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-3-6', 140501101, 112, 34, 1, 'برنامه ایمنی پرتویی (Radiation Safety) در بخش‌های تصویربرداری و پزشکی هسته‌ای اجرا می‌شود.', 0, 'ایمنی پرتویی', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-3-7', 140501101, 113, 34, 1, 'برنامه ایمنی شیمیایی (Chemical Safety) در بیمارستان تدوین و اجرا می‌شود.', 0, 'ایمنی شیمیایی', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-4-1', 140501101, 114, 34, 1, 'برنامه مدیریت خطاهای انسانی و ارتقای ایمنی بیمار با رویکرد سیستمیک اجرا می‌شود.', 0, 'مدیریت خطاهای انسانی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-4-2', 140501101, 115, 34, 1, 'برنامه پیشگیری و مدیریت خشونت علیه کارکنان در بیمارستان تدوین و اجرا می‌شود.', 0, 'پیشگیری از خشونت', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-4-3', 140501101, 116, 34, 1, 'تیم رهبری و مدیریت نسبت به مدیریت کارکنان درگیر در وقایع ناخواسته، بر اساس فرهنگ منصفانه ایمنی بیمار عمل می‌کند.', 0, 'فرهنگ منصفانه', '2', 1, 2, '2026-05-05 13:47:03', 0),
('الف-3-4-4', 140501101, 117, 34, 0, 'برنامه‌ریزی و اقدامات لازم برای پیشگیری از فرسودگی شغلی کارکنان انجام می‌شود.', 0, 'پیشگیری از فرسودگی شغلی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-3-4-5', 140501101, 118, 34, 0, 'برنامه مدون برای مدیریت خستگی و بار کاری پرستاران و کادر درمان اجرا می‌شود.', 0, 'مدیریت خستگی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-1-1', 140501101, 119, 35, 0, 'مدیر پرستاری بیمارستان واجد شرایط علمی و حرفه‌ای الزم است.', 0, 'مدیر پرستاری', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-1-2', 140501101, 120, 35, 0, 'ساختار مدیریت پرستاری در بیمارستان مشخص و مدون است.', 0, 'ساختار مدیریت پرستاری', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-1-3', 140501101, 121, 35, 0, 'تعداد و ترکیب نیروی پرستاری در هر بخش بر اساس استانداردهای کشوری تعیین می‌شود.', 0, 'نسبت پرستار به تخت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-1-4', 140501101, 122, 35, 0, 'برنامه نوبت‌بندی پرستاران بر اساس استاندارد و با رعایت عدالت تدوین و اجرا می‌شود.', 0, 'نوبت‌بندی پرستاران', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-1-5', 140501101, 123, 35, 0, 'برنامه جامع آموزش و توانمندسازی پرستاران بر اساس نیازسنجی تدوین و اجرا می‌شود.', 0, 'آموزش پرستاران', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-2-1', 140501101, 124, 35, 0, 'مدیریت پرستاری بر نحوه ارائه مراقبت‌های پرستاری نظارت مستمر دارد.', 0, 'نظارت بالینی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-2-2', 140501101, 125, 35, 0, 'فرایند پذیرش و ارزیابی اولیه پرستاری از بیماران بستری مطابق دستورالعمل انجام می‌شود.', 0, 'ارزیابی اولیه پرستاری', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-2-3', 140501101, 126, 35, 0, 'برنامه مراقبت پرستاری (Nursing Care Plan) برای هر بیمار تدوین و اجرا می‌شود.', 0, 'برنامه مراقبت پرستاری', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-2-4', 140501101, 127, 35, 1, 'فرایند تحویل و تحول بیمار بین شیفت‌های پرستاری به صورت ساختارمند و ایمن انجام می‌شود.', 0, 'تحویل ایمن بیمار', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-4-3-1', 140501101, 128, 35, 0, 'مدیریت پرستاری در کمیته‌های بیمارستانی مشارکت فعال دارد.', 0, 'مشارکت در کمیته‌ها', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-4-3-2', 140501101, 129, 35, 1, 'مدیریت پرستاری در فرایند بهبود کیفیت و ایمنی بیمار مشارکت فعال دارد.', 0, 'بهبود کیفیت و ایمنی', '1', 1, 2, '2026-05-05 13:47:03', 0),
('الف-4-3-3', 140501101, 130, 35, 0, 'رضایت شغلی پرستاران به صورت دوره‌ای ارزیابی و نتایج آن برای بهبود استفاده می‌شود.', 0, 'رضایت شغلی پرستاران', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-2', 140501101, 131, 36, 0, 'اطلاعات بیماران به صورت الکترونیکی ثبت، ذخیره و بازیابی می‌شود.', 0, 'پرونده الکترونیک سلامت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-3', 140501101, 132, 36, 0, 'امنیت اطلاعات بیماران در سامانه‌های اطلاعاتی تضمین می‌شود.', 0, 'امنیت اطلاعات', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-4', 140501101, 133, 36, 0, 'بیمارستان از سیستم کدینگ استاندارد برای ثبت تشخیص‌ها و اقدامات استفاده می‌کند.', 0, 'کدینگ استاندارد', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-5', 140501101, 134, 36, 0, 'گزارش‌های مدیریتی و آماری به صورت دوره‌ای و بر اساس داده‌های HIS تهیه و تحلیل می‌شود.', 0, 'گزارش‌های مدیریتی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-6', 140501101, 135, 36, 0, 'بیمارستان از راهنماهای طبابت بالینی الکترونیکی (e-CPG) در فرایندهای تشخیصی و درمانی استفاده می‌کند.', 0, 'راهنماهای طبابت بالینی الکترونیکی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-7', 140501101, 136, 36, 0, 'بیمارستان از سیستم‌های پشتیبانی تصمیم‌گیری بالینی (CDSS) در HIS استفاده می‌کند.', 0, 'سیستم پشتیبانی تصمیم‌گیری بالینی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-1-8', 140501101, 137, 36, 0, 'بیمارستان از فناوری تله مدیسین (پزشکی از راه دور) برای ارائه خدمات مشاوره‌ای و تخصصی استفاده می‌کند.', 0, 'تله مدیسین', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-1', 140501101, 138, 36, 0, 'واحد مدیریت اطلاعات سلامت دارای تشکیلات سازمانی، نیروی انسانی واجد شرایط و فضای فیزیکی مناسب است.', 0, 'واحد مدیریت اطلاعات سلامت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-2', 140501101, 139, 36, 0, 'پرونده‌های پزشکی به صورت کامل، دقیق و به موقع تکمیل می‌شوند.', 0, 'تکمیل پرونده پزشکی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-3', 140501101, 140, 36, 0, 'پرونده‌های پزشکی پس از ترخیص بیمار، از نظر کمی و کیفی ارزیابی می‌شوند.', 0, 'ارزیابی پرونده‌ها', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-4', 140501101, 141, 36, 0, 'نگهداری و بایگانی پرونده‌های پزشکی مطابق با ضوابط وزارت بهداشت انجام می‌شود.', 0, 'بایگانی پرونده‌ها', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-5', 140501101, 142, 36, 0, 'واحد مدیریت اطلاعات سلامت، آمار بیمارستانی را به صورت دقیق و به موقع تهیه و گزارش می‌کند.', 0, 'آمار بیمارستانی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-6', 140501101, 143, 36, 0, 'اطلاعات مربوط به فوت بیماران به صورت دقیق ثبت و گواهی فوت صادر می‌شود.', 0, 'ثبت فوت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-7', 140501101, 144, 36, 0, 'بیمارستان از سیستم ردیابی و مکانیابی پرونده‌های پزشکی استفاده می‌کند.', 0, 'ردیابی پرونده', '2', 1, 1, '2026-05-05 13:47:03', 0),
('الف-5-2-8', 140501101, 145, 36, 0, 'واحد مدیریت اطلاعات سلامت در کمیته‌های بیمارستانی مرتبط مشارکت فعال دارد.', 0, 'مشارکت واحد مدیریت اطلاعات سلامت', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-1-1', 140501101, 146, 22, 0, 'فرایند پذیرش بیمار در بخش های بستری برنامه ریزی شده و مطابق با آن اجرا می شود.', 0, 'شامل مراحل پذیرش، مسئولیت‌ها، مدارک، ارزیابی اولیه، ثبت اطلاعات و اولویت‌بندی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-2-1', 140501101, 147, 22, 0, 'ارزیابی اولیه بیماران در بخش های بستری منطبق بر دستورالعمل تدوین شده و توسط پزشک معالج انجام می شود.', 0, 'ارزیابی اولیه پزشکی باید شامل تاریخچه، معاینه فیزیکی کامل، تشخیص افتراقی و پلن درمانی باشد.', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-3-1', 140501101, 148, 22, 0, 'برنامه درمانی و مراقبتی بیمار بر اساس ارزیابی‌های اولیه و تشخیص‌های افتراقی تدوین و در پرونده ثبت می‌شود.', 0, 'برنامه درمانی (Care Plan)', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-4-1', 140501101, 149, 22, 0, 'سیر بیماری و مراقبت‌های پرستاری به طور مستمر و دقیق در پرونده ثبت می شود.', 0, 'ثبت سیر بیماری', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-5-1', 140501101, 150, 22, 0, 'دستورات پزشک به صورت خوانا، کامل و با قید تاریخ و زمان ثبت و امضاء می شود.', 0, 'دستورات پزشک', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-6-1', 140501101, 151, 22, 0, 'فرایند ترخیص بیمار از بخش های بستری برنامه ریزی شده و شامل ارائه خالصه ترخیص به بیمار است.', 0, 'ترخیص ایمن (Safe Discharge)', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-7-1', 140501101, 152, 22, 0, 'بیماران و خانواده آنان در خصوص بیماری، برنامه درمانی، مراقبت‌های پس از ترخیص و سبک زندگی سالم آموزش می‌بینند.', 0, 'آموزش بیمار و خانواده', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-8-1', 140501101, 153, 22, 0, 'خدمات تغذیه بالینی بر اساس ارزیابی وضعیت تغذیه‌ای بیمار و توسط کارشناس تغذیه ارائه می شود.', 0, 'خدمات تغذیه بالینی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-9-1', 140501101, 154, 22, 0, 'خدمات توانبخشی بر اساس نیاز بیماران و توسط کارشناسان مربوطه ارائه می‌شود.', 0, 'خدمات توانبخشی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-10-1', 140501101, 155, 22, 0, 'خدمات مددکاری اجتماعی برای بیماران نیازمند ارائه می‌شود.', 0, 'مددکاری اجتماعی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-11-1', 140501101, 156, 22, 0, 'خدمات روانشناسی بالینی برای بیماران نیازمند ارائه می‌شود.', 0, 'روانشناسی بالینی', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-1-12-1', 140501101, 157, 22, 1, 'بیماران پرخطر از نظر سقوط، زخم بستر و سایر خطرات شناسایی و تحت مراقبت ویژه قرار می‌گیرند.', 0, 'پیشگیری از خطرات', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-1-2', 140501101, 158, 23, 1, 'فرایند تریاژ بیماران در بخش اورژانس بر اساس سیستم استاندارد ESI انجام می‌شود.', 0, 'سیستم ESI', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-2-1', 140501101, 159, 23, 1, 'خدمات اورژانس به صورت شبانه روزی و بدون وقفه ارائه می شود و پزشک مقیم یا آنکال در دسترس است.', 0, 'خدمات اورژانس ۲۴ ساعته', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-2-2', 140501101, 160, 23, 1, 'بخش اورژانس دارای فضای فیزیکی مناسب، استاندارد و ایمن است.', 0, 'فضای فیزیکی اورژانس', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-2-3', 140501101, 161, 23, 0, 'زمان انتظار بیماران در بخش اورژانس برای دریافت خدمات کلیدی پایش و مدیریت می‌شود.', 0, 'زمان انتظار در اورژانس', '1', 1, 1, '2026-05-05 13:47:03', 0),
('ب-2-3-1', 140501101, 162, 23, 1, 'تجهیزات و داروهای ضروری برای احیاء قلبی-ریوی در تمام بخش های اورژانس و بستری آماده به کار است.', 0, 'ترالی احیاء باید شامل داروها، تجهیزات راه هوایی و مدیریت ریتم قلب باشد.', '1', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-4-1', 140501101, 163, 23, 1, 'مراقبت های ویژه (ICU) مطابق با استانداردهای ملی و با تامین نیروی انسانی و تجهیزات الزم ارائه می شود.', 0, 'مراقبت های ویژه (ICU) باید دارای فضای ایزوله و سیستم تهویه مناسب باشد.', '2', 1, 2, '2026-05-05 13:47:03', 0),
('ب-2-4-2', 140501101, 164, 23, 0, 'بیماران بستری در ICU مورد ویزیت روزانه تیم چند تخصصی (Multidisciplinary Round) قرار می‌گیرند.', 0, 'ویزیت چند تخصصی', '2', 1, 1, '2026-05-05 13:47:03', 0),
('20 الف', 14050221, 165, 37, 1, 'تست گردش', 0, 'فقط موارد تستی', '1', 1, 2, '2026-05-11 12:41:31', 2);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_arzibi_onvan`
--

DROP TABLE IF EXISTS `tbl_arzibi_onvan`;
CREATE TABLE IF NOT EXISTS `tbl_arzibi_onvan` (
  `dat_sabt` int DEFAULT NULL,
  `ID_onvan_arziabi` int NOT NULL AUTO_INCREMENT,
  `nom_onvan` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_onvan_arziabi`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_arzibi_onvan`
--

INSERT INTO `tbl_arzibi_onvan` (`dat_sabt`, `ID_onvan_arziabi`, `nom_onvan`, `UserID`, `zaman_sabt`) VALUES
(14041210, 18, 'راند عمومی بخش ها', 33, '2026-03-01 15:28:22'),
(14050209, 19, 'مدیریت و رهبری', 1, '2026-04-29 15:52:30'),
(14050209, 20, 'محورالف-1: رهبری و مدیریت کیفیت', 1, '2026-04-29 15:54:27'),
(14050101, 21, 'محور الف-2: مدیریت خطر حوادث و بلایا', 1, '2026-05-05 13:29:12'),
(14050101, 22, 'محور ب-1: مراقبت های عمومی بالینی', 1, '2026-05-05 13:29:12'),
(14050101, 23, 'محور ب-2: مراقبت های حاد و اورژانس', 1, '2026-05-05 13:29:12'),
(14050101, 24, 'محور ب-3: مراقبت های جراحی و بیهوشی', 1, '2026-05-05 13:29:12'),
(14050101, 25, 'محور ب-5: پیشگیری و کنترل عفونت', 1, '2026-05-05 13:29:12'),
(14050101, 26, 'محور ب-6: مدیریت دارویی', 1, '2026-05-05 13:29:12'),
(14050101, 27, 'محور ج-1: تامین تسهیلات برای گیرنده خدمت', 1, '2026-05-05 13:29:12'),
(14050101, 28, 'محور ج-2: احترام به حقوق گیرنده خدمت', 1, '2026-05-05 13:29:12'),
(14050101, 29, 'محور ب-4: مراقبت های مادر و نوزاد', 1, '2026-05-05 13:29:12'),
(14050101, 30, 'محور ب-7: خدمات تصویر برداری', 1, '2026-05-05 13:29:12'),
(14050101, 31, 'محور ب-8: خدمات آزمایشگاه', 1, '2026-05-05 13:29:12'),
(14050101, 32, 'محور ب-9: طب انتقال خون', 1, '2026-05-05 13:29:12'),
(14050101, 33, 'محور ب-10: خدمات سرپایی', 1, '2026-05-05 13:29:12'),
(14050101, 34, 'محور الف-3: مدیریت منابع انسانی و سلامت حرفه ای', 1, '2026-05-05 13:29:12'),
(14050101, 35, 'محور الف-4: مدیریت خدمات پرستاری', 1, '2026-05-05 13:29:12'),
(14050101, 36, 'محور الف-5: فناوری و مدیریت اطلاعات سلامت', 1, '2026-05-05 13:29:12'),
(14050221, 37, 'وضعیت تستی', 1, '2026-05-11 12:40:22');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_bakhsh`
--

DROP TABLE IF EXISTS `tbl_bakhsh`;
CREATE TABLE IF NOT EXISTS `tbl_bakhsh` (
  `dat_sabt` int DEFAULT NULL,
  `ID_nam_bakhsh` int NOT NULL AUTO_INCREMENT,
  `nam_bakhsh` varchar(55) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `amar` tinyint NOT NULL COMMENT 'نیازبه امار',
  `grop` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  PRIMARY KEY (`ID_nam_bakhsh`),
  UNIQUE KEY `tbl-bakhshnam-bakhsh` (`nam_bakhsh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_bakhsh`
--

INSERT INTO `tbl_bakhsh` (`dat_sabt`, `ID_nam_bakhsh`, `nam_bakhsh`, `UserID`, `zaman_sabt`, `amar`, `grop`) VALUES
(14041209, 30, 'مردان 1', 33, '2026-02-28 16:56:00', 1, 'درمانی'),
(14041209, 31, 'مردان 2', 33, '2026-02-28 16:56:13', 1, 'درمانی'),
(14041209, 32, 'زنان', 33, '2026-02-28 16:56:23', 1, 'درمانی'),
(14041209, 33, 'ژنیکولوژی', 33, '2026-02-28 16:56:38', 1, 'درمانی'),
(14041209, 34, 'اطفال', 33, '2026-02-28 16:57:10', 1, 'درمانی'),
(14041209, 35, 'پذیرش', 33, '2026-02-28 16:57:21', 0, ''),
(14041209, 36, 'داروخانه', 33, '2026-02-28 16:57:28', 0, ''),
(14041209, 37, 'دژبانی', 33, '2026-02-28 16:57:50', 0, 'خدماتی پشتیبانی'),
(14041209, 38, 'سی اس آر', 33, '2026-02-28 16:58:12', 0, ''),
(14050321, 42, 'بخش عموم', 1, '2026-06-11 14:05:10', 0, 'سایر');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_bakhsh_amar_config`
--

DROP TABLE IF EXISTS `tbl_bakhsh_amar_config`;
CREATE TABLE IF NOT EXISTS `tbl_bakhsh_amar_config` (
  `ID_config` int NOT NULL AUTO_INCREMENT,
  `bakhsh_id` int NOT NULL,
  `item_id` int NOT NULL,
  PRIMARY KEY (`ID_config`),
  KEY `bakhsh_id` (`bakhsh_id`),
  KEY `item_id` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_blood_faravardeh`
--

DROP TABLE IF EXISTS `tbl_blood_faravardeh`;
CREATE TABLE IF NOT EXISTS `tbl_blood_faravardeh` (
  `bloodT_key` int DEFAULT '0',
  `dat_sabt` int DEFAULT NULL,
  `groh_khoni_f` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `id_faravardeh_blood` int NOT NULL AUTO_INCREMENT,
  `nam_faravardeh` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `teda_vahed` int NOT NULL,
  `UserID` int DEFAULT '0',
  `vakonsh` tinyint(1) DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`id_faravardeh_blood`),
  KEY `bloodT_key` (`bloodT_key`),
  KEY `id_faravardeh_blood` (`id_faravardeh_blood`),
  KEY `tbl_blood_transtbl_blood_faravardeh` (`bloodT_key`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_blood_trans`
--

DROP TABLE IF EXISTS `tbl_blood_trans`;
CREATE TABLE IF NOT EXISTS `tbl_blood_trans` (
  `dat_sabt` int DEFAULT NULL,
  `groh_khoni_bimar` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `ID_blood` int NOT NULL AUTO_INCREMENT,
  `nam_bakhsh` int NOT NULL,
  `nam_bimar` varchar(55) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam_shift` int NOT NULL,
  `shomar_parvandeh` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `vakonsh_tavzih` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_blood`),
  KEY `shift_namTtbl_blood_trans` (`nam_shift`),
  KEY `tbl_bakhshtbl_blood_trans` (`nam_bakhsh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_chart_bohran`
--

DROP TABLE IF EXISTS `tbl_chart_bohran`;
CREATE TABLE IF NOT EXISTS `tbl_chart_bohran` (
  `dat_sabt` int DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `ID_chart_bohran` int NOT NULL AUTO_INCREMENT,
  `id_person` int DEFAULT '0',
  `nam_bohran` int DEFAULT '0',
  `id_nam_nagsh` int DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `Id_sath_bohran` int NOT NULL COMMENT 'گروه بندی بحران',
  PRIMARY KEY (`ID_chart_bohran`),
  KEY `id_person` (`id_person`),
  KEY `tbl_onvan_kod_omomytbl_naghsh_bohran` (`nam_bohran`),
  KEY `tbl_persontbl_naghsh_bohran` (`id_person`),
  KEY `UserID` (`UserID`),
  KEY `idnam_nagsh` (`id_nam_nagsh`),
  KEY `sathbohran` (`Id_sath_bohran`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_chart_call`
--

DROP TABLE IF EXISTS `tbl_chart_call`;
CREATE TABLE IF NOT EXISTS `tbl_chart_call` (
  `dat_sabt` int DEFAULT NULL,
  `ID_chart_call` int NOT NULL AUTO_INCREMENT,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `idcode_omomy` int NOT NULL,
  `idsath_bohran` int NOT NULL,
  PRIMARY KEY (`ID_chart_call`),
  KEY `UserID` (`UserID`),
  KEY `tblcode_omomy` (`idcode_omomy`),
  KEY `tblsath_bohran` (`idsath_bohran`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_ghaybat`
--

DROP TABLE IF EXISTS `tbl_ghaybat`;
CREATE TABLE IF NOT EXISTS `tbl_ghaybat` (
  `dat_sabt` int DEFAULT NULL,
  `ghaibat` tinyint(1) DEFAULT '0',
  `ID_ghaibat` int NOT NULL AUTO_INCREMENT,
  `nam_bakhsh` int NOT NULL,
  `nam_person` int NOT NULL,
  `nam_shift` int NOT NULL,
  `pas_saati` tinyint(1) DEFAULT '0',
  `taajil_khoroj` tinyint(1) DEFAULT '0',
  `takhir_saati` tinyint(1) DEFAULT '0',
  `tozihat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `rizshift` int DEFAULT NULL,
  PRIMARY KEY (`ID_ghaibat`),
  UNIQUE KEY `tbl-hozorID` (`ID_ghaibat`),
  KEY `shift_namTtbl_ghaybat` (`nam_shift`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_ghaybat`
--

INSERT INTO `tbl_ghaybat` (`dat_sabt`, `ghaibat`, `ID_ghaibat`, `nam_bakhsh`, `nam_person`, `nam_shift`, `pas_saati`, `taajil_khoroj`, `takhir_saati`, `tozihat`, `UserID`, `zaman_sabt`, `rizshift`) VALUES
(14050324, 1, 2, 34, 166, 140503242, 0, 0, 0, 'دیر جواب داد', 1, '2026-06-14 11:24:41', 2),
(14050324, 0, 3, 30, 367, 140503242, 1, 1, 1, '', 1, '2026-06-14 11:25:15', 2);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_gozaresh`
--

DROP TABLE IF EXISTS `tbl_gozaresh`;
CREATE TABLE IF NOT EXISTS `tbl_gozaresh` (
  `CreatedDate` datetime DEFAULT NULL,
  `dat_sabt` int DEFAULT NULL,
  `Date_ersal` datetime DEFAULT NULL,
  `eghdam_eslahi_avlieh` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `ersal_gozaresh` tinyint(1) DEFAULT '0',
  `ID_gozaresh` int NOT NULL AUTO_INCREMENT,
  `ID_shift` int DEFAULT '0',
  `mohtava_gozaresh` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `nam_modirit` int DEFAULT '0',
  `onvan_gozaresh` int DEFAULT '0',
  `statuse` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `statuse1` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `taid_aval` tinyint(1) DEFAULT '0',
  `UserID` int DEFAULT '0',
  `mostanad` varchar(250) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`ID_gozaresh`),
  KEY `ID_shift` (`ID_shift`),
  KEY `onvan_gozareshtbl_gozaresh` (`onvan_gozaresh`),
  KEY `shift_namTtbl_gozaresh` (`ID_shift`),
  KEY `tbl_nam_modiriattbl_gozaresh` (`nam_modirit`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=165 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_gozaresh`
--

INSERT INTO `tbl_gozaresh` (`CreatedDate`, `dat_sabt`, `Date_ersal`, `eghdam_eslahi_avlieh`, `ersal_gozaresh`, `ID_gozaresh`, `ID_shift`, `mohtava_gozaresh`, `nam_modirit`, `onvan_gozaresh`, `statuse`, `statuse1`, `taid_aval`, `UserID`, `mostanad`) VALUES
('2026-06-15 17:36:51', 14050325, '2026-06-15 17:36:51', 'ببژژژووپ. ', 1, 164, 140503255, 'ررابببژژ\r\nکمپپپپ', 27, 64, 'ارسال شده', NULL, 1, 1, 'uploads/gozaresh/164/17815323517248635497381883053531.jpg,uploads/gozaresh/164/17815323979706896589909509562457.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_gozaresh_modir_parastari`
--

DROP TABLE IF EXISTS `tbl_gozaresh_modir_parastari`;
CREATE TABLE IF NOT EXISTS `tbl_gozaresh_modir_parastari` (
  `dat_sabt` int DEFAULT NULL,
  `ersal_Date` datetime DEFAULT NULL,
  `ID_gozaresh` int DEFAULT '0',
  `ID_gozaresh_modir_parstati` int NOT NULL AUTO_INCREMENT,
  `taid_ersal` tinyint(1) DEFAULT '0',
  `UserID` int DEFAULT '0',
  `only_thisid` tinyint NOT NULL,
  PRIMARY KEY (`ID_gozaresh_modir_parstati`),
  KEY `ID_gozaresh` (`ID_gozaresh`),
  KEY `tbl_gozareshtbl_gozaresh_modir_parastari` (`ID_gozaresh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_hozor`
--

DROP TABLE IF EXISTS `tbl_hozor`;
CREATE TABLE IF NOT EXISTS `tbl_hozor` (
  `dat_sabt` int DEFAULT NULL,
  `ID_hazer` int NOT NULL AUTO_INCREMENT,
  `id_person` int DEFAULT '0',
  `ispresent` tinyint(1) DEFAULT '0',
  `nam_bakhsh` int NOT NULL,
  `nam_shift` int NOT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `rizshift` int NOT NULL,
  PRIMARY KEY (`ID_hazer`),
  UNIQUE KEY `tbl-hozorID` (`ID_hazer`),
  KEY `id_person` (`id_person`),
  KEY `shift_namTtbl_hozor` (`nam_shift`),
  KEY `tbl_bakhshtbl_hozor` (`nam_bakhsh`),
  KEY `tbl_persontbl_hozor` (`id_person`),
  KEY `UserID` (`UserID`),
  KEY `dat_sabt` (`dat_sabt`,`ID_hazer`,`id_person`,`ispresent`,`nam_bakhsh`,`nam_shift`,`UserID`,`zaman_sabt`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_hozor`
--

INSERT INTO `tbl_hozor` (`dat_sabt`, `ID_hazer`, `id_person`, `ispresent`, `nam_bakhsh`, `nam_shift`, `UserID`, `zaman_sabt`, `rizshift`) VALUES
(14050324, 9, 166, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 1),
(14050324, 10, 117, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 2),
(14050324, 11, 121, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 3),
(14050324, 12, 215, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 1),
(14050324, 13, 250, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 3),
(14050324, 14, 270, 0, 34, 140503242, 1, '2026-06-14 11:10:31', 2),
(14050324, 15, 263, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 3),
(14050324, 16, 109, 1, 34, 140503242, 1, '2026-06-14 11:10:31', 2),
(14050325, 17, 273, 0, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 18, 315, 1, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 19, 364, 0, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 20, 367, 1, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 21, 371, 0, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 22, 52, 1, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 23, 359, 1, 30, 140503246, 1, '2026-06-15 12:15:07', 6),
(14050325, 24, 166, 0, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 25, 117, 0, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 26, 121, 1, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 27, 215, 1, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 28, 250, 1, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 29, 270, 1, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 30, 263, 0, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 31, 109, 1, 34, 140503246, 1, '2026-06-15 12:15:31', 6),
(14050325, 32, 166, 1, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 33, 117, 0, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 34, 121, 1, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 35, 215, 1, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 36, 250, 0, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 37, 270, 0, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 38, 263, 1, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 39, 109, 0, 34, 140503251, 1, '2026-06-15 13:56:19', 1),
(14050325, 40, 273, 1, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 41, 315, 1, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 42, 364, 1, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 43, 367, 1, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 44, 371, 1, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 45, 52, 0, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 46, 359, 1, 30, 140503251, 1, '2026-06-15 13:56:39', 1),
(14050325, 47, 42, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 48, 238, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 49, 93, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 50, 172, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 51, 55, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 52, 177, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 53, 374, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 54, 315, 1, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 55, 372, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 56, 98, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 57, 70, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 58, 47, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 59, 255, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 60, 45, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 61, 208, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 62, 169, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 63, 160, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 64, 364, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 65, 366, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 66, 83, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 67, 363, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 68, 92, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 69, 57, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 70, 297, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 71, 311, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 72, 198, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 73, 150, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 74, 106, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 75, 82, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 76, 71, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 77, 360, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 78, 376, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 79, 131, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 80, 176, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 81, 54, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 82, 253, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 83, 375, 0, 31, 140503251, 1, '2026-06-15 13:56:59', 1),
(14050325, 92, 273, 1, 30, 140503255, 1, '2026-06-15 13:59:20', 5),
(14050325, 93, 315, 1, 30, 140503255, 1, '2026-06-15 13:59:20', 3),
(14050325, 94, 364, 0, 30, 140503255, 1, '2026-06-15 13:59:20', 5),
(14050325, 95, 367, 1, 30, 140503255, 1, '2026-06-15 13:59:20', 5),
(14050325, 96, 371, 0, 30, 140503255, 1, '2026-06-15 13:59:20', 5),
(14050325, 97, 52, 1, 30, 140503255, 1, '2026-06-15 13:59:20', 5),
(14050325, 98, 359, 1, 30, 140503255, 1, '2026-06-15 13:59:20', 6),
(14050325, 99, 166, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 3),
(14050325, 100, 117, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 5),
(14050325, 101, 121, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 6),
(14050325, 102, 215, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 3),
(14050325, 103, 250, 0, 34, 140503255, 1, '2026-06-15 14:01:31', 5),
(14050325, 104, 270, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 6),
(14050325, 105, 263, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 3),
(14050325, 106, 109, 1, 34, 140503255, 1, '2026-06-15 14:01:31', 3);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_hozor_temp`
--

DROP TABLE IF EXISTS `tbl_hozor_temp`;
CREATE TABLE IF NOT EXISTS `tbl_hozor_temp` (
  `dat_sabt` int DEFAULT NULL,
  `fulnam` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `ID_hazer` int NOT NULL AUTO_INCREMENT,
  `id_person` int DEFAULT '0',
  `ispresent` tinyint(1) DEFAULT '0',
  `nam_bakhsh` int NOT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_hazer`),
  UNIQUE KEY `tbl-hozorID` (`ID_hazer`),
  KEY `id_person` (`id_person`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=365 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_kod_omomy`
--

DROP TABLE IF EXISTS `tbl_kod_omomy`;
CREATE TABLE IF NOT EXISTS `tbl_kod_omomy` (
  `dat_sabt` int DEFAULT NULL,
  `eghdam` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `ID_kod_omomy` int NOT NULL AUTO_INCREMENT,
  `nam_mahal` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam_shift` int NOT NULL,
  `natijeh_amlit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `onvan_kod_omomy` int NOT NULL,
  `shedat_bohran` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT '0',
  `tavzih` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `time_saat_dagig_shoro` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `time_sat_dagigeh_paian` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `baieghani` tinyint NOT NULL COMMENT 'غیر قابل تغییر شدن',
  `mostanad` varchar(250) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT 'ذخیره سند ',
  PRIMARY KEY (`ID_kod_omomy`),
  KEY `shift_namTtbl_kod_omomy` (`nam_shift`),
  KEY `tbl_onvan_kod_omomytbl_kod_omomy` (`onvan_kod_omomy`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_kod_omomy_person`
--

DROP TABLE IF EXISTS `tbl_kod_omomy_person`;
CREATE TABLE IF NOT EXISTS `tbl_kod_omomy_person` (
  `adres` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `fam_person` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `id_cod_omomi` int NOT NULL DEFAULT '0',
  `ID_person_kod_omom` int NOT NULL AUTO_INCREMENT,
  `nam_person` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `number_mobil` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `number_tel` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `number2` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `preson_id` int DEFAULT '0',
  PRIMARY KEY (`ID_person_kod_omom`),
  KEY `id_cod_omomi` (`id_cod_omomi`),
  KEY `number_mobil` (`number_mobil`),
  KEY `number_tel` (`number_tel`),
  KEY `number_tel1` (`number2`),
  KEY `preson_id` (`preson_id`),
  KEY `tbl_kod_omomytbl_kod_omomy_person` (`id_cod_omomi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_naghsh_kod`
--

DROP TABLE IF EXISTS `tbl_naghsh_kod`;
CREATE TABLE IF NOT EXISTS `tbl_naghsh_kod` (
  `dat_sabt` int DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `ID_naghsh_kod` int NOT NULL AUTO_INCREMENT,
  `id_person` int DEFAULT '0',
  `nam_kod` int DEFAULT '0',
  `nam_nagsh` int DEFAULT '0',
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_naghsh_kod`),
  KEY `id_person` (`id_person`),
  KEY `tbl_amliat_kodtbl_naghsh_kod` (`nam_kod`),
  KEY `tbl_onvan_naghshtbl_naghsh_kod` (`nam_nagsh`),
  KEY `tbl_persontbl_naghsh_kod` (`id_person`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=216 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_nam_modiriat`
--

DROP TABLE IF EXISTS `tbl_nam_modiriat`;
CREATE TABLE IF NOT EXISTS `tbl_nam_modiriat` (
  `ID_nam_modirit` int NOT NULL AUTO_INCREMENT,
  `nam_modiriat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`ID_nam_modirit`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_nam_modiriat`
--

INSERT INTO `tbl_nam_modiriat` (`ID_nam_modirit`, `nam_modiriat`) VALUES
(26, 'مدیریت دارو و تجهیزات پزشکی'),
(27, 'مدیریت آماد و پشتیبانی'),
(28, 'مدیریت اطلاعات سلامت و فن آوری اطلاعات'),
(29, 'مدیریت خدمات پرستاری'),
(30, 'مدیریت بیمارستان'),
(31, 'مدیریت مالی و ذیحسابی'),
(32, 'مدیریت درمانگاه'),
(33, 'مدیریت منابع نیروری انسانی'),
(34, 'مسئول فنی بیمارستان'),
(35, 'رئیس / مدیر بیمارستان'),
(36, 'ادمین'),
(41, 'خارج از چارت سازمانی'),
(43, 'مسئول آزماشگاه'),
(45, 'مسئول بخش مردان1'),
(46, 'مسئول بخش مردان2'),
(47, 'مسئول بخش زنان');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_nazar_fanni`
--

DROP TABLE IF EXISTS `tbl_nazar_fanni`;
CREATE TABLE IF NOT EXISTS `tbl_nazar_fanni` (
  `dat_payan` datetime DEFAULT NULL,
  `dat_sabt` int DEFAULT '0',
  `ID_nazar_fanni` int NOT NULL AUTO_INCREMENT,
  `kod_gozaresh` int DEFAULT '0',
  `nazar_msol_fanni` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `taiid_nazar` tinyint(1) DEFAULT '0',
  `UserID` int DEFAULT '0',
  PRIMARY KEY (`ID_nazar_fanni`),
  KEY `tbl_gozareshtbl_nazar_fanni` (`kod_gozaresh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_nazar_raiis`
--

DROP TABLE IF EXISTS `tbl_nazar_raiis`;
CREATE TABLE IF NOT EXISTS `tbl_nazar_raiis` (
  `dat_payan` datetime DEFAULT NULL,
  `dat_sabt` int DEFAULT '0',
  `ID_nazar_raiis` int NOT NULL AUTO_INCREMENT,
  `kod_gozaresh` int DEFAULT '0',
  `nazar_raiss` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `taiid_nazar` tinyint(1) DEFAULT '0',
  `UserID` int DEFAULT '0',
  PRIMARY KEY (`ID_nazar_raiis`),
  KEY `tbl_gozareshtbl_nazar_raiis` (`kod_gozaresh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_gozaresh`
--

DROP TABLE IF EXISTS `tbl_onvan_gozaresh`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_gozaresh` (
  `ID_onvan_gozaresh` int NOT NULL AUTO_INCREMENT,
  `nam_onvan_gozaresh` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`ID_onvan_gozaresh`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_onvan_gozaresh`
--

INSERT INTO `tbl_onvan_gozaresh` (`ID_onvan_gozaresh`, `nam_onvan_gozaresh`) VALUES
(64, 'خرابی آسانسور');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_kod`
--

DROP TABLE IF EXISTS `tbl_onvan_kod`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_kod` (
  `dat_sabt` int DEFAULT NULL,
  `ID_onvan_kod` int NOT NULL AUTO_INCREMENT,
  `nam_kod` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_onvan_kod`),
  UNIQUE KEY `nam-takhasos` (`nam_kod`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_kod_omomy`
--

DROP TABLE IF EXISTS `tbl_onvan_kod_omomy`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_kod_omomy` (
  `dat_sabt` int DEFAULT NULL,
  `ID_onvan_kod_o` int NOT NULL AUTO_INCREMENT,
  `nam_kod_o` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_onvan_kod_o`),
  UNIQUE KEY `nam-takhasos` (`nam_kod_o`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_naghsh`
--

DROP TABLE IF EXISTS `tbl_onvan_naghsh`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_naghsh` (
  `id_onvan_kod` int DEFAULT '0',
  `ID_onvan_naghsh_kod` int NOT NULL AUTO_INCREMENT,
  `nam_naghsh_kod` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`ID_onvan_naghsh_kod`),
  KEY `id_onvan` (`id_onvan_kod`),
  KEY `tbl_onvan_kodtbl_onvan_naghsh` (`id_onvan_kod`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_naghsh_bohran`
--

DROP TABLE IF EXISTS `tbl_onvan_naghsh_bohran`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_naghsh_bohran` (
  `ID_onvan_naghsh_bohran` int NOT NULL AUTO_INCREMENT,
  `nam_onvan_naghsh_bohran` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_persian_ci NOT NULL,
  `tozihat` text CHARACTER SET utf8mb4 COLLATE utf8mb4_persian_ci,
  `mahal1` int NOT NULL,
  `mahal2` int NOT NULL,
  `mahal3` int NOT NULL,
  `mahal4` int NOT NULL,
  `rang_bohran` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_persian_ci NOT NULL COMMENT 'ذخیره رنگ جلیقه',
  PRIMARY KEY (`ID_onvan_naghsh_bohran`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_shoghl`
--

DROP TABLE IF EXISTS `tbl_onvan_shoghl`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_shoghl` (
  `dat_sabt` int DEFAULT NULL,
  `ID_shoghl` int NOT NULL AUTO_INCREMENT,
  `nam_shogl` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_shoghl`),
  UNIQUE KEY `nam-shogl` (`nam_shogl`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_onvan_shoghl`
--

INSERT INTO `tbl_onvan_shoghl` (`dat_sabt`, `ID_shoghl`, `nam_shogl`, `UserID`, `zaman_sabt`) VALUES
(14041209, 21, 'پرستار', 33, '2026-02-28 16:53:12'),
(14041209, 22, 'کمک پرستار', 33, '2026-02-28 16:53:58'),
(14041209, 23, 'بهیار', 33, '2026-02-28 16:54:14'),
(14041209, 24, 'کمک بهیار', 33, '2026-02-28 16:54:27'),
(14041209, 25, 'منشی', 33, '2026-02-28 16:54:37'),
(14041209, 26, 'خدمات', 33, '2026-02-28 16:54:45'),
(14041209, 27, 'سرپرستار', 33, '2026-02-28 16:55:00'),
(14041209, 28, 'نگهبان', 33, '2026-02-28 16:55:28');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_onvan_takhasos`
--

DROP TABLE IF EXISTS `tbl_onvan_takhasos`;
CREATE TABLE IF NOT EXISTS `tbl_onvan_takhasos` (
  `dat_sabt` int DEFAULT NULL,
  `ID_onvan_takhasos` int NOT NULL AUTO_INCREMENT,
  `nam_takhasos` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  `IS_Ankal` tinyint DEFAULT NULL,
  PRIMARY KEY (`ID_onvan_takhasos`),
  UNIQUE KEY `nam-takhasos` (`nam_takhasos`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_onvan_takhasos`
--

INSERT INTO `tbl_onvan_takhasos` (`dat_sabt`, `ID_onvan_takhasos`, `nam_takhasos`, `UserID`, `zaman_sabt`, `IS_Ankal`) VALUES
(14041209, 28, 'ارتوپدی', 33, '2026-02-28 16:58:50', 1),
(14041209, 29, 'زنان و زایمان', 33, '2026-02-28 16:59:13', 1),
(14041209, 30, 'نروسرجری', 33, '2026-02-28 16:59:34', 1),
(14041209, 31, 'نرولوژی', 33, '2026-02-28 16:59:44', 1),
(14041209, 32, 'جراحی عروق', 33, '2026-02-28 17:00:12', 0),
(14041209, 33, 'جراحی عمومی', 33, '2026-02-28 17:00:25', 1),
(14041209, 34, 'رادیولوژی', 33, '2026-02-28 17:00:44', 0),
(14041210, 35, 'عمومی', 33, '2026-03-01 12:19:49', 0),
(14050210, 36, 'ENT', 1, '2026-04-30 10:51:29', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_pasokh_modir_javab`
--

DROP TABLE IF EXISTS `tbl_pasokh_modir_javab`;
CREATE TABLE IF NOT EXISTS `tbl_pasokh_modir_javab` (
  `dat_payan` datetime DEFAULT NULL,
  `dat_sabt` int DEFAULT NULL,
  `ID_javab_modir` int NOT NULL AUTO_INCREMENT,
  `javab_sharh_kamel` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `kod_gozaresh` int NOT NULL DEFAULT '0',
  `pasokh_onvan` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `payan_kar` tinyint(1) DEFAULT '0',
  `UserID` int DEFAULT '0',
  `zaman_open` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_javab_modir`),
  KEY `tbl_gozareshtbl_pasokh_modir_javab` (`kod_gozaresh`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_person`
--

DROP TABLE IF EXISTS `tbl_person`;
CREATE TABLE IF NOT EXISTS `tbl_person` (
  `adress` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `dat_sabt` int DEFAULT NULL,
  `dat_tavalod` int DEFAULT NULL,
  `dat_vorod` int DEFAULT NULL,
  `famil` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `father_nam` varchar(55) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `hom_number1` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `ID_person` int NOT NULL AUTO_INCREMENT,
  `isActiv` tinyint(1) DEFAULT NULL,
  `jens` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `kod_meli` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `madrak` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `madrak_nam` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `mob_number` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `nam` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `other_number2` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `shenase_personli` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `shom_shenasnameh` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `UserID` int DEFAULT '0',
  `vazit_khedmat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `zaman_sabt` datetime DEFAULT NULL,
  `pic` varchar(250) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `list_pezeshk` tinyint NOT NULL,
  `specialty_id` int DEFAULT NULL,
  PRIMARY KEY (`ID_person`),
  UNIQUE KEY `shenase-personli` (`shenase_personli`),
  UNIQUE KEY `shomaeh-meli` (`kod_meli`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=380 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_person`
--

INSERT INTO `tbl_person` (`adress`, `dat_sabt`, `dat_tavalod`, `dat_vorod`, `famil`, `father_nam`, `hom_number1`, `ID_person`, `isActiv`, `jens`, `kod_meli`, `madrak`, `madrak_nam`, `mob_number`, `nam`, `other_number2`, `shenase_personli`, `shom_shenasnameh`, `UserID`, `vazit_khedmat`, `zaman_sabt`, `pic`, `list_pezeshk`, `specialty_id`) VALUES
('یبایایی لسلیسلل فلفثثقفث صثقصقصق', 14040420, 13550203, 13740722, 'ف', 'ا', NULL, 322, 1, 'برادر', NULL, 'کاردان', 'پرستاری', '09188578712', 'ق', NULL, '2', '4', 1, 'اضافه کار', NULL, NULL, 0, NULL),
(NULL, 14040420, NULL, NULL, 'ل', NULL, NULL, 325, 1, 'برادر', '6333333333', 'کارشناس', 'هوشبری', NULL, 'ل', NULL, NULL, NULL, 5, 'رسمی', '2025-07-11 15:01:35', NULL, 0, NULL),
('کمننن تتنت  تنخنتنت خحخمتهخمهن خحهخهخ خخت ححخح هنهخخ', 14040717, 13550202, 14040402, 'قربانی', 'بابا', NULL, 326, 1, 'برادر', '3333333333', 'کاردان', 'تاریخ', '11111111111', 'قربان', NULL, '3', '3', 9, 'بیمه', '2025-10-09 17:41:29', NULL, 0, NULL),
(NULL, 14040813, NULL, NULL, 'ریال', NULL, NULL, 328, -1, 'خواهر', NULL, 'دکترا', NULL, NULL, 'تومان', NULL, NULL, NULL, 5, NULL, '2025-11-04 22:29:01', NULL, 0, NULL),
('آدرس - شهر - خیابان - کوچه - پلاک', 14041210, 14000101, 14011210, 'تست2', 'تست3', '55555', 344, 1, 'زن', '1234567891', 'کارشناسی', 'هوافضا', '09188578755', 'تست1', '09113216549', '123', '587', 1, 'قراردادی', '2026-03-01 12:11:52', NULL, 0, NULL),
('نامعلوم', 14050108, 13900101, 14050108, 'فامیلی1', 'پدر1', '083300222', 357, 0, 'زن', '321654', 'سیکل', 'برق', '09213587454', 'نام1', '091200000', '1111', '123', 1, 'قراردادی', '2026-03-28 16:08:42', NULL, 0, NULL),
('ننن', 14050108, 14000102, 14050108, 'خانوادگی', 'پدر', '0321', 358, 1, 'مرد', '369', 'تخصص', 'پزشکی', '444', 'پزشک1', '0214', '456', '789', 1, 'پیمانی', '2026-03-28 16:17:57', NULL, 1, 29),
('لرستان- خیابن خیین - کوچه باریک- پلاک 55', 14050209, 13770503, 14050202, 'مرادی', 'کمال', '55555', 359, 1, 'مرد', '325', 'ارشد', 'پرستاری', '091823555', 'علی', '25555', '36', '25', 1, 'قراردادی', '2026-04-29 12:31:08', NULL, 0, NULL),
('تنتیسنتسنتسنی یسمسسنیمنسمن 111', 14050209, 14020202, 14050209, 'محمودی', 'مسلم', '083333', 360, 1, 'مرد', '2223232', 'سیکل', 'تعمیرات', '09122113645', 'مصطفی', '0522', '2323', '123', 1, 'قراردادی', '2026-04-29 14:46:25', NULL, 0, NULL),
('', 14050214, NULL, 14050214, 'آزمایشی2', '', '', 361, 1, 'مرد', NULL, '', '', NULL, 'آزمایشی 1', '', NULL, '', 1, 'رسمی', '2026-05-04 18:37:10', NULL, 1, 33),
('', 14050214, NULL, 14050214, 'دکتر2', '', '', 362, 1, 'مرد', NULL, '', '', NULL, 'دکتر1', '', NULL, '', 1, 'رسمی', '2026-05-04 18:37:49', NULL, 1, 28),
('نتاااذ ادرس جدید شهرک جدید خیبان قدم کوچه کناری پلاک 54422 من و شما لبلب یی کرمانشاه ایذان ببیبی بیببی یبیب', 14050215, 13550201, 14050215, 'صمدزاده', 'صمدی', '08325478455', 363, 1, 'زن', '5488844555', 'کارشناسی', 'پرستاری', '09214587541', 'صنم', '09125487965', '2654', '378', 1, 'قراردادی', '2026-05-05 23:41:36', NULL, 0, NULL),
('کرمانشاه - شهرک اول - خیابان دوم - کوچه سوم - آپارتمان 10 واحدی  - واحد 5 - پلاک 2541 - واحد جنوبی', 14050216, 13880505, 14020216, 'ساسی', 'ساسان', '08325415255', 364, 1, 'زن', '4555454455', 'کاردانی', 'اتاق عمل', '02154783154', 'ساسی', '0918', '654', '2541', 1, 'قراردادی', '2026-05-06 22:42:59', NULL, 0, NULL),
('', 14050216, NULL, 14050216, 'امیری', 'نادر', '', 365, 1, 'مرد', NULL, 'تخصص', 'پزشکی', NULL, 'امیر', '', NULL, '', 1, 'قراردادی', '2026-05-06 23:59:23', NULL, 1, 34),
('کرمان - کروام کورمان تارزلتحخقصسطس لیبیسبلت ننن21', 14050220, 14050201, 14050220, 'صابری', 'صابر', '08325416', 366, 1, 'مرد', '85421479', 'دیپلم', 'تعمیرات', '0913058444', 'محمد', '', NULL, '854', 1, 'پیمانی', '2026-05-10 16:29:41', NULL, 0, NULL),
('', 14050221, NULL, 14050221, 'سعیدی', 'ساعد', '', 367, 1, 'مرد', NULL, 'کارشناسی', 'پرستاری', '09188578712', 'سعید', '', NULL, '', 1, 'قراردادی', '2026-05-11 11:38:33', NULL, 0, NULL),
('', 14050221, NULL, 14050221, 'کککک', '', '', 369, 1, 'مرد', NULL, '', '', NULL, 'الک', '', NULL, '', 1, 'رسمی', '2026-05-11 12:17:06', NULL, 0, NULL),
('ادرس ادرس ادرس', 14050225, 14000203, 14050225, 'مامی', 'شامی', '083254111', 371, 1, 'زن', '9555', 'کارشناسی', 'سیاسی', '091855555555', 'مهندس', '854112', '777', '888', 1, 'قراردادی', '2026-05-15 18:30:19', NULL, 0, NULL),
('کرمان - خیابان - کوچه', 14050226, 13550305, 14030226, 'اکبری', 'تاری', '083125421', 372, 1, 'زن', '3333322', 'کارشناسی', 'اتاق عمل', '091857896451', 'ریما', '', '253641', '22222333', 35, 'قراردادی', '2026-05-16 09:16:30', NULL, 0, NULL),
('نتالا یی یتتی تتس تننسننس سننسنس', 14050226, 13820508, 14050226, 'اصیلی', 'حاصل', '08321547', 374, 1, 'زن', '25148774', 'دیپلم', 'تجربی', '09128457451', 'اصلی', '', '2514', '65418', 1, 'سایر', '2026-05-16 11:29:43', NULL, 0, NULL),
('', 14050226, NULL, 14050226, 'چراغی', 'تاری', '', 375, 1, 'مرد', '14715', 'کاردانی', 'تعمیرات', NULL, 'چراغ', '', '14222', '654', 1, 'طرحی', '2026-05-16 12:45:08', NULL, 0, NULL),
('', 14050226, 13570221, 14051101, 'موسوی', 'سهرا', '', 376, 1, 'مرد', '3651', 'کاردانی', 'اتاق عمل', '091825252525', 'سهراب', '', '5414444', '54144444', 1, 'پیمانی', '2026-05-16 16:35:17', NULL, 0, NULL),
('', 14050231, NULL, 14050231, 'راهی', '', '', 377, 1, 'مرد', NULL, 'دیپلم', 'تعمیرات', NULL, 'صغری', '', NULL, '', 1, 'رسمی', '2026-05-21 11:33:49', NULL, 0, NULL),
('', 14050231, NULL, 14050231, 'عزیز', '', '', 378, 1, 'مرد', NULL, 'کاردانی', 'تجربی', NULL, 'راشا', '', NULL, '', 1, 'پیمانی', '2026-05-21 11:34:49', NULL, 0, NULL),
('', 14050323, NULL, 14050323, 'لالالال', '', '', 379, 1, 'مرد', NULL, 'ارشد', 'پرستاری', NULL, 'ااالالالالا', '', NULL, '', 1, 'رسمی', '2026-06-13 14:43:33', NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_personnel_shifts`
--

DROP TABLE IF EXISTS `tbl_personnel_shifts`;
CREATE TABLE IF NOT EXISTS `tbl_personnel_shifts` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `ID_person` int NOT NULL,
  `shift_date` int NOT NULL,
  `ID_onvan_shift` int NOT NULL,
  `is_extra` int DEFAULT '0',
  `assigned_by` int DEFAULT NULL,
  `zaman_sabt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=148 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_personnel_shifts`
--

INSERT INTO `tbl_personnel_shifts` (`ID`, `ID_person`, `shift_date`, `ID_onvan_shift`, `is_extra`, `assigned_by`, `zaman_sabt`) VALUES
(44, 263, 14050326, 1, 0, 42, '2026-06-14 10:35:47'),
(43, 263, 14050325, 1, 0, 42, '2026-06-14 10:35:44'),
(42, 263, 14050324, 3, 0, 42, '2026-06-14 10:35:42'),
(41, 270, 14050326, 2, 0, 42, '2026-06-14 10:35:38'),
(40, 270, 14050325, 1, 0, 42, '2026-06-14 10:35:37'),
(39, 270, 14050324, 1, 0, 42, '2026-06-14 10:35:35'),
(38, 250, 14050326, 2, 0, 42, '2026-06-14 10:35:29'),
(37, 250, 14050325, 6, 0, 42, '2026-06-14 10:35:17'),
(36, 250, 14050324, 3, 0, 42, '2026-06-14 10:35:14'),
(35, 215, 14050326, 2, 0, 42, '2026-06-14 10:35:11'),
(34, 215, 14050325, 1, 0, 42, '2026-06-14 10:35:07'),
(33, 215, 14050324, 3, 0, 42, '2026-06-14 10:35:00'),
(32, 121, 14050326, 2, 0, 42, '2026-06-14 10:34:58'),
(31, 121, 14050325, 1, 0, 42, '2026-06-14 10:34:55'),
(30, 121, 14050324, 5, 0, 42, '2026-06-14 10:34:52'),
(29, 117, 14050326, 1, 0, 42, '2026-06-14 10:34:47'),
(28, 117, 14050325, 4, 0, 42, '2026-06-14 10:34:45'),
(27, 117, 14050324, 3, 0, 42, '2026-06-14 10:34:42'),
(26, 166, 14050326, 3, 0, 42, '2026-06-14 10:34:36'),
(25, 166, 14050325, 2, 0, 42, '2026-06-14 10:34:33'),
(24, 166, 14050324, 6, 1, 42, '2026-06-14 10:34:21'),
(23, 166, 14050324, 1, 0, 42, '2026-06-14 10:34:17'),
(45, 270, 14050325, 6, 1, 42, '2026-06-14 10:35:53'),
(46, 166, 14050323, 2, 1, 1, '2026-06-14 11:12:27'),
(137, 42, 14050321, 1, 0, 1, '2026-06-15 12:40:46'),
(48, 273, 14050324, 1, 0, 1, '2026-06-14 14:13:00'),
(49, 273, 14050324, 6, 1, 1, '2026-06-14 14:13:05'),
(50, 315, 14050324, 2, 0, 1, '2026-06-14 14:13:09'),
(51, 364, 14050324, 3, 0, 1, '2026-06-14 14:13:12'),
(52, 367, 14050324, 4, 0, 1, '2026-06-14 14:13:16'),
(53, 371, 14050324, 5, 0, 1, '2026-06-14 14:13:20'),
(54, 52, 14050324, 3, 0, 1, '2026-06-14 14:13:28'),
(55, 359, 14050324, 6, 0, 1, '2026-06-14 14:13:32'),
(56, 273, 14050325, 1, 0, 1, '2026-06-14 14:13:42'),
(57, 315, 14050325, 1, 0, 1, '2026-06-14 14:13:47'),
(58, 315, 14050325, 6, 1, 1, '2026-06-14 14:13:52'),
(59, 364, 14050325, 5, 0, 1, '2026-06-14 14:13:56'),
(60, 367, 14050325, 2, 0, 1, '2026-06-14 14:14:00'),
(61, 371, 14050325, 3, 0, 1, '2026-06-14 14:14:03'),
(62, 52, 14050325, 5, 0, 1, '2026-06-14 14:14:07'),
(63, 359, 14050325, 1, 0, 1, '2026-06-14 14:14:15'),
(64, 273, 14050326, 2, 0, 1, '2026-06-14 14:14:19'),
(65, 315, 14050326, 3, 0, 1, '2026-06-14 14:14:22'),
(66, 364, 14050326, 3, 0, 1, '2026-06-14 14:14:30'),
(67, 367, 14050326, 4, 0, 1, '2026-06-14 14:14:34'),
(68, 371, 14050326, 5, 0, 1, '2026-06-14 14:14:36'),
(69, 52, 14050326, 6, 0, 1, '2026-06-14 14:14:38'),
(70, 359, 14050326, 1, 0, 1, '2026-06-14 14:14:43'),
(71, 359, 14050326, 6, 1, 1, '2026-06-14 14:14:48'),
(72, 273, 14050327, 1, 0, 1, '2026-06-14 14:16:58'),
(73, 273, 14050327, 3, 1, 1, '2026-06-14 14:17:02'),
(74, 315, 14050327, 2, 0, 1, '2026-06-14 14:17:07'),
(75, 311, 14050301, 2, 0, 1, '2026-06-14 18:16:32'),
(76, 311, 14050302, 2, 0, 1, '2026-06-14 18:16:32'),
(77, 311, 14050303, 2, 0, 1, '2026-06-14 18:16:32'),
(78, 311, 14050304, 2, 0, 1, '2026-06-14 18:16:32'),
(79, 311, 14050305, 2, 0, 1, '2026-06-14 18:16:32'),
(80, 311, 14050306, 2, 0, 1, '2026-06-14 18:16:32'),
(81, 311, 14050307, 2, 0, 1, '2026-06-14 18:16:32'),
(82, 311, 14050308, 2, 0, 1, '2026-06-14 18:16:32'),
(83, 311, 14050309, 2, 0, 1, '2026-06-14 18:16:32'),
(84, 311, 14050310, 2, 0, 1, '2026-06-14 18:16:32'),
(85, 311, 14050311, 2, 0, 1, '2026-06-14 18:16:32'),
(86, 311, 14050312, 2, 0, 1, '2026-06-14 18:16:32'),
(87, 311, 14050313, 2, 0, 1, '2026-06-14 18:16:32'),
(88, 311, 14050314, 2, 0, 1, '2026-06-14 18:16:32'),
(89, 311, 14050315, 2, 0, 1, '2026-06-14 18:16:32'),
(90, 311, 14050316, 2, 0, 1, '2026-06-14 18:16:32'),
(91, 311, 14050317, 2, 0, 1, '2026-06-14 18:16:32'),
(92, 311, 14050318, 2, 0, 1, '2026-06-14 18:16:32'),
(93, 311, 14050319, 2, 0, 1, '2026-06-14 18:16:32'),
(94, 311, 14050320, 2, 0, 1, '2026-06-14 18:16:32'),
(95, 169, 14050324, 1, 0, 1, '2026-06-14 19:15:51'),
(97, 273, 14050322, 1, 0, 1, '2026-06-14 19:16:21'),
(98, 166, 14050321, 1, 0, 1, '2026-06-14 19:47:17'),
(99, 273, 14050323, 1, 0, 1, '2026-06-14 19:58:16'),
(100, 166, 14050327, 1, 0, 1, '2026-06-14 19:58:27'),
(101, 166, 14050320, 2, 0, 1, '2026-06-15 14:53:05'),
(102, 166, 14050319, 1, 0, 1, '2026-06-14 19:58:51'),
(103, 273, 14050321, 1, 0, 1, '2026-06-14 22:21:42'),
(104, 273, 14050321, 3, 1, 1, '2026-06-14 22:21:46'),
(105, 273, 14050320, 1, 0, 1, '2026-06-14 22:23:51'),
(106, 166, 14050318, 1, 0, 1, '2026-06-14 22:23:59'),
(107, 166, 14050317, 1, 0, 1, '2026-06-14 22:24:07'),
(108, 273, 14050319, 1, 0, 1, '2026-06-14 22:24:38'),
(109, 273, 14050318, 1, 0, 1, '2026-06-14 22:24:44'),
(110, 166, 14050331, 1, 0, 1, '2026-06-14 22:25:00'),
(111, 166, 14050330, 1, 0, 1, '2026-06-14 22:25:03'),
(112, 166, 14050329, 4, 0, 1, '2026-06-14 22:25:07'),
(113, 166, 14050328, 1, 0, 1, '2026-06-14 22:26:19'),
(114, 166, 14050316, 1, 0, 1, '2026-06-14 22:26:30'),
(115, 166, 14050315, 1, 0, 1, '2026-06-14 22:28:37'),
(116, 273, 14050317, 1, 0, 1, '2026-06-14 22:44:25'),
(117, 273, 14050317, 6, 1, 1, '2026-06-14 22:44:29'),
(118, 273, 14050314, 1, 0, 1, '2026-06-14 22:44:58'),
(119, 273, 14050328, 1, 0, 1, '2026-06-14 22:45:45'),
(120, 166, 14050314, 1, 0, 1, '2026-06-14 22:45:53'),
(121, 117, 14050327, 1, 0, 1, '2026-06-14 22:46:12'),
(122, 117, 14050318, 1, 0, 1, '2026-06-14 22:46:39'),
(123, 166, 14050331, 6, 1, 1, '2026-06-14 22:46:47'),
(124, 273, 14050318, 6, 1, 35, '2026-06-15 08:45:26'),
(125, 273, 14050301, 1, 0, 35, '2026-06-15 08:45:40'),
(126, 273, 14050302, 1, 0, 35, '2026-06-15 08:45:40'),
(127, 273, 14050303, 1, 0, 35, '2026-06-15 08:45:40'),
(128, 273, 14050304, 1, 0, 35, '2026-06-15 08:45:40'),
(129, 273, 14050305, 1, 0, 35, '2026-06-15 08:45:40'),
(130, 273, 14050306, 1, 0, 35, '2026-06-15 08:45:40'),
(131, 273, 14050307, 1, 0, 35, '2026-06-15 08:45:40'),
(132, 273, 14050308, 1, 0, 35, '2026-06-15 08:45:40'),
(133, 273, 14050309, 1, 0, 35, '2026-06-15 08:45:40'),
(134, 273, 14050310, 1, 0, 35, '2026-06-15 08:45:40'),
(135, 273, 14050311, 1, 0, 35, '2026-06-15 08:45:40'),
(138, 42, 14050321, 6, 1, 1, '2026-06-15 12:40:57'),
(139, 166, 14050330, 6, 1, 1, '2026-06-15 14:53:20'),
(140, 42, 14050323, 1, 0, 1, '2026-06-15 15:14:33'),
(141, 315, 14050319, 1, 0, 1, '2026-06-15 15:14:43'),
(142, 273, 14050125, 1, 0, 1, '2026-06-15 15:31:58'),
(143, 273, 14050126, 3, 0, 1, '2026-06-15 15:32:01'),
(144, 273, 14050127, 4, 0, 1, '2026-06-15 15:32:04'),
(145, 273, 14050128, 6, 0, 1, '2026-06-15 15:32:07'),
(146, 273, 14050129, 2, 0, 1, '2026-06-15 15:32:14'),
(147, 273, 14050122, 1, 0, 1, '2026-06-15 15:55:32');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_sath_bohran`
--

DROP TABLE IF EXISTS `tbl_sath_bohran`;
CREATE TABLE IF NOT EXISTS `tbl_sath_bohran` (
  `Id_sath_bohran` int NOT NULL AUTO_INCREMENT,
  `nam_sath_bohran` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `tozaihat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  PRIMARY KEY (`Id_sath_bohran`),
  UNIQUE KEY `nam-takhasos` (`nam_sath_bohran`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_sazema_person`
--

DROP TABLE IF EXISTS `tbl_sazema_person`;
CREATE TABLE IF NOT EXISTS `tbl_sazema_person` (
  `dat_payan` int DEFAULT NULL,
  `dat_sabt` int NOT NULL,
  `dat_shoro` int NOT NULL,
  `ID_sazman_person` int NOT NULL AUTO_INCREMENT,
  `nam_bakhsh` int NOT NULL,
  `nam_person` int NOT NULL,
  `payani_sazmandehi` tinyint(1) DEFAULT '0',
  `shoghl` int NOT NULL,
  `UserID` int DEFAULT '0',
  `UserID_payani` int DEFAULT '0',
  `zaman_sabt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_sazman_person`),
  UNIQUE KEY `ID` (`ID_sazman_person`),
  KEY `tbl_bakhshtbl_sazema_person` (`nam_bakhsh`),
  KEY `tbl_onvan_shoghltbl_sazema_person` (`shoghl`),
  KEY `tbl_persontbl_sazema_person` (`nam_person`),
  KEY `tbl-sazeman-personnam-person` (`nam_person`),
  KEY `UserID` (`UserID`),
  KEY `UserID1` (`UserID_payani`)
) ENGINE=InnoDB AUTO_INCREMENT=424 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `tbl_sazema_person`
--

INSERT INTO `tbl_sazema_person` (`dat_payan`, `dat_sabt`, `dat_shoro`, `ID_sazman_person`, `nam_bakhsh`, `nam_person`, `payani_sazmandehi`, `shoghl`, `UserID`, `UserID_payani`, `zaman_sabt`) VALUES
(NULL, 14041122, 14050101, 339, 31, 344, 1, 21, 1, 0, '2026-03-28 15:49:55'),
(14050216, 14050108, 14000108, 341, 30, 357, 1, 26, 1, 0, '2026-03-28 18:11:03'),
(NULL, 14050127, 14050127, 346, 31, 357, 1, 25, 1, 0, '2026-04-16 16:53:58'),
(14050217, 14050209, 13990119, 347, 30, 344, 1, 21, 1, 0, '2026-04-29 12:27:05'),
(14050216, 14050209, 14000108, 349, 30, 360, 1, 22, 1, 0, '2026-04-29 15:12:18'),
(NULL, 14050215, 14000108, 351, 30, 359, 0, 21, 1, 0, '2026-05-05 22:20:26'),
(NULL, 14050216, 14030216, 353, 30, 364, 0, 25, 1, 0, '2026-05-06 22:43:41'),
(NULL, 14050216, 14050216, 355, 31, 363, 0, 21, 1, 0, '2026-05-06 23:34:45'),
(NULL, 14050217, 14050217, 356, 38, 344, 0, 25, 1, 0, '2026-05-07 09:40:46'),
(14050220, 14050220, 14050220, 357, 33, 360, 1, 24, 1, 0, '2026-05-10 15:41:16'),
(14050220, 14050220, 14050220, 358, 31, 363, 1, 24, 1, 0, '2026-05-10 16:04:16'),
(NULL, 14050220, 14010220, 359, 31, 360, 0, 27, 1, 0, '2026-05-10 16:20:10'),
(NULL, 14050220, 14010220, 360, 31, 366, 0, 28, 1, 0, '2026-05-10 16:29:57'),
(NULL, 14050221, 14020221, 363, 31, 364, 0, 24, 1, 0, '2026-05-11 11:34:32'),
(NULL, 14050221, 14050221, 365, 38, 369, 0, 21, 1, 0, '2026-05-11 12:17:17'),
(NULL, 14050225, 14050225, 366, 35, 359, 0, 24, 35, 0, '2026-05-15 18:41:39'),
(NULL, 14050225, 14050225, 367, 30, 371, 0, 24, 35, 0, '2026-05-15 18:42:06'),
(NULL, 14050225, 14050225, 368, 38, 359, 0, 22, 35, 0, '2026-05-15 18:44:25'),
(NULL, 14050226, 14030226, 369, 31, 372, 0, 21, 35, 0, '2026-05-16 09:17:03'),
(NULL, 14050226, 14050226, 371, 31, 374, 0, 25, 1, 0, '2026-05-16 11:30:25'),
(NULL, 14050226, 14050226, 372, 31, 375, 0, 25, 1, 0, '2026-05-16 12:45:20'),
(NULL, 14050226, 14050226, 373, 30, 367, 0, 21, 1, 0, '2026-05-16 12:46:59'),
(NULL, 14050226, 14050226, 374, 31, 376, 0, 24, 1, 0, '2026-05-16 16:36:27'),
(NULL, 14050231, 14050231, 375, 33, 377, 0, 25, 1, 0, '2026-05-21 11:34:01'),
(NULL, 14050231, 14050231, 376, 32, 378, 0, 25, 1, 0, '2026-05-21 11:35:07'),
(NULL, 14050309, 14050309, 377, 30, 52, 0, 21, 1, 0, '2026-05-30 07:47:38'),
(NULL, 14050309, 14050310, 378, 30, 315, 0, 21, 1, 0, '2026-05-30 19:13:53'),
(NULL, 14050309, 13900201, 379, 32, 309, 0, 24, 1, 0, '2026-05-30 19:15:30'),
(NULL, 14050310, 14000203, 380, 31, 315, 0, 21, 1, 0, '2026-05-31 08:53:01'),
(NULL, 14050310, 14050310, 381, 33, 148, 0, 24, 1, 0, '2026-05-31 08:54:19'),
(NULL, 14050310, 14050310, 382, 32, 301, 0, 24, 1, 0, '2026-05-31 08:54:46'),
(NULL, 14050310, 14050310, 383, 31, 238, 0, 24, 1, 0, '2026-05-31 09:40:37'),
(NULL, 14050310, 14050310, 384, 36, 220, 0, 27, 1, 0, '2026-05-31 15:06:11'),
(NULL, 14050311, 14050311, 385, 32, 65, 0, 21, 1, 0, '2026-06-01 08:53:20'),
(NULL, 14050311, 14050111, 386, 34, 117, 0, 21, 1, 0, '2026-06-01 08:53:50'),
(NULL, 14050311, 14050311, 387, 30, 273, 0, 21, 1, 0, '2026-06-01 08:54:17'),
(NULL, 14050311, 14050311, 388, 38, 123, 0, 26, 1, 0, '2026-06-01 18:58:14'),
(NULL, 14050311, 14050311, 389, 31, 253, 0, 21, 1, 0, '2026-06-01 18:59:39'),
(NULL, 14050315, 14050315, 390, 31, 42, 0, 21, 1, 0, '2026-06-05 13:11:21'),
(NULL, 14050319, 14050319, 391, 31, 47, 0, 21, 41, 0, '2026-06-09 13:55:57'),
(NULL, 14050319, 14050319, 392, 31, 169, 0, 21, 41, 0, '2026-06-09 13:56:15'),
(NULL, 14050319, 14050319, 393, 31, 92, 0, 21, 41, 0, '2026-06-09 13:56:36'),
(NULL, 14050319, 14050319, 394, 31, 83, 0, 21, 41, 0, '2026-06-09 13:56:49'),
(NULL, 14050319, 14050319, 395, 31, 57, 0, 21, 41, 0, '2026-06-09 13:57:02'),
(NULL, 14050319, 14050319, 396, 31, 106, 0, 21, 41, 0, '2026-06-09 13:57:20'),
(NULL, 14050319, 14050319, 397, 31, 71, 0, 21, 41, 0, '2026-06-09 13:57:32'),
(NULL, 14050319, 14050319, 398, 31, 82, 0, 21, 41, 0, '2026-06-09 13:58:09'),
(NULL, 14050319, 14050319, 399, 31, 131, 0, 21, 41, 0, '2026-06-09 13:58:24'),
(NULL, 14050319, 14050319, 400, 31, 176, 0, 24, 41, 0, '2026-06-09 13:58:34'),
(NULL, 14050319, 14050319, 401, 31, 54, 0, 24, 41, 0, '2026-06-09 13:59:00'),
(NULL, 14050319, 14050319, 402, 31, 93, 0, 21, 1, 0, '2026-06-09 14:01:31'),
(NULL, 14050319, 14050319, 403, 31, 172, 0, 21, 1, 0, '2026-06-09 14:01:41'),
(NULL, 14050319, 14050319, 404, 31, 55, 0, 21, 1, 0, '2026-06-09 14:01:51'),
(NULL, 14050319, 14050319, 405, 31, 177, 0, 21, 1, 0, '2026-06-09 14:02:03'),
(NULL, 14050319, 14050319, 406, 31, 98, 0, 25, 1, 0, '2026-06-09 14:02:24'),
(NULL, 14050319, 14050319, 407, 31, 255, 0, 21, 1, 0, '2026-06-09 14:02:32'),
(NULL, 14050319, 14050319, 408, 31, 70, 0, 21, 1, 0, '2026-06-09 14:02:49'),
(NULL, 14050319, 14050319, 409, 31, 208, 0, 26, 1, 0, '2026-06-09 14:03:11'),
(NULL, 14050319, 14050319, 410, 31, 45, 0, 27, 1, 0, '2026-06-09 14:03:22'),
(NULL, 14050319, 14050319, 411, 31, 160, 0, 21, 1, 0, '2026-06-09 14:03:33'),
(NULL, 14050319, 14050319, 412, 31, 297, 0, 21, 1, 0, '2026-06-09 14:03:51'),
(NULL, 14050319, 14050319, 413, 31, 311, 0, 21, 1, 0, '2026-06-09 14:04:01'),
(NULL, 14050319, 14050319, 414, 31, 150, 0, 21, 1, 0, '2026-06-09 14:04:20'),
(NULL, 14050319, 14050319, 415, 31, 198, 0, 21, 1, 0, '2026-06-09 14:04:33'),
(NULL, 14050322, 14050322, 416, 34, 121, 0, 26, 1, 0, '2026-06-12 15:10:48'),
(NULL, 14050322, 14050322, 417, 34, 215, 0, 21, 1, 0, '2026-06-12 15:11:10'),
(NULL, 14050322, 14050322, 418, 34, 250, 0, 21, 1, 0, '2026-06-12 15:11:23'),
(NULL, 14050322, 14050322, 419, 34, 166, 0, 27, 1, 0, '2026-06-12 15:13:03'),
(NULL, 14050322, 14050322, 420, 34, 270, 0, 21, 1, 0, '2026-06-12 15:13:23'),
(NULL, 14050322, 14050322, 421, 34, 263, 0, 22, 1, 0, '2026-06-12 15:13:35'),
(NULL, 14050322, 14050322, 422, 34, 109, 0, 21, 1, 0, '2026-06-12 15:13:58'),
(14050323, 14050323, 14020323, 423, 31, 179, 1, 21, 1, 0, '2026-06-13 13:57:30');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_shift_approvals`
--

DROP TABLE IF EXISTS `tbl_shift_approvals`;
CREATE TABLE IF NOT EXISTS `tbl_shift_approvals` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `dep_id` int NOT NULL,
  `year` smallint NOT NULL,
  `month` tinyint NOT NULL,
  `level_no` tinyint NOT NULL,
  `approved_by` int NOT NULL,
  `approved_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `note` text,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_dep_ym_level` (`dep_id`,`year`,`month`,`level_no`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tbl_shift_approvals`
--

INSERT INTO `tbl_shift_approvals` (`ID`, `dep_id`, `year`, `month`, `level_no`, `approved_by`, `approved_at`, `note`) VALUES
(35, 34, 1405, 3, 1, 42, '2026-06-14 10:36:12', NULL),
(36, 34, 1405, 3, 2, 38, '2026-06-14 11:01:19', NULL),
(38, 34, 1405, 3, 3, 41, '2026-06-14 11:02:36', NULL),
(39, 30, 1405, 3, 1, 35, '2026-06-15 08:45:46', NULL),
(40, 30, 1405, 3, 2, 38, '2026-06-15 08:49:01', NULL),
(41, 30, 1405, 3, 3, 41, '2026-06-15 18:27:42', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_shift_approvers`
--

DROP TABLE IF EXISTS `tbl_shift_approvers`;
CREATE TABLE IF NOT EXISTS `tbl_shift_approvers` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `dep_id` int NOT NULL,
  `level_no` tinyint NOT NULL,
  `level_label` varchar(60) NOT NULL DEFAULT '',
  `user_id` int NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `idx_dep_level` (`dep_id`,`level_no`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tbl_shift_approvers`
--

INSERT INTO `tbl_shift_approvers` (`ID`, `dep_id`, `level_no`, `level_label`, `user_id`) VALUES
(32, 34, 1, 'مسئول بخش', 42),
(33, 34, 2, 'مدیر پرستاری', 38),
(34, 34, 3, 'مسئول کارگزینی', 41),
(35, 30, 1, 'مسئول بخش', 35),
(36, 30, 2, 'مدیر پرستاری', 38),
(37, 30, 3, 'مسئول کارگزینی', 41);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_shift_audit`
--

DROP TABLE IF EXISTS `tbl_shift_audit`;
CREATE TABLE IF NOT EXISTS `tbl_shift_audit` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `dep_id` int NOT NULL,
  `person_id` int NOT NULL,
  `shift_date` int NOT NULL,
  `action` varchar(20) NOT NULL COMMENT 'INSERT/UPDATE/DELETE',
  `old_shift` int DEFAULT NULL,
  `new_shift` int DEFAULT NULL,
  `is_extra` tinyint DEFAULT '0',
  `changed_by` int NOT NULL,
  `changed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `note` text,
  PRIMARY KEY (`ID`),
  KEY `idx_dep_date` (`dep_id`,`shift_date`),
  KEY `idx_person` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=189 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tbl_shift_audit`
--

INSERT INTO `tbl_shift_audit` (`ID`, `dep_id`, `person_id`, `shift_date`, `action`, `old_shift`, `new_shift`, `is_extra`, `changed_by`, `changed_at`, `note`) VALUES
(70, 34, 166, 14050324, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:34:17', NULL),
(71, 34, 166, 14050324, 'INSERT', NULL, 6, 1, 42, '2026-06-14 10:34:21', NULL),
(72, 34, 166, 14050325, 'INSERT', NULL, 2, 0, 42, '2026-06-14 10:34:33', NULL),
(73, 34, 166, 14050326, 'INSERT', NULL, 3, 0, 42, '2026-06-14 10:34:36', NULL),
(74, 34, 117, 14050324, 'INSERT', NULL, 3, 0, 42, '2026-06-14 10:34:42', NULL),
(75, 34, 117, 14050325, 'INSERT', NULL, 4, 0, 42, '2026-06-14 10:34:45', NULL),
(76, 34, 117, 14050326, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:34:47', NULL),
(77, 34, 121, 14050324, 'INSERT', NULL, 5, 0, 42, '2026-06-14 10:34:52', NULL),
(78, 34, 121, 14050325, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:34:55', NULL),
(79, 34, 121, 14050326, 'INSERT', NULL, 2, 0, 42, '2026-06-14 10:34:58', NULL),
(80, 34, 215, 14050324, 'INSERT', NULL, 3, 0, 42, '2026-06-14 10:35:00', NULL),
(81, 34, 215, 14050325, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:35:07', NULL),
(82, 34, 215, 14050326, 'INSERT', NULL, 2, 0, 42, '2026-06-14 10:35:11', NULL),
(83, 34, 250, 14050324, 'INSERT', NULL, 3, 0, 42, '2026-06-14 10:35:14', NULL),
(84, 34, 250, 14050325, 'INSERT', NULL, 6, 0, 42, '2026-06-14 10:35:17', NULL),
(85, 34, 250, 14050326, 'INSERT', NULL, 2, 0, 42, '2026-06-14 10:35:29', NULL),
(86, 34, 270, 14050324, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:35:35', NULL),
(87, 34, 270, 14050325, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:35:37', NULL),
(88, 34, 270, 14050326, 'INSERT', NULL, 2, 0, 42, '2026-06-14 10:35:38', NULL),
(89, 34, 263, 14050324, 'INSERT', NULL, 3, 0, 42, '2026-06-14 10:35:42', NULL),
(90, 34, 263, 14050325, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:35:44', NULL),
(91, 34, 263, 14050326, 'INSERT', NULL, 1, 0, 42, '2026-06-14 10:35:47', NULL),
(92, 34, 270, 14050325, 'INSERT', NULL, 6, 1, 42, '2026-06-14 10:35:53', NULL),
(93, 34, 166, 14050323, 'INSERT', NULL, 2, 1, 1, '2026-06-14 11:12:27', NULL),
(94, 34, 166, 14050322, 'INSERT', NULL, 2, 1, 1, '2026-06-14 13:56:05', NULL),
(95, 30, 273, 14050324, 'INSERT', NULL, 1, 0, 1, '2026-06-14 14:13:00', NULL),
(96, 30, 273, 14050324, 'INSERT', NULL, 6, 1, 1, '2026-06-14 14:13:05', NULL),
(97, 30, 315, 14050324, 'INSERT', NULL, 2, 0, 1, '2026-06-14 14:13:09', NULL),
(98, 30, 364, 14050324, 'INSERT', NULL, 3, 0, 1, '2026-06-14 14:13:12', NULL),
(99, 30, 367, 14050324, 'INSERT', NULL, 4, 0, 1, '2026-06-14 14:13:16', NULL),
(100, 30, 371, 14050324, 'INSERT', NULL, 5, 0, 1, '2026-06-14 14:13:20', NULL),
(101, 30, 52, 14050324, 'INSERT', NULL, 3, 0, 1, '2026-06-14 14:13:28', NULL),
(102, 30, 359, 14050324, 'INSERT', NULL, 6, 0, 1, '2026-06-14 14:13:32', NULL),
(103, 30, 273, 14050325, 'INSERT', NULL, 1, 0, 1, '2026-06-14 14:13:42', NULL),
(104, 30, 315, 14050325, 'INSERT', NULL, 1, 0, 1, '2026-06-14 14:13:47', NULL),
(105, 30, 315, 14050325, 'INSERT', NULL, 6, 1, 1, '2026-06-14 14:13:52', NULL),
(106, 30, 364, 14050325, 'INSERT', NULL, 5, 0, 1, '2026-06-14 14:13:56', NULL),
(107, 30, 367, 14050325, 'INSERT', NULL, 2, 0, 1, '2026-06-14 14:14:00', NULL),
(108, 30, 371, 14050325, 'INSERT', NULL, 3, 0, 1, '2026-06-14 14:14:03', NULL),
(109, 30, 52, 14050325, 'INSERT', NULL, 5, 0, 1, '2026-06-14 14:14:07', NULL),
(110, 30, 359, 14050325, 'INSERT', NULL, 1, 0, 1, '2026-06-14 14:14:15', NULL),
(111, 30, 273, 14050326, 'INSERT', NULL, 2, 0, 1, '2026-06-14 14:14:19', NULL),
(112, 30, 315, 14050326, 'INSERT', NULL, 3, 0, 1, '2026-06-14 14:14:22', NULL),
(113, 30, 364, 14050326, 'INSERT', NULL, 3, 0, 1, '2026-06-14 14:14:30', NULL),
(114, 30, 367, 14050326, 'INSERT', NULL, 4, 0, 1, '2026-06-14 14:14:34', NULL),
(115, 30, 371, 14050326, 'INSERT', NULL, 5, 0, 1, '2026-06-14 14:14:36', NULL),
(116, 30, 52, 14050326, 'INSERT', NULL, 6, 0, 1, '2026-06-14 14:14:38', NULL),
(117, 30, 359, 14050326, 'INSERT', NULL, 1, 0, 1, '2026-06-14 14:14:43', NULL),
(118, 30, 359, 14050326, 'INSERT', NULL, 6, 1, 1, '2026-06-14 14:14:48', NULL),
(119, 30, 273, 14050327, 'INSERT', NULL, 1, 0, 1, '2026-06-14 14:16:58', NULL),
(120, 30, 273, 14050327, 'INSERT', NULL, 3, 1, 1, '2026-06-14 14:17:02', NULL),
(121, 30, 315, 14050327, 'INSERT', NULL, 2, 0, 1, '2026-06-14 14:17:07', NULL),
(122, 31, 311, 14050301, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(123, 31, 311, 14050302, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(124, 31, 311, 14050303, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(125, 31, 311, 14050304, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(126, 31, 311, 14050305, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(127, 31, 311, 14050306, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(128, 31, 311, 14050307, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(129, 31, 311, 14050308, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(130, 31, 311, 14050309, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(131, 31, 311, 14050310, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(132, 31, 311, 14050311, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(133, 31, 311, 14050312, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(134, 31, 311, 14050313, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(135, 31, 311, 14050314, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(136, 31, 311, 14050315, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(137, 31, 311, 14050316, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(138, 31, 311, 14050317, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(139, 31, 311, 14050318, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(140, 31, 311, 14050319, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(141, 31, 311, 14050320, 'INSERT', NULL, 2, 0, 1, '2026-06-14 18:16:32', 'bulk'),
(142, 31, 169, 14050324, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:15:51', NULL),
(143, 31, 169, 14050325, 'INSERT', NULL, 1, 1, 1, '2026-06-14 19:15:56', NULL),
(144, 31, 169, 14050325, 'DELETE', 1, NULL, 1, 1, '2026-06-14 19:16:01', NULL),
(145, 30, 273, 14050322, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:16:21', NULL),
(146, 34, 166, 14050321, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:47:17', NULL),
(147, 30, 273, 14050323, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:58:16', NULL),
(148, 34, 166, 14050327, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:58:27', NULL),
(149, 34, 166, 14050320, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:58:39', NULL),
(150, 34, 166, 14050319, 'INSERT', NULL, 1, 0, 1, '2026-06-14 19:58:51', NULL),
(151, 30, 273, 14050321, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:21:42', NULL),
(152, 30, 273, 14050321, 'INSERT', NULL, 3, 1, 1, '2026-06-14 22:21:46', NULL),
(153, 30, 273, 14050320, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:23:51', NULL),
(154, 34, 166, 14050318, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:23:59', NULL),
(155, 34, 166, 14050317, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:24:07', NULL),
(156, 30, 273, 14050319, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:24:38', NULL),
(157, 30, 273, 14050318, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:24:44', NULL),
(158, 34, 166, 14050331, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:25:00', NULL),
(159, 34, 166, 14050330, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:25:03', NULL),
(160, 34, 166, 14050329, 'INSERT', NULL, 4, 0, 1, '2026-06-14 22:25:07', NULL),
(161, 34, 166, 14050328, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:26:19', NULL),
(162, 34, 166, 14050316, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:26:30', NULL),
(163, 34, 166, 14050315, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:28:37', NULL),
(164, 30, 273, 14050317, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:44:25', NULL),
(165, 30, 273, 14050317, 'INSERT', NULL, 6, 1, 1, '2026-06-14 22:44:29', NULL),
(166, 30, 273, 14050314, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:44:58', NULL),
(167, 30, 273, 14050328, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:45:45', NULL),
(168, 34, 166, 14050314, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:45:53', NULL),
(169, 34, 117, 14050327, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:46:12', NULL),
(170, 34, 117, 14050318, 'INSERT', NULL, 1, 0, 1, '2026-06-14 22:46:39', NULL),
(171, 34, 166, 14050331, 'INSERT', NULL, 6, 1, 1, '2026-06-14 22:46:47', NULL),
(172, 30, 273, 14050318, 'INSERT', NULL, 6, 1, 35, '2026-06-15 08:45:26', NULL),
(173, 30, 273, 14050301, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(174, 30, 273, 14050302, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(175, 30, 273, 14050303, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(176, 30, 273, 14050304, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(177, 30, 273, 14050305, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(178, 30, 273, 14050306, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(179, 30, 273, 14050307, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(180, 30, 273, 14050308, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(181, 30, 273, 14050309, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(182, 30, 273, 14050310, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(183, 30, 273, 14050311, 'INSERT', NULL, 1, 0, 35, '2026-06-15 08:45:40', 'bulk'),
(184, 34, 166, 14050322, 'DELETE', 2, NULL, 1, 1, '2026-06-15 10:57:26', NULL),
(185, 34, 166, 14050322, 'INSERT', NULL, 1, 1, 1, '2026-06-15 12:27:22', NULL),
(186, 34, 166, 14050322, 'DELETE', 1, NULL, 1, 1, '2026-06-15 12:27:25', NULL),
(187, 31, 42, 14050321, 'INSERT', NULL, 1, 0, 1, '2026-06-15 12:40:46', NULL),
(188, 31, 42, 14050321, 'INSERT', NULL, 6, 1, 1, '2026-06-15 12:40:57', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_user_depts`
--

DROP TABLE IF EXISTS `tbl_user_depts`;
CREATE TABLE IF NOT EXISTS `tbl_user_depts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `dep_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ud` (`user_id`,`dep_id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tbl_user_depts`
--

INSERT INTO `tbl_user_depts` (`id`, `user_id`, `dep_id`) VALUES
(51, 1, 30),
(52, 1, 31),
(49, 1, 32),
(54, 1, 33),
(45, 1, 34),
(53, 1, 35),
(47, 1, 36),
(48, 1, 37),
(50, 1, 38),
(46, 1, 42),
(65, 35, 30),
(86, 41, 30),
(87, 41, 31),
(88, 41, 32),
(89, 41, 33),
(90, 41, 34),
(91, 41, 35),
(92, 41, 36),
(93, 41, 37),
(94, 41, 38),
(95, 41, 42),
(41, 42, 30),
(42, 42, 31),
(39, 42, 32),
(44, 42, 33),
(36, 42, 34),
(43, 42, 35),
(37, 42, 36),
(38, 42, 37),
(40, 42, 38);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_user_units`
--

DROP TABLE IF EXISTS `tbl_user_units`;
CREATE TABLE IF NOT EXISTS `tbl_user_units` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `unit_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_uu` (`user_id`,`unit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tbl_user_units`
--

INSERT INTO `tbl_user_units` (`id`, `user_id`, `unit_id`) VALUES
(56, 1, 26),
(52, 1, 27),
(53, 1, 28),
(55, 1, 29),
(54, 1, 30),
(58, 1, 31),
(57, 1, 32),
(59, 1, 33),
(64, 1, 34),
(51, 1, 35),
(49, 1, 36),
(50, 1, 41),
(60, 1, 43),
(62, 1, 45),
(63, 1, 46),
(61, 1, 47),
(66, 35, 45),
(97, 41, 33),
(38, 42, 43),
(40, 42, 45),
(41, 42, 46),
(39, 42, 47),
(88, 44, 26),
(89, 44, 27),
(90, 44, 28),
(91, 44, 30),
(92, 44, 31),
(93, 44, 32),
(94, 44, 33);

-- --------------------------------------------------------

--
-- Table structure for table `userlevelpermissions`
--

DROP TABLE IF EXISTS `userlevelpermissions`;
CREATE TABLE IF NOT EXISTS `userlevelpermissions` (
  `UserLevelID` int NOT NULL,
  `TableName` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Permission` int NOT NULL,
  `dastrasi` tinyint NOT NULL,
  PRIMARY KEY (`UserLevelID`,`TableName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `userlevelpermissions`
--

INSERT INTO `userlevelpermissions` (`UserLevelID`, `TableName`, `Permission`, `dastrasi`) VALUES
(1, 'manager_management_reports', 1, 1),
(1, 'manager_reports', 1, 1),
(1, 'manager_shift_comparison', 1, 1),
(1, 'manager_shift_edit', 1, 1),
(1, 'manager_shift_review', 1, 1),
(1, 'manager_shifts', 1, 1),
(1, 'matron_checklist', 1, 1),
(1, 'matron_codes', 1, 1),
(1, 'matron_personnel', 1, 1),
(1, 'matron_reports', 1, 1),
(1, 'reports_ankal', 1, 1),
(1, 'reports_attendance', 1, 1),
(1, 'reports_blood', 1, 1),
(1, 'reports_codes', 1, 1),
(1, 'reports_crisis', 1, 1),
(1, 'reports_rounds', 1, 1),
(1, 'reports_stats', 1, 1),
(1, 'reports_workflow', 1, 1),
(1, 'supervisor_amar', 1, 1),
(1, 'supervisor_ankal', 1, 1),
(1, 'supervisor_attendance', 1, 1),
(1, 'supervisor_blood', 1, 1),
(1, 'supervisor_codes', 1, 1),
(1, 'supervisor_crisis', 1, 1),
(1, 'supervisor_ghaybat', 1, 1),
(1, 'supervisor_gozaresh', 1, 1),
(1, '⚙️ ادمین', 1, 1),
(1, '🔑 امنیت', 1, 1),
(1, '🏢 ریاست', 1, 1),
(1, '📊 گزارشات', 1, 1),
(1, '📋 مدیر پرستاری', 1, 1),
(1, '👔 مدیران اجرایی', 1, 1),
(1, '🛠️ مسئول فنی', 1, 1),
(1, '👨‍⚕️ سوپروایزر', 1, 1),
(2, 'manager_shift_comparison', 1, 1),
(2, 'manager_shift_edit', 1, 1),
(2, 'reports_ankal', 1, 1),
(2, 'reports_attendance', 1, 1),
(2, 'reports_blood', 1, 1),
(2, 'reports_codes', 1, 1),
(2, 'reports_crisis', 1, 1),
(2, 'reports_rounds', 1, 1),
(2, 'reports_stats', 1, 1),
(2, 'reports_workflow', 1, 1),
(2, 'supervisor_amar', 1, 1),
(2, 'supervisor_ankal', 1, 1),
(2, 'supervisor_attendance', 1, 1),
(2, 'supervisor_blood', 1, 1),
(2, 'supervisor_codes', 1, 1),
(2, 'supervisor_crisis', 1, 1),
(2, 'supervisor_ghaybat', 1, 1),
(2, 'supervisor_gozaresh', 1, 1),
(2, '⚙️ ادمین', 1, 1),
(2, '🔑 امنیت', 1, 1),
(2, '📊 گزارشات', 1, 1),
(2, '👨‍⚕️ سوپروایزر', 1, 1),
(3, 'manager_shift_comparison', 1, 1),
(3, 'reports_ankal', 1, 1),
(3, 'reports_attendance', 1, 1),
(3, 'reports_blood', 1, 1),
(3, 'reports_codes', 1, 1),
(3, 'reports_crisis', 1, 1),
(3, 'reports_rounds', 1, 1),
(3, 'reports_stats', 1, 1),
(3, 'reports_workflow', 1, 1),
(3, '🔑 امنیت', 1, 1),
(3, '📊 گزارشات', 1, 1),
(4, '🔑 امنیت', 1, 1),
(5, 'manager_reports', 1, 1),
(5, 'manager_shift_edit', 1, 1),
(5, 'manager_shift_review', 1, 1),
(5, 'manager_shifts', 1, 1),
(5, 'matron_checklist', 1, 1),
(5, 'matron_codes', 1, 1),
(5, 'matron_personnel', 1, 1),
(5, 'matron_reports', 1, 1),
(5, 'reports_ankal', 1, 1),
(5, 'reports_attendance', 1, 1),
(5, 'reports_blood', 1, 1),
(5, 'reports_codes', 1, 1),
(5, 'reports_crisis', 1, 1),
(5, 'reports_rounds', 1, 1),
(5, 'reports_stats', 1, 1),
(5, 'reports_workflow', 1, 1),
(5, '🔑 امنیت', 1, 1),
(5, '📊 گزارشات', 1, 1),
(5, '📋 مدیر پرستاری', 1, 1),
(5, '👔 مدیران اجرایی', 1, 1),
(6, 'manager_reports', 1, 1),
(6, 'manager_shift_comparison', 1, 1),
(6, 'manager_shift_edit', 1, 1),
(6, 'manager_shift_review', 1, 1),
(6, 'reports_crisis', 1, 1),
(6, 'reports_rounds', 1, 1),
(6, 'reports_stats', 1, 1),
(6, 'reports_workflow', 1, 1),
(6, '⚙️ ادمین', 1, 1),
(6, '🔑 امنیت', 1, 1),
(6, '📊 گزارشات', 1, 1),
(6, '👔 مدیران اجرایی', 1, 1),
(7, 'reports_ankal', 1, 1),
(7, 'reports_attendance', 1, 1),
(7, 'reports_blood', 1, 1),
(7, 'reports_codes', 1, 1),
(7, 'reports_crisis', 1, 1),
(7, 'reports_rounds', 1, 1),
(7, 'reports_stats', 1, 1),
(7, 'reports_workflow', 1, 1),
(7, '🔑 امنیت', 1, 1),
(7, '📊 گزارشات', 1, 1),
(7, '🛠️ مسئول فنی', 1, 1),
(8, 'reports_ankal', 1, 1),
(8, 'reports_attendance', 1, 1),
(8, 'reports_blood', 1, 1),
(8, 'reports_codes', 1, 1),
(8, 'reports_crisis', 1, 1),
(8, 'reports_rounds', 1, 1),
(8, 'reports_stats', 1, 1),
(8, 'reports_workflow', 1, 1),
(8, '🔑 امنیت', 1, 1),
(8, '🏢 ریاست', 1, 1),
(8, '📊 گزارشات', 1, 1),
(10, 'manager_shifts', 1, 1),
(10, 'matron_personnel', 1, 1),
(10, 'reports_blood', 1, 1),
(10, '🔑 امنیت', 1, 1),
(10, '📊 گزارشات', 1, 1),
(13, 'manager_shifts', 1, 1),
(13, 'reports_blood', 1, 1),
(13, 'reports_codes', 1, 1),
(13, 'reports_crisis', 1, 1),
(13, 'reports_rounds', 1, 1),
(13, 'reports_stats', 1, 1),
(13, 'reports_workflow', 1, 1),
(13, '⚙️ ادمین', 1, 1),
(13, '🔑 امنیت', 1, 1),
(13, '👔 مدیران اجرایی', 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `AccessLevelID` int NOT NULL DEFAULT '0',
  `CreatedDate` datetime DEFAULT NULL,
  `FullName` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '0',
  `PasswordHash` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `postmodir` int DEFAULT '0',
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `profile` longtext CHARACTER SET utf8mb3 COLLATE utf8mb3_bin,
  `pic` varchar(250) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `emza` varchar(250) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `userlevel` int NOT NULL,
  `dep_id` int NOT NULL,
  `emza_path` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `UserID` (`UserID`),
  UNIQUE KEY `Username` (`Username`),
  KEY `AccessLevelsUsers` (`AccessLevelID`),
  KEY `RoleID` (`AccessLevelID`),
  KEY `tbl_nam_modiriatUsers` (`postmodir`),
  KEY `userlevel` (`userlevel`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`AccessLevelID`, `CreatedDate`, `FullName`, `IsActive`, `PasswordHash`, `postmodir`, `UserID`, `Username`, `profile`, `pic`, `emza`, `userlevel`, `dep_id`, `emza_path`) VALUES
(1, '2026-02-28 12:07:22', 'امجد', 1, 'scrypt:32768:8:1$B2bW1i5liqyJvHOn$5513c67a939980764df3bb2d7ffc6beeffa9dd7bd3e41d6f537c5bac417fcbc5f41eda78cc32d4b5be86039e5a80868c81688f6ad31b41a6365cc12fc99b25f5', 36, 1, '2222222222', NULL, NULL, NULL, 0, 34, NULL),
(1, '2026-03-08 14:46:12', 'ایلیا', 1, 'scrypt:32768:8:1$vFtdYTZi039Bpqw1$f7f8bd883bcd3488ff5a666f13730dc5ede72b5c16360a8273284c56e4e4ff0cfba61500cdc72b4286eb320e1ce13440ea8f9339b7deb0aa0c216bed87ea9e51', 26, 34, '1212121212', NULL, NULL, NULL, 0, 30, NULL),
(13, '2026-04-30 09:17:51', 'نوا نوایی', 1, 'scrypt:32768:8:1$wXK8aTSLoqeTa3hO$185528b89e587118ad08748d0dc64a26d08c3e082562f10a92e04ccde131254272223940cfba86dc336fd486d22ae6c00cc2e1efcdc939b38bc58e8ed7f6db17', 45, 35, '5555555555', NULL, NULL, NULL, 0, 30, NULL),
(4, '2026-05-04 17:14:15', 'کاربر تستی', 1, 'scrypt:32768:8:1$Mhw7pZYXPCbX2CIT$ce00676d983480b8ac36186b70b1fcbc018ea25c9fee30e36cba504a1ff2c4dbebf46de700065bd1372004f11618dc976466418a4f07cabf4bc99dca6df4afec', 41, 37, '4', NULL, NULL, NULL, 0, 0, NULL),
(5, '2026-05-11 23:07:32', 'تست مترون', 1, 'scrypt:32768:8:1$iwJ1Dfx63niWrzXR$66400ebb4ae65a27b73813f3673bed908f9f0676453c5e96ace90fc911cc53d530e978f2c7ebaa7b0e0cedb508d57df1f842b9acddf336600b590bf8caa188f9', 29, 38, '8888888888', NULL, NULL, NULL, 0, 0, 'uploads/signatures/sig_8888888888_1781169975.jpg'),
(10, '2026-05-12 12:19:37', 'برای حذف', 1, 'scrypt:32768:8:1$kxqoBbDwgDiz5WAS$39bde6b0e7fec210d4d23542ea9646ecb65b3c8e36c42cb2fb88bb553f17c008bf1d17b2bb41d3980376f6db2a7decde8393dc1ee703d93552f58e524637a085', 31, 39, '3', NULL, NULL, NULL, 0, 33, NULL),
(13, '2026-06-05 11:49:34', 'صدرا صدرایی', 1, 'scrypt:32768:8:1$PiE3f7cH2l9qWaMs$e1804eeae0b624302fff8beb79a8040514489145c90a55271e942026991dfda7b89ca75aca1a4e350c627f28ea360ff1f6918967f5e80645603946b2bbe19a3a', 45, 40, '7777777777', NULL, NULL, NULL, 0, 30, NULL),
(6, '2026-06-08 15:01:59', 'تست کارگزینی', 1, 'scrypt:32768:8:1$hEOwqeICgjLF4Htq$989f9115b211e10f03bc01f90f9885641316f9b06faaecb8d84176c83524194bd3cb74b24527278da0b405e84d4141a958c56863339502ad4f23b4207ace8058', 33, 41, '6666666666', NULL, NULL, NULL, 0, 30, 'uploads/signatures/sig_6666666666_1781536862.png'),
(13, '2026-06-09 13:55:17', 'تست بخش', 1, 'scrypt:32768:8:1$xHAmqTWzRcJYyZTZ$2a6fa5ee89cd31deef2b7ca813df1e86b190a5e937bf1ca51597999d92229575bcfb3b62c7b6c201c9f0851274c5b77556b4dd66df8f11e39873f7c29e651ef5', 43, 42, '9999999999', NULL, NULL, NULL, 0, 34, 'uploads/signatures/sig_9999999999_1781090565.png'),
(1, '2026-06-10 17:12:02', 'جدید امضا', 1, 'scrypt:32768:8:1$chmeTZ0x9uqVQkCC$396612aaffde82ca5fd6b5f4175fc7493e6d53d42526199095a448d8ced1a2bcd13673713cf58908ad76b1b1745dc43821bb0c284b7be4d6d2a435c206627e29', 28, 43, '1231231230', NULL, NULL, NULL, 0, 30, 'uploads/signatures/sig_1231231230_1781098922.jpg'),
(6, '2026-06-11 14:02:49', 'مدیر تستی', 1, 'scrypt:32768:8:1$NJDuq25fJ0I9Bauq$326c21ca1462970ca4ec4079aa5527d8be19580b8fc11efa9bd569609f501d9d646bc00c97c27069bafaf6ca6c2e07f06e9575a8b1dffb4bd4fe9ae6aef931f4', 26, 44, '3333333333', NULL, NULL, NULL, 0, 0, 'uploads/signatures/sig_3333333333_1781533208.png');

-- --------------------------------------------------------

--
-- Table structure for table `user_settings`
--

DROP TABLE IF EXISTS `user_settings`;
CREATE TABLE IF NOT EXISTS `user_settings` (
  `user_id` int NOT NULL,
  `theme` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'light',
  `sidebar_collapsed` tinyint(1) DEFAULT '0',
  `primary_color` varchar(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '#3b82f6',
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_settings2`
--

DROP TABLE IF EXISTS `user_settings2`;
CREATE TABLE IF NOT EXISTS `user_settings2` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `setting_key` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_setting` (`user_id`,`setting_key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_amar_data`
--
ALTER TABLE `tbl_amar_data`
  ADD CONSTRAINT `tbl_amar_data_ibfk_1` FOREIGN KEY (`bakhsh_id`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`),
  ADD CONSTRAINT `tbl_amar_data_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `tbl_amar_items` (`ID_item`),
  ADD CONSTRAINT `tbl_amar_data_ibfk_3` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`);

--
-- Constraints for table `tbl_amliat_kod`
--
ALTER TABLE `tbl_amliat_kod`
  ADD CONSTRAINT `shift_namTtbl_amliat_kod` FOREIGN KEY (`nam_shift`) REFERENCES `shift_namt` (`ID_shift`),
  ADD CONSTRAINT `tbl_bakhshtbl_amliat_kod` FOREIGN KEY (`nam_bakhsh`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`),
  ADD CONSTRAINT `tbl_onvan_kodtbl_amliat_kod` FOREIGN KEY (`onvan_kod`) REFERENCES `tbl_onvan_kod` (`ID_onvan_kod`);

--
-- Constraints for table `tbl_ankal`
--
ALTER TABLE `tbl_ankal`
  ADD CONSTRAINT `shift_namTtbl_ankal` FOREIGN KEY (`nam_shift`) REFERENCES `shift_namt` (`ID_shift`),
  ADD CONSTRAINT `tbl_pezesktbl_ankal` FOREIGN KEY (`nam_pezshk`) REFERENCES `tbl_person` (`ID_person`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `tbl_arziabi_bakhsh`
--
ALTER TABLE `tbl_arziabi_bakhsh`
  ADD CONSTRAINT `shift_namTtbl_arziabi_bakhsh` FOREIGN KEY (`id_shift`) REFERENCES `shift_namt` (`ID_shift`),
  ADD CONSTRAINT `tbl_arziabi_cheklisttbl_arziabi_bakhsh` FOREIGN KEY (`id_ckeklist`) REFERENCES `tbl_arziabi_cheklist` (`ID_cheklist`),
  ADD CONSTRAINT `tbl_arzibi_onvantbl_arziabi_bakhsh` FOREIGN KEY (`id_onvan_arziabi`) REFERENCES `tbl_arzibi_onvan` (`ID_onvan_arziabi`),
  ADD CONSTRAINT `tbl_bakhshtbl_arziabi_bakhsh` FOREIGN KEY (`id_nam_bakhsh`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`);

--
-- Constraints for table `tbl_arziabi_cheklist`
--
ALTER TABLE `tbl_arziabi_cheklist`
  ADD CONSTRAINT `tbl_arzibi_onvantbl_arziabi_cheklist` FOREIGN KEY (`id_onvan_arziabi`) REFERENCES `tbl_arzibi_onvan` (`ID_onvan_arziabi`);

--
-- Constraints for table `tbl_bakhsh_amar_config`
--
ALTER TABLE `tbl_bakhsh_amar_config`
  ADD CONSTRAINT `tbl_bakhsh_amar_config_ibfk_1` FOREIGN KEY (`bakhsh_id`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`),
  ADD CONSTRAINT `tbl_bakhsh_amar_config_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `tbl_amar_items` (`ID_item`);

--
-- Constraints for table `tbl_blood_faravardeh`
--
ALTER TABLE `tbl_blood_faravardeh`
  ADD CONSTRAINT `tbl_blood_transtbl_blood_faravardeh` FOREIGN KEY (`bloodT_key`) REFERENCES `tbl_blood_trans` (`ID_blood`);

--
-- Constraints for table `tbl_blood_trans`
--
ALTER TABLE `tbl_blood_trans`
  ADD CONSTRAINT `shift_namTtbl_blood_trans` FOREIGN KEY (`nam_shift`) REFERENCES `shift_namt` (`ID_shift`),
  ADD CONSTRAINT `tbl_bakhshtbl_blood_trans` FOREIGN KEY (`nam_bakhsh`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`);

--
-- Constraints for table `tbl_chart_bohran`
--
ALTER TABLE `tbl_chart_bohran`
  ADD CONSTRAINT `idnam_nagsh` FOREIGN KEY (`id_nam_nagsh`) REFERENCES `tbl_onvan_naghsh_bohran` (`ID_onvan_naghsh_bohran`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `sathbohran` FOREIGN KEY (`Id_sath_bohran`) REFERENCES `tbl_sath_bohran` (`Id_sath_bohran`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `tbl_onvan_kod_omomytbl_naghsh_bohran` FOREIGN KEY (`nam_bohran`) REFERENCES `tbl_onvan_kod_omomy` (`ID_onvan_kod_o`);

--
-- Constraints for table `tbl_chart_call`
--
ALTER TABLE `tbl_chart_call`
  ADD CONSTRAINT `tblcode_omomy` FOREIGN KEY (`idcode_omomy`) REFERENCES `tbl_kod_omomy` (`ID_kod_omomy`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `tblsath_bohran` FOREIGN KEY (`idsath_bohran`) REFERENCES `tbl_sath_bohran` (`Id_sath_bohran`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `tbl_ghaybat`
--
ALTER TABLE `tbl_ghaybat`
  ADD CONSTRAINT `shift_namTtbl_ghaybat` FOREIGN KEY (`nam_shift`) REFERENCES `shift_namt` (`ID_shift`);

--
-- Constraints for table `tbl_gozaresh`
--
ALTER TABLE `tbl_gozaresh`
  ADD CONSTRAINT `onvan_gozareshtbl_gozaresh` FOREIGN KEY (`onvan_gozaresh`) REFERENCES `tbl_onvan_gozaresh` (`ID_onvan_gozaresh`),
  ADD CONSTRAINT `shift_namTtbl_gozaresh` FOREIGN KEY (`ID_shift`) REFERENCES `shift_namt` (`ID_shift`) ON UPDATE CASCADE,
  ADD CONSTRAINT `tbl_nam_modiriattbl_gozaresh` FOREIGN KEY (`nam_modirit`) REFERENCES `tbl_nam_modiriat` (`ID_nam_modirit`);

--
-- Constraints for table `tbl_gozaresh_modir_parastari`
--
ALTER TABLE `tbl_gozaresh_modir_parastari`
  ADD CONSTRAINT `tbl_gozareshtbl_gozaresh_modir_parastari` FOREIGN KEY (`ID_gozaresh`) REFERENCES `tbl_gozaresh` (`ID_gozaresh`);

--
-- Constraints for table `tbl_hozor`
--
ALTER TABLE `tbl_hozor`
  ADD CONSTRAINT `shift_namTtbl_hozor` FOREIGN KEY (`nam_shift`) REFERENCES `shift_namt` (`ID_shift`),
  ADD CONSTRAINT `tbl_bakhshtbl_hozor` FOREIGN KEY (`nam_bakhsh`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`),
  ADD CONSTRAINT `tbl_persontbl_hozor` FOREIGN KEY (`id_person`) REFERENCES `tbl_person` (`ID_person`);

--
-- Constraints for table `tbl_kod_omomy`
--
ALTER TABLE `tbl_kod_omomy`
  ADD CONSTRAINT `shift_namTtbl_kod_omomy` FOREIGN KEY (`nam_shift`) REFERENCES `shift_namt` (`ID_shift`),
  ADD CONSTRAINT `tbl_onvan_kod_omomytbl_kod_omomy` FOREIGN KEY (`onvan_kod_omomy`) REFERENCES `tbl_onvan_kod_omomy` (`ID_onvan_kod_o`);

--
-- Constraints for table `tbl_kod_omomy_person`
--
ALTER TABLE `tbl_kod_omomy_person`
  ADD CONSTRAINT `tbl_kod_omomytbl_kod_omomy_person` FOREIGN KEY (`id_cod_omomi`) REFERENCES `tbl_kod_omomy` (`ID_kod_omomy`);

--
-- Constraints for table `tbl_naghsh_kod`
--
ALTER TABLE `tbl_naghsh_kod`
  ADD CONSTRAINT `tbl_amliat_kodtbl_naghsh_kod` FOREIGN KEY (`nam_kod`) REFERENCES `tbl_amliat_kod` (`ID_kod`),
  ADD CONSTRAINT `tbl_onvan_naghshtbl_naghsh_kod` FOREIGN KEY (`nam_nagsh`) REFERENCES `tbl_onvan_naghsh` (`ID_onvan_naghsh_kod`),
  ADD CONSTRAINT `tbl_persontbl_naghsh_kod` FOREIGN KEY (`id_person`) REFERENCES `tbl_person` (`ID_person`);

--
-- Constraints for table `tbl_nazar_fanni`
--
ALTER TABLE `tbl_nazar_fanni`
  ADD CONSTRAINT `tbl_gozareshtbl_nazar_fanni` FOREIGN KEY (`kod_gozaresh`) REFERENCES `tbl_gozaresh` (`ID_gozaresh`);

--
-- Constraints for table `tbl_nazar_raiis`
--
ALTER TABLE `tbl_nazar_raiis`
  ADD CONSTRAINT `tbl_gozareshtbl_nazar_raiis` FOREIGN KEY (`kod_gozaresh`) REFERENCES `tbl_gozaresh` (`ID_gozaresh`);

--
-- Constraints for table `tbl_onvan_naghsh`
--
ALTER TABLE `tbl_onvan_naghsh`
  ADD CONSTRAINT `tbl_onvan_kodtbl_onvan_naghsh` FOREIGN KEY (`id_onvan_kod`) REFERENCES `tbl_onvan_kod` (`ID_onvan_kod`);

--
-- Constraints for table `tbl_pasokh_modir_javab`
--
ALTER TABLE `tbl_pasokh_modir_javab`
  ADD CONSTRAINT `tbl_gozareshtbl_pasokh_modir_javab` FOREIGN KEY (`kod_gozaresh`) REFERENCES `tbl_gozaresh` (`ID_gozaresh`);

--
-- Constraints for table `tbl_sazema_person`
--
ALTER TABLE `tbl_sazema_person`
  ADD CONSTRAINT `tbl_bakhshtbl_sazema_person` FOREIGN KEY (`nam_bakhsh`) REFERENCES `tbl_bakhsh` (`ID_nam_bakhsh`),
  ADD CONSTRAINT `tbl_onvan_shoghltbl_sazema_person` FOREIGN KEY (`shoghl`) REFERENCES `tbl_onvan_shoghl` (`ID_shoghl`),
  ADD CONSTRAINT `tbl_persontbl_sazema_person` FOREIGN KEY (`nam_person`) REFERENCES `tbl_person` (`ID_person`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `AccessLevelsUsers` FOREIGN KEY (`AccessLevelID`) REFERENCES `accesslevels` (`AccessLevelID`),
  ADD CONSTRAINT `tbl_nam_modiriatUsers` FOREIGN KEY (`postmodir`) REFERENCES `tbl_nam_modiriat` (`ID_nam_modirit`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
