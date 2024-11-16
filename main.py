from flask import Flask, jsonify
from dotenv import load_dotenv
from routes import api
from scheduler import run_scheduler
import threading
from flask import render_template, request, redirect, url_for
import os
from manager import agent_created
import data
from importlib import reload
from datetime import datetime
import threading
from storage import save_agent_info, load_agent_info
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.register_blueprint(api, url_prefix='/api')



@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'running'})


@app.route('/')
def home():
    return render_template('home.html')


def run_async_task(coin_name, symbol, total_supply):
    agent_created(coin_name, symbol, total_supply)

@app.route('/create_agent', methods=['POST'])
def create_agent():
    # Get form data
    global agent_info

    agent_info = {
        'coin_name': request.form.get('input1'),
        'symbol': request.form.get('input2'),
        'total_supply': request.form.get('input3'),
        'image_link': request.form.get('input4'),
        'pdf_name': request.files['pdf'].filename,
        'created_at': datetime.now().strftime('%B %d, %Y')
    }
    # Save agent info to file
    save_agent_info(agent_info)


    # Start async task in a simple background thread
    thread = threading.Thread(
        target=run_async_task,
        args=(agent_info['coin_name'], agent_info['symbol'], agent_info['total_supply'])
    )
    thread.daemon = True  # Make thread daemon so it doesn't block program exit
    thread.start()


    # Save PDF file
    # pdf = request.files['pdf']
    # if pdf:
    #     pdf.save(f'uploads/{pdf.filename}')


    return redirect(url_for('agent'))


@app.route('/agent')
def agent():
    reload(data)
    agent_info = load_agent_info()
    return render_template('agent.html',
                           posts_data=data.posts_data,
                           agent_info=agent_info)


def run_flask():
    app.run(host="0.0.0.0", port=5001, debug=True)

def main():
    load_dotenv()

    # Start scheduler in a separate thread
    # scheduler_thread = threading.Thread(target=run_scheduler)
    # scheduler_thread.start()

    # Start Flask app
    run_flask()



if __name__ == "__main__":
    main()
