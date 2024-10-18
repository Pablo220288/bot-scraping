import io
import math
import operator
import random
import ssl
import time
from functools import reduce

import instaloader
import numpy as np
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from PIL import Image, ImageChops
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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


""" @login_required """


""" def home(request):
    if request.method == "POST":
        # Variables de entorno
        INSTAGRAM_USER = request.POST.get("user")
        INSTAGRAM_PASSWORD = request.POST.get("password")
        TYPE_MATCH = request.POST.get("type-match")
        FILE = request.FILES.get("my_file")
        USERSTOTEST = request.POST.get("usersToTest")

        if FILE:
            # Guardar la imagen de prueba en memoria
            test_image_bytes = io.BytesIO(FILE.read())
            print(f"Imagen de prueba cargada en memoria.")

        # Ruta al ChromeDriver (con extensión .exe en Windows)
        PATH = "chromedriver/chromedriver.exe"

        chrome_options = Options()
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Configuración del servicio de ChromeDriver
        service = Service(executable_path=PATH)

        # Inicializa el driver de Chrome con el servicio configurado
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Abre Instagram
        driver.get("https://www.instagram.com/")

        ssl._create_default_https_context = ssl._create_unverified_context

        # Realiza el proceso de inicio de sesión manual
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(INSTAGRAM_USER)
        password_input.send_keys(INSTAGRAM_PASSWORD)
        password_input.send_keys(Keys.RETURN)

        # Esperar hasta que la sesión haya iniciado
        time.sleep(random.uniform(5, 15))

        # Buscador
        usuarios = USERSTOTEST.split(",")
        usuarios = [usuario.strip() for usuario in usuarios]

        def download_image_to_memory(src):
            response = requests.get(src)
            image_bytes = io.BytesIO(response.content)
            print(f"Imagen descargada en memoria.")
            return image_bytes

        def rmsdiff(im1, im2):

            diff = ImageChops.difference(im1, im2)
            h = diff.histogram()

            # Calcular la raíz cuadrada de la media de las diferencias cuadradas
            rms = math.sqrt(
                reduce(operator.add, (h * (i**2) for i, h in enumerate(h)))
                / (float(im1.size[0]) * im1.size[1])
            )
            return rms

        def compare_images(image_bytes):
            # Cargar las imágenes desde la memoria
            test_image = Image.open(test_image_bytes).convert(
                "L"
            )  # Convertir a escala de grises
            img_to_compare = Image.open(image_bytes).convert(
                "L"
            )  # Convertir a escala de grises

            # Redimensionar a un tamaño fijo
            test_image = test_image.resize((256, 256))
            img_to_compare = img_to_compare.resize((256, 256))

            # Calcular la diferencia RMS
            rms_difference = rmsdiff(test_image, img_to_compare)
            print(f"Diferencia RMS: {rms_difference}")

            # Establecer un umbral para considerar las imágenes "iguales"
            if rms_difference < 10:  # Ajusta el umbral según sea necesario
                print("Las imágenes son lo suficientemente similares.")
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
                historia = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@role='button']//span[@role='link']")
                    )
                )
                historia.click()

                time.sleep(random.uniform(1, 3))

                while True:
                    try:
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
                            image_bytes = download_image_to_memory(src)

                            if compare_images(image_bytes):
                                print(
                                    "Las imágenes son iguales, pasando al siguiente usuario."
                                )
                                results["coinciden"].append(usuario)
                                return
                            else:
                                print(
                                    "Las imágenes son diferentes, continuando con la siguiente historia."
                                )

                        except:
                            try:
                                video = div_container.find_element(
                                    By.CSS_SELECTOR, "video"
                                )
                                print("Es un video, pasamos a la siguiente historia...")
                            except:
                                print("No se encontró ni imagen ni video.")

                        try:
                            svg_next_button = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "svg[aria-label='Siguiente']")
                                )
                            )
                            next_button = svg_next_button.find_element(By.XPATH, "./..")
                            next_button.click()
                            print("Pasando a la siguiente historia...")
                        except:
                            results["no_coinciden"].append(usuario)
                            break

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
        time.sleep(random.uniform(2, 8))

        # Cerrar el navegador
        driver.quit()

        return render(
            request,
            "home.html",
            {
                "results": results,
                "coinciden": results["coinciden"],
                "no_coinciden": results["no_coinciden"],
            },
        )

    return render(request, "home.html") """


