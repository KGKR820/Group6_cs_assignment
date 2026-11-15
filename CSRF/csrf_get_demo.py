import secrets
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

BALANCES = {"surya": 10000, "friend": 2000, "attacker": 0}
SESSIONS = {}
CSRF_TOKENS = {}
MITIGATION = False


class BankHandler(BaseHTTPRequestHandler):
    def get_session_id(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        return cookie["session_id"].value if "session_id" in cookie else None

    def send_html(self, status, html_body, cookie_header=None):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()
        self.wfile.write(html_body.encode("utf-8"))

    def redirect(self, path="/", cookie_header=None):
        self.send_response(302)
        self.send_header("Location", path)
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()

    def do_GET(self):
        global MITIGATION
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        sid = self.get_session_id()
        user = SESSIONS.get(sid)

        if parsed.path == "/login":
            new_sid = secrets.token_hex(8)
            SESSIONS[new_sid] = "surya"
            CSRF_TOKENS[new_sid] = secrets.token_hex(8)
            return self.redirect("/", f"session_id={new_sid}; Path=/")

        if parsed.path == "/toggle":
            MITIGATION = not MITIGATION
            return self.redirect("/")

        if parsed.path == "/reset":
            BALANCES.update({"surya": 10000, "friend": 2000, "attacker": 0})
            return self.redirect("/")

        if parsed.path == "/transfer":
            if not user:
                return self.send_html(401, "<h2>401 Please log in first.</h2>")

            if MITIGATION:
                req_token = params.get("csrf_token", [""])[0]
                if req_token != CSRF_TOKENS.get(sid):
                    return self.send_html(
                        403,
                        "<div style='font-family:sans-serif;max-width:600px;margin:3rem auto;padding:1.5rem;border:2px solid #dc2626;border-radius:8px;background:#fef2f2;'>"
                        "<h2 style='color:#dc2626;margin-top:0;'>403 Forbidden — CSRF Attack Blocked!</h2>"
                        "<p><b>Reason:</b> Missing or invalid <code>csrf_token</code> in GET request.</p>"
                        "</div>",
                    )

            to_user = params.get("to", [""])[0]
            amount = int(params.get("amount", ["0"])[0])
            if to_user in BALANCES and 0 < amount <= BALANCES[user]:
                BALANCES[user] -= amount
                BALANCES[to_user] += amount
                return self.send_html(
                    200,
                    f"<div style='font-family:sans-serif;max-width:600px;margin:3rem auto;padding:1.5rem;border:2px solid #16a34a;border-radius:8px;background:#f0fdf4;'>"
                    f"<h2 style='color:#16a34a;margin-top:0;'>200 OK — Transfer Successful!</h2>"
                    f"<p>Transferred <b>₹{amount}</b> from <b>{user}</b> to <b>{to_user}</b>.</p>"
                    f"</div>",
                )
            return self.send_html(400, "<h2>400 Invalid Transfer Parameters</h2>")

        mode_text = "ON (Secured with CSRF Token)" if MITIGATION else "OFF (Vulnerable GET)"
        mode_color = "green" if MITIGATION else "red"
        token = CSRF_TOKENS.get(sid, "")

        if not user:
            body = "<h3>Not logged in</h3><a href='/login'><button>Log in as Surya</button></a>"
        else:
            token_input = f'<input type="hidden" name="csrf_token" value="{token}">' if MITIGATION else ""
            token_info = f"<p><small>Active CSRF Token in form: <code>{token}</code></small></p>" if MITIGATION else ""

            body = f"""
            <p>Logged in as: <b>{user}</b> (Cookie <code>session_id={sid}</code>)</p>
            <ul>
                <li><b>Surya (You):</b> ₹{BALANCES['surya']}</li>
                <li><b>Friend:</b> ₹{BALANCES['friend']}</li>
                <li><b>Attacker:</b> ₹{BALANCES['attacker']}</li>
            </ul>
            <h3>Send Money (GET Request)</h3>
            <form action="/transfer" method="GET">
                {token_input}
                To: <input name="to" value="friend">
                Amount: <input name="amount" type="number" value="1000">
                <button type="submit">Transfer</button>
            </form>
            {token_info}
            """

        self.send_html(
            200,
            f"""<div style="font-family:sans-serif;max-width:600px;margin:2rem auto;">
                <h2>IIITA CampusBank (Port 5000)</h2>
                <p>Mitigation: <b style="color:{mode_color};">{mode_text}</b>
                   | <a href="/toggle">Toggle Mitigation</a>
                   | <a href="/reset">Reset Balances</a></p>
                <hr>{body}
            </div>""",
        )


class AttackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/offer.svg":
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.end_headers()
            svg = """<svg xmlns="http://www.w3.org/2000/svg" width="420" height="140">
                <rect width="100%" height="100%" rx="12" fill="#1e293b"/>
                <text x="210" y="60" fill="#38bdf8" font-size="22" font-family="sans-serif" text-anchor="middle">GEEKHAVEN HACKATHON PASS</text>
                <text x="210" y="100" fill="#f8fafc" font-size="16" font-family="sans-serif" text-anchor="middle">Click this image to claim ₹500 Cloud Credits!</text>
            </svg>"""
            return self.wfile.write(svg.encode("utf-8"))

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        exploit_page = """
        <div style="font-family:sans-serif;max-width:600px;margin:2rem auto;text-align:center;">
            <h2>Attacker Promo Site (http://localhost:5001)</h2>
            <p>Right-click the image below and select <b>Inspect</b> to view the forged link, then click it:</p>
            <a href="http://localhost:5000/transfer?to=attacker&amount=5000">
                <img src="http://localhost:5001/offer.svg" alt="Claim Offer" style="cursor:pointer;border:3px solid #e11d48;border-radius:12px;">
            </a>
        </div>
        """
        self.wfile.write(exploit_page.encode("utf-8"))


if __name__ == "__main__":
    threading.Thread(
        target=HTTPServer(("127.0.0.1", 5001), AttackerHandler).serve_forever,
        daemon=True,
    ).start()
    print("Bank Server running at     : http://localhost:5000")
    print("Attacker Server running at : http://localhost:5001")
    HTTPServer(("127.0.0.1", 5000), BankHandler).serve_forever()