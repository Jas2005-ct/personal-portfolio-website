# 🚀 Premium Professional Portfolio

A sophisticated, modern portfolio platform built with **Django**, **Django REST Framework**, and a sleek frontend. Designed for professionals to showcase their expertise, projects, and achievements with elegance.

---

## ✨ Key Features

-   **👤 Comprehensive Profile**: Detailed bio, professional titles, and social links.
-   **💼 Work & Experience**: Showcase internships, professions, and education history.
-   **🛠️ Tech Stack & Skills**: Dynamic skill bars and technology tag management.
-   **📂 Project Showcase**: Filterable project gallery with detailed descriptions and links.
-   **📜 Certifications**: Highlight your professional achievements and certificates.
-   **📬 Contact System**: Integrated contact form for direct inquiries.
-   **🔐 Secure Admin Dashboard**: Full control over content management via a dedicated superuser interface.
-   **🌐 RESTful API**: Robust backend API serving portfolio data for headless or coupled frontends.

## 🛠️ Technology Stack

-   **Backend**: Django 5.2+, Django REST Framework
-   **Database**: PostgreSQL (Production), SQLite (Development)
-   **Styling**: Vanilla CSS with modern Flexbox/Grid
-   **Asset Management**: Cloudinary for media, WhiteNoise for static files
-   **Deployment**: Ready for Render/Heroku with Gunicorn

---

## 🚦 Getting Started

### Prerequisites

-   Python 3.12+
-   [Poetry](https://python-poetry.org/) for dependency management

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Jas2005-ct/personal-portfolio-website.git
    cd personal-portfolio-website
    ```

2.  **Install dependencies**:
    ```bash
    poetry install
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory and add your configurations (refer to `.env.example` if available).

4.  **Database Migrations**:
    ```bash
    poetry run python manage.py migrate
    ```

5.  **Create a Superuser**:
    ```bash
    poetry run python manage.py createsuperuser
    ```

6.  **Run Development Server**:
    ```bash
    poetry run python manage.py runserver
    ```

---

## 📸 Project Structure

-   `portfolio/`: Core application logic, models, and API views.
-   `project/`: Project configuration and settings.
-   `templates/`: HTML5 templates for the frontend.
-   `static/`: CSS, JavaScript, and asset files.
-   `media/`: User-uploaded content.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
