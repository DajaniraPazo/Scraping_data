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

    # Limpiar columnas numéricas
    df['Puntaje'] = pd.to_numeric(df['Puntaje'], errors='coerce')
    df['Mérito E.P'] = pd.to_numeric(df['Mérito E.P'], errors='coerce')

    # Crear dashboard
    dashboard_data = []
    
    # Por escuela (carrera)
    for escuela, group in df.groupby('Escuela'):
        total_postulantes = len(group)
        ingresantes = group['Observación'].str.contains('ALCANZÓ VACANTE', na=False).sum()
        
        puntaje_promedio = group['Puntaje'].mean()
        puntaje_maximo = group['Puntaje'].max()
        
        merito_promedio = group['Mérito E.P'].mean()
        merito_maximo = group['Mérito E.P'].max()
        
        dashboard_data.append({
            'Escuela': escuela,
            'Total Postulantes': total_postulantes,
            'Ingresantes': ingresantes,
            'Puntaje Promedio': puntaje_promedio,
            'Puntaje Máximo': puntaje_maximo,
            'Mérito Promedio': merito_promedio,
            'Mérito Máximo': merito_maximo
        })

    # Crear DataFrames ordenados para cada categoría
    df_postulantes = pd.DataFrame(dashboard_data).sort_values('Total Postulantes', ascending=False)
    df_ingresantes = pd.DataFrame(dashboard_data).sort_values('Ingresantes', ascending=False)
    df_puntaje_promedio = pd.DataFrame(dashboard_data).sort_values('Puntaje Promedio', ascending=False)
    df_puntaje_maximo = pd.DataFrame(dashboard_data).sort_values('Puntaje Máximo', ascending=False)
    df_merito_promedio = pd.DataFrame(dashboard_data).sort_values('Mérito Promedio', ascending=False)
    df_merito_maximo = pd.DataFrame(dashboard_data).sort_values('Mérito Máximo', ascending=False)

    os.makedirs("output", exist_ok=True)
    
    # Guardar Excel principal
    df.to_excel("output/resultados_sanmarcos.xlsx", index=False)
    
    # Guardar dashboard en otro Excel
    with pd.ExcelWriter("output/dashboard.xlsx") as writer:
        df_postulantes.to_excel(writer, sheet_name='Más Postulantes', index=False)
        df_ingresantes.to_excel(writer, sheet_name='Más Ingresantes', index=False)
        df_puntaje_promedio.to_excel(writer, sheet_name='Mejor Puntaje Promedio', index=False)
        df_puntaje_maximo.to_excel(writer, sheet_name='Mejor Puntaje Máximo', index=False)
        df_merito_promedio.to_excel(writer, sheet_name='Mejor Mérito Promedio', index=False)
        df_merito_maximo.to_excel(writer, sheet_name='Mejor Mérito Máximo', index=False)

    print("Excel generado correctamente")
    print("Dashboard creado: output/dashboard.xlsx")
    ##SE HIZO UN MERGE CON feat/new_excel

    driver.quit()


if __name__ == "__main__":
    main()
    
