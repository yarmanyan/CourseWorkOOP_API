# Программа для получения случайной картинки по API

import requests
import time
from settings import yd_token
import json
import os

api_url = f'https://dog.ceo/api/breed/'


# Класс для подключения к Я.Диску
class YDConnector:
    __yd_base = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.__headers = {
            'Authorization': f'OAuth {token}'
        }

    def create_folder(self, breed):
        """
        Создание директории на Яндекс.Диске.
        """
        params = {
            'path': f'dogs/{breed}'
        }

        response = requests.put(f'{YDConnector.__yd_base}/v1/disk/resources',
                                headers=self.__headers,
                                params=params)

        if response.status_code == 201:
            print(f"Папка dogs/{breed} создана на Яндекс.Диске")
        elif response.status_code == 409: # Пропускаем ошибку повторного создания
            pass
        else:
            print(f"Ошибка создания папки: {response.status_code} - {response.text}")

    def delete_folder(self, breed):
        """
        Удаление директории на Яндекс.Диске.
        """
        params = {
            'path': f'dogs/{breed}'
        }

        response = requests.delete(f'{YDConnector.__yd_base}/v1/disk/resources',
                                   headers=self.__headers,
                                   params=params)
        if response.status_code == 202:
            print(f"Папка dogs/{breed} удалена с Яндекс.Диска")
        else:
            print(f"Ошибка удаления папки: {response.status_code} - {response.text}")

    def image_upload(self, image_url, file_name, breed):
        """
        Загрузка картинки по url Яндекс.Диск.
        """
        params = {
            'url': f'{image_url}',
            'path': f'dogs/{breed}/{file_name}'
        }
        response = requests.post(f'{YDConnector.__yd_base}/v1/disk/resources/upload',
                                 headers=self.__headers,
                                 params=params)
        # Проверка на ошибку загрузки изображения
        if response.status_code == 202:
            print(f'Загружено: {file_name} в папку dogs/{breed}')
        else:
            print(f'Ошибка загрузки: {response.status_code} - {response.text}')

    def image_info(self, file_name, breed):
        """
        Получение метаданных загруженного файла с Яндекс.Диска.
        """

        # Небольшая пауза, чтобы Яндекс.Диск успел обработать загрузку
        print("Получаем информацию о файле...")
        time.sleep(2)

        params = {
            'path': f'dogs/{breed}/{file_name}'
        }

        response = requests.get(f'{YDConnector.__yd_base}/v1/disk/resources',
                                headers=self.__headers,
                                params=params)
        # Проверяем статус ответа
        if response.status_code == 200:
            data = response.json()

            file_info = {
                'name': data.get('name'),
                'created': data.get('created'),
                'path': data.get('path'),
                'type': data.get('type'),
                'size': data.get('size')
            }

            # Вызов функции для записи информации о картинке
            save_to_json_file(file_info)

            return file_info


def folder(image_url, file_name, breed):
    """
    Управляющая функция работы с экземпляром класса YDConnector
    """
    nfolder = YDConnector(yd_token)
    nfolder.create_folder(breed)
    nfolder.image_upload(image_url, file_name, breed)
    nfolder.image_info(file_name, breed)


def get_dog_url(breed, url_str):
    """
    Получает URL случайной картинки для указанной породы через API dog.ceo

    Параметры:
        breed (str): название породы (например, "hound")
        url_str (str): дополнительная часть URL (например, "/images/random")

    Возвращает:
        str или None: URL картинки, если успешно, иначе None
    """

    response = requests.get(f'{api_url}{breed}{url_str}')

    # Проверяем статус ответа
    if response.status_code == 200:
        # Преобразуем ответ в JSON
        return response.json()['message']
    else:
        # Если статус не 200, значит произошла ошибка
        print(f"Ошибка при запросе к API. Статус: {response.status_code}")
        return None


