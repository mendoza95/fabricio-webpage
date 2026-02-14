import os
from flask import Flask, render_template, redirect, session, url_for, request, flash
import json
import locale
from flask_flatpages import FlatPages, pygments_style_defs
from datetime import datetime, timezone
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from dotenv import load_dotenv
import smtplib, ssl
from weasyprint import HTML
from email.message import EmailMessage

load_dotenv(override=True)  # Force loading from .env, overriding existing env vars.

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Mail Configuration - IMPORTANT: Set these as environment variables for security
# We use .strip() to remove any accidental whitespace or invisible characters from the .env file.
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', '').strip()
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587').strip())
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').strip().lower() in ['true', 'on', '1']
# Explicitly set MAIL_USE_TLS to False if MAIL_USE_SSL is True, as they are mutually exclusive.
app.config['MAIL_USE_TLS'] = False if app.config['MAIL_USE_SSL'] else True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '').strip()
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '').strip()
app.config['MAIL_DEFAULT_SENDER'] = (os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME') or '').strip()


# Configuration for Flask-FlatPages
app.config['FLATPAGES_EXTENSION'] = '.md'
app.config['FLATPAGES_ROOT'] = 'posts'
app.config['FLATPAGES_AUTO_RELOAD'] = True

def _parse_date_flexible(d):
    """
    Robustly parse a date string from a few common formats. If all formats
    fail, log a warning and return a default date to prevent crashing.
    """
    date_str = str(d)
    # Add any other date formats you might use in your markdown files
    formats_to_try = [
        '%Y-%m-%d',  # eg. 2023-12-25
        '%d-%m-%Y',  # eg. 25-12-2023
        '%B %d, %Y', # eg. December 25, 2023
    ]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    app.logger.warning(f"Could not parse date '{date_str}' with any known format. Using a default date.")
    return datetime(1970, 1, 1)

app.config['FLATPAGES_META_PARSERS'] = {
    'date': _parse_date_flexible
}
flatpages = FlatPages(app)

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

def send_email(subject, body, recipient):
    """
    A robust function to send an email using smtplib, bypassing Flask-Mail.
    This uses the known-working connection logic.
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = recipient

    try:
        context = ssl.create_default_context()
        if app.config.get('MAIL_USE_SSL'):
            with smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], context=context) as server:
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                server.send_message(msg)
        else: # Fallback for TLS, though SSL is preferred
            with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
                server.starttls(context=context)
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                server.send_message(msg)
        return True, None
    except Exception as e:
        return False, e

def _process_translated_list(data_list: list, lang: str) -> list:
    """Helper function to process a list of items with translations."""
    processed_list = []
    for item in data_list:
        # Copy all non-translation keys
        processed_item = {k: v for k, v in item.items() if k != 'translations'}
        # Get translations for the current language, falling back to English
        translations = item.get('translations', {})
        lang_data = translations.get(lang, translations.get('en', {}))
        processed_item.update(lang_data)
        processed_list.append(processed_item)
    return processed_list

def load_site_data(lang: str) -> dict:
    """Loads and combines site data from JSON files for a given language."""
    # Construct absolute paths to data files to avoid issues with the working directory.
    base_path = app.root_path
    shared_data_path = os.path.join(base_path, 'data', 'shared_data.json')
    lang_data_path = os.path.join(base_path, 'data', f'{lang}.json')

    # Load shared data that is not language-specific
    with open(shared_data_path, 'r', encoding='utf-8') as f:
        shared_data = json.load(f)

    # Load language-specific data
    with open(lang_data_path, 'r', encoding='utf-8') as f:
        lang_data = json.load(f)

    # Merge the shared data and the language-specific data
    lang_data['projects'] = [{**p, **lang_data['projects'][i]} for i, p in enumerate(shared_data['projects'])]
    lang_data['education'] = [{**e, **lang_data['education'][i]} for i, e in enumerate(shared_data['education'])]
    lang_data['experience'] = [{**w, **lang_data['experience'][i]} for i, w in enumerate(shared_data['experience'])]
    lang_data['publications'] = [{**p, **lang_data['publications'][i]} for i, p in enumerate(shared_data['publications'])]
    lang_data['social_links'] = shared_data['social_media']
    return lang_data

@app.context_processor
def inject_now():
    """Injects the current year into all templates."""
    return {'now': datetime.now(timezone.utc)}

# Default route redirects to English or the session language if set
@app.route('/')
def default():
    lang = session.get('lang', 'en')
    return redirect(f'/{lang}/')

# Route to set language in session and redirect back
@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    # Redirect to the referring page or home if not available
    # For a single-page app, always redirect to the root for the new language.
    return redirect(url_for('index', lang=lang))

@app.route('/<lang>/', methods=['GET', 'POST'])
def index(lang):
    if lang not in ['en', 'es']:
        return "Language not supported", 404

    # Set locale for date formatting so month names appear in the correct language.
    # This requires the corresponding locale to be installed on your server.
    try:
        if lang == 'es':
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        else:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    except locale.Error:
        app.logger.warning(f"Locale for '{lang}' not supported on this system. Using default.")

    session['lang'] = lang

    # --- Load all site data from JSON files ---
    try:
        site_data = load_site_data(lang)
    except FileNotFoundError:
        return f"Data file for language '{lang}' not found.", 404

    # --- Fetch latest blog posts for the news section ---
    all_posts = [p for p in flatpages if p.path.startswith(lang + '/') and 'date' in p.meta]
    # Sort by the 'date' attribute, which is now a datetime object
    all_posts.sort(key=lambda item: item.meta['date'], reverse=True)
    latest_posts = all_posts[:3]  # Show the 3 most recent posts

    form = ContactForm()
    if form.validate_on_submit():
        try:
            email_body = f"From: {form.name.data} <{form.email.data}>\n\n{form.message.data}"
            success, error = send_email("New Contact Form Submission", email_body, app.config['MAIL_USERNAME'])
            if success:
                flash('Your message has been sent successfully!' if lang == 'en' else '¡Tu mensaje ha sido enviado con éxito!', 'success')
            else:
                raise error
        except Exception as e:
            # It's safer to log the actual error for debugging and show a generic message to the user.
            app.logger.error(f"Mail sending failed: {e}")
            error_message = 'An error occurred while sending your message. Please try again later.'
            error_message_es = 'Ocurrió un error al enviar tu mensaje. Por favor, inténtalo de nuevo más tarde.'
            flash(error_message if lang == 'en' else error_message_es, 'danger')
        # Redirect back to the index page for the current language after form submission.
        return redirect(url_for('index', lang=lang))

    if lang == 'es':
        form.name.label.text = 'Nombre'
        form.email.label.text = 'Correo Electrónico'
        form.message.label.text = 'Mensaje'
        form.submit.label.text = 'Enviar'

    # Pass all the prepared data to the index.html template
    # Render the single, unified index.html template
    return render_template('index.html',
                           lang=lang,
                           form=form,
                           about=site_data['about'],
                           projects=site_data['projects'],
                           education=site_data['education'],
                           experience=site_data['experience'],
                           ui_text=site_data['ui_text'],
                           latest_posts=latest_posts,
                           publications=site_data['publications'],
                           social_links=site_data['social_links'])

@app.route('/<lang>/cv/pdf')
def generate_cv_pdf(lang):
    """Generates a PDF version of the CV."""
    if lang not in ['en', 'es']:
        return "Language not supported", 404

    try:
        site_data = load_site_data(lang)
    except FileNotFoundError:
        return f"Data file for language '{lang}' not found.", 404

    # Use CV-specific profile text if available to ensure a professional tone
    if 'cv_title' in site_data['about']:
        site_data['about']['title'] = site_data['about']['cv_title']
    if 'cv_intro' in site_data['about']:
        site_data['about']['intro'] = site_data['about']['cv_intro']

    # Render the CV HTML template with the necessary data
    rendered_html = render_template('cv.html',
                                    lang=lang,
                                    about=site_data['about'],
                                    ui_text=site_data['ui_text'],
                                    education=site_data['education'],
                                    experience=site_data['experience'],
                                    projects=site_data['projects'],
                                    publications=site_data['publications'],
                                    social_links=site_data['social_links'],
                                    skills=site_data.get('skills', []))

    # Use WeasyPrint to generate the PDF from the rendered HTML
    pdf = HTML(string=rendered_html).write_pdf()

    # Return the PDF as a downloadable file
    return pdf, 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline; filename="Fabricio_Mendoza_CV.pdf"'
    }

@app.route('/<lang>/blog/')
def blog(lang):
    session['lang'] = lang
    lang_data_path = os.path.join(app.root_path, 'data', f'{lang}.json')

    with open(lang_data_path, 'r', encoding='utf-8') as f:
        ui_text = json.load(f)['ui_text']
    # Get all pages, filter by language, and sort by date from newest to oldest
    posts = [p for p in flatpages if p.path.startswith(lang + '/') and 'date' in p.meta]
    posts.sort(key=lambda item: item.meta['date'], reverse=True)
    return render_template('blog.html', lang=lang, posts=posts, ui_text=ui_text)


@app.route('/<lang>/blog/<path:path>/')
def post(lang, path):
    session['lang'] = lang
    lang_data_path = os.path.join(app.root_path, 'data', f'{lang}.json')

    with open(lang_data_path, 'r', encoding='utf-8') as f:
        ui_text = json.load(f)['ui_text']
    # The path for a post is its filename (e.g., 'my-first-post')
    # We need to construct the full path that FlatPages uses
    full_path = f'{lang}/{path}'
    post = flatpages.get_or_404(full_path)
    return render_template('post.html', lang=lang, post=post, ui_text=ui_text)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

if __name__ == '__main__':
    app.run(debug=True)
