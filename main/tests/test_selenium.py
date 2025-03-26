# hotel_management/main/tests/test_selenium.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from django.test import LiveServerTestCase
from main.models import User, Room, Booking
import os
from decimal import Decimal
import time
from datetime import datetime
from selenium.webdriver.support.ui import Select

class BookingTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        
        chrome_options = Options()
        # Для отладки запускаем в видимом режиме (закомментируйте для CI/CD)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(executable_path=chromedriver_path)
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 15)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаем тестовый номер
        self.room = Room.objects.create(
            room_number="101",
            room_type="standard",
            price=Decimal("2500.00"),
            description="Уютный номер",
            is_available=True
        )
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username="testuser",
            phone="+79001234567",
            full_name="Тест Тестов",
            password="Test12345!"
        )
        
        # Создаем суперпользователя
        self.superuser = User.objects.create_superuser(
            username="admin",
            phone="+79001234568",
            full_name="Администратор",
            password="Admin12345!"
        )

    def take_screenshot(self, name):
        """Создание скриншота для отладки"""
        self.driver.save_screenshot(f"debug_{name}.png")
        print(f"Скриншот сохранен: debug_{name}.png")
        time.sleep(1)  # Пауза после создания скриншота

    def test_complete_booking_flow(self):
        """Полный тест процесса бронирования"""
        driver = self.driver
        
        print("1. Открываем страницу входа...")
        driver.get(f"{self.live_server_url}/login/")
        self.take_screenshot("01_login_page")
        time.sleep(1)  # Пауза для просмотра страницы входа
        
        print("2. Вводим данные для входа...")
        driver.find_element(By.ID, "phone").send_keys("+79001234567")
        time.sleep(1)  # Пауза между вводом телефона и пароля
        driver.find_element(By.ID, "password").send_keys("Test12345!")
        time.sleep(1)  # Пауза перед нажатием кнопки входа
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.take_screenshot("02_after_login")
        time.sleep(1)  # Пауза после входа
        
        print("3. Проверяем успешный вход...")
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "display-4"))
        )
        self.take_screenshot("03_main_page")
        time.sleep(1)  # Пауза на главной странице
        
        print("4. Переходим на страницу номеров...")
        driver.find_element(By.LINK_TEXT, "Номера").click()
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "room-card"))
        )
        self.take_screenshot("04_rooms_page")
        time.sleep(1)  # Пауза для просмотра списка номеров
        
        print("5. Выбираем первый доступный номер...")
        first_room = driver.find_element(By.CLASS_NAME, "room-card")
        book_button = first_room.find_element(By.LINK_TEXT, "Забронировать")
        time.sleep(1)  # Пауза перед нажатием кнопки бронирования
        book_button.click()
        self.take_screenshot("05_booking_form")
        time.sleep(1)  # Пауза для просмотра формы бронирования
        
        print("6. Заполняем форму бронирования...")
        self.wait.until(
            EC.presence_of_element_located((By.NAME, "check_in"))
        )
        check_in_input = driver.find_element(By.NAME, "check_in")
        check_out_input = driver.find_element(By.NAME, "check_out")
        room_select = driver.find_element(By.NAME, "room")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Выбираем номер в выпадающем списке
        room_select_element = Select(room_select)
        room_select_element.select_by_value(str(self.room.id))
        
        check_in_input.send_keys("01042025")
        time.sleep(1)  # Пауза между вводом дат
        check_out_input.send_keys("05042025")
        time.sleep(1)  # Пауза перед отправкой формы
        
        submit_button.click()
        print("Форма отправлена")
        self.take_screenshot("06_after_booking")
        time.sleep(1)  # Пауза после отправки формы
        
        print("7. Проверяем успешное бронирование...")
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message = driver.find_element(By.CLASS_NAME, "alert-success").text
        self.assertIn("успешно", success_message.lower())
        print(f"Сообщение об успехе: {success_message}")
        self.take_screenshot("07_success_page")
        time.sleep(2)  # Финальная пауза для просмотра результата

    def tearDown(self):
        # Очищаем тестовые данные
        User.objects.all().delete()
        Room.objects.all().delete()
        Booking.objects.all().delete()