def home(request):
    if request.method == "POST":
        # Variables de entorno
        INSTAGRAM_USER = request.POST.get("user")
        INSTAGRAM_PASSWORD = request.POST.get("password")
        FILE = request.FILES.get("my_file")
        USERSTOTEST = request.POST.get("usersToTest")

        if FILE:
            # Guardar la imagen de prueba en memoria
            test_image_bytes = io.BytesIO(FILE.read())
            print(f"Imagen de prueba cargada en memoria.")

        # Crear una instancia de Instaloader
        L = instaloader.Instaloader()

        # Intentar cargar la sesión guardada
        session_file = f"./{INSTAGRAM_USER}_session"
        try:
            L.load_session_from_file(INSTAGRAM_USER, session_file)
            print(f"Sesión cargada desde el archivo {session_file}.")
        except FileNotFoundError:
            # Si no existe un archivo de sesión, iniciar sesión normalmente y guardar la sesión
            print(
                f"No se encontró el archivo de sesión. Iniciando sesión con usuario y contraseña."
            )
            L.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
            L.save_session_to_file(session_file)
            print(f"Sesión guardada en {session_file}.")

        # Esperar hasta que la sesión haya iniciado
        time.sleep(random.uniform(2, 5))

        # Lista de usuarios
        usuarios = USERSTOTEST.split(",")
        usuarios = [usuario.strip() for usuario in usuarios]

        def download_image_to_memory(src):
            response = requests.get(src)
            image_bytes = io.BytesIO(response.content)
            print(f"Imagen descargada en memoria.")
            return image_bytes

        def rmsdiff(im1, im2):

            diff = ImageChops.difference(im1, im2)
            h = diff.histogram()

            # Calcular la raíz cuadrada de la media de las diferencias cuadradas
            rms = math.sqrt(
                reduce(operator.add, (h * (i**2) for i, h in enumerate(h)))
                / (float(im1.size[0]) * im1.size[1])
            )
            return rms

        def compare_images(image_bytes):
            # Cargar las imágenes desde la memoria
            test_image = Image.open(test_image_bytes).convert(
                "L"
            )  # Convertir a escala de grises
            img_to_compare = Image.open(image_bytes).convert(
                "L"
            )  # Convertir a escala de grises

            # Redimensionar a un tamaño fijo
            test_image = test_image.resize((256, 256))
            img_to_compare = img_to_compare.resize((256, 256))

            # Calcular la diferencia RMS
            rms_difference = rmsdiff(test_image, img_to_compare)
            print(f"Diferencia RMS: {rms_difference}")

            # Establecer un umbral para considerar las imágenes "iguales"
            if rms_difference < 10:  # Ajusta el umbral según sea necesario
                print("Las imágenes son lo suficientemente similares.")
                return True
            else:
                print("Las imágenes son diferentes.")
                return False

        # Array para almacenar los resultados
        results = {
            "coinciden": [],
            "no_coinciden": [],
        }

        def obtener_historias_y_comparar(usuario):
            profile = instaloader.Profile.from_username(L.context, usuario)
            time.sleep(random.uniform(2, 5))
            try:
                print(f"Obteniendo historias de {usuario}...")
                for story in L.get_stories(userids=[profile.userid]):
                    for item in story.get_items():
                        # Descargar la imagen a la memoria
                        if item.typename == "GraphStoryImage":  # Verificar si es imagen
                            image_bytes = download_image_to_memory(item.url)

                            # Comparar con la imagen de prueba
                            if compare_images(image_bytes):
                                results["coinciden"].append(usuario)
                                print(
                                    f"Historia coincidente encontrada para {usuario}."
                                )
                                return  # Dejar de buscar más historias para este usuario
            except Exception as e:
                print(f"No se pudieron obtener historias para {usuario}: {str(e)}")

            # Si ninguna historia coincide, agregar al array de no coinciden
            results["no_coinciden"].append(usuario)

        # Procesar cada usuario
        for usuario in usuarios:
            obtener_historias_y_comparar(usuario)
            print("Siguiente usuario...")

        print("Usuarios con historias coincidentes:", results["coinciden"])
        print("Usuarios sin historias coincidentes:", results["no_coinciden"])

        print("Fin del Programa")

        # Contar los resultados
        num_coinciden = len(results["coinciden"])
        num_no_coinciden = len(results["no_coinciden"])

        # Guardar resultados y conteo en la sesión
        request.session["results"] = results
        request.session["num_coinciden"] = num_coinciden
        request.session["num_no_coinciden"] = num_no_coinciden
        return redirect("result")

    return render(request, "home.html")


def result(request):
    results = request.session.get(
        "results"
    )  # Supongamos que guardas los resultados en la sesión
    return render(request, "result.html", {"results": results})
