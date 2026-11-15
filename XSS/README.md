# Stored Cross-Site Scripting (Stored XSS) — Security Lab

## 1. Objective

Demonstrate how Stored Cross-Site Scripting (Stored XSS) occurs when an application saves attacker-controlled input and later renders that input as executable HTML or JavaScript in another user's browser.

This lab uses:
- **Backend:** FastAPI
- **Database:** SQLite (`comments.db`)
- **Templating:** Jinja2
- **Frontend:** HTML


---

## 2. How Stored XSS works

1. An attacker submits a comment containing HTML/JavaScript.
2. The application stores the comment in SQLite.
3. A user opens the comments page.
4. The application retrieves the stored comment and inserts it into the HTML response.
5. If the template treats the untrusted comment as trusted HTML, the victim's browser parses and executes the injected script.

**Important:** The script does not execute on every connected device at the moment it is submitted. Each browser executes it when that browser loads a page that renders the stored payload.

---

##  (a) Vulnerable implementation

### Backend: `app.py`

The application accepts a comment and stores it in the database:

```python
@app.post("/comment")
async def add_comment(comment: str = Form(...)):
    conn = get_db()
    conn.execute(
        "INSERT INTO comments (content) VALUES (?)",
        (comment,)
    )
    conn.commit()
    conn.close()

    return RedirectResponse("/comments", status_code=303)
```

The comments route retrieves the stored values:

```python
@app.get("/comments", response_class=HTMLResponse)
async def view_comments(request: Request):
    conn = get_db()
    cursor = conn.execute("SELECT content FROM comments")
    comments = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="comments.html",
        context={"comments": comments}
    )
```

### Vulnerable template: `templates/comments.html`

**The vulnerable line is `{{ comment[0] | safe }}`.** Jinja2's `safe` filter marks the value as trusted HTML and bypasses normal HTML escaping.

```html
{% for comment in comments %}
    <div>
        {{ comment[0] | safe }}
    </div>
{% endfor %}
```

The SQL statement uses a parameterized query. The flaw demonstrated here is **not SQL injection**; it is unsafe output rendering.

---

## (b) Working exploit

### Exact proof-of-execution payload

Submit this comment through the application's comment form:

```html
<script>alert('Stored XSS executed')</script>
```

### Exact HTTP request

Assuming the application is running on `127.0.0.1:8000`:

```http
POST /comment HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/x-www-form-urlencoded

comment=%3Cscript%3Ealert%28%27Stored%20XSS%20executed%27%29%3C%2Fscript%3E
```

Or submit the decoded payload in the browser's comment form.

### Optional redirect proof

For a demonstration of a stored redirect instead of an alert, submit:

```html
<script>window.location.href='/search'</script>
```

This redirects each browser that renders the stored comment to `/search` on the same origin. Use the alert payload as the primary proof because it makes execution easy to observe in a recording.

**Evidence to capture:** the submitted comment, the alert dialog, the refreshed comments page triggering the alert again, and (if demonstrated) the second device loading `/comments`.

---

## (c) Root cause

The application accepts user-controlled comment text, stores it, and later renders it in an HTML page using Jinja2's `|safe` filter. This disables automatic output escaping, so the browser interprets the stored input as markup and executes the injected JavaScript.

---

##  (d) Mitigation implemented

### Fix: restore Jinja2 automatic HTML escaping

In `templates/comments.html`, replace the vulnerable line:

```jinja2
{{ comment[0] | safe }}
```

with:

```jinja2
{{ comment[0] }}
```

Jinja2 autoescaping is enabled for HTML templates, so characters such as `<` and `>` are encoded before the value is placed in the page.

### Retest using the same payload

Submit the exact same payload again:

```html
<script>alert('Stored XSS executed')</script>
```

**Expected secure result:**
- The payload is displayed as literal text (or escaped markup).
- No alert dialog appears.
- Refreshing `/comments` still does not execute it.

## (e) Other Mitigation Techniques (Theory)

Apart from the primary prevention techniques, several additional security measures can help protect web applications against Stored Cross-Site Scripting (XSS) attacks.

