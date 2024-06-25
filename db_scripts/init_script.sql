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
    ('N', 'Unverified'), 
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

-- product instance increment starting value
alter table `product_instance` AUTO_INCREMENT=300000;

-- default user
insert into `accounts` (`first_name`, `last_name`, `country_code`, `user_role`, `verification`, `account_group`)
values ('Admin', 'Admin', 'BGR', 'A', 'Y', 'EMP');

-- default user firstpass 
insert into `login_credentials` (`account_id`, `password`) 
values (2000000, 'qwerty');

-- Ensure the Event Scheduler is enabled
SET GLOBAL event_scheduler = ON;

-- Create the event to delete old login sessions
CREATE EVENT IF NOT EXISTS delete_old_login_sessions
ON SCHEDULE EVERY 1 HOUR
DO
  DELETE FROM login_sessions
  WHERE create_dt < NOW() - INTERVAL 2 HOUR;

-- document profiles 
insert into `document_profiles` (`doc_profile_id`, `description`)
values 
	('CON', 'Contract'), 
    ('AWP', 'Account Worthiness Proof');

-- product statuses
INSERT INTO product_statuses (code, status_name, call_to_action, status_description) VALUES
	('APL', 'Applied', NULL, 'Application submitted'),
	('REV', 'Reviewed', 'Review', 'Application is under review'),
	('APR', 'Approved', 'Approve', 'Application is approved'),
	('DEN', 'Denied', 'Deny', 'Application is denied'),
	('CNL', 'Cancelled', 'Cancel', 'The application or the exchange of the underlying was cancelled'),
	('AMD', 'Amended', 'Amend', 'An employee made a change, and the client has to agree to it'),
	('SGN', 'Sent for Signing', 'Send for Signing', 'Contract has been sent for signing'),
	('AWT', 'Awaiting Disbursement Date', 'Await Disbursement Date', 'Awaiting Begin Date'),
	('NOR', 'Current', 'Disbursed', 'Exchange of the underlying occurred and the end date is not reached yet'),
	('TRG', 'Triggered', 'Trigger', 'An instrument condition has been triggered'),
	('DUE', 'Final Exchange Due', 'Final Exchange Due', 'Final exchange is due'),
	('CMP', 'Complete', 'Complete', 'Complete'),
	('ORD', 'Overdue', 'Overdue', 'Overdue'),
	('WOF', 'Written Off', 'Write Off', 'Written Off');

    
-- product category 'Loans'
insert into `product_categories` (`category_id`, `category_name`, `description`)
values 
	('LON', 'Loan', 'Loans are agreements in which Alex Bank lends money out to the loan applicant in exchange for an interest.'), 
    ('PEQ', 'Private Equity Offerring', 'Private Equity Offerings involve the sale of private equity, facilitated by Alex Bank.'), 
    ('DER', 'Exotic Derivatives', 'Instruments whose price depends on the performance of some underlying asset or condition.');
 
 
DELIMITER //

-- product status update trigger
CREATE TRIGGER before_product_instance_update
BEFORE UPDATE ON product_instance
FOR EACH ROW
BEGIN
  IF NEW.status_code != OLD.status_code THEN
    INSERT INTO product_status_updates (product_uid, was_status, is_code, update_dt)
    VALUES (OLD.product_uid, OLD.status_code, NEW.status_code, NOW());
  END IF;
END;  
//

-- Create the event to update product instance status to DUE
CREATE EVENT IF NOT EXISTS update_product_instance_status
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 1 MINUTE
DO
BEGIN
    UPDATE product_instance
    SET status_code = 'DUE'
    WHERE product_end_date = CURDATE()
    AND status_code IN ('NOR', 'TRG');
END;
//

-- Create the event to update product instance status to ORD 7 days after it was DUE
CREATE EVENT IF NOT EXISTS update_due_to_ord_status
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 1 MINUTE
DO
BEGIN
    UPDATE product_instance
    SET status_code = 'ORD'
    WHERE status_code = 'DUE'
    AND CURDATE() = DATE_ADD(product_end_date, INTERVAL 7 DAY);
END;
//

DELIMITER ;




