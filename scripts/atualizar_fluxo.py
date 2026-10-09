"""
Atualiza as issues do PCI-LEADS para o novo fluxo de trabalho:

  - Pedro: escreve o código das issues dele, faz os commits e o push na branch.
  - Marcos: abre todos os PRs, revisa, analisa, faz os merges e cuida das
    configurações do repositório.

O que o script muda:
  - Issue "Leia primeiro" (#1): reescreve as seções de combinados.
  - Todas as issues: troca a linha "Revisor" por "Revisão, PR e merge: Marcos André".
  - Issue do CI (#5): a parte de configurar o repositório passa para o Marcos.

Uso:
  python scripts/atualizar_fluxo.py --dry-run   # só mostra o que mudaria
  python scripts/atualizar_fluxo.py             # aplica
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

REPO = "Marcos-Dev-PCI/PCI-LEADS"
MARCADOR = re.compile(r"<!-- pci-leads:([\w-]+) -->")

NOVO_GUIA = """## Como dividimos

Cada um é dono das suas issues (veja o mapa abaixo). Os papéis no fluxo são:

| Quem | Faz |
|---|---|
| **Pedro** | Escreve o código das issues dele, faz os commits e o push na branch da issue |
| **Marcos** | Escreve o código das issues dele, **abre todos os PRs, revisa e analisa todo o código, faz os merges** e cuida das configurações do repositório (Settings, proteção de branches, quadro) |

As decisões que afetam o projeto inteiro (issues com a etiqueta `dupla`) continuam sendo feitas juntos.

## Fluxo de uma issue do Pedro

1. Pedro cria a branch a partir da `develop` (ex.: `feature/importacao-csv`) e move o card para **Fazendo**.
2. Pedro faz os commits e o `git push` da branch.
3. Pedro comenta na issue: **"Pronto para revisão — branch `nome-da-branch`"**.
4. Marcos abre o PR, move o card para **Em revisão** e revisa.
5. Se precisar de ajuste, Marcos comenta no PR; Pedro corrige **na mesma branch** e dá push de novo.
6. Marcos faz o merge; a issue fecha sozinha e vai para **Feito**.

## Combinados

- Ninguém faz push direto na `main` nem na `develop` (as duas são protegidas).
- Mudança no modelo de dados ou no formato da API: atualizar `docs/modelo-de-dados.md`.
- Travou? Comente na issue e marque o outro (`@usuario`).
- Precisa mudar alguma configuração do repositório? Peça ao Marcos na própria issue.
- Branches e mensagens de commit seguem o padrão do README.

## Ao terminar uma issue (Pedro)

- [ ] Commits feitos na branch da issue e `git push` enviado
- [ ] Testado localmente (`docker compose exec backend python manage.py test` e/ou `npm run build`)
- [ ] Comentário na issue avisando que está pronta para revisão, com o nome da branch

"""

LINHA_REVISOR = re.compile(r"^- \*\*Revisor:\*\* .*$", re.MULTILINE)
NOVA_LINHA_REVISOR = "- **Revisão, PR e merge:** Marcos André"

TROCAS_ESPECIFICAS = {
    "f0-ci": [
        (
            "- [ ] Exigir o CI verde para fazer merge (proteção de branch)",
            "- [ ] Avisar o Marcos com os nomes dos jobs, para ele exigir o CI verde no merge "
            "(configuração do repositório, feita só por ele)",
        ),
    ],
}


def gh(args: list[str], entrada: str | None = None) -> str:
    exe = shutil.which("gh")
    if not exe:
        sys.exit("ERRO: GitHub CLI (gh) não encontrado.")
    r = subprocess.run([exe, *args], input=entrada, capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(f"ERRO: gh {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


def novo_corpo(chave: str, corpo: str) -> str:
    novo = corpo.replace("\r\n", "\n")

    if chave == "guia":
        inicio = novo.find("## Como dividimos")
        fim = novo.find("## Mapa das tarefas")
        if inicio != -1 and fim != -1:
            novo = novo[:inicio] + NOVO_GUIA + novo[fim:]

    novo = LINHA_REVISOR.sub(NOVA_LINHA_REVISOR, novo)

    for antigo, atual in TROCAS_ESPECIFICAS.get(chave, []):
        novo = novo.replace(antigo, atual)

    return novo


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="só mostra o que mudaria")
    a = p.parse_args()

    issues = json.loads(gh(["issue", "list", "--repo", REPO, "--state", "all",
                            "--limit", "500", "--json", "number,body"]))
    alteradas = 0
    for issue in sorted(issues, key=lambda i: i["number"]):
        corpo = issue.get("body") or ""
        m = MARCADOR.search(corpo)
        if not m:
            continue
        chave = m.group(1)
        atualizado = novo_corpo(chave, corpo)
        if atualizado == corpo.replace("\r\n", "\n"):
            print(f"  sem mudança  #{issue['number']}")
            continue
        alteradas += 1
        if a.dry_run:
            print(f"  [dry-run] mudaria #{issue['number']} ({chave})")
        else:
            gh(["issue", "edit", str(issue["number"]), "--repo", REPO, "--body-file", "-"],
               entrada=atualizado)
            print(f"  ok  #{issue['number']} ({chave})")

    print(f"\n{alteradas} issue(s) {'seriam alteradas' if a.dry_run else 'alteradas'}.")


if __name__ == "__main__":
    main()