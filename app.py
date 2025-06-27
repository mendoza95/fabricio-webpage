from flask import Flask, render_template, redirect, session, url_for, request

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong, random value in production

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
    next_url = request.referrer or url_for('index', lang=lang)
    return redirect(next_url)

@app.route('/<lang>/')
def index(lang):
    session['lang'] = lang
    return render_template(f'{lang}/index.html', lang=lang)

@app.route('/<lang>/about')
def about(lang):
    session['lang'] = lang
    return render_template(f'{lang}/about.html', lang=lang)

@app.route('/<lang>/projects')
def projects(lang):
    session['lang'] = lang
    return render_template(f'{lang}/projects.html', lang=lang)

@app.route('/<lang>/education')
def education(lang):
    session['lang'] = lang
    return render_template(f'{lang}/education.html', lang=lang)

if __name__ == '__main__':
    app.run(debug=True)
