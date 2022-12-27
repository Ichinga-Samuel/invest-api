-- upgrade --
CREATE TABLE IF NOT EXISTS `Users` (
    `user_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `gender` VARCHAR(6) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `created` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `last_login` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `referral_id` VARCHAR(32) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `verified` BOOL NOT NULL  DEFAULT 0,
    UNIQUE KEY `uid_Users_email_1c70a8` (`email`, `name`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `Accounts` (
    `account_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `balance` DOUBLE NOT NULL,
    `user_id` BIGINT NOT NULL UNIQUE,
    CONSTRAINT `fk_Accounts_Users_d58cf2c6` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `Referrals` (
    `ref_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `paid` BOOL NOT NULL,
    `amount` DOUBLE NOT NULL,
    `referrer_id` BIGINT NOT NULL,
    `referred_id` BIGINT NOT NULL UNIQUE,
    CONSTRAINT `fk_Referral_Users_e53b7b7b` FOREIGN KEY (`referrer_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_Referral_Users_f6f75df1` FOREIGN KEY (`referred_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `plans` (
    `name` VARCHAR(256) NOT NULL  PRIMARY KEY,
    `minimum` DOUBLE NOT NULL,
    `maximum` DOUBLE NOT NULL,
    `duration` BIGINT NOT NULL,
    `payout` DOUBLE NOT NULL,
    `referral_bonus` DOUBLE NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `Deposits` (
    `deposit_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `amount` DOUBLE NOT NULL,
    `payment_date` DATETIME(6),
    `due_date` DATETIME(6),
    `settled` BOOL NOT NULL  DEFAULT 0,
    `confirmed` BOOL NOT NULL  DEFAULT 0,
    `amount_due` DOUBLE,
    `account_id` BIGINT NOT NULL,
    `plan_id` VARCHAR(256),
    CONSTRAINT `fk_Deposits_Accounts_f5bb5f87` FOREIGN KEY (`account_id`) REFERENCES `Accounts` (`account_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_Deposits_plans_0781898f` FOREIGN KEY (`plan_id`) REFERENCES `plans` (`name`) ON DELETE SET NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `Withdrawals` (
    `withdrawal_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `amount` DOUBLE NOT NULL,
    `paid` BOOL NOT NULL  DEFAULT 0,
    `withdrawal_date` DATETIME(6),
    `wallet_id` VARCHAR(100) NOT NULL,
    `account_id` BIGINT NOT NULL,
    CONSTRAINT `fk_Withdraw_Accounts_29275310` FOREIGN KEY (`account_id`) REFERENCES `Accounts` (`account_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `admin` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(200) NOT NULL,
    `wallet_id` VARCHAR(64),
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
