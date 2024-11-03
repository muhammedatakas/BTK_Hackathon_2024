-- MySQL Script generated by MySQL Workbench
-- Sun Nov  3 12:14:08 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`user` (
  `user_id`  NOT NULL,
  `user_name` VARCHAR(45) NOT NULL,
  `user_surname` VARCHAR(45) NOT NULL,
  `user_email` VARCHAR(90) NOT NULL,
  `user_password` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_email_UNIQUE` (`user_email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


-- -----------------------------------------------------
-- Table `mydb`.`user_data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`user_data` (
  `user_id`  NOT NULL,
  `pdf_name` VARCHAR(255) NOT NULL,
  `pdf_category` VARCHAR(45) NOT NULL,
  `pdf_summary` LONGTEXT NOT NULL,
  `created_at`  NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `pdf_name`),
  INDEX `idx_user_category` (`user_id` ASC, `pdf_category` ASC) VISIBLE,
  CONSTRAINT `fk_user_data_User1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`user` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


-- -----------------------------------------------------
-- Table `mydb`.`user_question`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`user_question` (
  `question_id`  NOT NULL,
  `user_id`  NOT NULL,
  `q_topic` VARCHAR(45) NOT NULL,
  `q_title` LONGTEXT NOT NULL,
  `qA`  NOT NULL,
  `qB`  NOT NULL,
  `qC`  NOT NULL,
  `qD`  NOT NULL,
  `qra` VARCHAR(45) NOT NULL,
  `qua` VARCHAR(45) NULL DEFAULT NULL,
  `qex` TEXT NOT NULL,
  `qdiff` VARCHAR(45) NOT NULL,
  `created_at`  NULL DEFAULT CURRENT_TIMESTAMP,
  `topic_mastery` FLOAT NULL DEFAULT '0',
  PRIMARY KEY (`question_id`),
  INDEX `fk_Questions_User_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_Questions_User`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`user` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 31
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
