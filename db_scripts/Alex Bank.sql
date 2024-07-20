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
  `created_dt` timestamp DEFAULT (now())
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
  `subcategory_id` integer,
  `name` varchar(255),
  `description` text,
  `terms_and_conditions` text,
  `currency` varchar(3),
  `term` integer COMMENT '(in months)',
  `percentage` float,
  `monetary_amount` float,
  `percentage_label` varchar(255),
  `mon_amt_label` varchar(255),
  `available_from` datetime,
  `available_till` datetime,
  `picture_name` varchar(255)
);

CREATE TABLE `product_categories` (
  `category_id` varchar(3) PRIMARY KEY,
  `category_name` varchar(255),
  `description` varchar(255)
);

CREATE TABLE `product_subcategories` (
  `subcategory_id` integer PRIMARY KEY AUTO_INCREMENT,
  `category_id` varchar(3),
  `subcategory_name` varchar(255),
  `subcategory_description` varchar(255)
);

CREATE TABLE `product_custom_column_def` (
  `pcc_id` integer PRIMARY KEY AUTO_INCREMENT,
  `product_id` integer NOT NULL,
  `column_name` varchar(255),
  `customer_visible_yn` char(1),
  `customer_populatable_yn` char(1),
  `column_type` ENUM ('integer', 'float', 'char', 'varchar', 'text', 'date', 'datetime'),
  `default_value` varchar(255),
  `exercise_date_yn` char(1)
);

CREATE TABLE `product_custom_column_values` (
  `pcc_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `pcc_id` integer,
  `product_uid` integer,
  `int_value` integer,
  `float_value` float,
  `varchar_value` varchar(255),
  `text_value` text,
  `date_value` date,
  `datetime_value` datetime
);

CREATE TABLE `applications` (
  `application_id` integer PRIMARY KEY AUTO_INCREMENT,
  `account_id` integer,
  `product_id` integer,
  `application_dt` timestamp DEFAULT (now()),
  `standard_yn` char(1),
  `amount_requested` float,
  `special_notes` text,
  `collateral` varchar(255),
  `approved_yn` char(1),
  `approved_by` integer,
  `approval_dt` timestamp,
  `lead_status` varchar(3),
  `lead_probability` float,
  `visible_yn` char(1)
);

CREATE TABLE `product_instances` (
  `product_uid` integer PRIMARY KEY AUTO_INCREMENT,
  `application_id` integer NOT NULL,
  `account_id` integer,
  `amount` float,
  `yield` float,
  `status_code` varchar(3),
  `contract_id` integer,
  `expected_revenue` float,
  `product_start_date` date,
  `product_end_date` date,
  `special_notes` text,
  `actual_end_date` date,
  `actual_revenue` float,
  `latest_update_user_id` integer,
  `latest_note` text,
  `latest_note_public_yn` char(1),
  `notifications_yn` char(1) DEFAULT 'Y'
);

CREATE TABLE `lead_statuses` (
  `order_no` integer,
  `code` varchar(3) PRIMARY KEY,
  `status_name` varchar(255),
  `status_description` varchar(255)
);

CREATE TABLE `product_statuses` (
  `order_no` integer,
  `code` varchar(3) PRIMARY KEY,
  `status_name` varchar(255),
  `call_to_action` varchar(255),
  `status_description` varchar(255)
);

CREATE TABLE `product_status_updates` (
  `product_uid` integer,
  `was_status` varchar(3),
  `is_code` varchar(3),
  `update_dt` timestamp DEFAULT (now()),
  `update_user` int,
  `update_note` text,
  `update_note_public_yn` char(1)
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

CREATE TABLE `contracts` (
  `contract_id` integer PRIMARY KEY AUTO_INCREMENT,
  `contract_title` varchar(255),
  `unsigned_contract` text,
  `amended_contract` text,
  `signature_date` date,
  `signed_contract` text,
  `document_id` integer
);

CREATE UNIQUE INDEX `worthiness_check_steps_index_0` ON `worthiness_check_steps` (`account_group_code`, `version`, `step_no`);

ALTER TABLE `accounts` ADD FOREIGN KEY (`user_role`) REFERENCES `user_roles` (`role`);

ALTER TABLE `accounts` ADD FOREIGN KEY (`verification`) REFERENCES `verifications` (`verification_status`);

ALTER TABLE `products` ADD FOREIGN KEY (`currency`) REFERENCES `currencies` (`currency_code`);

ALTER TABLE `applications` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `applications` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

ALTER TABLE `documents` ADD FOREIGN KEY (`document_profile`) REFERENCES `document_profiles` (`doc_profile_id`);

ALTER TABLE `product_instances` ADD FOREIGN KEY (`application_id`) REFERENCES `applications` (`application_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`category_id`) REFERENCES `product_categories` (`category_id`);

ALTER TABLE `product_instances` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `account_worthiness` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `account_worthiness` ADD FOREIGN KEY (`verification_user`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `account_worthiness` ADD FOREIGN KEY (`document_proof`) REFERENCES `documents` (`document_id`);

ALTER TABLE `login_credentials` ADD FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `accounts` ADD FOREIGN KEY (`account_group`) REFERENCES `account_groups` (`group_code`);

ALTER TABLE `worthiness_check_steps` ADD FOREIGN KEY (`account_group_code`) REFERENCES `account_groups` (`group_code`);

ALTER TABLE `account_worthiness_notes` ADD FOREIGN KEY (`wc_step_uid`) REFERENCES `worthiness_check_steps` (`step_uid`);

ALTER TABLE `account_worthiness_notes` ADD FOREIGN KEY (`prime_uid`) REFERENCES `account_worthiness` (`prime_uid`);

ALTER TABLE `product_instances` ADD FOREIGN KEY (`status_code`) REFERENCES `product_statuses` (`code`);

ALTER TABLE `product_status_updates` ADD FOREIGN KEY (`product_uid`) REFERENCES `product_instances` (`product_uid`);

ALTER TABLE `product_status_updates` ADD FOREIGN KEY (`was_status`) REFERENCES `product_statuses` (`code`);

ALTER TABLE `product_status_updates` ADD FOREIGN KEY (`is_code`) REFERENCES `product_statuses` (`code`);

ALTER TABLE `applications` ADD FOREIGN KEY (`approved_by`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `product_instances` ADD FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`contract_id`);

ALTER TABLE `contracts` ADD FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`);

ALTER TABLE `product_instances` ADD FOREIGN KEY (`latest_update_user_id`) REFERENCES `accounts` (`account_id`);

ALTER TABLE `product_subcategories` ADD FOREIGN KEY (`category_id`) REFERENCES `product_categories` (`category_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`subcategory_id`) REFERENCES `product_subcategories` (`subcategory_id`);

ALTER TABLE `product_custom_column_def` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

ALTER TABLE `product_custom_column_values` ADD FOREIGN KEY (`pcc_id`) REFERENCES `product_custom_column_def` (`pcc_id`);

ALTER TABLE `product_custom_column_values` ADD FOREIGN KEY (`product_uid`) REFERENCES `product_instances` (`product_uid`);

ALTER TABLE `applications` ADD FOREIGN KEY (`lead_status`) REFERENCES `lead_statuses` (`code`);
