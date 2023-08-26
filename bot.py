from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests, random
import os, logging
from dotenv import load_dotenv


# configuration for the logger, just using for error tracking
logging.basicConfig(filename="debug.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN') 
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')


# list of some contries eg. in-India, us-USA, gb-England, ru-Russia etc.
COUNTRIES = ('in', 'us', 'gb', 'au', 'ca', 'ru', 'fr', 'de', 'it', 'jp', 'cn')

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I am a bot which can help you with weather information and news")

def help(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='HTML', text="\
        <b>List of commands:</b>\n\n\
        /start - restarts the bot\n\
        /help - lists all available commands\n/weather [city name] - shows the weather\n\
        /news - shows random news\n"
    )

def weather(update: Update, context: CallbackContext):
    try:
        # checks if a city name is provided
        if context.args:
            city = ' '.join(context.args)

            # fetches the weather details from the OpenWeather API
            response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}')

            # parses the data as dictionary
            result = response.json()

            # if the response_code is 200, the city exists and we have the data and thus proceed
            if result['cod'] == 200:
                context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='HTML', text=f'\
                    <b>Weather Details of <em>{result["name"]}, {result["sys"]["country"]}</em></b>\n\n<b>\
                    Weather : {result["weather"][0]["main"]}</b> \n\
                    Temperature : {round(result["main"]["temp"]- 273.15, 2)}°C \n\
                    Humidity : {result["main"]["humidity"]} % \n\
                    Pressure :{result["main"]["pressure"]} hPa \n\
                    Wind : {result["wind"]["speed"]} m/s \n\
                    Description : {result["weather"][0]["description"]}'
                )
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=result['message'])
        else:
            update.message.reply_text('Please provide the city name.', reply_markup=ForceReply(selective=True))
    except Exception as err:
        logging.error(err)


def weather_reply(update: Update, context: CallbackContext):
    try:

        # takes the city name as gets the weather data from the API
        city = update.message.text
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}')
        result = response.json()

        if result['cod'] == 200:
            context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='HTML', text=f'\
                <b>Weather Details of <em>{result["name"]}, {result["sys"]["country"]}</em></b>\n\n\
                <b>Weather : {result["weather"][0]["main"]}</b> \n\
                Temperature : {round(result["main"]["temp"] - 273.15, 2)}°C \n\
                Humidity : {result["main"]["humidity"]} % \n\
                Pressure :{result["main"]["pressure"]} hPa \n\
                Wind : {result["wind"]["speed"]} m/s \n\
                Description : {result["weather"][0]["description"]}'
            )
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=result['message'])
    except Exception as err:
        logging.error(err)

def news(update: Update, context: CallbackContext):
    try:

        # takes a random country and gets the top 5 news of the country
        random_country = random.choice(COUNTRIES)
        response = requests.get(f'https://newsapi.org/v2/top-headlines?country={random_country}&apiKey={NEWS_API_KEY}&pageSize=5')

        # handle and parse the response
        result = response.json()
        if result['status'] == 'ok':
            # sends the five news
            for article in result['articles']:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f'<b>{article["title"]}</b>\n\n \
                                         <a href="{article["url"]}">{article["url"]}</a>', parse_mode='HTML')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=result['message'])
    except Exception as err:
        logging.error(err)

# initialize the app
def main():
    try:
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(start_handler)
        help_handler = CommandHandler('help', help)
        dispatcher.add_handler(help_handler)
        weather_handler = CommandHandler('weather', weather)
        dispatcher.add_handler(weather_handler)
        weather_reply_handler = MessageHandler(Filters.reply & Filters.text, weather_reply)
        dispatcher.add_handler(weather_reply_handler)
        news_handler = CommandHandler('news', news)
        dispatcher.add_handler(news_handler)
        updater.start_polling()
        updater.idle()
    except Exception as err:
        logging.error(err)

if __name__ == '__main__':
    main()


# - Ayon/FakeCoder01