import os
import redis
from dotenv import load_dotenv

# use the slack bolt library
from slack_bolt import App

# load environment variables
load_dotenv()


# initialize your app with bot token and signing secret
app = App(
     token=os.getenv('slack_bot_token'),
     signing_secret=os.getenv('slack_signing_secret')
)

# function executed when slash command /cubert is used
@app.command("/cubert")
def enter_skills(ack, respond, command):
    ack()
    if "i know nothing about" in command['text'].lower():
        knowledge = command['text'][21:]
        for index in knowledge.split(','):
            # remove knowledge from user's expertise
            deregister_knowledge(index, command['user_name'])
        respond(f"i have removed you from knowing {knowledge}")
    elif "what do i know" in command['text'].lower():
        # list all the things you know
        i_know = what_do_i_know(command['user_name'])
        respond(f"this is what you know about:\n {i_know}")
    elif "what do people know" in command['text'].lower():
        # gives a listing of all subject areas
        respond(f"this is all the things that people know about:\n {what_everyone_knows()}")
    elif "i know" in command['text'].lower():
        # register yourself as knowing something if Yes button is pressed. If No button is pressed,
        # don't store knowledge.
        knowledge = command['text'][7:]
        user = command['user_name']
        respond(
            blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"i have memorized that you know {knowledge}. is this correct?",
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Yes",
                            "emoji": True
                        },
                        "value": f"{knowledge}|{user}",
                        "style": "primary",
                        "action_id": "store_knowledge"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "No",
                            "emoji": True
                        },
                        "value": "no",
                        "action_id": "discard_knowledge"
                    },
                ]
            }
        ])
    elif "who knows" in command['text'].lower():
        # gives a listing of who knows about something
        knowledge = command['text'][10:]
        who = ','.join(["<@" + x + ">" for x in pull_from_redis(knowledge)])
        if who:
            respond(f"*{who}* knows about *{knowledge}*")
        else:
            respond(f"*Nobody* knows about *{knowledge}*")
    elif "knows" in command['text'].lower():
        # memorize that @user knows something if Yes button is pressed. If No button is pressed, then
        # don't memorize the knowledge.
        user = command['text'].split()[0][1:]
        index = len(user) + 8
        knowledge = command['text'][index:]
        respond(
            blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"i have memorized that <@{user}> knows about {knowledge}. is this correct?",
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Yes",
                            "emoji": True
                        },
                        "value": f"{knowledge}|{user}",
                        "style": "primary",
                        "action_id": "store_knowledge",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "No",
                            "emoji": True
                        },
                        "value": "no",
                        "action_id": "discard_knowledge"
                    },

                ]
            }
        ])
    elif command['text'] == "help":
        respond(f" available commands are: \n"
                f" */cubert _i know [thing] or [multiple things separated by ,]_* - register yourself for a mention whenever someone asks about [thing] or [thing1, thing2...]\n"
                f" */cubert _i know nothing about [thing] or [multiple things separated by ,]_* - deregister yourself from mentions about [thing] or [thing1, thing2....]\n"
                f" */cubert _@user knows [thing]_or [multiple things separated by ,]_* - register a user whenever someone asks about [thing] or [thing1, thing2 ....]\n"
                f" */cubert _what do i know_* - list all of the things that you know about\n"
                f" */cubert _who knows about [thing]_* - find a list of people wo know about [thing]\n"
                f" */cubert _what do people know_* - list all the things that people know about\n")
    else:
        respond("sorry! i can't understand what you want. type /cubert help to get usage directions")


# Function to remove knowledge from redis database for the passed in user
def deregister_knowledge(knowledge, user):
    r = connect_to_redis()
    r.lrem(knowledge, 0, user)


# Function to store the knowledge when user presses Yes button.
@app.action("store_knowledge")
def action_yes_click(ack, body, respond):
    ack()
    knowledge = body['actions'][0]['value'].split('|')[0]
    user = body['actions'][0]['value'].split('|')[1]
    for index in knowledge.split(','):
        index.strip()
        push_to_redis(index, user)
    respond(f"I have *memorized* that *<@{user}>* knows *{knowledge}*")


# Function to discard knowledge when user presses No button
@app.action("discard_knowledge")
def action_no_click(ack, body, respond):
    ack()
    respond(f"I have *not* memorized that!")


# Function to return the list of knowledge areas for the user
def what_do_i_know(user):
    i_know = []
    r = connect_to_redis()
    for index in r.keys():
        if user.encode('utf-8') in r.lrange(index, 0, -1):
            i_know.append("- " + index.decode('utf-8'))
    return "\n".join(i_know)


# Function to return all the knowledge areas that exist in the database.
def what_everyone_knows():
    r = connect_to_redis()
    return "\n".join(["- " + x.decode('utf-8') for x in r.keys() if len(x) > 1])


# REDIS DATABASE FUNCTIONS
# connect tot he redis database
def connect_to_redis():
    # connect using a redis pool in order to improve efficiency.
    pool = redis.ConnectionPool(host='localhost', port=6379)
    return redis.Redis(connection_pool=pool)


# Store value into redis database. Key is the knowledge and value is the user(s) that know the knolwedge
def store_to_redis(key, value):
    # open up a connection
    r = connect_to_redis()
    # if that knowledge area exists already (ie the key exists) then don't create a new entry but just
    # append to the existing value the user
    if r.exists(key) and value.encode('utf-8') not in r.get(key):
        value = " " + value
        r.append(key, value.encode('utf-8'))
    # else if that knowledge area exists for this user (ie duplicate) then don't store anything
    elif r.exists(key):
        pass
    else:
        r.set(key, value)


# Get value from Redis
def get_from_redis(key):
    r = connect_to_redis()
    return r.get(key)


# Store or push value to redis
def push_to_redis(key, value):
    r = connect_to_redis()
    value.strip()
    if not r.exists(key):
        r.rpush(key, value)
    elif r.exists(key) and value.encode('utf-8') not in r.lrange(key, 0, -1):
        r.rpush(key, value)


# Pull data from Redis
def pull_from_redis(key):
    r = connect_to_redis()
    return [x.decode('utf-8') for x in r.lrange(key, 0, -1)]


# Return all the keys in redis
def get_all_redis_keys():
    r = connect_to_redis()
    return r.keys().decode('utf-8')


# Start the Cubert app
if __name__ == "__main__":
     app.start(port=int(os.environ.get("PORT", 3000)))