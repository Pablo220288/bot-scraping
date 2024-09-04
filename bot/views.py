import os
import pickle
import random
import ssl
import time
import urllib.request

import numpy as np
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Create your views here.


def index(request):
    if "next" in request.GET:
        messages.warning(request, "You must be logged in to access this page")
        print(request.method)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect("home")
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect(reverse_lazy("index"))

    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return redirect(reverse_lazy("index"))


@login_required
def home(request):
    print(request.method)
    print(request.method)
    if request.method == "POST":
        # Variables de entorno
        INSTAGRAM_USER = request.POST.get("user")
        INSTAGRAM_PASSWORD = request.POST.get("password")

        """ INSTAGRAM_USER = os.getenv("INSTAGRAM_USER")
        INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD") """

        # Ruta al ChromeDriver (con extensión .exe en Windows)
        PATH = "C:/Program Files/chromedriver.exe"

        chrome_options = Options()
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Configuración del servicio de ChromeDriver
        service = Service()

        # Inicializa el driver de Chrome con el servicio configurado
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Abre Instagram
        driver.get("https://www.instagram.com/")

        ssl._create_default_https_context = ssl._create_unverified_context

        # Función para guardar cookies
        def save_cookies(driver, filepath):
            with open(filepath, "wb") as file:
                pickle.dump(driver.get_cookies(), file)

        # Función para cargar cookies
        def load_cookies(driver, filepath):
            with open(filepath, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)

        # Ruta donde se guardarán las cookies
        cookies_path = "cookies.pkl"

        # Login
        # Si el archivo de cookies existe, cargamos las cookies
        if os.path.exists(cookies_path):
            load_cookies(driver, cookies_path)
            driver.refresh()
            time.sleep(random.uniform(1, 3))

            # Verificamos si la sesión está activa
            try:
                driver.find_element(By.XPATH, "//div[text()='Home']")
                print("Inicio de sesión con cookies exitoso.")
            except:
                print(
                    "No se pudo iniciar sesión con cookies. Procediendo con inicio de sesión manual."
                )
                os.remove(cookies_path)  # Elimina cookies si fallan

        else:
            # Realiza el proceso de inicio de sesión manual
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = driver.find_element(By.NAME, "password")

            username_input.send_keys(INSTAGRAM_USER)
            password_input.send_keys(INSTAGRAM_PASSWORD)
            password_input.send_keys(Keys.RETURN)

            # Esperar hasta que la sesión haya iniciado
            time.sleep(random.uniform(5, 10))

            # Guarda las cookies después de iniciar sesión
            save_cookies(driver, cookies_path)

            print("Inicio de sesión manual completado y cookies guardadas.")

        # Buscador
        usuarios = ["mariapombo", "luisinhaoliveira99"]

        def download_image(src, usuario, folder="historias"):
            if not os.path.exists(folder):
                os.makedirs(folder)
            file_name = f"{folder}/{usuario}_{int(time.time())}.jpg"
            urllib.request.urlretrieve(src, file_name)
            print(f"Imagen descargada: {file_name}")
            return file_name

        def compare_images(image):
            # Cargar las imágenes
            print("aqui")
            img1 = Image.open("test.jpg")
            print(img1)
            img2 = Image.open(image)
            # Convertir imágenes a matrices numpy
            np_img1 = np.array(img1)
            np_img2 = np.array(img2)

            # Comparar las matrices
            if np.array_equal(np_img1, np_img2):
                print("Las imágenes son iguales.")
                return True
            else:
                print("Las imágenes son diferentes.")
                return False

        # Array para almacenar los resultados
        results = {
            "coinciden": [],
            "no_coinciden": [],
        }

        def obtener_historias(usuario):
            driver.get(f"https://www.instagram.com/{usuario}/")
            time.sleep(random.uniform(1, 3))

            try:
                # Hacemos click en las historias del Usuario
                historia = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@role='button']//span[@role='link']")
                    )
                )
                historia.click()

                # Esperamos un tiempo aleatorio para imitar el comportamiento humano
                time.sleep(random.uniform(1, 3))

                historias = []

                while True:
                    try:
                        # Buscar el contenedor principal
                        div_container = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "/html/body/div[2]/div/div/div/div[3]/div/div/div[3]/div/section/div[1]/div/div/div[1]/div/div[2]/div/div[1]/div/div",
                                )
                            )
                        )

                        svg_stop_button = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (
                                    By.CSS_SELECTOR,
                                    "svg[aria-label='Pausar']",
                                )
                            )
                        )
                        stop_button = svg_stop_button.find_element(By.XPATH, "./..")
                        stop_button.click()

                        try:
                            # Buscar si hay una imagen dentro del contenedor
                            img = div_container.find_element(By.CSS_SELECTOR, "img")
                            src = img.get_attribute("src")
                            print(f"Imagen encontrada: {src}")
                            image_path = download_image(
                                src, usuario
                            )  # Descargar la imagen

                            # Comparar la imagen descargada con la imagen test
                            if compare_images(image_path):
                                # Si las imágenes son iguales, pasar al siguiente usuario
                                print(
                                    "Las imágenes son iguales, pasando al siguiente usuario."
                                )
                                results["coinciden"].append(usuario)
                                os.remove(image_path)
                                return  # Pasamos al siguiente usuario
                            else:
                                print(
                                    "Las imágenes son diferentes, continuando con la siguiente historia."
                                )
                                os.remove(image_path)

                        except:
                            # Si no es una imagen, intentar buscar un video
                            try:
                                video = div_container.find_element(
                                    By.CSS_SELECTOR, "video"
                                )
                                print("Es un video pasamos a la siguiente historia...")
                            except:
                                print("No se encontró ni imagen ni video.")

                        # Intentar hacer clic en el botón "Siguiente"
                        try:
                            svg_next_button = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (
                                        By.CSS_SELECTOR,
                                        "svg[aria-label='Siguiente']",
                                    )
                                )
                            )
                            next_button = svg_next_button.find_element(By.XPATH, "./..")
                            next_button.click()
                            print("Pasando a la siguiente historia...")
                        except Exception as e:
                            print(f"No se pudo hacer clic en el botón 'Siguiente'")
                            results["no_coinciden"].append(usuario)
                            break

                        # Esperar un tiempo aleatorio para imitar el comportamiento humano
                        time.sleep(random.uniform(1, 2))

                    except Exception as e:
                        print(f"Error: {e}")
                        break

                return historias
            except Exception as e:
                print(f"No se pudieron obtener historias para {usuario}: {str(e)}")
                return []

        for usuario in usuarios:
            historias = obtener_historias(usuario)
            print("Siguiente usuario...")

        print("Usuarios con historias coincidentes:", results["coinciden"])
        print("Usuarios sin historias coincidentes:", results["no_coinciden"])
        print("Fin del Programa")

        # Espera un tiempo aleatorio antes de cerrar el navegador
        time.sleep(random.uniform(10, 15))

        # Cerrar el navegador
        driver.quit()

        return render(
            request,
            "home.html",
            {
                "coinciden": results["coinciden"],
                "no_coinciden": results["no_coinciden"],
            },
        )

    return render(request, "home.html")
