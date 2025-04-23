import base64
import random
import requests
from urllib.parse import urlparse, parse_qs

def convert_post_link(url):
    """
    Extract Facebook post ID from various URL formats
    """
    try:
        p = urlparse(url)
        parts = p.path.split('/')
        if 'posts' in parts:
            i = parts.index('posts')
            return f"{parts[i-1]}_{parts[i+1]}"
        if 'story.php' in p.path:
            fbid = parse_qs(p.query).get('story_fbid', [None])[0]
            return f"{parts[1]}_{fbid}"
        return parts[-1]
    except:
        return None

def extract_comment_id_from_url(url):
    """
    Extract Facebook comment ID from a comment URL
    """
    try:
        p = urlparse(url)
        eid = parse_qs(p.query).get('comment_id', [None])[0]
        dec = base64.b64decode(eid).decode()
        return dec.split("_")[-1]
    except:
        return None

def react_to_post(token, post_id, reaction_type="LIKE"):
    """
    Add a reaction to a Facebook post
    """
    try:
        url = f"https://graph.facebook.com/v19.0/{post_id}/reactions"
        res = requests.post(url, params={"type": reaction_type, "access_token": token})
        return res.json()
    except Exception as e:
        print(f"Error reacting to post: {e}")
        return None

def react_to_comment(token, comment_id, reaction_type="LIKE"):
    """
    Add a reaction to a Facebook comment
    """
    try:
        url = f"https://graph.facebook.com/v19.0/{comment_id}/reactions"
        res = requests.post(url, params={"type": reaction_type, "access_token": token})
        return res.json()
    except Exception as e:
        print(f"Error reacting to comment: {e}")
        return None
