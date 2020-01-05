CREATE TABLE `yt_video_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appid` int(11) DEFAULT NULL,
  `gameName` varchar(255) DEFAULT NULL,
  `videoId` varchar(45) NOT NULL,
  `videoTitle` varchar(255) DEFAULT NULL,
  `channelId` varchar(45) DEFAULT NULL,
  `description` text,
  `viewCount` int(24) DEFAULT NULL,
  `likeCount` int(11) DEFAULT NULL,
  `dislikeCount` int(11) DEFAULT NULL,
  `favoriteCount` int(11) DEFAULT NULL,
  `commentCount` int(11) DEFAULT NULL,
  `pub_date` datetime DEFAULT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2909 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
