import os
from flask import Flask, render_template, redirect, session, url_for, request, flash
import locale
from flask_flatpages import FlatPages, pygments_style_defs
from datetime import datetime, timezone
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong, random value in production

# Mail Configuration - IMPORTANT: Set these as environment variables for security
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')

mail = Mail(app)

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

# Data for the home page with translations
home_data = {
    'en': {
        'title': "Hi, I'm Fabricio Mendoza",
        'subtitle': "This is my personal website showcasing my work and interests.",
        'button_text': "View My Work",
        'button_url_key': 'projects'
    },
    'es': {
        'title': "Hola, soy Fabricio Mendoza",
        'subtitle': "Este es mi sitio web personal donde muestro mi trabajo e intereses.",
        'button_text': "Ver Mis Proyectos",
        'button_url_key': 'projects'
    }
}

# Data for the about section with translations
about_data = {
    'en': {
        'title': 'About Me',
        'intro': "I'm a Ph.D. candidate in Computing Science based in Glasgow.",
        'details': "My research focuses on computational complexity, and I have a passion for building web applications and exploring new technologies. I enjoy tackling complex problems and turning ideas into reality.",
        'cv_button': 'Download CV',
        'cv_filename': 'cv.pdf'
    },
    'es': {
        'title': 'Sobre Mí',
        'intro': 'Soy un candidato a Doctor en Ciencias de la Computación en Glasgow.',
        'details': 'Mi investigación se centra en la complejidad computacional, y me apasiona construir aplicaciones web y explorar nuevas tecnologías. Disfruto abordando problemas complejos y convirtiendo ideas en realidad.',
        'cv_button': 'Descargar CV',
        'cv_filename': 'cv.pdf'
    }
}

# A list of project data with translations to avoid repetition
projects_data = [
    {
        'technologies': ['Python', 'Flask', 'JavaScript', 'PostgreSQL'],
        'image': 'img/project-one.png',
        'live_url': 'https://example.com',
        'repo_url': 'https://github.com/mendoza95/project-one',
        'translations': {
            'en': {
                'id': 'project-one',
                'name': 'My Awesome App',
                'description': 'A web application that solves a real-world problem by leveraging modern technologies.',
            },
            'es': {
                'id': 'proyecto-uno',
                'name': 'Mi Aplicación Increíble',
                'description': 'Una aplicación web que resuelve un problema del mundo real aprovechando tecnologías modernas.',
            }
        }
    },
    {
        'technologies': ['Python', 'Pandas', 'Plotly', 'Dash'],
        'image': 'img/project-two.png',
        'live_url': None,
        'repo_url': 'https://github.com/mendoza95/project-two',
        'translations': {
            'en': {
                'id': 'project-two',
                'name': 'Data Analysis Dashboard',
                'description': 'An interactive dashboard for visualizing complex datasets.',
            },
            'es': {
                'id': 'proyecto-dos',
                'name': 'Dashboard de Análisis de Datos',
                'description': 'Un dashboard interactivo para visualizar conjuntos de datos complejos.',
            }
        }
    }
]

