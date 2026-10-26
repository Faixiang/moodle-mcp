# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · **Português (BR)** · [Русский](README.ru.md)

Um servidor MCP (Model Context Protocol) que expõe a **API Web Service do Moodle** como ferramentas que um agente de IA pode chamar diretamente. Sem navegador, sem scraper, sem clicar em páginas.

O Moodle sustenta as plataformas de ensino de incontáveis instituições pelo mundo, mas não existia um servidor MCP genérico para ele. Este projeto preenche essa lacuna: arquivo único, zero dependências, seis ferramentas, compatível com qualquer site Moodle 3.x/4.x com Web Services habilitados.

> Sem pacote pip, sem node, sem navegador. Apenas `python server.py`.

## Por que ele existe

Um agente consegue ler o plano de ensino e dizer o que vence amanhã, mas a maior parte do conteúdo do curso fica atrás de um login. Raspar o Moodle com navegador headless é lento, frágil e costuma esbarrar no WAF. O Moodle já tem uma API REST estável e documentada; faltava apenas a camada MCP.

Este servidor usa somente a biblioteca padrão do Python (`urllib`, `json`, `ssl`) e fala JSON-RPC 2.0 sobre stdio, conectando-se direto ao Claude Desktop, Cursor, Marvis ou qualquer cliente compatível com MCP.

## Ferramentas

| Ferramenta | O que faz | Parâmetros |
|---|---|---|
| `moodle_site_info` | Valida o token e retorna nome do site, versão do Moodle, usuário atual e a lista de funções liberadas para a conta (diagnóstico). | — |
| `moodle_list_courses` | Lista todos os cursos matriculados com ID, nome curto e nome completo. | — |
| `moodle_recent_updates` | Conteúdo adicionado ou atualizado nos últimos N dias (tarefas, arquivos, avisos), do mais recente para o mais antigo. | `days` (padrão 7), `course_ids` |
| `moodle_pending_assignments` | Tarefas não entregues, classificadas em **a vencer** / **atrasadas** / **sem pressão**, com prazo e dias restantes. | `ahead_days` (padrão 14), `course_ids` |
| `moodle_course_files` | Estrutura de seções e lista de arquivos de um curso, com link direto de download e data de modificação. **Retorna apenas metadados, não baixa arquivo algum.** | `course_id` |
| `moodle_weekly_digest` | Resumo completo: novidades recentes + a vencer + atrasadas + estatísticas. Recomendado como ponto de partida. | `days` (padrão 7), `ahead_days` (padrão 14) |

Todas as ferramentas são **somente leitura**. Não há, por decisão de projeto, interfaces de envio, matrícula, exclusão ou edição.

## Instalação

### 1. Obter o token

O Moodle exige um token de acesso pessoal. Escolha conforme o seu site:

**A. Interface web (recomendado, funciona também com contas SSO)**

1. Faça login no seu site Moodle
2. Avatar → *Preferências* → *Conta* → *Segurança* → *Gerenciar chaves de acesso*
3. Clique em «Criar», use `moodle-mcp` como nome e escolha o serviço *Moodle mobile web service*
4. Copie a chave gerada

**B. Script pelo serviço mobile (apenas se o site mantiver senha local)**

```bash
python get_token.py
```

O script troca as credenciais por um token via `/login/token.php` e o serviço `moodle_mobile_app`, validando em seguida. A senha não é exibida nem gravada em log. Contas somente SSO recebem `invalidlogin`; nesse caso use a opção A.

**C. Variáveis de ambiente**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. Configuração

Crie `config.json` no mesmo diretório de `server.py`:

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Variáveis de ambiente têm prioridade sobre o arquivo de configuração.

### 3. Registrar o servidor

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

Em `args`, use o caminho absoluto de `server.py`. Com várias versões de Python instaladas, aponte `command` para o caminho completo do interpretador.

## Exemplo

> «O que ainda tenho para entregar esta semana?»

O agente chama `moodle_weekly_digest` e recebe um resumo pronto para leitura:

```
## Vencem nos próximos 7 dias, não entregues
| Curso | Tarefa | Prazo | Restante |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 dias |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 dias |

## Atrasadas
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 dias de atraso |

## Estatísticas
Entregues/corrigidas: 51 ｜ Não entregues: 25 (a vencer 4, atrasadas 14, outras 7)
```

## Limitações conhecidas

- **Turnitin (`turnitintooltwo`) e o módulo `quiz` não são cobertos.** São módulos independentes, sem a semântica de `mod_assign`; os prazos devem ser conferidos na web.
- Tarefas sem prazo definido aparecem como «não definido».
- O resumo semanal conta apenas itens **não entregues**; entregues sem correção entram nas estatísticas, mas não nas tabelas.
- Alguns WAFs devolvem `502` para requisições consecutivas. O servidor já serializa as chamadas com 150 ms de intervalo; se ainda ocorrer, tente novamente com intervalo maior.
- O site precisa ter Web Services ativos e a conta a permissão `webservice/rest:use`. A maioria libera a lista completa de funções; alguns apenas o subconjunto mobile.

## Segurança

- O token é uma **credencial**. Guarde apenas em `config.json` ou variáveis de ambiente e nunca o envie ao repositório; o `.gitignore` já exclui `config.json` e `get_token.log`.
- `get_token.py` não registra a senha, apenas o comprimento, e a lê com `getpass`.
- Todas as ferramentas são somente leitura: mesmo com o token vazado, não é possível alterar ou apagar tarefas por este servidor. Se vazar, revogue em «Gerenciar chaves de acesso».
- Não publique capturas de tráfego: o `wstoken` vai no corpo da requisição.

## Compatibilidade

| Item | Detalhe |
|---|---|
| Python | 3.8+ (somente biblioteca padrão) |
| Protocolo MCP | `2024-11-05` |
| Moodle | 3.x / 4.x com Web Services e protocolo REST ativos |
| Ambiente testado | Moodle 4.3.6, conta com 435 funções liberadas (permissões completas) |

## Licença

MIT — veja [LICENSE](LICENSE).
