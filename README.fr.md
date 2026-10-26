---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_73b0faacd14e11f18460525400393706
    ReservedCode1: oC9bM0AA484lZODVd5gvCKJWuJiPPe7wzfxmKQpEDJGnrqwzMz6SHutPNXeKuxXbvvSZTkZDYKUzvJ8UfyJGYKF3m1OumLJH9VDTlKjQ6cFVUoRf40qQWWnIVfU/XFCYzMcZlUq/pxdbAdSPkfDH4PXgD3A2K/g/ivbuhyXWl2NNl+t8mU7WPjDked0=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_73b0faacd14e11f18460525400393706
    ReservedCode2: oC9bM0AA484lZODVd5gvCKJWuJiPPe7wzfxmKQpEDJGnrqwzMz6SHutPNXeKuxXbvvSZTkZDYKUzvJ8UfyJGYKF3m1OumLJH9VDTlKjQ6cFVUoRf40qQWWnIVfU/XFCYzMcZlUq/pxdbAdSPkfDH4PXgD3A2K/g/ivbuhyXWl2NNl+t8mU7WPjDked0=
---

# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · **Français** · [Deutsch](README.de.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md)

Un serveur MCP (Model Context Protocol) qui expose l'**API Web Service de Moodle** sous forme d'outils directement appelables par un agent IA. Pas de navigateur, pas de scraper, pas de clics sur des pages.

Moodle fait tourner les plateformes d'enseignement d'innombrables établissements dans le monde, mais aucun serveur MCP générique n'existait. Ce projet comble ce manque : un seul fichier, zéro dépendance, six outils, compatible avec tout site Moodle 3.x/4.x dont les Web Services sont activés.

> Ni paquet pip, ni node, ni navigateur. Juste `python server.py`.

## Pourquoi ce projet

Un agent sait lire un syllabus et vous dire ce qui est à rendre demain, mais l'essentiel du contenu des cours reste derrière un mur d'authentification. Scraper Moodle avec un navigateur headless est lent, fragile et déclenche souvent le WAF. Moodle dispose déjà d'une API REST stable et documentée ; il ne manquait que l'enveloppe MCP.

Ce serveur n'utilise que la bibliothèque standard de Python (`urllib`, `json`, `ssl`) et parle JSON-RPC 2.0 sur stdio. Il se branche directement sur Claude Desktop, Cursor, Marvis ou tout client compatible MCP.

## Outils

| Outil | Rôle | Paramètres |
|---|---|---|
| `moodle_site_info` | Valide le jeton et renvoie le nom du site, la version de Moodle, l'utilisateur courant et la liste des fonctions accessibles au compte (diagnostic). | — |
| `moodle_list_courses` | Liste tous les cours inscrits avec identifiant, nom court et nom complet. | — |
| `moodle_recent_updates` | Contenus ajoutés ou modifiés depuis N jours (devoirs, fichiers, annonces), du plus récent au plus ancien. | `days` (7 par défaut), `course_ids` |
| `moodle_pending_assignments` | Devoirs non rendus, classés en **échéance proche** / **en retard** / **sans pression**, avec date limite et jours restants. | `ahead_days` (14 par défaut), `course_ids` |
| `moodle_course_files` | Structure des sections et liste des fichiers d'un cours, avec lien de téléchargement direct et date de modification. **Renvoie uniquement des métadonnées, ne télécharge aucun fichier.** | `course_id` |
| `moodle_weekly_digest` | Synthèse complète : nouveautés récentes + échéances proches + retards + statistiques. Recommandé comme point de départ. | `days` (7 par défaut), `ahead_days` (14 par défaut) |

Tous les outils sont en **lecture seule**. Aucune interface de remise, d'inscription, de suppression ou de modification n'est fournie, volontairement.

## Installation

### 1. Obtenir le jeton

Moodle exige un jeton d'accès personnel. Choisissez selon votre site :

**A. Interface web (recommandé, fonctionne aussi avec un compte SSO)**

1. Connectez-vous à votre site Moodle
2. Avatar → *Préférences* → *Compte* → *Sécurité* → *Gérer les clés d'accès*
3. Cliquez sur « Créer », nommez-la `moodle-mcp`, choisissez le service *Moodle mobile web service*
4. Copiez la clé générée

**B. Script via le service mobile (uniquement si le site conserve un mot de passe local)**

```bash
python get_token.py
```

Le script échange vos identifiants via `/login/token.php` et le service `moodle_mobile_app`, puis valide le jeton immédiatement. Le mot de passe n'est ni affiché ni journalisé. Si le compte n'utilise que le SSO, la réponse sera `invalidlogin` : utilisez alors l'option A.

**C. Variables d'environnement**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. Configuration

Créez `config.json` dans le même dossier que `server.py` :

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Les variables d'environnement sont prioritaires sur le fichier de configuration.

### 3. Enregistrer le serveur

Claude Desktop / Cursor (`mcp.json`) :

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

Indiquez le chemin absolu de `server.py` dans `args`. Si plusieurs versions de Python coexistent, pointez `command` vers l'interpréteur complet.

## Exemple

> « Qu'est-ce que je dois encore rendre cette semaine ? »

L'agent appelle `moodle_weekly_digest` et reçoit une synthèse directement lisible :

```
## À rendre sous 7 jours, non remis
| Cours | Devoir | Échéance | Restant |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 jours |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 jours |

## En retard
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 jours de retard |

## Statistiques
Rendus/notés : 51 ｜ Non rendus : 25 (échéance proche 4, retard 14, autres 7)
```

## Limites connues

- **Turnitin (`turnitintooltwo`) et le module `quiz` ne sont pas couverts.** Ce sont des modules distincts, sans la sémantique de `mod_assign` : leurs échéances doivent être vérifiées sur le web.
- Les devoirs sans date limite apparaissent comme « non définie ».
- La synthèse hebdomadaire ne compte que les éléments **non rendus** ; les rendus non notés entrent dans les statistiques mais pas dans les tableaux.
- Certains WAF renvoient `502` sur des requêtes successives. Le serveur sérialise déjà les appels avec un intervalle de 150 ms ; si le problème persiste, réessayez avec un intervalle plus large.
- Le site doit avoir les Web Services actifs et le compte la permission `webservice/rest:use`. La plupart accordent la liste complète des fonctions, d'autres seulement le sous-ensemble mobile.

## Sécurité

- Le jeton est un **identifiant secret**. Ne le placez que dans `config.json` ou des variables d'environnement, jamais dans le dépôt ; `.gitignore` exclut déjà `config.json` et `get_token.log`.
- `get_token.py` ne journalise pas le mot de passe, seulement sa longueur, et le lit via `getpass`.
- Tous les outils sont en lecture seule : même en cas de fuite du jeton, ce serveur ne permet ni de modifier ni de supprimer un devoir. En cas de fuite, révoquez-le dans « Gérer les clés d'accès ».
- Ne publiez pas de captures de trafic : le `wstoken` figure dans le corps de la requête.

## Compatibilité

| Élément | Détail |
|---|---|
| Python | 3.8+ (bibliothèque standard uniquement) |
| Protocole MCP | `2024-11-05` |
| Moodle | 3.x / 4.x avec Web Services et protocole REST activés |
| Environnement testé | Moodle 4.3.6, compte disposant de 435 fonctions (droits complets) |

## Licence

MIT — voir [LICENSE](LICENSE).
*（内容由AI生成，仅供参考）*
