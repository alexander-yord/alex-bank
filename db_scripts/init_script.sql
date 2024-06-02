-- currencies 
insert into `currencies` (`currency_code`, `currency_name`) 
values 
	('BGN', 'Bulgarian Lev'), 
    ('EUR', 'Euro'), 
    ('USD', 'United States Dollar');
 
-- user roles 
insert into `user_roles` (`role`, `description`) 
values 
	('A', 'Administrator'),
    ('C', 'C-level Executive'),
    ('E', 'Employee'),
    ('U', 'User');
    
-- verifications 
insert into `verifications` (`verification_status`, `description`)
values 
	('Y', 'Verified'), 
    ('N', 'Uverified'), 
    ('R', 'Revoked Verification'), 
    ('C', 'Contacted for Verification');

-- account groups 
insert into `account_groups` (`group_code`, `group_name`, `group_description`, `default_YN`)
values 
	('FTC', 'Regular Client', 'Regular first time client', 'Y'), 
    ('LTP', 'Long Term Partner', 'Long term partner of Alex Bank or affiliated entities', 'N'), 
    ('EMP', 'Employee', 'Code for any employee, inlcuding admins, C-suite, and regular employees', 'N');

-- user increment starting value
alter table `accounts` AUTO_INCREMENT=2000000;

-- default user
insert into `accounts` (`first_name`, `last_name`, `country_code`, `user_role`, `verification`, `account_group`)
values ('Admin', 'Admin', 'BGR', 'A', 'Y', 'EMP');

-- default user firstpass 
insert into `login_credentials` (`account_id`, `password`) 
values (2000000, 'qwerty');

-- document profiles 
insert into `document_profiles` (`doc_profile_id`, `description`)
values 
	('APP', 'Application Certificate'), 
    ('APR', 'Account Proof');
    
-- product category 'Loans'
insert into `product_categories` (`category_id`, `category_name`, `description`)
values 
	('LON', 'Loan', 'Loans in which Alex Bank Lends Money Out to the Loan Applicant');

-- products Small and Medium Short-Term BGN Loans
insert into `products` (`category_id`, `name`, `description`, `terms_and_conditions`, 
`currency`, `term`, `yield`, `max_amount`, `available_from`, `available_till`)
values 
	('LON', 'Small 1-Month Loan',  'Loan of less than BGN 100 with term of 1 month', NULL, 'BGN', 1, 0.0000, 100.0, '2024-05-25', NULL), 
	('LON', 'Small 3-Month Loan',  'Loan of less than BGN 100 with term of 3 month', NULL, 'BGN', 1, 0.0100, 100.0, '2024-05-25', NULL), 
    ('LON', 'Medium 1-Month Loan', 'Loan of less than BGN 500 with term of 1 month', NULL, 'BGN', 1, 0.0100, 500.0, '2024-05-25', NULL), 
    ('LON', 'Medium 1-Month Loan', 'Loan of less than BGN 500 with term of 3 month', NULL, 'BGN', 1, 0.0200, 500.0, '2024-05-25', NULL);





