<div align="center">

<img src="docs/banner.svg" alt="moodle-mcp" width="100%">

# moodle-mcp

### Le Moodle que les agents IA peuvent vraiment utiliser

Lisez les devoirs, les échéances et les fichiers de cours directement depuis l'API Web Service de Moodle. Sans navigateur, sans scraper, sans clics.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="Zéro dépendance">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<a href="README.md">English</a> ·
<a href="README.zh-CN.md">简体中文</a> ·
<a href="README.zh-TW.md">繁體中文</a> ·
<a href="README.ja.md">日本語</a> ·
<a href="README.ko.md">한국어</a> ·
<a href="README.es.md">Español</a> ·
<b>Français</b> ·
<a href="README.de.md">Deutsch</a> ·
<a href="README.pt-BR.md">Português</a> ·
<a href="README.ru.md">Русский</a>
</p>

</div>

## Aperçu 🖥️

<img src="docs/preview.svg" alt="Exemple de session MCP" width="100%">

---

## Pourquoi ce projet 🎯

Moodle fait tourner les plateformes pédagogiques d'universités du monde entier, mais n'avait jamais eu de serveur MCP générique. Le scraping par navigateur headless est lent, fragile et déclenche souvent le WAF ; or Moodle expose déjà une API REST stable et documentée.

Ce projet est la couche manquante : **un fichier Python sans dépendance, six outils en lecture seule**, compatible avec tout Moodle 3.x/4.x dont les Web Services sont activés.

```text
Pas de pip install. Pas de node. Pas de navigateur. Juste python server.py.
```

## Fonctionnalités ✨

### Récupération des données
- **Échéances lisibles** — les devoirs sont classés en « bientôt dû », « en retard » et « sans urgence », avec le nombre de jours restants déjà calculé
- **Digest hebdomadaire** — nouveautés + échéances proches + retards en un seul appel, déjà mis en forme
- **Fichiers de cours** — structure des sections et liste des fichiers, avec liens directs et dates de modification ; métadonnées uniquement, aucun téléchargement
- **Diagnostic intégré** — `moodle_site_info` indique la version du site, l'identité du compte et les fonctions réellement appelables avec le token

### Implémentation
- **Zéro dépendance** — uniquement la bibliothèque standard (`urllib`, `json`, `ssl`), rien à installer
- **Fichier unique** — copiez `server.py` n'importe où ; pas de paquet, pas d'étape de build
- **stdio JSON-RPC 2.0** — se branche directement sur Claude Desktop, Cursor, Marvis ou tout client compatible MCP
- **Respectueux du WAF** — requêtes sérialisées à 150 ms d'intervalle, car insister sur Moodle ne renvoie qu'un `502`
- **Lecture seule par conception** — aucun code de remise, d'inscription, de modification ou de suppression

## Outils 🧰

| Outil | Rôle | Paramètres |
|---|---|---|
| `moodle_site_info` | Valide le token et renvoie le nom du site, la version de Moodle, l'utilisateur courant et les fonctions disponibles (diagnostic). | — |
| `moodle_list_courses` | Liste tous les cours inscrits avec ID, nom abrégé et nom complet. | — |
| `moodle_recent_updates` | Contenus ajoutés ou modifiés ces N derniers jours (devoirs, fichiers, annonces), du plus récent au plus ancien. | `days` (7 par défaut), `course_ids` |
| `moodle_pending_assignments` | Devoirs non rendus, classés en **bientôt dû** / **en retard** / **sans urgence**, avec échéance et jours restants. | `ahead_days` (14 par défaut), `course_ids` |
| `moodle_course_files` | Structure des sections et fichiers d'un cours, avec liens de téléchargement et dates de modification. **Métadonnées seules : aucun téléchargement.** | `course_id` |
| `moodle_weekly_digest` | Synthèse en un appel : nouveautés + échéances proches + retards + statistiques. Point de départ recommandé. | `days` (7 par défaut), `ahead_days` (14 par défaut) |

## Prérequis 📦

| Élément | Détail |
|---|---|
| Python | 3.8+ (bibliothèque standard uniquement) |
| Protocole MCP | `2024-11-05` |
| Moodle | 3.x / 4.x avec Web Services et protocole REST activés |
| Compte | Disposant du droit `webservice/rest:use` |
| Environnement testé | Moodle 4.3.6, compte doté de 435 fonctions (droits complets) |

## Démarrage rapide 🚀

### ① Obtenir un token

Moodle exige une clé d'accès personnelle. Choisissez selon votre site :

**A. Interface web (recommandé, fonctionne aussi avec SSO)**

1. Connectez-vous à votre Moodle
2. Photo de profil → *Préférences* → *Compte* → *Sécurité* → *Gérer les clés d'accès*
3. Cliquez sur « Créer », nom `moodle-mcp`, service *Moodle mobile web service*
4. Copiez la clé générée

**B. Via script avec le service mobile (seulement si le site conserve un mot de passe local)**

```bash
python get_token.py
```

Le script échange vos identifiants via `/login/token.php` et le service `moodle_mobile_app`, puis valide le token immédiatement. Le mot de passe n'est ni affiché ni journalisé. Avec un compte SSO uniquement, il renvoie `invalidlogin` : utilisez alors l'option A.

**C. Variables d'environnement**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② Configurer

Créez `config.json` à côté de `server.py` (ou copiez `config.example.json`) :

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Les variables d'environnement priment sur le fichier.

### ③ Enregistrer le serveur

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

Indiquez le chemin absolu de `server.py` dans `args`. Avec plusieurs versions de Python, pointez `command` vers l'interpréteur complet.

