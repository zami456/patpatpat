from website import create_app
from flask import Flask, render_template, request, url_for, flash



app = create_app()

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
      app.run(debug=True)