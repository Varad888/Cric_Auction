from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()

# Session middleware (for login)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Static files (images, players)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- USERS ---------------- #
users_db = {
    "admin": {"password": "1234", "role": "admin"}
}

# ---------------- AUTH ---------------- #
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user

def require_login(request: Request):
    if "user" not in request.session:
        return False
    return True

# ---------------- MAIN PAGE ---------------- #
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if not require_login(request):
        return RedirectResponse("/login")

    with open("frontend/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# ---------------- LOGIN ---------------- #
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <h2 style='text-align:center;margin-top:100px;'>Login</h2>
    <form method='post' style='text-align:center;'>
        <input name='username' placeholder='Username'><br><br>
        <input name='password' type='password' placeholder='Password'><br><br>
        <button type='submit'>Login</button>
    </form>
    """

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users_db and users_db[username]["password"] == password:
        request.session["user"] = username
        return RedirectResponse("/", status_code=302)
    
    return HTMLResponse("<h3>Invalid Credentials</h3>")

# ---------------- LOGOUT ---------------- #
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

# ---------------- ADMIN PANEL ---------------- #
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    user = get_current_user(request)
    if not user or users_db[user]["role"] != "admin":
        return RedirectResponse("/login")

    users_list = "".join([f"<li>{u}</li>" for u in users_db])

    return f"""
    <h2>Admin Panel</h2>

    <h3>Users</h3>
    <ul>{users_list}</ul>

    <h3>Create User</h3>
    <form method="post" action="/create-user">
        <input name="username" placeholder="Username">
        <input name="password" placeholder="Password">
        <button>Create</button>
    </form>

    <h3>Delete User</h3>
    <form method="post" action="/delete-user">
        <input name="username" placeholder="Username">
        <button>Delete</button>
    </form>

    <br><br>
    <a href="/">Go to Auction</a> |
    <a href="/logout">Logout</a>
    """

@app.post("/create-user")
def create_user(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_current_user(request)
    if users_db[user]["role"] != "admin":
        raise HTTPException(status_code=403)

    users_db[username] = {"password": password, "role": "user"}
    return RedirectResponse("/admin", status_code=302)

@app.post("/delete-user")
def delete_user(request: Request, username: str = Form(...)):
    user = get_current_user(request)
    if users_db[user]["role"] != "admin":
        raise HTTPException(status_code=403)

    if username != "admin" and username in users_db:
        del users_db[username]

    return RedirectResponse("/admin", status_code=302)

# ---------------- PLAYERS API ---------------- #
@app.get("/players")
def get_players():
    folder = "static/Players"

    try:
        # 🔥 Debug print (check Railway logs)
        print("Looking for folder:", folder)

        if not os.path.exists(folder):
            print("Folder NOT found")
            return []

        players = os.listdir(folder)

        players = [
            p for p in players
            if p.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        print("Players found:", players)

        return players

    except Exception as e:
        print("ERROR in /players:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
