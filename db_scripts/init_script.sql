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
alter table `product_instances` AUTO_INCREMENT=300000;

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
    (12, 'EXC', 'Exercise Date', 'Exercise Date', 'Indicates that the current date is an exercise date'),
	(13, 'TRG', 'Exercised', 'Exercise', 'An instrument condition has been triggered'),
	(14, 'DUE', 'Final Exchange Due', 'Final Exchange Due', 'Final exchange is due'),
	(15, 'CMP', 'Complete', 'Complete', 'Complete'),
	(16, 'ORD', 'Overdue', 'Overdue', 'Overdue'),
	(17, 'WOF', 'Written Off', 'Write Off', 'Written Off');

DELIMITER //

-- product status update trigger
CREATE TRIGGER product_instances_status_update
BEFORE UPDATE ON product_instances
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

CREATE TRIGGER after_insert_product_instances
AFTER INSERT ON product_instances
FOR EACH ROW
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE pcc_id INT;
    DECLARE column_name VARCHAR(255);
    DECLARE column_type VARCHAR(255);
    DECLARE default_value VARCHAR(255);

    -- Declare a cursor to select all custom columns for the product_id
    DECLARE custom_column_cursor CURSOR FOR
        SELECT pccd.pcc_id, pccd.column_name, pccd.column_type, pccd.default_value
        FROM product_instances pi
        JOIN applications appl ON appl.application_id = pi.application_id
        JOIN product_custom_column_def pccd ON appl.product_id = pccd.product_id
        WHERE pi.product_uid = NEW.product_uid;

    -- Declare a handler to set 'done' to 1 when the cursor is exhausted
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN custom_column_cursor;

    custom_columns: LOOP
        FETCH custom_column_cursor INTO pcc_id, column_name, column_type, default_value;
        IF done THEN
            LEAVE custom_columns;
        END IF;

        -- Insert a row into product_custom_column_values for each custom column
        CASE 
			WHEN column_type = "integer" THEN 
				INSERT INTO product_custom_column_values (product_uid, pcc_id, int_value)
				VALUES (NEW.product_uid, pcc_id, CAST(default_value AS SIGNED));
			WHEN column_type = "float" THEN 
				INSERT INTO product_custom_column_values (product_uid, pcc_id, float_value)
				VALUES (NEW.product_uid, pcc_id, CAST(default_value AS FLOAT));
			WHEN column_type = "varchar" THEN 
				INSERT INTO product_custom_column_values (product_uid, pcc_id, varchar_value)
				VALUES (NEW.product_uid, pcc_id, default_value);
			WHEN column_type = "text" THEN 
				INSERT INTO product_custom_column_values (product_uid, pcc_id, text_value)
				VALUES (NEW.product_uid, pcc_id, default_value);
			WHEN column_type = "date" THEN 
				INSERT INTO product_custom_column_values (product_uid, pcc_id, date_value)
				VALUES (NEW.product_uid, pcc_id, CAST(default_value AS DATE));
			WHEN column_type = "datetime" THEN 
				INSERT INTO product_custom_column_values (product_uid, pcc_id, datetime_value)
				VALUES (NEW.product_uid, pcc_id, CAST(default_value AS DATETIME));
            ELSE 
				INSERT INTO product_custom_column_values (product_uid, pcc_id)
				VALUES (NEW.product_uid, pcc_id);
        END CASE;
    END LOOP;

    CLOSE custom_column_cursor;
END;

//






