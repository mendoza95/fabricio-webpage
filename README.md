# Personal Portfolio & Blog Website

This is a personal portfolio and blog website built with Flask. It is designed to be a clean, modern, and easily maintainable platform to showcase professional work, publications, and personal blog posts. The site is fully bilingual (English and Spanish) and features dynamic content generation.

## Features

*   **Bilingual Content**: The entire website supports both English and Spanish, with an easy-to-use language switcher.
*   **Data-Driven Content**: Most of the site's content (like project descriptions, work experience, and education) is managed through simple JSON files in the `data/` directory, making updates easy without touching the code.
*   **Markdown Blog**: A complete blog section powered by Flask-FlatPages, where posts are written in simple Markdown (`.md`) files.
*   **Dynamic PDF CV Generation**: A standout feature that automatically generates a professional, up-to-date CV in PDF format from the website's data using the WeasyPrint library.
*   **Contact Form**: A fully functional contact form that sends emails to the site owner upon submission.
*   **Responsive Design**: The website is fully responsive and works seamlessly on desktops, tablets, and mobile devices.

## Tech Stack

*   **Backend**: Python, Flask
*   **Frontend**: HTML, CSS, JavaScript
*   **Content Management**:
    *   Flask-FlatPages for the blog (Markdown files)
    *   JSON for structured site data
*   **PDF Generation**: WeasyPrint
*   **Forms**: Flask-WTF
*   **Deployment**: Gunicorn

## Project Structure

```
my-personal-webpage/
├── app.py                  # Main Flask application logic
├── data/
│   ├── en.json             # English site content
│   ├── es.json             # Spanish site content
│   └── shared_data.json    # Data shared across languages
├── posts/
│   ├── en/                 # English blog posts (.md files)
│   └── es/                 # Spanish blog posts (.md files)
├── static/
│   ├── css/style.css       # Main stylesheet
│   ├── images/             # Site images (profile photo, etc.)
│   └── script.js           # JavaScript for frontend interactivity
├── templates/
│   ├── base.html           # Base template with header and footer
│   ├── index.html          # Main page template
│   ├── blog.html           # Blog archive page
│   ├── post.html           # Single blog post page
│   └── cv.html             # Template for the PDF CV
├── .env                    # Environment variables (for email config)
├── requirements.txt        # Python package dependencies
└── README.md               # This file
```

## Local Setup and Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mendoza95/my-personal-webpage.git
    cd my-personal-webpage
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file** in the root directory for your email configuration. This is required for the contact form to work.
    ```
    SECRET_KEY='a_very_long_and_random_secret_key'
    MAIL_SERVER='smtp.your-email-provider.com'
    MAIL_PORT=587
    MAIL_USERNAME='your-email@example.com'
    MAIL_PASSWORD='your-email-password'
    ```

5.  **Run the Flask development server:**
    ```bash
    python app.py
    ```
    The website will be available at `http://127.0.0.1:5000`.