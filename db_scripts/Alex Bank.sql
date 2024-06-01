CREATE TABLE `accounts` (
  `account_id` integer PRIMARY KEY AUTO_INCREMENT,
  `first_name` varchar(255),
  `last_name` varchar(255),
  `email` varchar(255),
  `phone` varchar(15),
  `country_code` char(3),
  `address` text,
  `user_role` char(1),
  `verification` char(1),
  `account_group` varchar(3),
  `created_dt` timestamp
);

CREATE TABLE `user_roles` (
  `role` char(1) PRIMARY KEY,
  `description` varchar(255)
);

CREATE TABLE `verifications` (
  `verification_status` char(1) PRIMARY KEY,
  `description` varchar(255)
);

CREATE TABLE `login_credentials` (
  `account_id` integer PRIMARY KEY,
  `password` varchar(255)
);

CREATE TABLE `login_sessions` (
  `prime_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `account_id` integer,
  `token` varchar(512),
  `create_dt` timestamp
);

CREATE TABLE `currencies` (
  `currency_code` varchar(3) PRIMARY KEY,
  `currency_name` varchar(255)
);

CREATE TABLE `account_worthiness` (
  `prime_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `account_id` integer,
  `version` integer,
  `verification_date` date,
  `verification_user` integer,
  `worthiness` float COMMENT 'from 0 to 100',
  `notes` text,
  `document_proof` integer
);

CREATE TABLE `products` (
  `product_id` integer PRIMARY KEY AUTO_INCREMENT,
  `category_id` varchar(3),
  `name` varchar(255),
  `description` text,
  `terms_and_conditions` text,
  `currency` varchar(3),
  `term` integer COMMENT '(in months)',
  `yield` float,
  `max_amount` float,
  `available_from` datetime,
  `available_till` datetime
);

CREATE TABLE `product_categories` (
  `category_id` varchar(3) PRIMARY KEY,
  `category_name` varchar(255),
  `description` varchar(255)
);

CREATE TABLE `applications` (
  `application_id` integer PRIMARY KEY AUTO_INCREMENT,
  `account_id` integer,
  `product_id` integer,
  `application_dt` timestamp,
  `standard_yn` char(1),
  `amount` float,
  `special_notes` text,
  `collateral` varchar(255),
  `application_certificate` integer,
  `approved_yn` char(1),
  `approval_dt` timestamp
);

CREATE TABLE `product_instance` (
  `product_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `application_id` integer,
  `account_id` integer,
  `approved_by` integer,
  `final_amount` float,
  `final_yield` float,
  `expcted_revenue` float,
  `product_start_date` date,
  `product_end_date` date,
  `special_notes` text,
  `actual_end_date` date,
  `actual_revenue` float
);

CREATE TABLE `documents` (
  `document_id` integer PRIMARY KEY AUTO_INCREMENT,
  `document_name` varchar(255),
  `document_profile` varchar(3)
);

CREATE TABLE `document_profiles` (
  `doc_profile_id` varchar(3) PRIMARY KEY,
  `description` varchar(255),
  `template_name` varchar(255)
);

CREATE TABLE `account_groups` (
  `group_code` varchar(3) PRIMARY KEY,
  `group_name` varchar(255),
  `group_description` varchar(255),
  `default_YN` char(1)
);

CREATE TABLE `worthiness_check_steps` (
  `step_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `account_group_code` varchar(3),
  `version` integer,
  `step_no` integer,
  `step_name` integer,
  `step_description` varchar(255)
);

CREATE TABLE `account_worthiness_notes` (
  `prime_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `aw_record_uid` integer,
  `wc_step_uid` integer,
  `client_note` text,
  `employee_note` text,
  `passed_yn` char(1)
);

CREATE UNIQUE INDEX `worthiness_check_steps_index_0` ON `worthiness_check_steps` (`account_group_code`, `version`, `step_no`);

ALTER TABLE `accounts` ADD FOREIGN KEY (`user_role`) REFERENCES `user_roles` (`role`);

ALTER TABLE `accounts` ADD FOREIGN KEY (`verification`) REFERENCES `verifications` (`verification_status`);

ALTER TABLE `products` ADD FOREIGN KEY (`currency`) REFERENCES `currencies` (`currency_code`);

ALTER TABLE `applications` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `applications` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

ALTER TABLE `documents` ADD FOREIGN KEY (`document_profile`) REFERENCES `document_profiles` (`doc_profile_id`);

ALTER TABLE `product_instance` ADD FOREIGN KEY (`application_id`) REFERENCES `applications` (`application_id`);

ALTER TABLE `product_instance` ADD FOREIGN KEY (`approved_by`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `applications` ADD FOREIGN KEY (`application_certificate`) REFERENCES `documents` (`document_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`category_id`) REFERENCES `product_categories` (`category_id`);

ALTER TABLE `product_instance` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `account_worthiness` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `account_worthiness` ADD FOREIGN KEY (`verification_user`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `account_worthiness` ADD FOREIGN KEY (`document_proof`) REFERENCES `documents` (`document_id`);

ALTER TABLE `login_credentials` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `login_sessions` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `accounts` ADD FOREIGN KEY (`account_group`) REFERENCES `account_groups` (`group_code`);

ALTER TABLE `worthiness_check_steps` ADD FOREIGN KEY (`account_group_code`) REFERENCES `account_groups` (`group_code`);

ALTER TABLE `account_worthiness_notes` ADD FOREIGN KEY (`wc_step_uid`) REFERENCES `worthiness_check_steps` (`step_uid`);

ALTER TABLE `account_worthiness_notes` ADD FOREIGN KEY (`prime_uid`) REFERENCES `account_worthiness` (`prime_uid`);
