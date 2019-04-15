#!/usr/bin/env python

from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import config
from rail.parser import FileLoader
from rail.route import Route

# App config.
DEBUG = True
app = Flask(__name__, static_url_path='/static')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = config.SECRET

_map = FileLoader().load(config.DATA_FILE)
route = Route(_map)
    
class QueryForm(Form):
  query = TextField('Query:', validators=[validators.required()])

  @app.route("/", methods=['GET', 'POST'])
  def query():
    form = QueryForm(request.form)

    if request.method == 'POST':
      query=request.form['query']

      if form.validate():
        try:
          path = route.query(query)
          flash([query] + path)
        except Exception as e:
          flash([query] + ['Error: %s' % str(e)])
    else:
      flash(['Error: All the fields are required.'])

    return render_template('route.html', form=form, examples=config.EXAMPLES)

if __name__ == "__main__":
  app.run()
