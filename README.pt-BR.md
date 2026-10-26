<div align="center">

<img src="docs/banner.svg" alt="Moodle-Mcp" width="100%">

# Moodle-Mcp

### O Moodle que agentes de IA realmente conseguem usar

Leia tarefas, prazos e arquivos do curso direto da Web Service API do Moodle. Sem navegador, sem scraper, sem cliques.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="Zero dependências">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<a href="README.md">English</a> ·
<a href="README.zh-CN.md">简体中文</a> ·
<a href="README.zh-TW.md">繁體中文</a> ·
<a href="README.ja.md">日本語</a> ·
<a href="README.ko.md">한국어</a> ·
<a href="README.es.md">Español</a> ·
<a href="README.fr.md">Français</a> ·
<a href="README.de.md">Deutsch</a> ·
<b>Português</b> ·
<a href="README.ru.md">Русский</a>
</p>

</div>

## Prévia 🖥️

<img src="docs/preview.svg" alt="Exemplo de sessão MCP" width="100%">

---

## Por que existe 🎯

O Moodle sustenta as plataformas de ensino de universidades no mundo todo, mas nunca teve um servidor MCP genérico. Raspar com navegador headless é lento, frágil e costuma esbarrar no WAF; já o Moodle oferece uma API REST estável e documentada.

Este projeto é a camada que faltava: **um arquivo Python sem dependências, seis ferramentas somente leitura**, válido para qualquer Moodle 3.x/4.x com Web Services ativados.

```text
Sem pip install. Sem node. Sem navegador. Só python server.py.
```

## Recursos ✨

### Obtenção de dados
- **Prazos legíveis** — as tarefas são classificadas em «a vencer», «atrasadas» e «sem pressa», com os dias restantes já calculados
- **Resumo semanal** — novidades + a vencer + atrasadas em uma chamada, já formatado para leitura
- **Arquivos do curso** — estrutura de seções e lista de arquivos, com links diretos e data de modificação; apenas metadados, sem baixar nada
- **Diagnóstico embutido** — `moodle_site_info` informa a versão do site, a identidade da conta e as funções que o token realmente pode chamar

### Implementação
- **Zero dependências** — só biblioteca padrão do Python (`urllib`, `json`, `ssl`)
- **Arquivo único** — copie `server.py` para qualquer lugar; sem estrutura de pacote, sem etapa de build
- **stdio JSON-RPC 2.0** — conecta direto no Claude Desktop, Cursor, Marvis ou qualquer cliente compatível com MCP
- **Amigável ao WAF** — requisições serializadas com 150 ms de intervalo, porque insistir no Moodle só devolve `502`
- **Somente leitura por projeto** — não existe código para enviar, matricular, editar ou excluir

## Ferramentas 🧰

| Ferramenta | Função | Parâmetros |
|---|---|---|
| `moodle_site_info` | Valida o token e devolve nome do site, versão do Moodle, usuário atual e funções disponíveis para a conta (diagnóstico). | — |
| `moodle_list_courses` | Lista todos os cursos matriculados com ID, nome curto e nome completo. | — |
| `moodle_recent_updates` | Conteúdo novo ou alterado nos últimos N dias (tarefas, arquivos, avisos), do mais recente ao mais antigo. | `days` (padrão 7), `course_ids` |
| `moodle_pending_assignments` | Tarefas não enviadas, classificadas em **a vencer** / **atrasadas** / **sem pressa**, com prazo e dias restantes. | `ahead_days` (padrão 14), `course_ids` |
| `moodle_course_files` | Estrutura de seções e arquivos de um curso, com links de download e data de modificação. **Apenas metadados: não baixa nada.** | `course_id` |
| `moodle_download_week` | Baixa os arquivos de uma semana (slides + anexos de tarefas) para uma pasta local `Week N`: cria diretórios, confere tamanhos e ignora o que já existe. Sem `dest_root`, apenas lista. | `course_id`, `week` (ex.: `6` ou `"Week 6"`, ou `all`), `dest_root` |
| `moodle_weekly_digest` | Resumo completo em uma chamada: novidades + a vencer + atrasadas + estatísticas. Ponto de partida recomendado. | `days` (padrão 7), `ahead_days` (padrão 14) |

## Requisitos 📦

| Item | Detalhe |
|---|---|
| Python | 3.8+ (somente biblioteca padrão) |
| Protocolo MCP | `2024-11-05` |
| Moodle | 3.x / 4.x com Web Services e protocolo REST ativos |
| Conta | Com permissão `webservice/rest:use` |
| Ambiente testado | Moodle 4.3.6, conta com 435 funções atribuídas (permissões completas) |

## Início rápido 🚀

### ① Obter um token

O Moodle exige uma chave de acesso pessoal. Escolha conforme o seu site:

**A. Interface web (recomendado, funciona também com SSO)**

1. Entre no seu Moodle
2. Foto do perfil → *Preferências* → *Conta* → *Segurança* → *Gerenciar chaves de acesso*
3. Clique em «Criar», nome `moodle-mcp`, serviço *Moodle mobile web service*
4. Copie a chave gerada

**B. Por script usando o serviço móvel (só se o site mantiver senha local)**

```bash
python get_token.py
```

O script troca credenciais em `/login/token.php` com o serviço `moodle_mobile_app` e valida o token na hora. A senha não é exibida nem registrada. Em contas apenas SSO ele retorna `invalidlogin`: use a opção A.

**C. Variáveis de ambiente**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② Configurar

