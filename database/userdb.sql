-- Active: 1727284684419@@127.0.0.1@3306@dnd
-- MySQL Workbench Forward Engineering
-- Insert sample data into the User table
INSERT INTO `mydb`.`User` (user_id, user_name, user_surname, user_email, user_password)
VALUES 
(1, 'John', 'Doe', 'john.doe@example.com', 'password123'),
(2, 'Jane', 'Smith', 'jane.smith@example.com', 'password456');

-- Insert sample data into the user_data table
INSERT INTO `mydb`.`user_data` (pid, user_id, pdf_name, pdf_category, pdf_summary)
VALUES 
(1, 1, 'Sample PDF 1', 'Science', 'This is a summary of Sample PDF 1. It covers various scientific topics.'),
(2, 1, 'Sample PDF 2', 'Math', 'This is a summary of Sample PDF 2. It covers various mathematical concepts.'),
(3, 2, 'Sample PDF 3', 'History', 'This is a summary of Sample PDF 3. It covers various historical events.');

use mydb;
ALTER TABLE `user_question` MODIFY COLUMN `question_id` INT NOT NULL AUTO_INCREMENT;

SELECT* FROM user_question;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`User` (
  `user_id` INT NOT NULL auto_increment,
  `user_name` VARCHAR(45) NOT NULL,
  `user_surname` VARCHAR(45) NOT NULL,
  `user_email` VARCHAR(90) NOT NULL,
  `user_password` VARCHAR(200) NOT NULL,
  `user_qid` INT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_email_UNIQUE` (`user_email` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`user_question`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`user_question` (
  `question_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `q_topic` VARCHAR(45) NOT NULL,
  `q_title` LONGTEXT NOT NULL,
  `qA` MEDIUMTEXT NOT NULL,
  `qB` MEDIUMTEXT NOT NULL,
  `qC` MEDIUMTEXT NOT NULL,
  `qD` MEDIUMTEXT NOT NULL,
  `qra` VARCHAR(45) NOT NULL,
  `qua` VARCHAR(45) NOT NULL,
  `qex` TEXT NOT NULL,
  `qdiff` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`question_id`),
  INDEX `fk_Questions_User_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_Questions_User`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`user_data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`user_data` (
  `pid` INT NOT NULL,
  `user_id` INT NOT NULL,
  `pdf_name` VARCHAR(45) NOT NULL,
  `pdf_category` VARCHAR(45) NULL,
  `pdf_summary` LONGTEXT NULL,
  PRIMARY KEY (`pid`),
  INDEX `fk_user_data_User1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_user_data_User1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
