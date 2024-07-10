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
	('FTC', 'First-Time Client', 'Regular first-time client', 'Y'),
    ('FTP', 'First-Time Partner', 'Credible first-time client', 'N'),
    ('RTC', 'Returning Client', 'Client with at least one completed product', 'N'),
    ('LTP', 'Long Term Partner', 'Long term partner of Alex Bank or affiliated entities', 'N'), 
    ('EMP', 'Employee', 'Code for any employee, inlcuding admins, C-suite, and regular employees', 'N');

-- API userl; does not have credentials, i.e., cannot login with it
insert into `accounts` (`account_id`, `first_name`, `last_name`, `country_code`, `user_role`, `verification`, `account_group`)
values (0, 'Automated', 'Action', 'BGR', 'A', 'Y', 'EMP');

-- user increment starting value
alter table `accounts` AUTO_INCREMENT=2000000;

-- product instance increment starting value
alter table `product_instance` AUTO_INCREMENT=300000;

-- default admin user
insert into `accounts` (`first_name`, `last_name`, `country_code`, `user_role`, `verification`, `account_group`)
values ('Admin', 'Admin', 'BGR', 'A', 'Y', 'EMP');

-- default admin user firstpass 
insert into `login_credentials` (`account_id`, `password`) 
values (2000000, 'qwerty');

-- document profiles 
insert into `document_profiles` (`doc_profile_id`, `description`)
values 
	('CON', 'Contract'), 
    ('AWP', 'Account Worthiness Proof');

-- product statuses
INSERT INTO product_statuses (order_no, code, status_name, call_to_action, status_description) VALUES
	(1, 'APL', 'Applied', NULL, 'Application submitted'),
	(2, 'REV', 'Reviewed', 'Review', 'Application is under review'),
    (3, 'AGR', 'Agreed', 'Agree', 'The client agrees to the change proposed by the employee'), 
    (4, 'DIS', 'Disagreed', 'Disagree', 'The client does not agree with the change proposed by the employee'),
	(5, 'CNL', 'Cancelled', 'Cancel', 'The application or the exchange of the underlying was cancelled'),
	(6, 'AMD', 'Amended', 'Amend', 'An employee made a change, and the client has to agree to it'),
	(7, 'APR', 'Approved', 'Approve', 'Application is approved'),
	(8, 'DEN', 'Denied', 'Deny', 'Application is denied'),
	(9, 'SGN', 'Sent for Signing', 'Send for Signing', 'Contract has been sent for signing'),
	(10, 'AWT', 'Awaiting Disbursement Date', 'Sign', 'Awaiting Begin Date'),
	(11, 'NOR', 'Current', 'Disbursed', 'Exchange of the underlying occurred and the end date is not reached yet'),
	(12, 'TRG', 'Triggered', 'Trigger', 'An instrument condition has been triggered'),
	(13, 'DUE', 'Final Exchange Due', 'Final Exchange Due', 'Final exchange is due'),
	(14, 'CMP', 'Complete', 'Complete', 'Complete'),
	(15, 'ORD', 'Overdue', 'Overdue', 'Overdue'),
	(16, 'WOF', 'Written Off', 'Write Off', 'Written Off');

DELIMITER //

-- product status update trigger
CREATE TRIGGER product_instance_status_update
BEFORE UPDATE ON product_instance
FOR EACH ROW
BEGIN
  IF NEW.status_code != OLD.status_code THEN
    INSERT INTO product_status_updates (product_uid, was_status, is_code, update_dt, update_user, update_note, update_note_public_yn)
    VALUES (
		OLD.product_uid, 
        OLD.status_code, 
        NEW.status_code, 
        NOW(), 
        NEW.latest_update_user_id,
        CASE WHEN OLD.latest_note != NEW.latest_note THEN NEW.latest_note ELSE NULL END,
        CASE WHEN OLD.latest_note != NEW.latest_note THEN NEW.latest_note_public_yn ELSE NULL END
    );
  END IF;
END;  
//





