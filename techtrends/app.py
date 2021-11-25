import logging # NOTE: This import is needed to the logging features
import sqlite3
import sys

from datetime import datetime #  NOTE: This import is needed for logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

connection_count = 0

def current_time():
    return datetime.now().strftime('%m/%d/%Y, %H:%M:%S')

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      # DONE: logging
      message = 'Article under "{}" post ID does not exist.'.format(post_id)
      app.logger.debug('[{}] "{}"'.format(current_time()), message)
      return render_template('404.html'), 404
    else:
      # DONE: logging
      message = 'Article under "{}" post ID retrieved.'.format(post_id)
      app.logger.debug('[{}] "{}"'.format(current_time()), message)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    # DONE: logging
    message = 'About us page retrieved.'
    app.logger.debug('[{}] "{}"'.format(current_time()), message)
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            # DONE: logging
            message = 'New article is created under {} title.'.format(title)
            app.logger.debug('[{}] "{}"'.format(current_time()), message)
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


# DONE: Defining the health endpoint
@app.route('/healthz')
def get_status():
    """
    get the status of the server
    ============================

    Returns
    -------
    json response
    """
    try:
        get_db_connection()
        return app.response_class(
               response=json.dumps({'result':'OK - healthy'}),
               status=200,
               mimetype='application/json')
    except Exception as e:
        return app.response_class(
               response=json.dumps({'result':'ERROR - non healthy'}),
               status=500,
               mimetype='application/json')


# DONE: Defining the metrics endpoint
@app.route('/metrics')
def get_metrics():
    """
    get the metrics from the server
    ===============================

    Returns
    -------
    json response
    """
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) from posts').fetchone()[0]
    return app.response_class(
           response=json.dumps({'post_count': post_count,
                                'db_connection_count': connection_count}),
           status=200,
           mimetype='application/json')


# start the application on port 3111
if __name__ == "__main__":
    # Debug logging to a console
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [stderr_handler, stdout_handler]
    log_format = '%(asctime)s - %(funcName)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        handlers=handlers)
    # NOTE: The next line is moved right due to indenting error
    app.run(host='0.0.0.0', port='3111')
