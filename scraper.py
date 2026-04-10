import pandas as pd
import time

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
                        fila_data = [col.text for col in columnas]
                        fila_data.append(nombre)
                        data.append(fila_data)

                # Intentar ir a siguiente página
                try:
                    boton_next = driver.find_element(By.ID, "example_next")

                    if "disabled" in boton_next.get_attribute("class"):
                        break

                    boton_next.click()
                    time.sleep(3)

                except:
                    break

        except Exception as e:
            print(f"Error en {nombre}: {e}")
            continue

    # GUARDAR EXCEL
    df = pd.DataFrame(data)

    if not df.empty:
        columnas = [f"col_{i}" for i in range(len(df.columns)-1)] + ["carrera"]
        df.columns = columnas

    df.to_excel("output/resultados_sanmarcos.xlsx", index=False)

    print("Excel generado correctamente")

    driver.quit()


if __name__ == "__main__":
    main()
    