# Data for the education page with translations
education_data = [
    {
        'institution_logo': 'img/uofg_logo.png', # You will need to add this logo to your static/img folder
        'start_year': 2022,
        'end_year': 2026,
        'institution_url': 'https://www.gla.ac.uk/',
        'translations': {
            'en': {
                'degree': 'Ph.D. in Computing Science',
                'institution': 'University of Glasgow',
                'location': 'Glasgow, UK',
                'description': 'Currently a Ph.D. candidate focusing on the complexity of the b-chromatic number and related problems. My work involves searching polynomial-time/np-hardness results on a the b-chromatic number problem and other variants.'
            },
            'es': {
                'degree': 'Doctorado en Ciencias de la Computación',
                'institution': 'Universidad de Glasgow',
                'location': 'Glasgow, Reino Unido',
                'description': 'Actualmente candidato a Doctorado con un enfoque en complejidad computacional del problem the coloreo b-chromatic y otras variantes. Mi trabajo implica buscar soluciones polinomiales/np-difíciles en el problema del número de colores b-chromatic y otras variantes.'
            }
        }
    },
     {
         'institution_logo': 'img/previous_uni_logo.png',
         'start_year': 2018,
         'end_year': 2020,
         'institution_url': 'https://nidtec.pol.una.py',
         'translations': {
             'en': { 'degree': 'M.Sc. in Computer Science,', 
                    'institution': 'National University of Asunción, Nucleo de Investigación y Desarrollo Tecnológico de la Facultad Politecnica', 
                    'location': 'San Lorenzo, Paraguay', 
                    'description': 'Course focused on general aspects of computer science and research. My master thesis was focused on unsupervised machine learning, spectral graph theory, and communication complexity.' },
             'es': { 'degree': 'Maestria en Ciencias de la Computación', 
                    'institution': 'Universidad Nacional de Asunción, Nucleo de Investigación y Desarrollo Tecnológico de la Facultad Politecnica', 
                    'location': 'San Lorenzo, Paraguay', 
                    'description': 'Curso enfocado en aspectos generales de las ciencias de la computación y la investigación. Mi tesis de máster se centró en el aprendizaje automático no supervisado, la teoría espectral de grafos y la complejidad de la comunicación.' }
         }
     },
    {
        'institution_logo': 'img/previous_highschool_logo.png',
        'start_year': 2013,
        'end_year': 2017,
        'institution_url': 'https://www.pol.una.py',
        'translations': {
            'en': {
                'degree': 'B.Sc. in Computer Science',
                'institution': 'National University of Asunción, Polytechnic School',
                'location': 'San Lorenzo, Paraguay',
                'description': 'Course focused on computer science fundamentals, mathematics, and programming. Graduated with a strong foundation in software engineering.'
            },
            'es': {
                'degree': 'Licenciatura en Ciencias de la Computación, Facultad Politécnica',
                'institution': 'Universidad Nacional de Asunción',
                'location': 'San Lorenzo, Paraguay',
                'description': 'Curso enfocado en los fundamentos de la informática, las matemáticas y la programación. Me gradué con una sólida base en ingeniería de software.'
            }
        }
    }
]

