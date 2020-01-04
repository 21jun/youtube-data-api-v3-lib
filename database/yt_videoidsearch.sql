CREATE TABLE `yt_videoidsearch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `query` varchar(255) NOT NULL,
  `videoId` varchar(45) NOT NULL,
  `videoTitle` varchar(255) DEFAULT NULL,
  `channelId` varchar(45) DEFAULT NULL,
  `channelTitle` varchar(255) DEFAULT NULL,
  `description` text,
  `pub_date` datetime DEFAULT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
