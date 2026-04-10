# Proyecto: Scraping + API RAWG

Este repositorio contiene el desarrollo de dos tareas enfocadas en la extracción y análisis de datos utilizando Python.

---

## Tarea 1: Web Scraping (UNMSM)

Se implementó un scraper utilizando Selenium para extraer información del proceso de admisión de la UNMSM.

### Funcionalidades:
- Extracción de todas las carreras disponibles
- Navegación automática por tablas dinámicas (DataTables)
- Recolección de datos de postulantes
- Exportación de resultados a Excel

---

## Tarea 2: API RAWG

Se utilizó la API de RAWG para analizar datos de videojuegos.

### Actividades:
- Total de videojuegos registrados
- Top 5 juegos por Metacritic
- Top 10 juegos en Steam
- Comparación PC vs PS5
- Análisis por géneros
- Comparación por años
- Exportación a CSV

---

## Estructura del proyecto
Scraping_data/
│
├── api/
│ ├── output/
│ │ └── top20_rawg.csv
│ └── tarea_rawg_api.ipynb
│
├── scraper.py
├── requirements.txt
├── README.md
└── video/
└── link.txt



## Tecnologías utilizadas

- Python
- Selenium
- Requests
- Pandas
- Jupyter Notebook

---

## Cómo ejecutar

1. Clonar el repositorio:
```bash
git clone https://github.com/DajaniraPazo/Scraping_data.git

