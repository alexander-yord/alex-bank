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

-- API user; does not have credentials, i.e., cannot login with it
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
	(10, 'APL', 'Applied', NULL, 'Application submitted'),
	(20, 'REV', 'Reviewed', 'Review', 'Application is under review'),
    (21, 'AGR', 'Agreed', 'Agree', 'The client agrees to the change proposed by the employee'), 
    (22, 'DIS', 'Disagreed', 'Disagree', 'The client does not agree with the change proposed by the employee'),
	(101, 'CNL', 'Cancelled', 'Cancel', 'The application or the exchange of the underlying was cancelled'),
	(23, 'AMD', 'Amended', 'Amend', 'An employee made a change, and the client has to agree to it'),
	(30, 'APR', 'Approved', 'Approve', 'Application is approved'),
	(102, 'DEN', 'Denied', 'Deny', 'Application is denied'),
	(35, 'SGN', 'Sent for Signing', 'Send for Signing', 'Contract has been sent for signing'),
	(40, 'AWT', 'Awaiting Disbursement Date', 'Sign', 'Awaiting Begin Date'),
	(50, 'NOR', 'Current', 'Disbursed', 'Exchange of the underlying occurred and the end date is not reached yet'),
    (60, 'EXC', 'Exercise Date', 'Exercise Date', 'Indicates that the current date is an exercise date'),
	(65, 'TRG', 'Exercised', 'Exercise', 'An instrument condition has been triggered'),
	(70, 'DUE', 'Final Exchange Due', 'Final Exchange Due', 'Final exchange is due'),
	(100, 'CMP', 'Complete', 'Complete', 'Complete'),
	(80, 'ORD', 'Overdue', 'Overdue', 'Overdue'),
	(103, 'WOF', 'Written Off', 'Write Off', 'Written Off');

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

CREATE FUNCTION copy_product_custom_column_def(input_product_id INTEGER)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE inserted_count INT DEFAULT 0;

    -- Insert the data into the product_custom_column_def table
    INSERT INTO product_custom_column_def (product_id, column_name, customer_visible_yn, 
                                           customer_populatable_yn, column_type, default_value, 
                                           exercise_date_yn, available_before)
    SELECT 
        draft.product_id,
        draft.column_name,
        draft.customer_visible_yn,
        draft.customer_populatable_yn,
        draft.column_type,
        draft.default_value,
        draft.exercise_date_yn,
        draft.available_before
    FROM 
        draft_product_custom_column_def draft
    WHERE 
        draft.product_id = input_product_id
    ORDER BY 
        draft.order_no;

    -- Get the number of rows inserted
    SET inserted_count = ROW_COUNT();

    RETURN inserted_count;
END 
//

CREATE FUNCTION clone_product_and_custom_columns(p_product_id INT, p_account_id INT)
RETURNS INT
BEGIN
    DECLARE v_new_product_id INT;

    -- Insert the new product into the products table
    INSERT INTO products (
        category_id,
        subcategory_id,
        name,
        description,
        terms_and_conditions,
        currency,
        term,
        percentage,
        monetary_amount,
        percentage_label,
        mon_amt_label,
        available_from,
        available_till,
        picture_name,
        draft_yn,
        draft_owner
    )
    SELECT 
        category_id,
        subcategory_id,
        name,
        description,
        terms_and_conditions,
        currency,
        term,
        percentage,
        monetary_amount,
        percentage_label,
        mon_amt_label,
        NULL,
        NULL,
        picture_name,
        'Y',                  -- Set draft_yn to 'Y' for the new product
        p_account_id          -- Set the draft_owner to the passed account_id
    FROM products
    WHERE product_id = p_product_id;

    -- Get the new product_id
    SET v_new_product_id = LAST_INSERT_ID();

    -- Insert the custom column definitions into the draft_product_custom_column_def table
    INSERT INTO draft_product_custom_column_def (
        product_id,
        order_no,
        column_name,
        customer_visible_yn,
        customer_populatable_yn,
        column_type,
        default_value,
        exercise_date_yn,
        available_before
    )
    SELECT
        v_new_product_id,                -- New product_id
        @order_no := @order_no + 1,      -- Incremented order_no using a user variable
        column_name,
        customer_visible_yn,
        customer_populatable_yn,
        column_type,
        default_value,
        exercise_date_yn,
        available_before
    FROM product_custom_column_def
    CROSS JOIN (SELECT @order_no := 0) AS var_init   -- Initialize the order_no variable
    WHERE product_id = p_product_id
    ORDER BY pcc_id; -- Assuming you want to maintain the original order

    -- Return the new product_id
    RETURN v_new_product_id;
END

//


