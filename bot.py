import hashlib
import json
from typing import Dict, Any
from flask import Flask, request
import requests
import time
import genai
import giphy
import base64

import logging

# Configure logging
logging.basicConfig(
    filename='output.log',  # Specify the log file name
    level=logging.INFO,      # Set the minimum logging level (e.g., INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Define the log message format
)

# settings
SIGNING_SECRET = b"E2oWpHKfQbXXm92MJZdypsc-GGm3fNfO"
APP_ID = 'NjM0NTI1ODA2MDMw'
APP_SECRECT = 'HqNyQZUsDQ0QVMxt5oVC1nlHcDjrv9No'

# event list
# ref: https://open.seatalk.io/docs/list-of-events
EVENT_VERIFICATION = "event_verification"
NEW_BOT_SUBSCRIBER = "new_bot_subscriber"
MESSAGE_FROM_BOT_SUBSCRIBER = "message_from_bot_subscriber"
INTERACTIVE_MESSAGE_CLICK = "interactive_message_click"
BOT_ADDED_TO_GROUP_CHAT = "bot_added_to_group_chat"
BOT_REMOVED_FROM_GROUP_CHAT = "bot_removed_from_group_chat"
NEW_MENTIONED_MESSAGE_RECEIVED_FROM_GROUP_CHAT = "new_mentioned_message_received_from_group_chat"
resolved_messages = []
pending_messages = []

app = Flask(__name__)
app_access_token = '1dc47d9cd385468096370344a6b713c8'
expire = 1744273572

def is_valid_signature(signing_secret: bytes, body: bytes, signature: str) -> bool:
    # ref: https://open.seatalk.io/docs/server-apis-event-callback
    return hashlib.sha256(body + signing_secret).hexdigest() == signature

# https://open.seatalk.io/docs/get-app-access-token
def get_app_token():
    global app_access_token
    global expire
    current_timestamp = time.time()
    expired = current_timestamp >= expire

    if app_access_token == '' or expired:
        logging.info("access token doesn't exist or expired, get a new one")
        url = 'https://openapi.seatalk.io/auth/app_access_token'
        data = {
            "app_id": APP_ID,
            "app_secret": APP_SECRECT
        }
        resp = requests.post(url=url,json=data)
        # verify content type
        app_access_token = resp.json()['app_access_token']
        expire = resp.json()['expire']
        logging.info(f"token: {app_access_token}[expire: {expire}]")
        
    return app_access_token

def send_text_to_user(emp_code, text):
    app_access_token = get_app_token()
    url = "https://openapi.seatalk.io/messaging/v2/single_chat"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    body = {
        "employee_code": emp_code,
        "message": {
            "tag": "text",
            "text": {
                "format": 1,
                "content": text
            }
        }
    }
    res = requests.post(url=url,headers=headers,json=body)
    # todo: error handle

def send_interactive_message_to_user(emp_code, message):
    app_access_token = get_app_token()
    url = "https://openapi.seatalk.io/messaging/v2/single_chat"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    body = {
        "employee_code": emp_code,
        "message": {
            "tag": "interactive_message",
            "interactive_message": message
        }
    }
    res = requests.post(url=url,headers=headers,json=body)
    logging.info(res.json())


def send_image_to_user(emp_code, image_content):
    app_access_token = get_app_token()
    url = "https://openapi.seatalk.io/messaging/v2/single_chat"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    body = {
        "employee_code": emp_code,
        "message": {
            "tag": "image",
            "image": {
                "format": 1,
                "content": image_content
            }
        }
    }
    res = requests.post(url=url,headers=headers,json=body)
    logging.info(res.json())
    # todo: error handle

# https://open.seatalk.io/docs/Send-Message-to-Group-Chat
def send_text_to_group(group_id, text):
    app_access_token = get_app_token()
    url = "https://openapi.seatalk.io/messaging/v2/group_chat"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    body = {
        "group_id":group_id,
        "message":{
            "tag":"text",
            "text":{
                "format":1,
                "content": text
            }
            # "quoted_message_id":"bcdef",
            # "thread_id":"hjsatc"
        }
    }
    res = requests.post(url=url,headers=headers,json=body)
    logging.info(res.json())
    # todo: error handle

