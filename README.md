# 🌟 Gurukul

**Gurukul** is a modern, open-source web-based platform designed to streamline learning and assessment. Built using **Django**, **Bootstrap 5**, and **JavaScript**, it enables educators to design interactive quizzes, manage virtual classes, and collaborate in real-time through integrated chat features.

---

## 📚 Table of Contents

* [Features](#features)
* [Technology Stack](#technology-stack)
* [Code Structure](#code-structure)
* [Real-Time Chat (WebSockets)](#real-time-chat-websockets)
* [Installation & Setup](#installation--setup)
* [Running the Application](#running-the-application)
* [Demo & Comparison](#demo--comparison)
* [Contributing](#contributing)


---

## 🚀 Features

* ✅ **Quiz Management**: Build, assign, and auto-submit timed quizzes. Interface mimics real exam settings for a focused experience, with randomized questions and options per user to ensure fairness.
* 🧠 **Question Types**: Supports MCQs, true/false, and subjective text-based answers.
* 🧾 **Grading System**: Automated grading for objective questions; manual evaluation for subjective/descriptive answers.
* 🏫 **Class & User Roles**: Teachers can create classes; students join using access codes. Classes include full management features like schedules, current topics, upcoming lessons, and syllabus tracking.
* 📂 **Resource Sharing**: Upload and share notes or books with public/private visibility options.
* 📣 **Announcements & Assignments**: Post important updates and assignments with time-based control.
* 📊 **Analytics**: Track performance using two metrics:  
  - **Raw Marks**: Total score earned.  
  - **Weighted Score**: Combines marks with time taken to reflect both accuracy and efficiency.
* 📘 **Quiz Review & Insights**: After submission, users can review wrong or missed answers. Each question displays a success rate based on how others performed, aiding focused revision.
* 🔐 **Access-Controlled Content**: Classes, quizzes, notes, and books can be private and protected by access codes. Users can search for these entries but must enter the correct code to access them. Codes are shared by creators or admins.
* 💬 **Live Chat**: Real-time messaging with WebSocket support for individual and group chats. Admins can create and manage groups, assign roles, and share group links.
* 🌑 **Dark Theme UI**: Modern, responsive, and mobile-first interface built with Bootstrap 5 and dark mode aesthetics.


---

## 🧰 Technology Stack

* **Backend**: Django 4.x, Django Channels (ASGI), Python 3.10+
* **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
* **WebSockets**: Daphne server via ASGI + Redis (optional)
* **Database**: Oracle RDBMS (`django.db.backends.oracle`)
* **Deployment**: WSGI (HTTP) + ASGI (WebSockets)

---

## 🗂 Code Structure

```bash
Gurukul/
├── Chat/                 # Dedicated app for real-time messaging
│   ├── consumers.py      # WebSocket logic for chat
│   ├── models.py         # Message model
│   ├── routing.py        # WebSocket URL routing
│   ├── templates/        # Chat templates
│   └── urls.py           # App-specific routes
├── Users/                # Core app
│   ├── models.py         # UserProfile, Quiz, Question, etc.
│   ├── forms.py          # Forms for user and quiz logic
│   ├── views.py          # Handlers for pages and logic
│   ├── consumers.py      # WebSocket consumers (chat)
│   ├── urls.py           # App routing
│   └── templates/        # Organized by feature (Bootstrap 5)
│       ├── users/
│       ├── quiz/
│       ├── class/
│       └── chat/
├── Gurukul/              # Project settings & config
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
├── static/               # CSS, JS, images
├── media/                # Uploaded files
├── docs/                 # Diagrams & reports
├── manage.py             # Django CLI tool
└── requirements.txt      # Python dependencies
```


## 💬 Real-Time Chat (WebSockets)

* Implemented with **Django Channels** and **ASGI**.
* `ChatConsumer` handles WebSocket lifecycle.
* Configurable with optional **Redis** support.

---


## 🛠 Installation & Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/i0Ta07/Gurukul.git
   cd Gurukul
   ```
2. **Set up virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Update DB settings** in `Gurukul/settings.py`
5. **Apply migrations and create superuser**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## ▶️ Running the Application

* **Start Django server**:

  ```bash
  python manage.py runserver
  ```
* **Start Daphne WebSocket server**:

  ```bash
  daphne -b 0.0.0.0 -p 8001 Gurukul.asgi:application
  ```

Visit: `http://localhost:8000/`
WebSocket: Port `8001`

---

## 🎥 Demo & Comparison

📹 **Project Walkthrough & Google Classroom Comparison**  
Watch the full demonstration here: [Google Drive Video](https://drive.google.com/drive/folders/1Vxray1KSyuxuMMmAZlM44bU89c7zpDlf?usp=sharing)

| Feature                            | Gurukul                                                                 | Google Classroom                      |
| ------------------------------     | ----------------------------------------------------------------------- | ------------------------------------- |
| **Quiz Flexibility**               | Timed, auto-submission, MCQ/TF/Subjective types                         | Limited quiz options                  |
| **Grading**                        | Auto + manual descriptive grading                                       | Only auto for MCQs                    |
| **Material Sharing**               | Notes/books with public/private access                                  | Files only, no control over access    |
| **Class Creation**                 | Teachers create + manage schedules, topics                              | Limited schedule/tracking features    |
| **Chat System**                    | Built-in chat (WebSockets), groups, admin roles                         | No integrated messaging               |
| **Analytics**                      | Raw + weighted marks with time insight                                  | Basic score listing                   |
| **Access Security**                | Private content unlockable via access codes                             | No per-resource access control        |
| **Theming**                        | Dark UI, Bootstrap 5, mobile-first                                      | No theme customization                |
| **Shuffled Questions and options** | Each user have different set of shuffled questions and options          | No shuffle  options                   |

👉 **We highly encourage you to explore the working demonstration video** to truly grasp Gurukul’s capabilities in action.  
Because **true art cannot be captured or written—it must be experienced.**

---

## 🤝 Contributing

We welcome contributions to improve Gurukul! Submit issues or PRs for:

* New features or analytics
* Improved UI/UX or dark/light theme toggles
* Code refactoring or test coverage

---

