
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from django.core.exceptions import ObjectDoesNotExist

from main.models import Habit_guide, Habit_user
from main.views import UserListAPIView
from users.models import User

# постоянные значения для всех тестов
user_test = {
    "email": "k17911971@yandex.ru",
    "password": "userYandex"
}

action_test = {
    "action": "лизать мороженку"
}

action_test_up = {
    "action": "бег"
}

user_unauthorized = {
    "email": "k971@yan.ru",
    "password": "urYanx"
}


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        records = User.objects.all()
        records.delete()

        # создание суперюзера
        user = User.objects.create(
            email='admin@sky.pro',
            first_name='admin',
            last_name='SkyPro',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        user.set_password('admin171717')
        user.save()

        user = User.objects.create(
            email='k1779@mail.ru',
            first_name='userMail',
            last_name='mailRu',
            is_staff=True,
            is_superuser=False,
            is_active=True
        )

        user.set_password('userMail')
        user.save()

        user = User.objects.create(
            email='k17911971@yandex.ru',
            first_name='userYandex',
            last_name='YandexRu',
            is_staff=True,
            is_superuser=False,
            is_active=True
        )

        user.set_password('userYandex')
        user.save()


    def test_create_user(self):
        # Тестирование POST-запроса создание нового пользователя // доступ без аутентификации
        data = {
            "email": "xxxx@mail.ru",
            "telegram_id": "11122233",
            "password": "1234567"
                                }

        response = self.client.post('/user/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_token(self):
        # Тестирование POST-запроса на авторизацию // создание токена пользователя из базы

        response = self.client.post('/users/token/', user_test)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тестирование POST-запроса на авторизацию // создание токена пользователя которого нет в базе



        response = self.client.post('/users/token/', user_unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_user_list(self, user=None):

        # Авторизация пользователя и получение токена доступа
        response = self.client.post('/users/token/', user_test)
        access_token = response.data.get('access')

        # Установка заголовка авторизации с токеном доступа
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Отправка Get-запроса на получение списка пользователей
        response = self.client.get('/user/list/')
        # Проверка ответа сервера на доступ к данным
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка соответсвия запрашиваемых данных авторизованному пользователю
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['count'], 1) # одно значение в выдаче
        self.assertEqual(response.data['results'][0]['email'], user_test['email']) # значение совпадает с авторизованным пользователем

        # Установка заголовка авторизации без данных токена // пользователь не авторизован
        self.client.credentials(HTTP_AUTHORIZATION=f'')

        # Отправка Get-запроса на получение списка пользователей
        response = self.client.get('/user/list/')
        # Проверка ответа сервера на доступ к данным
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_user_update(self, user=None):

           # Авторизация пользователя и получение токена доступа
        response = self.client.post('/users/token/', user_test)
        access_token = response.data.get('access')

        # Установка заголовка авторизации с токеном доступа
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        user = User.objects.get(email=user_test['email'])
        pk = user.pk

        # Обновляемые данные
        up_data = {
           "email": "k17911971@yandex.ru",
           "password": "userYandex",
           "phone": "170479",
           "telegram_id": "5418"
        }

        # Отправка Put-запроса на обновление данных пользователя
        response = self.client.put(f'/user/update/{pk}/', up_data)
        # Проверка ответа сервера на доступ к данным
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # обновление объекта user
        user = User.objects.get(email=user_test['email'])

        # Проверка на проведенное обновление
        self.assertEqual(user.phone, up_data["phone"])
        self.assertEqual(user.telegram_id, up_data["telegram_id"])

        # Проверка соответсвия запрашиваемых данных авторизованному пользователю
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['id'], pk)  # значение id  в выдаче совпадает с авторизованным пользователем pk

    def test_user_delete(self, user=None):

        # Авторизация пользователя и получение токена доступа
        response = self.client.post('/users/token/', user_test)
        access_token = response.data.get('access')

        # Установка заголовка авторизации с токеном доступа
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        user = User.objects.get(email=user_test['email'])
        pk = user.pk
        print(pk)

        # Отправка Del-запроса на удаление данных пользователя
        response = self.client.delete(f'/user/delete/{pk}/', user_test)
        # Проверка ответа сервера на доступ к данным
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверка отсутствия данных пользователя в базе данных
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=pk)




