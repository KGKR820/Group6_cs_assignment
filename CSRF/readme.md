# CSRF – GET-Based Forged Action

## 1. Overview
This project demonstrates a Cross-Site Request Forgery (CSRF) vulnerability using a GET-based forged action done by

Name: Surya Raghuram
Roll no: IIT2024093

The application simulates a banking website where an authenticated user can transfer money. An attacker tricks the user into clicking a malicious link, causing an unintended transfer using the user's existing session.

## 2. Technologies Used
- Python 3
- HTTPServer and BaseHTTPRequestHandler
- HTML
- HTTP Cookies and GET Requests

## 3. How to Run

1. Ensure Python 3 is installed.
2. Run the application:

   ```bash
   python csrf_demo.py
   ```

3. Open the banking application:
   `http://localhost:5000`

4. Open the attacker webpage:
   `http://localhost:5001`

## 4. Vulnerability Demonstration

- Log in to the simulated banking application as Surya.
- The application creates a session cookie.
- Open the attacker webpage and click the promotional image.
- The image redirects the victim to a forged GET request:

  ```text
  /transfer?to=attacker&amount=5000
  ```

- The browser automatically sends the victim's session cookie.
- Since the vulnerable application does not verify the user's intent, the transfer is executed.

## 5. Root Cause

The application performs a state-changing operation (money transfer) through a GET request. It trusts the authenticated session cookie without verifying whether the request was intentionally initiated by the user.

## 6. Mitigation Implemented – CSRF Token

A synchronizer CSRF token mechanism is implemented.

- A unique token is generated for each session.
- The token is included in the legitimate transfer form.
- The server validates the submitted token before processing the transfer.
- Requests with missing or invalid tokens are rejected with HTTP 403 Forbidden.

The same malicious link is tested again with mitigation enabled, and the forged request is blocked.

## 7. Other Mitigation Techniques

- **SameSite Cookies:** Restrict cookies from being sent with certain cross-site requests.
- **Re-authentication:** Require users to authenticate again before sensitive operations.
- **Avoid State-Changing GET Requests:** GET should be used for retrieving information, not modifying application state.

## 8. Screenshots / Evidence

Add your demonstration screenshots below:

- Vulnerable application and initial balances.
- Attacker promotional webpage.
- Successful forged transfer.
- Mitigation enabled.
- Forged transfer blocked with HTTP 403.

## 9. Conclusion

This demonstration shows how an attacker can exploit an authenticated user's session through a forged GET request. Implementing CSRF token validation helps prevent unauthorized requests from being executed.

## 10. Author

- **Name:** Durga Surya Raghuram Gadepalli
- **Roll Number:** [Add your roll number]
- **Category:** Cross-Site Request Forgery (CSRF)
- **Variant:** GET-Based Forged Action