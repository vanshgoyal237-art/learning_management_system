# Learning Management System — ML Student Performance Prediction

A website (Flask + MySQL + Bootstrap 5 / Chart.js) where an **admin** runs the college, **teachers** teach and
**students** learn. A scikit-learn model labels each student **Good**, **Average** or **At Risk** and turns that
into recommendations, teacher alerts and library / placement actions.

Seven subjects come ready to use: **DSA, DBMS, SQL, Engineering Mathematics, Python, Full Stack Development and
Operating Systems**, each with materials, assignments, quizzes and a weekly timetable.

## Run it on Windows (the easy way)

**You need:** Python 3.11+ (tick *Add python.exe to PATH* when installing), MySQL 8 (running), and optionally VS Code.

1. **First time only:** double-click **`setup.bat`**. It creates the virtual environment, installs the packages,
   asks for your MySQL root password *once* to create the database and your `.env`, loads the demo data and
   finishes with a message.
2. **Every other time:** double-click **`start.bat`**. The website opens at <http://127.0.0.1:5000>.
   Keep the black window open while you use the site; close it (or press Ctrl+C) to stop.

That is all. You never have to type commands again, and VS Code is not needed to run the site.

> Do **not** use VS Code's *Go Live* button or the ▶ Run button on `app.py`. *Go Live* only shows a file list, and
> ▶ runs the file as a script without starting the website. Use `start.bat`, or in VS Code press **F5** and choose
> *LMS: run website (debug)*.

### Sign in

`setup.bat` creates the demo data and writes **`DEMO_ACCOUNTS.md`** in the project folder: every demo teacher and
student with their e-mail, subjects, roll number and section. The administrator is `admin@lms.test`.
Passwords are `Admin@12345`, `Teacher@12345` and `Student@12345` (public, for local testing only).

Signed in already? The login page tells you who, and offers **Sign out and use another account**. As administrator you
can also open **Students** or **Teachers**, pick a person and press **Sign in as …**.

To make **your own** admin account run `venv\Scripts\python scripts\make_admin.py`. Everyone can change their own
password from **Change password** in the sidebar.

## What the admin can do

| Page | What you do there |
|---|---|
| **Overview** | Counts, teachers waiting for approval (approve / reject right there), recent sign-ups, student outcomes, subjects |
| **Registrations** | Everyone who signed up, newest first; filter Everyone / Needs approval / Students / Teachers |
| **Students** | Search by name or e-mail, filter by prediction or subject; open any student for scores, attendance, submissions, quiz attempts, alerts and prediction history; enrol or remove them from subjects |
| **Teachers** | Search; open any teacher for their subjects, students and weekly timetable; **Add teacher** creates an approved account |
| **Subjects** | Create a subject (code, name, teacher), change its teacher, see its students, assignments, quizzes and class times, delete it (type the code to confirm) |
| **Assignments / Quizzes** | Every assignment and quiz on the platform with submission counts, scores and teacher |
| **Timetable** | The whole college week, colour-coded per subject. Add or remove classes. The site refuses a class that would put one teacher in two places, or two classes in one room, at the same time |

Teachers keep the teaching work: they create assignments and quizzes, grade, take attendance and see their own
timetable. Students see only their own subjects, deadlines and class times.

## Real assignments, quizzes and lecture videos

**Assignments and quizzes.** Every subject has 3 assignments (full briefs: scenario, numbered tasks, deliverable,
marking scheme that adds up to the marks) and 3 quizzes of 8 questions, each with a one-line "why" shown after the
quiz. All of it lives in `curriculum/` (one file per subject), so a teacher or you can edit the wording in one place.
`tests/test_curriculum.py` proves the answer keys: questions marked `py=` are run by Python and questions marked
`sql=` are run on a real database, and the printed result must equal the marked answer.

**Lecture videos** (sidebar: *Lecture videos*). A student who missed a class opens the subject, picks the topic and
plays the video inside the site; "Mark as watched" tracks progress, and the dashboard shows a *You missed a class*
banner with a link to the lecture. Teachers and the admin manage them under *Lecture videos*.