def upload_image(breed):
    """
    Функция загрузки изображения.
    Возвращает True, если успешно загружено, False если порода не найдена.
    """

    response = requests.get(f'{api_url}{breed}/list')
    # Проверяем статус ответа
    if response.status_code != 200:
        print(f"Ошибка при проверке породы. Статус: {response.status_code}")
        return False

    if response.json()['message']:  # Проверяем на пустой список
        breed_list = response.json()['message']  # Получаем список подпород
        success = False
        for sbreed in breed_list:
            url_str = f'/{sbreed}/images/random'
            image_url = get_dog_url(breed, url_str)

            if image_url and image_url != 'Breed not found (main breed does not exist)':
                file_name = f'{breed}-{sbreed}-{image_url.split("/")[-1]}'
                print(f"Найдено: {image_url}")
                folder(image_url, file_name, breed)
                success = True
            else:
                print(f"Не удалось получить картинку для подпороды {sbreed}")
        if not success:
            print("Не удалось получить ни одной картинки для указанной породы.")
            return False
        return True


    else:  # Нет подпород
        url_str = f'/images/random'
        image_url = get_dog_url(breed, url_str)

        if image_url and image_url != 'Breed not found (main breed does not exist)':
            file_name = f'{breed}-{image_url.split("/")[-1]}'
            print(f"Найдено: {image_url}")
            folder(image_url, file_name, breed)
            return True
        else:
            print("Не удалось получить картинку. Проверьте название породы или повторите позже.")
            return False


def save_to_json_file(file_info, filename='downloaded_images.json'):
    """
    Сохраняет информацию о загруженном файле в JSON-файл.

    """
    # Создаем запись с информацией о файле
    image_record = {
        'name': file_info.get('name'),
        'created': file_info.get('created'),
        'path': file_info.get('path'),
        'type': file_info.get('type'),
        'size': file_info.get('size')
    }

    # Проверяем, существует ли уже файл
    if os.path.exists(filename):
        # Если файл существует, читаем существующие данные
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                # Если файл поврежден, начинаем с пустого списка
                existing_data = []
    else:
        # Если файла нет, создаем пустой список
        existing_data = []

    # Добавляем новую запись
    existing_data.append(image_record)

    # Сохраняем обновленные данные обратно в файл
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"Информация сохранена в файл {filename}")


def main():
    print("=" * 60)
    print("Программа для получения случайных картинок по породе собак")
    print("=" * 60)
    print("Примеры пород: hound, beagle, husky, labrador, poodle и др.")
    print("-" * 60)

    while True:
        print("\n--- Главное меню ---")
        print("1. Найти картинку по породе")
        print("2. Удалить директорию Я.Диск вместе с содержимым")
        print("3. Выйти")

        choice = input("Выберите действие (1, 2, 3): ").strip()

        if choice == '3':
            print("До свидания!")
            break

        elif choice == '1':
            # Бесконечный цикл для повторного ввода при ошибке
            while True:
                breed = input("\nУкажите породу на английском: ").strip().lower()
                if not breed:
                    print("Порода не может быть пустой. Попробуйте снова.")
                    continue

                print(f"\nИщем картинку для породы '{breed}'...")

                # upload_image возвращает True при успехе, False при ошибке
                if upload_image(breed):
                    # При успехе выходим из внутреннего цикла и возвращаемся в главное меню
                    break
                else:
                    # При ошибке спрашиваем, хочет ли пользователь попробовать снова
                    retry = input("\nХотите попробовать другую породу? (да/нет): ").strip().lower()
                    if retry not in ['да', 'yes', 'y', 'д']:
                        print("Возврат в главное меню.")
                        break
                    # Если хочет, цикл продолжается, снова запрашиваем породу

            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == '2':
            folder_name = input("\nУкажите название директории (только имя папки, например 'hound'): ").strip()
            if not folder_name:
                print("Название не может быть пустым. Попробуйте снова.")
                continue
            del_folder = YDConnector(yd_token)
            del_folder.delete_folder(folder_name)
            input("\nНажмите Enter, чтобы продолжить...")

        else:
            print("Неверный ввод. Пожалуйста, выберите 1, 2 или 3.")
            input("\nНажмите Enter, чтобы продолжить...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")
        import traceback

        traceback.print_exc()
    finally:
        input("\nНажмите Enter для выхода...")