---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_7206b01ad14e11f18460525400393706
    ReservedCode1: 6LiIY5EM5UjhiBf9ATlPJhdG7+gCI5F3LH2aV/nR/agu5PHYXQsSZnMJ1Bf8oxjbIWyew16cc1TOx7v+Vg8GkMDfhOrWmZb9R4iZdlxtOfZzobGK63j8WtcP5xdnTR1MYxbHFbLFL+z+WwCMsR5aY2N2D5Gzsmgbwc9/5FS3iR5feegC8wXU6HoU1tw=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_7206b01ad14e11f18460525400393706
    ReservedCode2: 6LiIY5EM5UjhiBf9ATlPJhdG7+gCI5F3LH2aV/nR/agu5PHYXQsSZnMJ1Bf8oxjbIWyew16cc1TOx7v+Vg8GkMDfhOrWmZb9R4iZdlxtOfZzobGK63j8WtcP5xdnTR1MYxbHFbLFL+z+WwCMsR5aY2N2D5Gzsmgbwc9/5FS3iR5feegC8wXU6HoU1tw=
---

# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Español** · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md)

Un servidor MCP (Model Context Protocol) que expone la **API Web Service de Moodle** como herramientas que un agente de IA puede invocar directamente. Sin navegador, sin scraper, sin hacer clic en páginas.

Moodle sostiene las plataformas de enseñanza de innumerables universidades de todo el mundo, pero no existía un servidor MCP genérico para él. Este proyecto llena ese hueco: un solo archivo, cero dependencias y seis herramientas, válido para cualquier sitio Moodle 3.x/4.x con Web Services habilitados.

> Sin paquetes pip, sin node, sin navegador. Solo `python server.py`.

## Por qué existe

Un agente puede leer el programa de la asignatura y decirte qué vence mañana, pero la mayor parte del contenido del curso está detrás de un muro de inicio de sesión. Raspar Moodle con un navegador headless es lento, frágil y suele chocar con el WAF. Moodle ya trae una API REST estable y documentada; lo único que faltaba era un envoltorio MCP.

Este servidor usa únicamente la biblioteca estándar de Python (`urllib`, `json`, `ssl`) y habla JSON-RPC 2.0 sobre stdio, por lo que se conecta directamente a Claude Desktop, Cursor, Marvis o cualquier cliente compatible con MCP.

## Herramientas

| Herramienta | Qué hace | Argumentos |
|---|---|---|
| `moodle_site_info` | Valida el token y devuelve el nombre del sitio, la versión de Moodle, el usuario actual y la lista de funciones disponibles para la cuenta (diagnóstico). | — |
| `moodle_list_courses` | Lista todos los cursos matriculados con ID, nombre corto y nombre completo. | — |
| `moodle_recent_updates` | Contenido añadido o actualizado en los últimos N días (tareas, archivos, anuncios), ordenado de más reciente a más antiguo. | `days` (7 por defecto), `course_ids` |
| `moodle_pending_assignments` | Tareas sin entregar, clasificadas en **próximas a vencer** / **vencidas** / **sin presión**, con fecha límite y días restantes. | `ahead_days` (14 por defecto), `course_ids` |
| `moodle_course_files` | Estructura de secciones y lista de archivos de un curso, con enlace directo de descarga y fecha de modificación. **Solo devuelve metadatos, no descarga ningún archivo.** | `course_id` |
| `moodle_weekly_digest` | Resumen completo: novedades recientes + próximas a vencer + vencidas + estadísticas. Recomendado como punto de partida. | `days` (7 por defecto), `ahead_days` (14 por defecto) |

Todas las herramientas son de **solo lectura**. No se ofrecen interfaces de entrega, matriculación, borrado ni edición, de forma deliberada.

## Instalación

### 1. Obtener el token

Moodle requiere un token de acceso personal. Elige una opción según tu sitio:

**A. Interfaz web (recomendado, también sirve con cuentas SSO)**

1. Inicia sesión en tu sitio Moodle
2. Avatar → *Preferencias* → *Cuenta* → *Seguridad* → *Gestionar claves de acceso*
3. Pulsa «Crear», pon `moodle-mcp` como nombre y elige el servicio *Moodle mobile web service*
4. Copia la clave generada

**B. Script con el servicio móvil (solo si el sitio conserva contraseña local)**

```bash
python get_token.py
```

El script obtiene el token mediante `/login/token.php` y el servicio `moodle_mobile_app`, y lo valida enseguida. La contraseña no se muestra en pantalla ni se escribe en el registro. Si la cuenta funciona solo con SSO, devolverá `invalidlogin`; usa entonces la opción A.

**C. Variables de entorno**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. Configuración

Crea `config.json` en el mismo directorio que `server.py`:

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Las variables de entorno tienen prioridad sobre el archivo de configuración.

### 3. Registrar el servidor

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

En `args` pon la ruta absoluta a `server.py`. Si tienes varias versiones de Python, apunta `command` a la ruta completa del intérprete.

## Ejemplo

> «¿Qué me queda pendiente esta semana?»

El agente llama a `moodle_weekly_digest` y recibe un resumen listo para leer:

```
## Vencen en los próximos 7 días y sin entregar
| Curso | Tarea | Fecha límite | Restante |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 días |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 días |

## Vencidas
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 días de retraso |

## Estadísticas
Entregadas/calificadas: 51 ｜ Sin entregar: 25 (próximas 4, vencidas 14, otras 7)
```

## Limitaciones conocidas

- **No cubre Turnitin (`turnitintooltwo`) ni el módulo `quiz`.** Son módulos independientes sin la semántica de `mod_assign`, así que sus fechas límite hay que comprobarlas en la web.
- Las tareas sin fecha límite configurada aparecen como «sin definir».
- El resumen semanal solo cuenta las **no entregadas**; las entregadas sin calificar suman en las estadísticas pero no aparecen en las tablas.
- Algunos WAF responden `502` a peticiones consecutivas. El servidor ya serializa las llamadas con 150 ms de separación; si aun así ocurre, reintenta con más margen.
- El sitio debe tener Web Services activos y la cuenta el permiso `webservice/rest:use`. La mayoría concede la lista completa de funciones; otros solo abren el subconjunto móvil.

## Seguridad

- El token es una **credencial**. Guárdalo solo en `config.json` o en variables de entorno y no lo subas al repositorio; `.gitignore` ya excluye `config.json` y `get_token.log`.
- `get_token.py` no registra la contraseña, solo su longitud, y la lee con `getpass`.
- Todas las herramientas son de solo lectura: aunque el token se filtre, no se puede modificar ni borrar trabajo con este servidor. Si se filtra, revócalo en «Gestionar claves de acceso».
- No publiques capturas de tráfico: el `wstoken` viaja en el cuerpo de la petición.

## Compatibilidad

| Componente | Detalle |
|---|---|
| Python | 3.8+ (solo biblioteca estándar) |
| Protocolo MCP | `2024-11-05` |
| Moodle | 3.x / 4.x con Web Services y protocolo REST activos |
| Entorno probado | Moodle 4.3.6, cuenta con 435 funciones habilitadas (permisos completos) |

## Licencia

MIT — ver [LICENSE](LICENSE).
*（内容由AI生成，仅供参考）*