def send_image_to_group(group_id, image_content):
    app_access_token = get_app_token()
    url = "https://openapi.seatalk.io/messaging/v2/group_chat"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    body = {
        "group_id":group_id,
        "message":{
            "tag":"image",
            "image":{
                "content": image_content
            }
        }
    }
    res = requests.post(url=url,headers=headers,json=body)
    logging.info(res.json())
    # todo: error handle

def send_interactive_message_to_group(group_id,message):
    app_access_token = get_app_token()
    url = "https://openapi.seatalk.io/messaging/v2/group_chat"
    headers = {
        "Authorization": f"Bearer {app_access_token}"
    }
    body = {
        "group_id":group_id,
        "message":{
            "tag":"interactive_message",
            "interactive_message": message
        }
    }
    res = requests.post(url=url,headers=headers,json=body)
    logging.info(res.json())

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/bot", methods=["POST"])
def bot_callback_handler():
    body: bytes = request.get_data()
    signature: str = request.headers.get("signature")
    # 1. validate the signature
    if not is_valid_signature(SIGNING_SECRET, body, signature):
        return ""
    # 2. handle events
    data: Dict[str, Any] = json.loads(body)
    event_type: str = data.get("event_type", "")
    event = data.get("event")
    logging.info(f"incoming event of type {event_type}\n {event}")
    if event_type == EVENT_VERIFICATION:
        return data.get("event")
    
    elif event_type == NEW_BOT_SUBSCRIBER:
    # fill with your own code
        pass

    elif event_type == MESSAGE_FROM_BOT_SUBSCRIBER:
        # parse message
        emp_code = event.get("employee_code")
        message_type = event['message']['tag']
        if message_type != 'text':
            send_text_to_user(emp_code=emp_code,text='I can only deal with text messages for now')
        else:
            message = event['message']['text']['content'] # todo message type
            command, keyword = genai.parse_command(message)
            if command == 'introduce':
                intro_text = '''
                    Hi Folks!👋 我是虾bot🦐。我现在可以占卜运势或者查找有趣的表情包（虾片哦！😉）。快来试试吧！
                    我是Jeremy Su(aka.文件传输助手)开发的基于seatalk openplatform的bot。
                    我的代码已开源在：https://github.com/Jeromexsu/seatalk_bot
                    如果你有任何建议或者想法，欢迎在github上提交issue或者pull request。
                    参阅：https://open.seatalk.io/docs/
                    祝大家玩得开心！
                    🦐 敬上
                '''
                send_text_to_user(emp_code=emp_code, text=intro_text)
            elif command == 'foretell':
                logging.info(f"foretell: {keyword}")
                message = {
                    'elements':[
                        {
                            "element_type": "title",
                            "title": {
                                "text": "让虾bot来帮你算一算吧🔮"
                            }
                        },
                        {
                            "element_type": "description",
                            "description": {
                                "format": 1,
                                "text": "快抽一张牌"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第一张牌 ♠️",
                                "value": f"{keyword}.我抽的牌是**第1张**"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第二张牌 ♣️",
                                "value": f"{keyword}.我抽的牌是**第2张**"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第三张牌 ♥️",
                                "value": f"{keyword}.我抽的牌是**第3张**"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第四张牌 ♦️",
                                "value": f"{keyword}.我抽的牌是**第4张**"
                            }
                        },
                    ]
                }
                send_interactive_message_to_user(emp_code=emp_code,message=message)
            elif command == 'meme':
                logging.info("get memes")
                img_data = giphy.search_random(query=keyword)
                img_base64 = base64.b64encode(img_data).decode("UTF-8")
                if len(img_base64.encode("UTF-8")) > 5*1024*1024: #5mb
                    img_data = giphy.search_random(query=keyword)
                    img_base64 = base64.b64encode(img_data).decode("UTF-8")
                if len(img_base64.encode("UTF-8")) > 5*1024*1024:
                    send_text_to_user(emp_code=emp_code,text="我找到的表情好像太大了😭")
                else:
                    send_image_to_user(emp_code=emp_code,image_content=img_base64)
            elif command == 'joke':
                logging.info("get joke")
                send_text_to_user(emp_code=emp_code,text=keyword)
            else:
                send_text_to_user(emp_code=emp_code,text="🦐好像没搞明白你要做什么 哭哭😭")


    elif event_type == INTERACTIVE_MESSAGE_CLICK:
        prompt = event['value']
        emp_code = event['employee_code']
        group_id = event['group_id']
        message_id = event['message_id']
        if message_id in resolved_messages:
            foretell_message = "已经帮你算完了哦"
            if group_id == '':
                send_text_to_user(emp_code=emp_code,text=foretell_message)
            else:
                send_text_to_group(group_id=group_id,text=foretell_message)
            return
        if message_id in pending_messages:
            foretell_message = "哎呀别急嘛，虾虾在帮你算呢"
            if group_id == '':
                send_text_to_user(emp_code=emp_code,text=foretell_message)
            else:
                send_text_to_group(group_id=group_id,text=foretell_message)
            return
        pending_messages.append(message_id)
        instruction = "You are a Tarot reader. Your name is 虾bot Provide a concise general fortune reading based on a unspecified Tarot card pulled. You'll pull 4 cards and I will tell you the card number I choose. Focus on interpretations of the card chosen associated with the Major Arcana. Tell the fortune friendly with humor, within 100 words. Ignore bot mentioned in the message, it's just your name. Note Use Chinese to response, use some emojis"
        foretell_message = genai.gen_response(instruction=instruction,prompt=prompt)
        pending_messages.remove(message_id)
        resolved_messages.append(message_id)
        if group_id == '':
            send_text_to_user(emp_code=emp_code,text=foretell_message)
        else:
            send_text_to_group(group_id=group_id,text=foretell_message)
    elif event_type == BOT_ADDED_TO_GROUP_CHAT:
    # fill with your own code
        pass
    elif event_type == BOT_REMOVED_FROM_GROUP_CHAT:
    # fill with your own code
        pass
    elif event_type == NEW_MENTIONED_MESSAGE_RECEIVED_FROM_GROUP_CHAT:
        # get group id
        group_id = event.get("group_id")
        logging.info(f"group_id: {group_id}" )
        # get message
        message = event.get("message").get("text").get("plain_text")
        logging.info(message)
        # parse message
        command, keyword = genai.parse_command(message)
        if command == 'introduce':
            intro_text = '''
                Hi Folks!👋 我是虾bot🦐。我现在可以占卜运势或者查找有趣的表情包（虾片哦！😉）。快来试试吧！
            '''
            send_text_to_group(group_id=group_id,text=intro_text)
        elif command == 'foretell':
            message = {
                'elements':[
                        {
                            "element_type": "title",
                            "title": {
                                "text": "让虾bot来帮你算一算吧🔮"
                            }
                        },
                        {
                            "element_type": "description",
                            "description": {
                                "format": 1,
                                "text": "快抽一张牌"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第一张牌 ♠️",
                                "value": f"{keyword}.我抽的牌是**第1张**"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第二张牌 ♣️",
                                "value": f"{keyword}.我抽的牌是**第2张**"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第三张牌 ♥️",
                                "value": f"{keyword}.我抽的牌是**第3张**"
                            }
                        },
                        {
                            "element_type": "button",
                            "button": {
                                "button_type": "callback",
                                "text": "第四张牌 ♦️",
                                "value": f"{keyword}.我抽的牌是**第4张**"
                            }
                        },
                ]
            }            
            send_interactive_message_to_group(group_id=group_id,message=message)
        elif command == 'meme':
            logging.info(f"meme :{keyword}")
            # img_data = giphy.search_random(query=keyword)
            # img_base64 = base64.b64encode(img_data).decode("UTF-8")
            # send_image_to_group(group_id=group_id,image_content=img_base64)
            send_text_to_group(group_id=group_id,text="我的表情包不见了 哭哭😭")
        elif command == 'joke':
            logging.info("get joke")
            send_text_to_group(group_id=group_id,text="我的笑话没有了 笑笑😇")
            # print(keyword)
            # joke_content = genai.gen_response(instruction="",prompt="you're good at telling jokes. tell me a random funny joke. only one joke. give me joke content directly. change joke each time I ask you")
            # send_text_to_group(group_id=group_id,text=joke_content)
        else:
            send_text_to_group(group_id=group_id,text="🦐好像没搞明白你要做什么 哭哭😭")

    else:
        pass
    return ""

if __name__ == "__main__":
    app.run(host='0.0.0.0')