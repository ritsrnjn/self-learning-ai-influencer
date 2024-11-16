# curl --location 'https://hook.eu2.make.com/9mmrxaqepudttp3o18865ktr0nxpz8vj' \
# --header 'Content-Type: application/json' \
# --data '{
#     "caption" : "My portfolio after discovering $BRETT: Nobody'\''s gonna know... they'\''re gonna know!!!!!",
#     "url": "https://zyvdcnaeooqyyujcwkmn.supabase.co/storage/v1/object/public/ai-created-files-public/photo_6174644718344979048_y.jpg?t=2024-11-14T16%3A33%3A43.596Z",
#     "firstComment": "Ritesh-Local-Machine"
# }'


# make a function to do above http call
import requests
import json

def create_new_post(caption, url, firstComment):
    webhook_url = 'https://hook.eu2.make.com/9mmrxaqepudttp3o18865ktr0nxpz8vj'

    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "caption": caption,
        "url": url,
        "firstComment": firstComment
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return response


def reply_to_comment(comment_id, reply):
    webhook_url = 'https://hook.eu2.make.com/pmrt5ew8n6ln2t9t2xopj6woedq2edue'

    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "reply": reply,
        "comment_id": comment_id
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return response