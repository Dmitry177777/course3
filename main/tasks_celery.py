import os
from datetime import timedelta, datetime
from celery import shared_task
import telebot
import pytz

from main.models import Habit_user
from users.models import User
from .serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from dotenv import load_dotenv

from django.conf import settings

# Объявление переменной бота
load_dotenv()
TELEGRAM_BOT_API_KEY = os.environ.get('TELEGRAM_BOT_API_KEY')
# take environment variables from .env.
bot = telebot.TeleBot(TELEGRAM_BOT_API_KEY)


@shared_task
def send_telegram_confirmation(user_instance):
    try:
        latest_habit_user =\
            (Habit_user.objects.filter
             (email=user_instance).latest('date_of_habit'))
        action = latest_habit_user.action.action
    except ObjectDoesNotExist:
        action = "No action found"

    serializer = UserSerializer(user_instance)
    serialized_user = serializer.data

    message_text = (f"Hello {serialized_user['email']},"
                    f" you have a new habit: {action}.")
    send_telegram_message.delay(serialized_user, message_text)


@shared_task
def check_periodicity():
    # Получаем часовой пояс проекта
    time_zone = pytz.timezone(settings.TIME_ZONE)

    # получаем текущую дату с учетом часового пояса
    now = datetime.now(time_zone)
    print(now)

    # Получаем объект Habit_user только активные позиции
    instance = Habit_user.objects.filter(is_activ=True)

    # проходим циклом по всем привычкам
    for i in instance:
        # Определение разницы даты последнего входа пользователя и текущей даты
        time_diff = now-i.date_of_habit
        t_days = time_diff.days

        # если разница больше запускается
        # уведомление о времени выполнения действия
        if timedelta(days=t_days) > i.periodicity:
            # дата выполнения привычки меняется на текущую
            i.date_of_habit = now
            i.save()

            user_instance = User.objects.get(email=i.email)
            serializer = UserSerializer(user_instance)
            serialized_user = serializer.data

            message_text = (f"Привет {i.email},"
                            f" пора выполнить следующее действие: {i.action}.")
            # вызавыется функция рассылки
            send_telegram_message.delay(serialized_user, message_text)


@shared_task
def send_telegram_message(serialized_user, message_text):
    try:
        bot.send_message(serialized_user['telegram_id'], message_text)
    except Exception as e:
        # Обработка ошибок отправки сообщения, если необходимо
        print(e)
