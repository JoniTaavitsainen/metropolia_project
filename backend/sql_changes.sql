-- these are all the changes after original flightgame sql dump.


-- first sql changes
delete from goal_reached;
delete from game;

ALTER TABLE `goal_reached`
  DROP FOREIGN KEY `goal_reached_ibfk_1`;

ALTER TABLE `game`
  MODIFY `id` int NOT NULL AUTO_INCREMENT,
  MODIFY `screen_name` varchar(40) NOT NULL,
  ADD `password` varchar(255) NOT NULL AFTER `screen_name`,
  ADD UNIQUE KEY `screen_name` (`screen_name`);

ALTER TABLE `goal_reached`
  MODIFY `game_id` int NOT NULL;

ALTER TABLE `goal_reached`
  ADD CONSTRAINT `goal_reached_ibfk_1`
  FOREIGN KEY (`game_id`) REFERENCES `game` (`id`);

-- --

-- second sql changes 
-- jos oli jo käyttäjä joutuu tekee uuden näiden jälkeen.

ALTER TABLE `game`
  DROP COLUMN `password`,
  DROP COLUMN `screen_name`;

CREATE TABLE `account` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `screen_name` VARCHAR(40) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `screen_name` (`screen_name`)
);

delete from game;

ALTER TABLE `game`
  ADD COLUMN `account_id` INT NOT NULL AFTER `id`,
  ADD CONSTRAINT `game_account_id_fk`
  FOREIGN KEY (`account_id`) REFERENCES `account` (`id`);

alter table game
  ADD COLUMN `last_played` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `account_id`,
  modify column `co2_budget` int(8) not null default "5",
  modify column `location` varchar(10) not null default "EFHK";



--

--third sql changes

alter table `account`
  add column `win` INT UNSIGNED NOT NULL DEFAULT 0,
  add column `loss` INT UNSIGNED NOT NULL DEFAULT 0;


ALTER TABLE `game`
  add column `wincon` varchar(10),
  drop column `co2_consumed`,
  drop column `co2_budget`;

CREATE TABLE `visited_locations` (
  `game_id` int(11) NOT NULL,
  `icao` varchar(10) NOT NULL,
  `location_name` varchar(100) NOT NULL,
  `event_type` varchar(10) NOT NULL,
  `finished` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`game_id`,`icao`,`location_name`),
  CONSTRAINT `visited_locations_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `game` (`id`) ON DELETE CASCADE
);

CREATE TABLE `inventory` (
  `game_id` int(11) NOT NULL,
  `item_type` varchar(20) NOT NULL,
  `item_key` varchar(100) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `item_description` text NOT NULL,
  `icon` varchar(40) NOT NULL,
  `quantity` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`game_id`, `item_key`),
  CONSTRAINT `inventory_game_id_fk`
    FOREIGN KEY (`game_id`) REFERENCES `game` (`id`) ON DELETE CASCADE
);

DROP TABLE `goal_reached`;
DROP TABLE `goal`;

ALTER TABLE `airport`
  DROP FOREIGN KEY `airport_ibfk_1`;

ALTER TABLE `airport`
  ADD CONSTRAINT `airport_ibfk_1`
  FOREIGN KEY (`iso_country`) REFERENCES `country` (`iso_country`)
  ON DELETE CASCADE;

ALTER TABLE `game`
  DROP FOREIGN KEY `game_account_id_fk`;

ALTER TABLE `game`
  ADD CONSTRAINT `game_account_id_fk`
  FOREIGN KEY (`account_id`) REFERENCES `account` (`id`)
  ON DELETE CASCADE;

ALTER TABLE `game`
  DROP FOREIGN KEY `game_ibfk_1`;

ALTER TABLE `game`
  ADD CONSTRAINT `game_ibfk_1`
  FOREIGN KEY (`location`) REFERENCES `airport` (`ident`)
  ON DELETE CASCADE;

ALTER TABLE `account`
  ADD COLUMN `win` INT UNSIGNED NOT NULL DEFAULT 0,
  ADD COLUMN `loss` INT UNSIGNED NOT NULL DEFAULT 0;


-- --