- **Input Validation:**
  - Validate all user-submitted data before processing or storing it in the database.
  - Restrict input according to expected data types, formats, and maximum lengths.
  - Reject unexpected or malformed input that does not meet the application's requirements.
  - For example, a comment field can have a maximum length of 500 characters.
  - Input validation reduces the possibility of accepting malicious or unexpected data, but it cannot completely prevent XSS attacks. Therefore, output encoding is still necessary.

- **Context-Aware Output Encoding:**
  - Convert special characters into safe representations before displaying user-generated content.
  - The encoding method should depend on where the data is being inserted.
  - Different contexts, such as HTML content, HTML attributes, URLs, and JavaScript, require different encoding techniques.
  - Characters such as `<`, `>`, and `"` should be encoded appropriately so that the browser treats them as text rather than executable code.
  - In Jinja2, automatic HTML escaping helps protect template variables from being interpreted as HTML elements or scripts.
  - Avoid disabling automatic escaping using the `safe` filter on untrusted data.

- **HTML Sanitization:**
  - HTML sanitization removes potentially dangerous HTML elements, attributes, and scripts from user-submitted content.
  - It is particularly useful when an application allows users to submit formatted content, such as comments containing bold text, hyperlinks, or paragraphs.
  - Use well-maintained sanitization libraries that follow an allowlist-based approach.
  - An allowlist specifies which HTML tags and attributes are permitted while removing potentially dangerous ones.
  - For example, tags such as `<b>`, `<i>`, and `<p>` may be allowed, while dangerous event-handler attributes such as `onerror` and `onclick` are removed.
  - In Python applications, libraries such as **Bleach** can be used for HTML sanitization.

- **Content Security Policy (CSP):**
  - CSP is an additional browser-level security mechanism that controls which resources a webpage is allowed to load and execute.
  - It can restrict JavaScript execution to trusted sources and block unauthorized scripts.
  - It can also prevent the execution of inline scripts when configured appropriately.
  - CSP is implemented using the `Content-Security-Policy` HTTP response header.
  - Example:
    ```http
    Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
    ```
  - This policy restricts resource loading to the application's own origin by default, allows scripts from the same origin, and blocks plugins.
  - CSP reduces the impact of XSS vulnerabilities but does not eliminate the underlying vulnerability.

- **Framework Autoescaping:**
  - Modern web frameworks provide automatic escaping mechanisms to prevent untrusted data from being interpreted as executable HTML or JavaScript.
  - In FastAPI applications using Jinja2, automatic HTML escaping should always remain enabled for HTML templates.
  - Display user-generated content using normal Jinja2 expressions such as `{{ comment }}`.
  - Avoid using the `|safe` filter on untrusted user input because it disables automatic escaping.
  - This ensures that potentially malicious HTML content is displayed as plain text rather than executed by the browser.

- **Avoid Unsafe DOM Manipulation:**
  - Avoid inserting untrusted user input directly into webpages using unsafe JavaScript methods.
  - Functions such as `innerHTML`, `document.write()`, and `eval()` can introduce XSS vulnerabilities when used with untrusted data.
  - Prefer safer alternatives such as `textContent`, which treats the supplied value as plain text instead of interpreting it as HTML.
  - This reduces the risk of executing malicious scripts during dynamic webpage updates.

- **Secure Cookie Configuration:**
  - Configure session cookies with security attributes such as `HttpOnly`, `Secure`, and `SameSite`.
  - The `HttpOnly` attribute prevents JavaScript from directly accessing session cookies.
  - The `Secure` attribute ensures cookies are transmitted only over HTTPS.
  - The `SameSite` attribute helps restrict cross-site cookie transmission.
  - These settings help reduce the impact of certain attacks but do not directly prevent Stored XSS.

### Conclusion

No single mitigation technique can completely eliminate Stored XSS. A combination of input validation, context-aware output encoding, HTML sanitization, framework autoescaping, and CSP provides stronger protection. For FastAPI applications using Jinja2, keeping automatic escaping enabled and avoiding unsafe rendering of user-generated content are particularly important.

---
# Stored Cross-Site Scripting (Stored XSS)

## ME

| Field | Details |
|---|---|
| **Name** | Victor Daniel |
| **Roll Number** | IIT2024014 |
| **Category** | XSS (Cross-Site Scripting) |
| **Variant** | Stored XSS (Persistent Cross-Site Scripting) |

---