The rule that keeps links honest: **nothing is saved or shown until YouTube confirms the video exists and can be
embedded** (YouTube's oEmbed service). The title and channel students see come from YouTube, not from this project.

* `setup.bat` asks YouTube about the built-in list (`curriculum/videos.py`) and saves only what it confirms.
  It needs internet; offline, no video is saved and the seed says so.
* Later, press **Add recommended videos** or **Check links now** on the *Lecture videos* page, or run
  `venv\Scripts\python scripts\verify_videos.py` (`--dry-run` prints YouTube's verdict for every video without saving).
* Paste your own link on that page: it is checked the same way before it is saved.
* A video that is later removed or made private is marked *broken* and hidden from students.
* The video plays after the student presses the poster; until then nothing is loaded from YouTube. If a college
  network blocks YouTube the poster still offers "open it on YouTube".

## Pages for everyone

`/` home · `/about` how the prediction works · `/privacy` · `/login` · `/register` (teachers wait for approval).

| Who | Main pages |
|---|---|
| Student | Dashboard (charts, risk badge, personal plan, missed-class catch-up) · Subjects · Lecture videos · Assignments · Quizzes (timed, marked on the server, explanations after) · Timetable |
| Teacher | Dashboard (risk alerts, batch breakdown) · My subjects (materials, assignments, quizzes, attendance, grading) · Lecture videos · Timetable |

## Run it by hand (VS Code or any terminal)

1. Open the folder in VS Code. Create the environment: `python -m venv venv`, activate it
   (PowerShell: `venv\Scripts\Activate.ps1`), pick it with *Ctrl+Shift+P → Python: Select Interpreter*.
2. `pip install -r requirements.txt`
3. `python scripts/setup_db.py` — creates the database, a limited `lms_user` and `.env` (asks for the MySQL root password once).
4. `python scripts/seed_demo.py --reset` — 100 demo students (`--students 80..120`), 23 teachers, 24 subject sections (7 subjects, several sections each), attendance (present/absent/late), submissions, quiz attempts and predictions. Takes about 10 seconds. All demo accounts end in `@lms.test`; passwords: `Admin@12345`, `Teacher@12345`, `Student@12345`.
5. `python -m flask --app app run --debug`, then open <http://127.0.0.1:5000>.
6. Tests: `python -m pytest tests -q` (65 tests; they need steps 3–4 done first).

**Upgrading an older copy:** the app creates the new `timetable_slots` table by itself on start-up, so an existing
database keeps working. Re-run `seed_demo.py --reset` to get the seven subjects, teachers and timetable.

**If something fails**

| Message | Cause and fix |
|---|---|
| `Could not reach MySQL` / `Can't connect to MySQL server` | MySQL is not running. *Win+R → services.msc → MySQL80 → Start* |
| MySQL refused the password (setup) | Use the root password you chose when installing MySQL |
| `Access denied for user 'lms_user'` | `.env` and MySQL disagree. Delete `.env`, run `python scripts/setup_db.py` again |
| `ModuleNotFoundError` | Wrong interpreter, or `pip install -r requirements.txt` was skipped. `setup.bat` fixes both |
| `pip` fails building numpy / pandas / scikit-learn | Very new Python without wheels. Install Python 3.12, delete the `venv` folder, run `setup.bat` |
| Browser shows a file list at port 5500 | That is Live Server. Use `start.bat` and <http://127.0.0.1:5000> |
| Dashboard says the model is missing | `python -m model.train_model` |

## Project structure

```
lms-ml/
├── setup.bat, start.bat      first-time setup and one-click start (Windows)
├── app.py, config.py, requirements.txt, .env.example
├── .vscode/                  F5 configs, tasks, recommended extensions
├── database/
│   ├── database.sql          full schema (18 tables)
│   └── migrations/           upgrade scripts (applied automatically by services/schema.py where safe)
├── model/                    features.py, data_generator.py, train_model.py, artifacts/ (.pkl + metrics.json)
├── services/                 db, security, users, feature_builder, predictor, recommender, analytics,
│                             prediction_service, activity_tracker, uploads, timetable, schema
├── blueprints/               auth, pages, student, teacher, admin, videos, api
├── curriculum/               the teaching content: assignments, quizzes and the video list, one file per subject
├── templates/                one HTML page per screen (extends base.html)
├── static/                   css, js (dashboard, quiz timer, tracker), vendor/ (Bootstrap, Chart.js)
├── scripts/                  setup_db.py, seed_demo.py, make_admin.py, verify_videos.py
├── tests/                    335 tests (including a crawler that opens every reachable page as student, teacher and admin): security, pages, quiz, uploads, attendance, admin, timetable, ML endpoint,
│                             curriculum answer keys, lecture videos
└── uploads/                  materials/ and assignments/ (created by the app)
```

## How the pieces connect

```
browser ──heartbeat / material opens──> activity_logs ─┐
quizzes · assignments · attendance ────────────────────┼─> feature_builder.py ─> 8 features
                                                        │                              │
                          model/artifacts/*.pkl <── train_model.py       scaler + Random Forest
                                                                                       │
                          POST /api/predict ─> label + probabilities ─> recommender.py
                                                  │                        ├─ Good    → placement_flags
                                                  └─> predictions history   ├─ Average → revision / remedial plan
                                                                           └─ At Risk → risk_alerts + library books
```

The 8 features (`model/features.py` is the single source of truth): `attendance_pct, quiz_avg,
assignment_avg, course_completion_pct, study_hours, login_frequency, submission_delay_hours,
resource_interaction_count`. The behavioural ones come from `activity_logs` over a rolling 30-day window.

## Honesty notes (put these in your report)

* The first model is trained on **synthetic** data (`model/data_generator.py`). Its scores show the pipeline
  works, **not** real-world accuracy. Retrain on real data once a semester of it exists.
* The synthetic features are generated linearly, so Logistic Regression scores about the same as the Random
  Forest. Report both numbers from `metrics.json`; don't claim the forest wins.
* Labels in the synthetic set come from a written rule plus noise, so the model learns that rule.
* The demo students, quizzes scores and attendance come from `seed_demo.py`, not from real people.
* Predictions are suggestions for teachers, not decisions — the About and Privacy pages say so.

## Put it on GitHub and on the internet

See **DEPLOY.md** for the step-by-step guide (GitHub first, then a free host). Short version:
`python scripts/remove_demo_data.py`, set a real `SECRET_KEY`, `SESSION_COOKIE_SECURE=1` behind HTTPS, run
`python model/train_model.py` once on the server, and serve with `gunicorn wsgi:application`.

## Not built yet

Teachers cannot yet edit or delete an assignment or quiz after creating it (they can remove materials and
questions); students cannot un-enrol themselves (the admin can remove them); there is no e-mail notification
or one-click "retrain on real data" button; the timetable has no exam or holiday dates.