### ④ Vérifier

Demandez au client d'appeler `moodle_site_info`. Si la configuration est correcte, vous obtiendrez le nom du site, la version de Moodle et votre utilisateur. En cas d'échec, voir la FAQ ci-dessous.

## Référence de configuration ⚙️

| Clé | Type | Requis | Description |
|---|---|---|---|
| `url` / `MOODLE_URL` | chaîne | Oui | URL racine du site, sans chemin final |
| `token` / `MOODLE_TOKEN` | chaîne | Oui | Token personnel créé dans « Gérer les clés d'accès » |
| `config.json` | fichier | Facultatif | Lu depuis le répertoire de `server.py` |

Priorité : variables d'environnement → `config.json` → erreur.

## Exemples d'usage 💬

> « Qu'est-ce que je dois encore rendre cette semaine ? »

L'agent appelle `moodle_weekly_digest` et renvoie une synthèse directement lisible :

```text
## À rendre sous 7 jours
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3 jours |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 jours |

## En retard
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 jours de retard |

## Statistiques
Rendus/notés : 51 ｜ Restants : 25 (bientôt 4, retard 14, autres 7)
```

Autres demandes utiles :

| Vous dites | Outil appelé |
|---|---|
| « Quoi de neuf dans CIS225 cette semaine ? » | `moodle_recent_updates` |
| « Liste les fichiers de GER405, sans les télécharger » | `moodle_course_files` |
| « Quels cours n'ont rien en retard ? » | `moodle_pending_assignments` |
| « Mon token est-il toujours valide ? » | `moodle_site_info` |

## FAQ 🤔

<details>
<summary><b>get_token.py renvoie <code>invalidlogin</code></b></summary>

Votre compte fonctionne uniquement en SSO/OIDC et `/login/token.php` n'a aucun mot de passe local à valider. Utilisez l'option A pour créer un token dans « Gérer les clés d'accès ».
</details>

<details>
<summary><b>L'appel renvoie <code>502</code> ou la connexion est coupée</b></summary>

C'est la limitation de débit du WAF du site. Ce serveur sérialise déjà les requêtes à 150 ms d'intervalle ; si cela persiste, attendez quelques minutes et évitez d'appeler plusieurs outils en parallèle.
</details>

<details>
<summary><b>L'outil renvoie une liste vide</b></summary>

Vérifiez trois points : les Web Services et REST sont activés, le compte possède `webservice/rest:use`, et le filtre `course_ids` est correct. Lancez d'abord `moodle_site_info` : si la liste de fonctions est très courte, l'administrateur n'a ouvert que le sous-ensemble mobile.
</details>

<details>
<summary><b>Les échéances Turnitin ou quiz n'apparaissent pas</b></summary>

C'est le comportement attendu. `turnitintooltwo` et `quiz` sont des modules indépendants sans la sémantique de `mod_assign` ; ce serveur ne peut pas les lire. Vérifiez sur le web.
</details>

<details>
<summary><b>Une échéance affiche « not set »</b></summary>

L'enseignant n'a pas fixé d'échéance pour ce devoir : il n'y a donc aucune valeur à calculer. Le devoir reste listé pour ne pas le manquer.
</details>

<details>
<summary><b>Caractères illisibles dans le terminal Windows</b></summary>

La sortie est en UTF-8. Sur une console ancienne, lancez `chcp 65001` ou utilisez Windows Terminal.
</details>

## Sécurité 🔒

- Le token est un **identifiant sensible**. Placez-le uniquement dans `config.json` ou des variables d'environnement, jamais dans le dépôt ; `.gitignore` exclut déjà `config.json` et `get_token.log`.
- `get_token.py` ne journalise pas le contenu du mot de passe, seulement sa longueur, et le lit via `getpass`.
- Tous les outils sont en lecture seule : même en cas de fuite du token, ce serveur ne permet ni modification ni suppression. En cas de fuite, révoquez la clé dans « Gérer les clés d'accès ».
- Ne publiez pas de captures de trafic : `wstoken` apparaît dans le corps de la requête.

## Compatibilité ✅

| Client / plateforme | État |
|---|---|
| Claude Desktop | Pris en charge (entrée serveur stdio) |
| Cursor | Pris en charge (`mcp.json`) |
| Marvis | Pris en charge (registre MCP) |
| Autres clients MCP | Pris en charge — JSON-RPC 2.0 standard sur stdio |
| Windows / macOS / Linux | Pris en charge — aucun code spécifique à une plateforme |

## Feuille de route 🗺️

- [ ] Prendre en charge les échéances Turnitin et quiz dans les limites de l'API
- [ ] Cache local optionnel pour limiter les allers-retours sur les gros cours
- [ ] Indications de pagination pour les comptes à très nombreux cours
- [ ] Détail du **statut** de remise (noté / avec retour), toujours en lecture seule
- [ ] Porter la même surface d'outils vers des LMS non Moodle

## Contribution 🤝

Issues et pull requests bienvenues. Le serveur tient en un fichier : lire `server.py` prend quelques minutes.

- Gardez le zéro dépendance : bibliothèque standard uniquement.
- Tous les outils doivent rester en lecture seule.
- Ne commitez jamais `config.json`, un token ou une capture de trafic.
- En ajoutant un outil, mettez à jour le tableau et le README de **toutes les langues**.

## Retours 📢

Bugs et suggestions : [ouvrez une issue](https://github.com/Faixiang/moodle-mcp/issues).

## Licence 📝

MIT — voir [LICENSE](LICENSE).
