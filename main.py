import telebot
import requests
from telebot import types
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Схема: /search <Название фильма>, бот передает название
# https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=10&query=<название фильма в кодировке>
# возвращается куча инфы, включая id фильма, id вставляем в url https://www.kinopoisk.ru/film/<id>/,
# получаем страницу фильма


def find_movie(movie_name):
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=10&query={movie_name}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": os.environ.get('KINOPOISK_API_KEY')
    }

    response = requests.get(url, headers=headers)

    # Достаем id
    if response.status_code == 200:
        data = response.json()
        if data.get('docs') and len(data.get('docs')) > 0:
            movie_id = data['docs'][0]['id']
            movie_name = data['docs'][0]['name']
            movie_alt_name = data['docs'][0]['alternativeName']
            link = f"https://www.kinopoisk.ru/film/{movie_id}/"
            return movie_name, movie_alt_name, link
        else:
            return None
    else:
        return None


token = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)


@bot.inline_handler(lambda query: len(query.query) > 0)
def mention_search(message):
    print(message.from_user.username)
    try:
        query = message.query
        movie = find_movie(query)
        if movie:
            movie_name, movie_alt_name, movie_link = movie
            print(movie_name, movie_alt_name, movie_link)
            if movie_name:
                result_1 = types.InlineQueryResultArticle(
                    id='1',
                    title=movie_name,
                    input_message_content=types.InputTextMessageContent(movie_link)
                )
                bot.answer_inline_query(message.id, [result_1], cache_time=0)
            elif movie_alt_name:
                result_1 = types.InlineQueryResultArticle(
                    id='1',
                    title=movie_alt_name,
                    input_message_content=types.InputTextMessageContent(movie_link)
                )
                bot.answer_inline_query(message.id, [result_1], cache_time=0)
        else:
            pass

    except Exception as e:
        print(e)


bot.polling(none_stop=True)
