========================================================================
   SQL Injection - Authentication Bypass Lab (Windows Quickstart)
========================================================================

--- METHOD 1: 1-CLICK AUTOMATIC (EASIEST) ---
Just double-click "run.bat".
It will automatically:
1. Create virtual environment
2. Install Flask
3. Initialize the database
4. Start server on http://127.0.0.1:5001/
5. Automatically open the browser!

---------------------------------------------
--- METHOD 2: MANUAL COMMANDS (CMD / PowerShell) ---
If you prefer running commands in Command Prompt (cmd) or PowerShell:

Step 1: Open Command Prompt inside this folder
Step 2: Install dependencies:
   pip install -r requirements.txt

Step 3: Initialize database:
   python init_db.py

Step 4: Start application:
   python app.py

Step 5: Open your browser:
   http://127.0.0.1:5001/

---------------------------------------------
--- DEMO / TEST DETAILS ---

1. Vulnerable Login:
   URL: http://127.0.0.1:5001/login
   Payload:
      Username: ' OR '1'='1' --
      Password: anything
   Result: Logged in as administrator without a password!

2. Secure Login:
   URL: http://127.0.0.1:5001/login-secure
   Payload:
      Username: ' OR '1'='1' --
      Password: anything
   Result: Blocked with "Invalid credentials."

Test Accounts in DB:
- admin   / SuperSecret123
- alice   / alice_pass
- bob     / bob_pass
- charlie / charlie_pass
========================================================================
