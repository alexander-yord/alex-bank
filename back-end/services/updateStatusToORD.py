import sys
import os
import logging
import configparser

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dependencies import database as db


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


def update_status_to_due():
    if not db.cnx.is_connected():
        db.cnx, db.cursor = db.connect()

    stmt = "UPDATE product_instances SET status_code='ORD', latest_update_user_id=1, latest_note=NULL " \
           "WHERE DATE(product_end_date) = DATE(DATE_ADD(NOW(), INTERVAL 7 DAY)) and status_code = 'DUE'"

    try:
        db.cursor.execute(stmt)
        db.cnx.commit()
        rows_updated = db.cursor.rowcount
        logging.info(f"Status updated to 'ORD' for {rows_updated} product(s) with today's end date.")
    except Exception as e:
        logging.error(f"Failed to update status: {e}")

    return


if __name__ == "__main__":
    update_status_to_due()
