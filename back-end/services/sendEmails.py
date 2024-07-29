import sys
import os
import logging
import configparser

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dependencies import database as db, mail as m


try:
    # Initialize ConfigParser
    cfile = configparser.ConfigParser()

    # Construct the path to the config.ini file in the parent directory
    config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))

    # Read the config file
    cfile.read(config_file_path)

    # Access the SERVICE_LOG key from the LOG section
    log_file_name = cfile["LOG"]["SERVICE_LOG"]

    # Configure logging
    logging.basicConfig(filename=log_file_name, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
except FileNotFoundError as err:
    log_file_name = None
    print(f"Config file not found: {err}")
except KeyError as err:
    log_file_name = None
    print(f"Configuration key error: {err}")
except Exception:
    print("Could not configure logging")


def send_due_emails():
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "SELECT product_uid FROM product_instances " \
           "WHERE (DATE(product_end_date) = DATE(NOW()) AND status_code = 'DUE') OR status_code = 'EXC'"

    db.cursor.execute(stmt)
    if db.cursor.rowcount == 0:
        logging.info(f"No DUE or EXC products today to send an email to.")
        return

    products = db.cursor.fetchall()[:][0]

    logging.info("Starting to send Due and Exercise Day Emails")
    for product in products:
        m.send_due_emails(product)
        logging.info(f"Email sent for Product UID: {product}")

    logging.info(f"Sending Due/Exercise Date Emails successfully completed. {len(products)} emails sent")


def send_overdue_emails():
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "SELECT product_uid FROM product_instances WHERE status_code = 'ORD'"

    db.cursor.execute(stmt)
    if db.cursor.rowcount == 0:
        logging.info(f"No Overdue products today to send an email to.")
        return

    products = db.cursor.fetchall()[:][0]

    logging.info("Starting to send Overdue Emails")
    for product in products:
        m.send_overdue_emails(product)
        logging.debug(f"Email sent for Product UID: {product}")

    logging.info(f"Sending Overdue Emails successfully completed. {len(products)} emails sent")


if __name__ == "__main__":
    send_due_emails()
    send_overdue_emails()