class Habit_userAPITestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

        #Удаление всех объектов User
        records = User.objects.all()
        records.delete()

        # создание суперюзера
        user = User.objects.create(
            email='admin@sky.pro',
            first_name='admin',
            last_name='SkyPro',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        user.set_password('admin171717')
        user.save()

        user = User.objects.create(
            email='k1779@mail.ru',
            first_name='userMail',
            last_name='mailRu',
            is_staff=True,
            is_superuser=False,
            is_active=True
        )

        user.set_password('userMail')
        user.save()

        user = User.objects.create(
            email='k17911971@yandex.ru',
            first_name='userYandex',
            last_name='YandexRu',
            is_staff=True,
            is_superuser=False,
            is_active=True
        )

        user.set_password('userYandex')
        user.save()

        # Удаление всех объектов Habit_guide
        records = Habit_guide.objects.all()
        records.delete()

        # создание привычек
        habit_guide = Habit_guide.objects.create(
            action=action_test['action'],
            is_useful=False,
            is_nice=True,
            is_activ=True
        )
        habit_guide.save()

        habit_guide = Habit_guide.objects.create(
            action=action_test_up['action'],
            is_useful=True,
            is_nice=False,
            is_activ=True
        )
        habit_guide.save()

        habit_guide = Habit_guide.objects.create(
            action="кушать мороженку",
            is_useful=False,
            is_nice=True,
            is_activ=True
        )
        habit_guide.save()

        habit_guide = Habit_guide.objects.create(
            action="сидеть",
            is_useful=False,
            is_nice=False,
            is_activ=True
        )
        habit_guide.save()

        habit_guide = Habit_guide.objects.create(
            action="сон",
            is_useful=False,
            is_nice=True,
            is_activ=True
        )
        habit_guide.save()

    # Удаление всех объектов Habit_user
    records = Habit_user.objects.all()
    records.delete()

    def test_create_habit_user(self):
        # данные для авторизации пользователя

        # Авторизация пользователя и получение токена доступа
        response = self.client.post('/users/token/', user_test)
        access_token = response.data.get('access')

        # Установка заголовка авторизации с токеном доступа
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        user = User.objects.get(email=user_test['email'])
        habit_guide = Habit_guide.objects.get(action=action_test['action'])

        # Тестирование POST-запроса создание новой привычки пользователя // доступ с аутентификацией
        data = {
            "email": user.email,
            "action": habit_guide.action
        }

        response = self.client.post('/habit_user/create/', data)

        #Проверка успешного создания записи
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_habit_user_list(self, user=None):

        # Авторизация пользователя и получение токена доступа
        response = self.client.post('/users/token/', user_test)
        access_token = response.data.get('access')

        # Установка заголовка авторизации с токеном доступа
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Создание новой привычки пользователя // доступ с аутентификацией

        user = User.objects.get(email=user_test['email'])
        habit_guide = Habit_guide.objects.get(action=action_test['action'])

        habit_user = Habit_user.objects.create(email=user, action=habit_guide)
        habit_user.save()

        # Отправка Get-запроса на получение списка привычек пользователя
        response = self.client.get('/habit_user/')
        # Проверка ответа сервера на доступ к данным
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка соответсвия запрашиваемых данных авторизованному пользователю
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['count'], 1)  # одно значение в выдаче
        self.assertEqual(response.data['results'][0]['email'],
                         user_test['email'])  # значение совпадает с авторизованным пользователем
        self.assertEqual(response.data['results'][0]['action'],
                         action_test['action'])  # значение совпадает с записываемой привычкой

        # Установка заголовка авторизации без данных токена // пользователь не авторизован
        self.client.credentials(HTTP_AUTHORIZATION=f'')

        # Отправка Get-запроса на получение списка пользователя
        response = self.client.get('/habit_user/')
        # Проверка ответа сервера на доступ к данным
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_habit_user_update(self, user=None):
        # Авторизация пользователя и получение токена доступа
        response = self.client.post('/users/token/', user_test)
        access_token = response.data.get('access')

        # Установка заголовка авторизации с токеном доступа
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        # Установка тестовой привычки
        user = User.objects.get(email=user_test['email'])
        habit_guide = Habit_guide.objects.get(action=action_test['action'])

        user_action = Habit_user.objects.create(email=user, action=habit_guide)
        user_action.save()
        pk = user_action.pk

        # Обновляемые данные
        up_data = {
            "email": user_test['email'],
            "action": action_test_up['action']
                  }

        # Отправка Put-запроса на обновление данных пользователя
        response = self.client.put(f'/habit_user/update/{pk}/', up_data)

        # Проверка ответа сервера
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # обновленный объект hubit_user
        user_up = Habit_user.objects.get(id=pk)

        # Проверка на проведенное обновление
        self.assertEqual(user_up.email.email, up_data["email"])
        self.assertEqual(user_up.action.action, up_data["action"])

        # Проверка соответсвия запрашиваемых данных авторизованному пользователю
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['email'],
                         user.email)  # значение id  в выдаче совпадает с авторизованным пользователем pk