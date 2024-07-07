# Alex Bank
Alex Bank is a forward-thinking private bank project, dedicated to providing tailored financial services that cater to a diverse range of clients. At Alex Bank, we believe that everyone deserves access to high-quality financial products, which is why we specialize in offering Over-the-Counter (OTC) services of small value, making sophisticated financial instruments available to a broader audience. For more info, visit [alex-bank.com](https://alex-bank.com).

This repository is "split" in three folders:
```plaintext
alex-bank/
├── back-end
├── db_scripts
├── front-end
└── README.md
```

## Database 
Alex Bank uses a MySQL database. Once you have a local instance installed, run: 
```sql
CREATE DATABASE alex_bank;
USE alex_bank;
```
Then, run each of the SQL scripts found in `db_scripts` in this order:
1. `Alex Bank.sql` -- this will create all tables, indeces, and foreign relations in the alex_bank schema. 
2. `init_script.sql` -- this will load some basic configuration into the database, such as currencies, the initial user roles and groups, and will create an Admin account. 
3. `product_config.sql` -- this will create four initial products, of type Loan (LON)

## Back-End 
#### Dependencies 
The `back-end` folder contains the FastAPI back-end. To set it up, 
```sh
cd back-end
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt 
```

#### Credentials
In the `back-end` folder, you will need to create a file, called `config.ini`. Then, you will have to put your information in it: 
```
[DATABASE]
DB_HOST = 
DB_USER = 
DB_PASS = 
DB_NAME = alex_bank

[SMTP]
MAIL_USER = 
MAIL_PASS = 

[UPLOAD]
UPLOAD_DIR = 

[ENCRYPT]
SECRET_KEY = 
```

#### Development Run 
To run it in development:
```
fastapi dev main.py
```
If you want to deactivate the virtual environment:
```sh
deactivate
```
## Front-End 
You will need a live server for the front-end. You can create your own account then, or alternatively, you can log into the admin user with initial password `qwerty`. It is highly recommended that you change it immediately. 

> [!NOTE]
> By default, the back-end API is set at `http://127.0.0.1:8000/api`, however, your instance may be located elsewhere, on a different port. Change the `API_BASE_URL` variable in the `alex-bank/front-end/src/functions.js`.
