import pytest

from assistant.storage.json_storage import JSONStorage
from assistant.storage.storage import StorageError


# Тест: збій під час запису не має знищити старі дані.
def test_failed_save_keeps_previous_data(tmp_path, monkeypatch):
    path = tmp_path / "contacts.json"
    storage = JSONStorage(path)

    # Спочатку записуємо нормальні дані, які треба захистити.
    storage.save([{"id": "1", "name": "Ada"}])

    # Імітуємо збій: замість os.replace ця функція завжди кидає помилку,
    # ніби диск зламався саме в момент заміни файлу.
    def broken_replace(src, dst):
        raise OSError("disk error")

    # На час цього тесту підміняємо справжній os.replace нашою функцією.
    monkeypatch.setattr("assistant.storage.json_storage.os.replace", broken_replace)

    # Намагаємося зберегти нові дані. Має піднятися StorageError.
    with pytest.raises(StorageError):
        storage.save([{"id": "2", "name": "Bob"}])

    # Старі дані мають лишитися цілими.
    assert storage.load() == [{"id": "1", "name": "Ada"}]


# Тест: пошкоджений JSON-файл має давати зрозумілу помилку StorageError.
def test_corrupted_json_raises_storage_error(tmp_path):
    path = tmp_path / "contacts.json"
    # Вручну записуємо в файл зламаний вміст, який не є JSON.
    path.write_text("{ не json", encoding="utf-8")
    storage = JSONStorage(path)

    # load() має прочитати файл, побачити помилку і кинути StorageError.
    with pytest.raises(StorageError):
        storage.load()


# Тест: якщо файлу ще немає, load() має повернути порожній список, а не впасти.
def test_missing_file_loads_empty_list(tmp_path):
    # Створюємо об'єкт для шляху, де файлу немає, і нічого не записуємо.
    storage = JSONStorage(tmp_path / "contacts.json")

    assert storage.load() == []


# Тест: повторне збереження має замінити старі дані, а не додати до них.
def test_save_replaces_existing_data(tmp_path):
    storage = JSONStorage(tmp_path / "contacts.json")
    # Перший запис: Ada.
    storage.save([{"id": "1", "name": "Ada"}])
    # Другий запис: Bob. Ada має зникнути.
    storage.save([{"id": "2", "name": "Bob"}])

    # У файлі має бути тільки Bob.
    assert storage.load() == [{"id": "2", "name": "Bob"}]


# Тест: якщо дані не можна перетворити в JSON, файл не має змінитися.
def test_serialization_failure_keeps_previous_data(tmp_path):
    storage = JSONStorage(tmp_path / "contacts.json")
    storage.save([{"id": "1", "name": "Ada"}])

    # object() не є JSON-сумісним значенням, тому json.dumps має впасти
    # ще до того, як що-небудь буде записано у файл.
    with pytest.raises(StorageError):
        storage.save([{"id": object()}])

    # Старий запис Ada має лишитися на місці.
    assert storage.load() == [{"id": "1", "name": "Ada"}]
