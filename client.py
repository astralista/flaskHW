import requests

# Логин и пароль пользователя
username = "user1"
password = "123456789" #Сюда писать логин и пароль которые задавались при создании (не из базы)

# Отправка логина и пароля на сервер для аутентификации
response = requests.post("http://127.0.0.1:5000/login", json={"username": username, "password": password})

# Проверка ответа сервера
if response.status_code == 200:
    print("Аутентификация прошла успешно")
else:
    print("Ошибка аутентификации")


# response = requests.post("http://127.0.0.1:5000/users/",
#                          json={'name': 'user3', 'password': 'fno32no4j453n224knm23'})
#
# print(response.status_code)
# print(response.text)

response = requests.post("http://127.0.0.1:5000/ads/",
                         json={'headline': 'Ad#1', 'description': 'Тут могла быть ваша реклама'})

print(response.status_code)
print(response.text)
