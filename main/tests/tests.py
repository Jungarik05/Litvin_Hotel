# hotel_management/main/tests/test_selenium.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.test import LiveServerTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from main.models import Role, User, ComplaintStatus, Complaint, Booking

class HotelManagementSeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Настройка ChromeDriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 15)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаем роли
        self.guest_role = Role.objects.create(
            name='Гость',
            description='Обычный пользователь системы'
        )
        self.staff_role = Role.objects.create(
            name='Персонал',
            description='Сотрудник отеля'
        )
        self.admin_role = Role.objects.create(
            name='Администратор',
            description='Администратор системы'
        )

        # Создаем тестового пользователя (гостя)
        self.guest = User.objects.create_user(
            phone='+79123456789',
            full_name='Иван Иванов',
            password='GuestPass123!',
            role=self.guest_role
        )

        # Создаем сотрудника
        self.staff = User.objects.create_user(
            phone='+79876543210',
            full_name='Петр Петров',
            password='StaffPass123!',
            role=self.staff_role,
            is_staff=True
        )

        # Создаем администратора
        self.admin = User.objects.create_user(
            phone='+79001112233',
            full_name='Алексей Администраторов',
            password='AdminPass123!',
            role=self.admin_role,
            is_staff=True,
            is_admin=True
        )

        # Создаем тестовое бронирование
        self.booking = Booking.objects.create(
            user=self.guest,
            room_number=101,
            check_in='2023-01-01',
            check_out='2023-01-10'
        )

        # Создаем статусы жалоб
        self.status_new = ComplaintStatus.objects.create(name='Новая')
        self.status_in_progress = ComplaintStatus.objects.create(name='В работе')
        self.status_resolved = ComplaintStatus.objects.create(name='Решена')

    def test_guest_can_create_complaint(self):
        """Тест создания жалобы гостем"""
        driver = self.driver
        
        # 1. Авторизация гостя (по телефону)
        driver.get(f"{self.live_server_url}/login/")
        driver.find_element(By.NAME, "username").send_keys("+79123456789")
        driver.find_element(By.NAME, "password").send_keys("GuestPass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 2. Проверка успешного входа
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".user-profile"),
                "Иван Иванов"
            )
        )
        
        # 3. Переход на страницу создания жалобы
        driver.find_element(By.LINK_TEXT, "Подать жалобу").click()
        
        # 4. Заполнение формы жалобы
        self.wait.until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        
        # Выбор бронирования
        driver.find_element(By.XPATH, "//select[@name='booking']/option[text()='Бронирование №101']").click()
        
        # Ввод текста жалобы
        driver.find_element(By.NAME, "text").send_keys("В номере не работает кондиционер")
        
        # 5. Отправка формы
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 6. Проверка успешного создания
        success_message = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("жалоба успешно создана", success_message.text.lower())
        
        # 7. Проверка в БД
        complaint = Complaint.objects.first()
        self.assertEqual(complaint.text, "В номере не работает кондиционер")
        self.assertEqual(complaint.status, self.status_new)
        self.assertEqual(complaint.booking, self.booking)

    def test_staff_can_process_complaint(self):
        """Тест обработки жалобы сотрудником"""
        # Создаем тестовую жалобу
        complaint = Complaint.objects.create(
            booking=self.booking,
            text="Грязный ковер в номере",
            status=self.status_new
        )
        
        driver = self.driver
        
        # 1. Авторизация сотрудника
        driver.get(f"{self.live_server_url}/login/")
        driver.find_element(By.NAME, "username").send_keys("+79876543210")
        driver.find_element(By.NAME, "password").send_keys("StaffPass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 2. Переход к списку жалоб
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "Управление жалобами"))
        ).click()
        
        # 3. Открытие жалобы
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '/complaints/{complaint.id}/')]"))
        ).click()
        
        # 4. Изменение статуса
        status_select = self.wait.until(
            EC.element_to_be_clickable((By.NAME, "status"))
        )
        status_select.click()
        driver.find_element(By.XPATH, "//option[text()='В работе']").click()
        
        # 5. Добавление комментария
        driver.find_element(By.NAME, "resolution_notes").send_keys("Отправлена уборка в номер")
        
        # 6. Сохранение изменений
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 7. Проверка обновления
        self.wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".status-badge"), "В работе")
        )
        
        # 8. Проверка в БД
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, self.status_in_progress)
        self.assertEqual(complaint.resolved_by, self.staff)

    def test_admin_can_manage_users(self):
        """Тест управления пользователями администратором"""
        driver = self.driver
        
        # 1. Авторизация администратора
        driver.get(f"{self.live_server_url}/login/")
        driver.find_element(By.NAME, "username").send_keys("+79001112233")
        driver.find_element(By.NAME, "password").send_keys("AdminPass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 2. Переход в панель администратора
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "Администрирование"))
        ).click()
        
        # 3. Создание нового пользователя
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "Добавить пользователя"))
        ).click()
        
        # 4. Заполнение формы
        self.wait.until(
            EC.presence_of_element_located((By.NAME, "phone"))
        ).send_keys("+79005553535")
        
        driver.find_element(By.NAME, "full_name").send_keys("Новый Пользователь")
        driver.find_element(By.NAME, "password1").send_keys("NewPass123!")
        driver.find_element(By.NAME, "password2").send_keys("NewPass123!")
        
        # Выбор роли
        driver.find_element(By.XPATH, "//select[@name='role']/option[text()='Гость']").click()
        
        # 5. Отправка формы
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 6. Проверка создания
        success_message = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("пользователь успешно создан", success_message.text.lower())
        
        # 7. Проверка в БД
        new_user = User.objects.get(phone="+79005553535")
        self.assertEqual(new_user.full_name, "Новый Пользователь")
        self.assertEqual(new_user.role, self.guest_role)

    def test_user_profile_editing(self):
        """Тест редактирования профиля пользователем"""
        driver = self.driver
        
        # 1. Авторизация
        driver.get(f"{self.live_server_url}/login/")
        driver.find_element(By.NAME, "username").send_keys("+79123456789")
        driver.find_element(By.NAME, "password").send_keys("GuestPass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 2. Переход в профиль
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "Мой профиль"))
        ).click()
        
        # 3. Редактирование
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "Редактировать"))
        ).click()
        
        # 4. Изменение данных
        full_name = self.wait.until(
            EC.presence_of_element_located((By.NAME, "full_name"))
        )
        full_name.clear()
        full_name.send_keys("Иван Измененный")
        
        # 5. Загрузка фото
        photo_input = driver.find_element(By.NAME, "photo")
        photo_input.send_keys("G:/path/to/test_photo.jpg")  # Укажите реальный путь к тестовому изображению
        
        # 6. Сохранение
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 7. Проверка изменений
        self.wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".user-profile"), "Иван Измененный")
        )
        
        # 8. Проверка в БД
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.full_name, "Иван Измененный")
        self.assertTrue(self.guest.photo)  # Проверяем, что фото загружено