<div align="center">

<img src="docs/banner.svg" alt="moodle-mcp" width="100%">

# moodle-mcp

### La Moodle que los agentes de IA sí pueden usar

Lee tareas, fechas de entrega y archivos del curso directamente de la Web Service API de Moodle. Sin navegador, sin scrapers, sin clics.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="Sin dependencias">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<a href="README.md">English</a> ·
<a href="README.zh-CN.md">简体中文</a> ·
<a href="README.zh-TW.md">繁體中文</a> ·
<a href="README.ja.md">日本語</a> ·
<a href="README.ko.md">한국어</a> ·
<b>Español</b> ·
<a href="README.fr.md">Français</a> ·
<a href="README.de.md">Deutsch</a> ·
<a href="README.pt-BR.md">Português</a> ·
<a href="README.ru.md">Русский</a>
</p>

</div>

## Vista previa 🖥️

<img src="docs/preview.svg" alt="Ejemplo de sesión MCP" width="100%">

---

## Por qué existe 🎯

Moodle sostiene las plataformas docentes de universidades de todo el mundo, pero nunca tuvo un servidor MCP genérico. Scrapear con un navegador headless es lento, frágil y suele chocar con el WAF; en cambio, Moodle ya ofrece una API REST estable y documentada.

Este proyecto es esa capa que faltaba: **un archivo Python sin dependencias, seis herramientas de solo lectura**, válido para cualquier Moodle 3.x/4.x con Web Services activado.

```text
Sin pip install. Sin node. Sin navegador. Solo python server.py.
```

## Características ✨

### Obtención de datos
- **Fechas de entrega legibles** — las tareas se clasifican en «próximas», «vencidas» y «sin prisa», con los días restantes ya calculados
- **Resumen semanal** — novedades + próximas + vencidas en una sola llamada, con formato listo para leer
- **Archivos del curso** — estructura de secciones y lista de archivos, con enlaces de descarga y fecha de modificación; solo metadatos, nunca descarga archivos
- **Diagnóstico integrado** — `moodle_site_info` informa la versión del sitio, tu identidad y las funciones que el token puede invocar realmente

### Implementación
- **Cero dependencias** — solo biblioteca estándar de Python (`urllib`, `json`, `ssl`), sin ensuciar el entorno
- **Un solo archivo** — copia `server.py` donde quieras; sin estructura de paquete ni paso de compilación
- **stdio JSON-RPC 2.0** — se conecta directo a Claude Desktop, Cursor, Marvis o cualquier cliente compatible con MCP
- **Amable con el WAF** — peticiones serializadas con 150 ms de separación, porque insistir con Moodle solo devuelve `502`
- **Solo lectura por diseño** — no existe código para entregar, matricularse, editar ni borrar

## Herramientas 🧰

| Herramienta | Función | Parámetros |
|---|---|---|
| `moodle_site_info` | Valida el token y devuelve nombre del sitio, versión de Moodle, usuario actual y funciones disponibles para la cuenta (diagnóstico). | — |
| `moodle_list_courses` | Lista todos los cursos matriculados con ID, nombre corto y nombre completo. | — |
| `moodle_recent_updates` | Contenido nuevo o modificado en los últimos N días (tareas, archivos, avisos), del más reciente al más antiguo. | `days` (7 por defecto), `course_ids` |
| `moodle_pending_assignments` | Tareas sin entregar, clasificadas en **próximas** / **vencidas** / **sin prisa**, con fecha límite y días restantes. | `ahead_days` (14 por defecto), `course_ids` |
| `moodle_course_files` | Estructura de secciones y archivos de un curso, con enlaces de descarga y fecha de modificación. **Solo metadatos: no descarga nada.** | `course_id` |
| `moodle_weekly_digest` | Resumen completo en una llamada: novedades + próximas + vencidas + estadísticas. Recomendado como punto de partida. | `days` (7 por defecto), `ahead_days` (14 por defecto) |

## Requisitos 📦

| Elemento | Detalle |
|---|---|
| Python | 3.8+ (solo biblioteca estándar) |
| Protocolo MCP | `2024-11-05` |
| Moodle | 3.x / 4.x con Web Services y protocolo REST activos |
| Cuenta | Con permiso `webservice/rest:use` |
| Entorno probado | Moodle 4.3.6, cuenta con 435 funciones asignadas (permisos completos) |

## Inicio rápido 🚀

### ① Obtener un token

Moodle requiere una clave de acceso personal. Elige según tu sitio:

**A. Interfaz web (recomendado, funciona también con SSO)**

1. Inicia sesión en tu Moodle
2. Foto de perfil → *Preferencias* → *Cuenta* → *Seguridad* → *Gestionar claves de acceso*
3. Pulsa «Crear», nombre `moodle-mcp`, servicio *Moodle mobile web service*
4. Copia la clave generada

**B. Mediante script con el servicio móvil (solo si el sitio conserva contraseña local)**

```bash
python get_token.py
```

Obtiene el token vía `/login/token.php` con el servicio `moodle_mobile_app` y lo valida al instante. La contraseña no se muestra ni se registra. Con cuentas solo SSO devuelve `invalidlogin`: usa entonces la opción A.

**C. Variables de entorno**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② Configurar

Crea `config.json` junto a `server.py` (puedes copiar `config.example.json`):

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Las variables de entorno tienen prioridad sobre el archivo.

### ③ Registrar el servidor

Claude Desktop / Cursor (`mcp.json`):

```json
{
  "mcpServers": {
    "moodle": {
      "command": "python",
      "args": ["/absolute/path/to/moodle-mcp/server.py"]
    }
  }
}
```

