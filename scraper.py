import pandas as pd
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def main():
    print("INICIO DEL SCRIPT")

    # CONFIGURACIÓN DEL NAVEGADOR
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # ABRIR PÁGINA PRINCIPAL
    print("Abriendo página...")
    driver.get("https://admision.unmsm.edu.pe/Website20262/A/A.html")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    print("Página cargada correctamente")
    time.sleep(5)

    # EXTRAER LINKS DE CARRERAS
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"Links encontrados: {len(links)}")

    carreras = []

    for link in links:
        try:
            texto = link.text.strip()
            href = link.get_attribute("href")

            if href and "results.html" in href:
                carreras.append((texto, href))
        except:
            continue

    print(f"Carreras reales detectadas: {len(carreras)}")

    # MOSTRAR ALGUNAS
    for c in carreras[:10]:
        print(c)

    # SCRAPING
    data = []
    columnas_excel = [
        "Código",
        "Apellidos y Nombres",
        "Escuela",
        "Puntaje",
        "Mérito E.P",
        "Observación",
    ]

    for nombre, url in carreras:
        try:
            print(f"\nEntrando a: {nombre}")
            driver.get(url)

            time.sleep(5)

            # 🔥 PAGINACIÓN (SOLUCIÓN REAL)
            while True:
                filas = driver.find_elements(By.TAG_NAME, "tr")

                for fila in filas:
                    columnas = fila.find_elements(By.TAG_NAME, "td")

                    if len(columnas) > 0:
                        fila_data = []

                        for i, col in enumerate(columnas[: len(columnas_excel)]):
                            valor = col.text.strip()

                            if i == 3 and not valor:
                                valor = col.get_attribute("data-score") or ""

                            if i == 4 and not valor:
                                valor = col.get_attribute("data-merit") or ""

                            fila_data.append(valor)

                        if len(fila_data) < len(columnas_excel):
                            fila_data.extend([""] * (len(columnas_excel) - len(fila_data)))
                        data.append(fila_data)

                # Intentar ir a siguiente página
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                    boton_next = driver.find_element(By.CSS_SELECTOR, "button.page-link.next")

                    if boton_next.get_attribute("aria-disabled") == "true":
                        break

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_next)
                    time.sleep(0.5)

                    try:
                        boton_next.click()
                    except:
                        driver.execute_script("arguments[0].click();", boton_next)

                    time.sleep(3)

                except:
                    break

        except Exception as e:
            print(f"Error en {nombre}: {e}")
            continue

    # GUARDAR EXCEL
    df = pd.DataFrame(data, columns=columnas_excel)

    os.makedirs("output", exist_ok=True)
    df.to_excel("output/resultados_sanmarcos.xlsx", index=False)

    print("Excel generado correctamente")

    driver.quit()


if __name__ == "__main__":
    main()
    
