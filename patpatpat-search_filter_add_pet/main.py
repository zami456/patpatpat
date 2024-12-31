from website import create_app
from flask import Flask, render_template, request, url_for, flash



app = create_app()



if __name__ == '__main__':
      app.run(debug=True)
    