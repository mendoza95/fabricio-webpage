from flask import Flask, render_template, redirect

app = Flask(__name__)

# Default route redirects to English
@app.route('/')
def default():
    return redirect('/en/')

@app.route('/<lang>/')
def index(lang):
    return render_template(f'{lang}/index.html', lang=lang)

@app.route('/<lang>/about')
def about(lang):
    return render_template(f'{lang}/about.html', lang=lang)

@app.route('/<lang>/projects')
def projects(lang):
    return render_template(f'{lang}/projects.html', lang=lang)

@app.route('/<lang>/education')
def education(lang):
    return render_template(f'{lang}/education.html', lang=lang)

if __name__ == '__main__':
    app.run(debug=True)
