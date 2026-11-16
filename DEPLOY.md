# Putting the project on GitHub and on the internet

Two different things, so do them in this order:

* **GitHub** stores and shows your *code* (what recruiters and teachers open). GitHub **cannot run** a Flask + MySQL
  site: GitHub Pages only serves plain HTML files.
* **A host** (this guide uses **PythonAnywhere**, which has a free plan with MySQL and gives you
  `https://yourname.pythonanywhere.com`) *runs* the site.

Do Part A first; Part B is optional but gives you a live link for your resume.

---

## Part A: upload the code to GitHub (Windows)

1. **Install Git** from <https://git-scm.com/download/win> (accept the defaults). Close and reopen VS Code.
2. **Create a GitHub account** at <https://github.com> if you do not have one.
3. **Create the repository:** GitHub > **+** > *New repository*. Name it `lms-ml`. Choose **Public**
   (or Private). Leave *Add a README*, *.gitignore* and *license* **unticked** (the project already has them). Click *Create*.
4. **Tell Git who you are** (once). In the VS Code terminal (Ctrl+`):
   ```
   git config --global user.name "Vansh Goel"
   git config --global user.email "your-github-email@example.com"
   ```
5. **Check what will be uploaded.** In the project folder:
   ```
   git init
   git add .
   git status
   ```
   Read the list. You must **not** see `.env`, `DEMO_ACCOUNTS.md`, `venv/` or any `.pkl` file. They are listed in
   `.gitignore` on purpose (passwords and generated files). If one of them appears, stop and ask before continuing.
6. **Save and upload:**
   ```
   git commit -m "Initial commit: LMS with ML performance prediction"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/lms-ml.git
   git push -u origin main
   ```
   A browser window asks you to sign in to GitHub the first time. Approve it.
7. Open the repository page and refresh. You should see the README. Add a short *About* text and topics
   (`flask`, `mysql`, `machine-learning`, `scikit-learn`) with the gear icon on the right.
8. **Later changes:** `git add .` then `git commit -m "what you changed"` then `git push`.

> If you ever commit `.env` by mistake: change your MySQL password and `SECRET_KEY` immediately. Deleting the file
> later does not remove it from GitHub's history.

---

## Part B: run it live on PythonAnywhere (free)

Free-plan limits to know: one website at `yourname.pythonanywhere.com`, 512 MB disk, and the site can only reach
a short list of outside web addresses. That last point matters for **lecture videos**: the check that confirms a
YouTube video is real may be blocked, so videos you add there can be refused. Everything else works.

1. **Sign up** at <https://www.pythonanywhere.com> (Beginner plan). Your username becomes your web address.
2. **Create the database.** *Databases* tab > set a MySQL password > under *Create a database* type `lms_ml` > Create.
   Note three values: the host (`yourname.mysql.pythonanywhere-services.com`), your user (`yourname`) and the full
   database name (`yourname$lms_ml`).
3. **Get the code.** *Consoles* tab > *Bash*:
   ```
   git clone https://github.com/YOUR-USERNAME/lms-ml.git
   cd lms-ml
   mkvirtualenv lms --system-site-packages
   pip install Flask Flask-Login PyMySQL cryptography python-dotenv Faker
   ```
   (`--system-site-packages` reuses the pre-installed numpy, pandas, scikit-learn and matplotlib, which saves disk space.
   "Requirement already satisfied" lines are fine.) If the repository is private, GitHub asks for a personal access
   token instead of a password (GitHub > Settings > Developer settings > Tokens).
4. **Create the settings file** (`.env`) in that console:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   nano .env
   ```
   Paste this, replacing the capitals with your own values (the long text is the output of the first command):
   ```
   SECRET_KEY=PASTE-THE-LONG-RANDOM-TEXT
   DB_HOST=YOURNAME.mysql.pythonanywhere-services.com
   DB_PORT=3306
   DB_USER=YOURNAME
   DB_PASSWORD=YOUR-MYSQL-PASSWORD
   DB_NAME=YOURNAME$lms_ml
   FLASK_DEBUG=0
   SESSION_COOKIE_SECURE=1
   ```
   Save with **Ctrl+O**, Enter, **Ctrl+X**.
5. **Create the tables, train the model, make your admin** (still in the console, still in `lms-ml`):
   ```
   python scripts/load_schema.py
   python model/train_model.py
   python scripts/make_admin.py
   ```
   `train_model.py` runs here because a saved model only loads with the same scikit-learn version that trained it.
   `make_admin.py` asks for your name, e-mail and password: that is your real administrator account.
6. **Create the website.** *Web* tab > *Add a new web app* > *Manual configuration* > pick the same Python
   version as the console (`python --version`). Then on the Web tab set:
   * **Virtualenv:** `/home/YOURNAME/.virtualenvs/lms`
   * **Static files:** URL `/static/`, directory `/home/YOURNAME/lms-ml/static`
   * **WSGI configuration file** (click the link, delete everything, paste):
     ```python
     import os
     import sys

     project = "/home/YOURNAME/lms-ml"
     if project not in sys.path:
         sys.path.insert(0, project)
     os.chdir(project)

     from wsgi import application  # noqa: E402
     ```
7. Press the green **Reload** button and open `https://YOURNAME.pythonanywhere.com`. 
8. **Try it:** sign in with the admin you created, add a teacher and a subject, register a student. If you want
   sample data for a demonstration, run `python scripts/seed_demo.py --reset --skip-videos` in the console, show it,
   then **remove it** before sharing the link, because those accounts have public passwords:
   `python scripts/remove_demo_data.py --yes`.
9. **Update the live site later:** push from your laptop, then in a PythonAnywhere console: `cd lms-ml && git pull`,
   and press **Reload** on the Web tab.

### If something goes wrong

| What you see | Cause and fix |
|---|---|
| "Something went wrong" page, or error page on the Web tab | Open the **Error log** link on the Web tab. The last lines say what failed. |
| `Access denied for user` in the log | `DB_USER`, `DB_PASSWORD` or `DB_NAME` in `.env` is wrong. The name must include `YOURNAME$`. |
| `Can't connect to MySQL server` | `DB_HOST` must be the `...mysql.pythonanywhere-services.com` address, not `127.0.0.1`. |
| `ModuleNotFoundError` | Run `pip install <that name>` in a console with `workon lms`, then Reload. |
| Page appears with no styling | The *Static files* row is missing or the path is wrong. |
| You cannot stay signed in | `SESSION_COOKIE_SECURE=1` needs `https://`. Use the https address. |
| Predictions say the model is not trained | Run `python model/train_model.py` again, then Reload. |
| Uploads fail | Make sure `uploads/materials` and `uploads/assignments` exist: `mkdir -p uploads/materials uploads/assignments`. |

### Before you share the link

* No demo accounts left (`python scripts/remove_demo_data.py`), your own admin exists.
* `SECRET_KEY` is your own random value and `FLASK_DEBUG=0`.
* The About page says the model was trained on synthetic data. Keep that honesty until you retrain on real records.
* Login attempts are not rate-limited yet. Fine for a college project, add Flask-Limiter before real use.