# Data for work experience with translations
work_experience_data = [
    {
        'company_logo': 'img/company_logo.png', # You will need to add this logo to your static/img folder
        'start_date': 'Jan 2023',
        'end_date': 'Present',
        'company_url': 'https://www.gla.ac.uk/',
        'translations': {
            'en': {
                'role': 'Graduate Teaching Assistant',
                'company': 'School of Computing Science, University of Glasgow',
                'location': 'Glasgow, UK',
                'description': 'I am in charge of running lab tutorials for the undergraduate courses of Algorithmic foundations and Algorithms and Data Structures. In algorithmic foundations, students learn about discrete mathematics, proof methods and graphs theory. In Algorithms and Data Structures, students learn about sorting algorithms, complexity analysis and data structures such as linked lists and trees.'
            },
            'es': {
                'role': 'Asistente de Enseñanza Graduado',
                'company': 'Escuela de Ciencias de la Computación, Universidad de Glasgow',
                'location': 'Glasgow, Reino Unido',
                'description': 'Soy responsable de dirigir los tutoriales de laboratorio para los cursos de pregrado de Fundamentos Algorítmicos y Algoritmos y Estructuras de Datos. En Fundamentos Algorítmicos, los estudiantes aprenden sobre matemáticas discretas, métodos de prueba y teoría de grafos. En Algoritmos y Estructuras de Datos, los estudiantes aprenden sobre algoritmos de ordenamiento, análisis de complejidad y estructuras de datos como listas enlazadas y árboles.'
            }
        }
    },
    {
        'company_logo': 'img/previous_company_logo.png',
        'start_date': 'Feb 2021',
        'end_date': 'Feb 2022',
        'company_url': 'https://nidtec.pol.una.py',
        'translations': {
            'en': {
                'role': 'Data Mining Analyst',
                'company': 'Nucleo S.A., Paraguay',
                'location': 'Asuncion, Paraguay',
                'description': 'I was in charge of implementing new techniques for performing feature selection in a churn prediction model. My weekly duties were reading articles about the subject and coding the proposed solutions in the Apache Spark cloud with PySpark. I was also in charge of researching out-of-the-box approaches to boost the current performance model. I mainly worked with a state-of-the-art algorithm for performing feature selection called Minimum Redundancy Maximum Relevance (mRMR). Details of the implementation can be found here: https://github.com/mendoza95/mRMR.'
            },
            'es': {
                'role': 'Analista de Minería de Datos',
                'company': 'Nucleo S.A., Paraguay',
                'location': 'Asunción, Paraguay',
                'description': 'Fui responsable de implementar nuevas técnicas para realizar la selección de características en un modelo de predicción de abandono. Mis tareas semanales consistían en leer artículos sobre el tema y codificar las soluciones propuestas en la nube de Apache Spark con PySpark. También me encargaba de investigar enfoques innovadores para mejorar el rendimiento del modelo actual. Trabajé principalmente con un algoritmo de vanguardia para realizar la selección de características llamado Minimum Redundancy Maximum Relevance (mRMR). Los detalles de la implementación se pueden encontrar aquí:'
            }
        }
    },
    {
        'company_logo': 'img/previous_internship_logo.png',
        'start_date': 'Sep 2018',
        'end_date': 'Dec 2020',
        'company_url': 'https://nidtec.pol.una.py',
        'translations': {
            'en': {
                'role': 'Teaching Assistant',
                'company': 'National University of Asungion, Engeering School, Paraguay',
                'location': 'San Lorenzo, Paraguay',
                'description': 'I have been a teaching assistant on the course of algorithms on the undergraduate course of Mechatronic Engineering. My weekly duties were preparing classes notes on undergraduate topics such as sorting algorithms, divide and conquer algorithms, greedy algorithms, dynamic programming, linear programming, fundamental graph algorithms and the game tree and alpha-beta pruning algorithms.'
            },
            'es': {
                'role': 'Asistente de Enseñanza',
                'company': 'Universidad Nacional de Asunción, Facultad de Ingeniería, Paraguay',
                'location': 'San Lorenzo, Paraguay',
                'description': 'He sido asistente de enseñanza en el curso de algoritmos del curso de pregrado de Ingeniería Mecatrónica. Mis tareas semanales consistían en preparar notas de clase sobre temas de pregrado como algoritmos de ordenamiento, algoritmos de divide y vencerás, algoritmos codiciosos, programación dinámica, programación lineal, algoritmos fundamentales de grafos y los algoritmos de árbol de juego y poda alfa-beta.'
            }
        }
    }
]

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

    # --- Gather all data for the page ---
    home_content = home_data.get(lang, home_data['en'])
    about_content = about_data.get(lang, about_data['en'])

    # Refactored data processing to a helper function to avoid repetition
    processed_projects = _process_translated_list(projects_data, lang)
    processed_education = _process_translated_list(education_data, lang)
    processed_experience = _process_translated_list(work_experience_data, lang)

    # --- Fetch latest blog posts for the news section ---
    all_posts = [p for p in flatpages if p.path.startswith(lang + '/') and 'date' in p.meta]
    # Sort by the 'date' attribute, which is now a datetime object
    all_posts.sort(key=lambda item: item.meta['date'], reverse=True)
    latest_posts = all_posts[:3]  # Show the 3 most recent posts

    form = ContactForm()
    if form.validate_on_submit():
        try:
            msg = Message("New Contact Form Submission from your Website",
                          recipients=[os.environ.get('MAIL_USERNAME')]) # Sends to your configured email
            msg.body = f"From: {form.name.data} <{form.email.data}>\n\n{form.message.data}"
            mail.send(msg)
            flash('Your message has been sent successfully!' if lang == 'en' else '¡Tu mensaje ha sido enviado con éxito!', 'success')
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
    return render_template(f'{lang}/index.html',
                           lang=lang,
                           form=form,
                           home=home_content,
                           about=about_content,
                           projects=processed_projects,
                           education=processed_education,
                           experience=processed_experience,
                           latest_posts=latest_posts)

@app.route('/<lang>/blog/')
def blog(lang):
    session['lang'] = lang
    # Get all pages, filter by language, and sort by date from newest to oldest
    posts = [p for p in flatpages if p.path.startswith(lang + '/') and 'date' in p.meta]
    posts.sort(key=lambda item: item.meta['date'], reverse=True)
    return render_template(f'{lang}/blog.html', lang=lang, posts=posts)


@app.route('/<lang>/blog/<path:path>/')
def post(lang, path):
    session['lang'] = lang
    # The path for a post is its filename (e.g., 'my-first-post')
    # We need to construct the full path that FlatPages uses
    full_path = f'{lang}/{path}'
    post = flatpages.get_or_404(full_path)
    return render_template(f'{lang}/post.html', lang=lang, post=post)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

if __name__ == '__main__':
    app.run(debug=True)