Crie `config.json` ao lado de `server.py` (pode copiar `config.example.json`):

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Variáveis de ambiente têm prioridade sobre o arquivo.

### ③ Registrar o servidor

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

Use o caminho absoluto de `server.py` em `args`. Havendo várias versões de Python, aponte `command` para o interpretador completo.

### ④ Verificar

Peça ao cliente para chamar `moodle_site_info`. Com a configuração correta virão o nome do site, a versão do Moodle e seus dados de usuário. Se falhar, veja «Perguntas frequentes».

## Referência de configuração ⚙️

| Chave | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `url` / `MOODLE_URL` | string | Sim | URL raiz do site, sem caminho no final |
| `token` / `MOODLE_TOKEN` | string | Sim | Token pessoal gerado em «Gerenciar chaves de acesso» |
| `config.json` | arquivo | Opcional | Lido do diretório de `server.py` |

Prioridade: variáveis de ambiente → `config.json` → erro.

## Exemplos de uso 💬

> «O que ainda falta entregar esta semana?»

O agente chama `moodle_weekly_digest` e devolve um resumo pronto para ler:

```text
## Vence em 7 dias e não enviado
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3 dias |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 dias |

## Atrasadas
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 dias de atraso |

## Estatísticas
Enviadas/corrigidas: 51 ｜ Pendentes: 25 (a vencer 4, atrasadas 14, outras 7)
```

Outros comandos úteis:

| Você diz | Ferramenta chamada |
|---|---|
| «O que há de novo em CIS225 esta semana?» | `moodle_recent_updates` |
| «Liste os arquivos de GER405, sem baixar» | `moodle_course_files` |
| «Quais cursos não têm nada atrasado?» | `moodle_pending_assignments` |
| «Meu token ainda é válido?» | `moodle_site_info` |

## Perguntas frequentes 🤔

<details>
<summary><b>get_token.py retorna <code>invalidlogin</code></b></summary>

Sua conta funciona apenas com SSO/OIDC e `/login/token.php` não tem senha local para validar. Use a opção A e crie o token em «Gerenciar chaves de acesso».
</details>

<details>
<summary><b>A chamada retorna <code>502</code> ou a conexão cai</b></summary>

É o limite de taxa do WAF do site. Este servidor já serializa as requisições com 150 ms de intervalo; se ainda ocorrer, espere alguns minutos e evite chamar várias ferramentas em paralelo.
</details>

<details>
<summary><b>A ferramenta retorna lista vazia</b></summary>

Verifique três pontos: Web Services e REST ativos, conta com `webservice/rest:use` e filtro `course_ids` correto. Rode primeiro `moodle_site_info`: se a lista de funções for muito curta, o administrador liberou apenas o subconjunto móvel.
</details>

<details>
<summary><b>Prazos de Turnitin ou quiz não aparecem</b></summary>

Comportamento esperado. `turnitintooltwo` e `quiz` são módulos independentes sem a semântica de `mod_assign`, então este servidor não os lê. Confira na web.
</details>

<details>
<summary><b>Uma tarefa mostra «not set» como prazo</b></summary>

O docente não definiu prazo para essa tarefa, então não há valor a calcular. A tarefa continua na lista para você não perdê-la de vista.
</details>

<details>
<summary><b>Acentuação quebrada no terminal do Windows</b></summary>

A saída é UTF-8. Em consoles antigos execute `chcp 65001` ou use o Windows Terminal.
</details>

## Segurança 🔒

- O token é uma **credencial**. Deixe apenas em `config.json` ou variáveis de ambiente, nunca no repositório; o `.gitignore` já exclui `config.json` e `get_token.log`.
- `get_token.py` não registra o conteúdo da senha, apenas o comprimento, e a lê com `getpass`.
- Todas as ferramentas são somente leitura: mesmo com o token vazado, nada pode ser alterado ou excluído por este servidor. Em caso de vazamento, revogue a chave em «Gerenciar chaves de acesso».
- Não publique capturas de tráfego: o `wstoken` vai no corpo da requisição.

## Compatibilidade ✅

| Cliente / plataforma | Estado |
|---|---|
| Claude Desktop | Suportado (entrada de servidor stdio) |
| Cursor | Suportado (`mcp.json`) |
| Marvis | Suportado (registro MCP) |
| Outros clientes MCP | Suportado — JSON-RPC 2.0 padrão sobre stdio |
| Windows / macOS / Linux | Suportado — sem código específico de plataforma |

## Roteiro 🗺️

- [ ] Suportar prazos de Turnitin e quiz no limite do que a API permite
- [ ] Cache local opcional para reduzir idas e voltas em listas grandes
- [ ] Avisos de paginação para contas com muitos cursos
- [ ] Detalhes do **status** de entrega (corrigida / com feedback), sempre somente leitura
- [ ] Levar a mesma superfície de ferramentas para LMS que não sejam Moodle

## Contribuindo 🤝

Issues e pull requests são bem-vindos. O servidor é um único arquivo: ler `server.py` leva minutos.

- Mantenha zero dependências: apenas biblioteca padrão.
- Todas as ferramentas devem continuar somente leitura.
- Nunca faça commit de `config.json`, tokens ou capturas de tráfego.
- Ao adicionar ferramenta, atualize a tabela e o README de **todos os idiomas**.

## Feedback 📢

Bugs e sugestões: [abra uma issue](https://github.com/Faixiang/moodle-mcp/issues).

## Licença 📝

MIT — veja [LICENSE](LICENSE).
