from flask import Flask, render_template, request, redirect, url_for
from crontab import CronTab
import os 

app = Flask(__name__)

# Replace 'administrator' with the desired username
CRON_USER = 'administrator'
# Define the folder where files will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to list files in the uploads folder
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return files

@app.route('/editor')
def editor():
    files = list_files()
    return render_template('editor.html', files=files)

@app.route('/create_file', methods=['POST'])
def create_file():
    new_file_name = request.form['file_name']
    content = request.form['content']

    # Check if the file already exists
    if os.path.isfile(os.path.join(UPLOAD_FOLDER, new_file_name)):
        return "File already exists. Choose a different name."

    # Create and write content to the new file
    with open(os.path.join(UPLOAD_FOLDER, new_file_name), 'w') as file:
        file.write(content)

    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html',files = list_files())

@app.route('/create', methods=['POST'])
def create_cron_job():
    command = request.form.get('command')
    schedule = request.form.get('schedule')
    
    if command and schedule:
        try:
            cron = CronTab(user=CRON_USER)
            job = cron.new(command=command)
            job.setall(schedule)
            job.enable()
            cron.write()
            return redirect(url_for('list_cron_jobs'))
        except Exception as e:
            return str(e)
    
    return "Invalid command or schedule."

@app.route('/list')
def list_cron_jobs():
    try:
        cron = CronTab(user=CRON_USER)
        jobs = list(cron)
        return render_template('list.html', jobs=jobs)
    except Exception as e:
        return str(e)

@app.route('/delete/<int:job_id>')
def delete_cron_job(job_id):
    try:
        cron = CronTab(user=CRON_USER)
        job = cron[job_id]
        cron.remove(job)
        cron.write()
        return redirect(url_for('list_cron_jobs'))
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True,port=5001)
