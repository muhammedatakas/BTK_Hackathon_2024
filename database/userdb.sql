-- Drop existing database and recreate
DROP DATABASE IF EXISTS mydb;
CREATE DATABASE mydb;
USE mydb;

-- User table
CREATE TABLE IF NOT EXISTS `user` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR(45) NOT NULL,
  `user_surname` VARCHAR(45) NOT NULL,
  `user_email` VARCHAR(90) NOT NULL,
  `user_password` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_email_UNIQUE` (`user_email` ASC)
) ENGINE = InnoDB;

-- PDF Data table
CREATE TABLE IF NOT EXISTS `user_data` (
  `user_id` INT NOT NULL,
  `pdf_name` VARCHAR(255) NOT NULL,
  `pdf_category` VARCHAR(45) NOT NULL,
  `pdf_summary` LONGTEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `pdf_name`),
  CONSTRAINT `fk_user_data_User1`
    FOREIGN KEY (`user_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;


-- Question table
-- Update user_question table structure
CREATE TABLE IF NOT EXISTS `user_question` (
  `question_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `q_topic` VARCHAR(45) NOT NULL,
  `q_title` LONGTEXT NOT NULL,
  `qA` MEDIUMTEXT NOT NULL,
  `qB` MEDIUMTEXT NOT NULL,
  `qC` MEDIUMTEXT NOT NULL,
  `qD` MEDIUMTEXT NOT NULL,
  `qra` VARCHAR(45) NOT NULL,
  `qua` VARCHAR(45) NULL,
  `qex` TEXT NOT NULL,
  `qdiff` VARCHAR(45) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `topic_mastery` FLOAT DEFAULT 0.0,
  PRIMARY KEY (`question_id`),
  INDEX `fk_Questions_User_idx` (`user_id` ASC),
  CONSTRAINT `fk_Questions_User`
    FOREIGN KEY (`user_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;

-- Add indexes for better performance
ALTER TABLE `user_question` ADD INDEX `idx_user_topic` (`user_id`, `q_topic`);
ALTER TABLE `user_data` ADD INDEX `idx_user_category` (`user_id`, `pdf_category`);

-- Set character set
ALTER DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE User CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE user_data CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE user_question CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;