from flask import Blueprint, jsonify, request
from data import posts_data, comments_data
from flask import Response, render_template

from manager import reply_to_comments, create_content_to_post, event_stream, transfer_tokens
from storage import get_updates


api = Blueprint('api', __name__)


@api.route('/update')
def update_page():
    return render_template('updates.html')

@api.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


@api.route('/post-created', methods=['POST'])
def post_created():
    posts_data[request.json['post_id']] = request.json
    return jsonify({'message': 'Post created successfully'})

@api.route('/post-insights', methods=['POST'])
def post_insights():
    print(request.json)
    reply = reply_to_comments(request.json)
    return jsonify({'message': 'Post insights received successfully', 'reply': reply})

@api.route('/create-post', methods=['GET'])
def create_post():
    new_post = create_content_to_post()
    return jsonify(new_post)

@api.route('/fund-transfer', methods=['POST'])
def fund_transfer():
    transfer_tokens(request.json)
    return jsonify({'message': 'Fund transfer completed'})


@api.route('/updates')
def get_updates_api():
    """API endpoint to get updates"""
    updates = get_updates()
    return jsonify(updates)
