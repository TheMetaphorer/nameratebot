import bot

__author__ = "Dorian Dore"

def start(subreddit, json_file):
    nmrbot = bot.NameRateBot(
        client_id='',
        client_secret='',
        user_agent='A bot by u/TheMetaphorer',
        username='nameratebot',
        password=''
    )
    nmrbot.run(subreddit, json_file)