Usa la ruta absoluta de `server.py` en `args`. Si hay varias versiones de Python, apunta `command` al intérprete completo.

### ④ Verificar

Pide al cliente que invoque `moodle_site_info`. Si la configuración es correcta verás el nombre del sitio, la versión de Moodle y tu usuario. Si falla, consulta «Preguntas frecuentes».

## Referencia de configuración ⚙️

| Clave | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `url` / `MOODLE_URL` | string | Sí | URL raíz del sitio, sin ruta final |
| `token` / `MOODLE_TOKEN` | string | Sí | Token personal generado en «Gestionar claves de acceso» |
| `config.json` | archivo | Opcional | Se lee desde el directorio de `server.py` |

Prioridad: variables de entorno → `config.json` → error.

## Ejemplos de uso 💬

> «¿Qué me queda por entregar esta semana?»

El agente llama a `moodle_weekly_digest` y devuelve un resumen listo para leer:

```text
## Vence en 7 días y sin entregar
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3 días |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 días |

## Vencidas
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 días de retraso |

## Estadísticas
Entregadas/calificadas: 51 ｜ Pendientes: 25 (próximas 4, vencidas 14, otras 7)
```

Otras instrucciones útiles:

| Lo que dices | Herramienta invocada |
|---|---|
| «¿Qué material nuevo hay en CIS225 esta semana?» | `moodle_recent_updates` |
| «Lista los archivos de GER405, no los descargues» | `moodle_course_files` |
| «¿Qué cursos no tienen nada vencido?» | `moodle_pending_assignments` |
| «¿Mi token sigue siendo válido?» | `moodle_site_info` |

## Preguntas frecuentes 🤔

<details>
<summary><b>get_token.py devuelve <code>invalidlogin</code></b></summary>

Tu cuenta funciona solo con SSO/OIDC y `/login/token.php` no tiene contraseña local que validar. Usa la opción A y crea el token en «Gestionar claves de acceso».
</details>

<details>
<summary><b>La llamada devuelve <code>502</code> o se corta la conexión</b></summary>

Es el límite de tasa del WAF del sitio. Este servidor ya serializa las peticiones con 150 ms de separación; si aun así ocurre, espera unos minutos y evita invocar varias herramientas en paralelo.
</details>

<details>
<summary><b>La herramienta devuelve una lista vacía</b></summary>

Revisa tres cosas: que Web Services y REST estén activos, que la cuenta tenga `webservice/rest:use` y que el filtro `course_ids` sea correcto. Ejecuta primero `moodle_site_info`: si la lista de funciones es muy corta, el administrador solo habilitó el subconjunto móvil.
</details>

<details>
<summary><b>No aparecen las fechas de Turnitin ni de los cuestionarios</b></summary>

Es el comportamiento esperado. `turnitintooltwo` y `quiz` son módulos independientes sin la semántica de `mod_assign`, así que este servidor no puede leerlos. Verifícalos en la web.
</details>

<details>
<summary><b>Una tarea muestra «not set» como fecha límite</b></summary>

El docente no fijó fecha límite para esa tarea, así que no hay valor que calcular. La tarea sigue en la lista para que no la pierdas de vista.
</details>

<details>
<summary><b>Caracteres corruptos en la terminal de Windows</b></summary>

La salida es UTF-8. En consolas antiguas ejecuta `chcp 65001` o usa Windows Terminal.
</details>

## Seguridad 🔒

- El token es una **credencial**. Déjalo solo en `config.json` o en variables de entorno; nunca lo subas al repositorio. `.gitignore` ya excluye `config.json` y `get_token.log`.
- `get_token.py` no registra el contenido de la contraseña, solo su longitud, y la lee con `getpass`.
- Todas las herramientas son de solo lectura: aunque el token se filtre, no se puede modificar ni borrar nada por este servidor. Si se filtra, revócalo en «Gestionar claves de acceso».
- No publiques capturas de tráfico: `wstoken` viaja en el cuerpo de la petición.

## Compatibilidad ✅

| Cliente / plataforma | Estado |
|---|---|
| Claude Desktop | Compatible (entrada de servidor stdio) |
| Cursor | Compatible (`mcp.json`) |
| Marvis | Compatible (registro MCP) |
| Otros clientes MCP | Compatible — JSON-RPC 2.0 estándar sobre stdio |
| Windows / macOS / Linux | Compatible — sin código dependiente de plataforma |

## Hoja de ruta 🗺️

- [ ] Soportar fechas de Turnitin y cuestionarios en la medida que permita la API
- [ ] Caché local opcional para reducir idas y vueltas en listas grandes
- [ ] Avisos de paginación para cuentas con muchísimos cursos
- [ ] Detalle del **estado** de entrega (calificada / con retroalimentación), siempre en solo lectura
- [ ] Reutilizar la misma superficie de herramientas en LMS que no sean Moodle

## Contribuir 🤝

Issues y pull requests son bienvenidos. Todo el servidor es un archivo: leer `server.py` toma minutos.

- Mantén las cero dependencias: solo biblioteca estándar.
- Todas las herramientas deben seguir siendo de solo lectura.
- Nunca subas `config.json`, tokens ni capturas de tráfico.
- Al añadir una herramienta, actualiza la tabla y el README de **todos los idiomas**.

## Comentarios 📢

Errores y sugerencias: [abre un issue](https://github.com/Faixiang/moodle-mcp/issues).

## Licencia 📝

MIT — ver [LICENSE](LICENSE).
