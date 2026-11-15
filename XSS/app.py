
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    return sqlite3.connect("comments.db")


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/comment")
async def add_comment(comment: str = Form(...)):
    conn = get_db()

    conn.execute("INSERT INTO comments (content) VALUES (?)",(comment,))

    conn.commit()
    conn.close()

    return RedirectResponse("/comment", status_code=303)

@app.get("/comment", response_class=HTMLResponse)
async def comment_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

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


# VULNERABLE SQL INJECTION ENDPOINT
@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, search: str = ""):

    conn = get_db()

    # VULNERABILITY: Directly concatenating user input

    # query = f"SELECT content FROM comments WHERE content LIKE '%{search}%'"
    # cursor = conn.execute(query)

    query = "SELECT content FROM comments WHERE content LIKE ?"
    cursor = conn.execute(query, (f"%{search}%",))

    results = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "query": search,
            "results": results
        }
    )


@app.post("/delete-comments")
async def delete_comments():
    conn = get_db()

    conn.execute("DELETE FROM comments")

    conn.commit()
    conn.close()

    return RedirectResponse("/comments", status_code=303)


init_db()
