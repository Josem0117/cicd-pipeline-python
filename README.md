# cicd-pipeline-python

Calculadora web (Flask) con un pipeline de Integración Continua en GitHub Actions:
Black, Pylint, Flake8, pytest + cobertura, pruebas de aceptación con Selenium contra
la imagen Docker, análisis en SonarCloud y publicación de la imagen en Docker Hub.

## Integrantes

Jose Miguel Blanco

| Integrante | Usuario de GitHub | Rol |
|---|---|---|
| Jose Miguel Blanco | [@Josem0117](https://github.com/Josem0117) | Propietario del repositorio |

## Evidencias

- Pull Request integrado (sección 9.2): https://github.com/Josem0117/cicd-pipeline-python/pull/1
- Ejecución fallida del pipeline con el error intencional en `restar`: https://github.com/Josem0117/cicd-pipeline-python/actions/runs/43542439279

## Respuestas

### 1. ¿Qué ventajas le aporta a un proyecto el uso de un pipeline de CI?

Cada cambio se valida de forma automática y siempre igual: formato, análisis estático,
pruebas y construcción de la imagen. Los errores aparecen minutos después del commit,
cuando corregirlos es barato, y no dependen de que alguien recuerde ejecutar las
pruebas en su máquina. Además deja evidencia de cada ejecución, evita que `main`
reciba código roto y produce un artefacto (la imagen Docker) que ya fue probado.

### 2. ¿Cuál es la diferencia entre una prueba unitaria, una de componente y una de aceptación?

- **Unitaria** (`tests/test_calculadora.py`): prueba una función aislada, sin servidor
  ni navegador. Es la más rápida y señala con precisión dónde está el fallo.
- **De componente** (`tests/test_app.py`): prueba la aplicación Flask completa (rutas,
  lógica y plantilla) con el cliente de pruebas de Flask, sin levantar un servidor real.
- **De aceptación** (`tests/test_acceptance_app.py`): prueba la aplicación como un
  usuario, con un navegador real (Selenium) contra el contenedor en ejecución. Es la
  más lenta, pero valida el sistema tal como se va a entregar.

### 3. ¿Qué hace cada uno de los principales steps del workflow?

- **Checkout**: clona el repositorio con historial completo (SonarCloud lo usa para
  identificar el código nuevo).
- **Set up Python / Install dependencies**: instala Python 3.13 y `requirements-dev.txt`.
- **Run Black**: verifica el formato con `--check`; si falla, detiene el pipeline.
- **Run Pylint / Run Flake8**: generan los reportes que importa SonarCloud; con
  `--exit-zero` los hallazgos no detienen el pipeline.
- **Run Unit and Component Tests**: ejecuta pytest y falla si alguna prueba falla o la
  cobertura total es menor al 80 %. Genera `coverage.xml`.
- **Build Docker image**: construye la imagen una sola vez, etiquetada con el SHA.
- **Start container**: levanta el contenedor y espera a que responda en el puerto 8000.
- **Run Acceptance Tests**: ejecuta Selenium contra ese contenedor.
- **Upload Test Reports Artifacts**: guarda los reportes aunque el pipeline falle.
- **SonarCloud Scan**: envía los reportes y espera el Quality Gate.
- **Login to Docker Hub / Push Docker image**: solo en un push a `main`, publican la
  imagen con las etiquetas del SHA y `latest`.

### 4. ¿Qué dificultades encontró cada integrante y cómo las resolvió?

N/A

### 5. ¿Qué ventajas tiene publicar la misma imagen que fue probada?

Lo que se despliega es exactamente lo que pasó las pruebas: mismas dependencias, mismo
código y misma configuración. Si se reconstruyera la imagen para publicarla, podría
cambiar una dependencia o la imagen base y se entregaría algo que nadie validó. La
etiqueta con el SHA da trazabilidad entre la imagen y el commit, y permite volver a
una versión anterior.

### 6. Análisis del Pull Request con el error intencional

En el Pull Request #1 se cambió a propósito `restar` para que devolviera `a + b`. El
pipeline falló en el step **Run Unit and Component Tests**: pytest reportó fallos en
`test_restar` y `test_restar_resultado_negativo` de `tests/test_calculadora.py` y en
`test_index_post_restar` de `tests/test_app.py`, y el step terminó con código de
salida 1.

Como cada step solo se ejecuta si el anterior termina bien, no se construyó la imagen
Docker, no corrieron las pruebas de aceptación ni el análisis de SonarCloud, y no se
publicó nada en Docker Hub. Solo se ejecutaron los steps marcados con `if: always()`
o `if: failure()` (subir los reportes y mostrar los logs del contenedor).

La regla `proteger-main` exige que el check `build-and-test` esté en verde y una
aprobación, así que GitHub bloqueó el botón de merge mientras el error estuvo en la
rama. El cambio solo se pudo integrar después de corregir `restar`, de que el pipeline
volviera a pasar y de que el revisor aprobara el Pull Request. El error se detectó en
unos 20 segundos y nunca llegó a `main` ni a la imagen publicada.

## Ejecución local

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.app                                  # http://localhost:5000
pytest --ignore=tests/test_acceptance_app.py --cov-fail-under=80
pytest tests/test_acceptance_app.py --no-cov --html=acceptance-report.html   # con la app en ejecución
```
