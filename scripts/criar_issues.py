"""
Cria no GitHub as etiquetas, as fases (milestones) e todas as issues do PCI-LEADS,
já divididas entre Marcos André e Pedro Esmeraldo.

Requisitos:
  - GitHub CLI instalado (https://cli.github.com) e autenticado: `gh auth login`
  - Rodar de dentro da pasta do repositório (ou usar --repo dono/repositorio)

Uso:
  python scripts/criar_issues.py --dry-run                      # só mostra o que faria
  python scripts/criar_issues.py --marcos SEU_USUARIO --pedro USUARIO_DO_PEDRO

Pode ser executado mais de uma vez: issues já criadas por ele são reconhecidas
e não são duplicadas.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

# ---------------------------------------------------------------------------
# Pessoas
# ---------------------------------------------------------------------------

PESSOAS = {
    "marcos": "Marcos André",
    "pedro": "Pedro Esmeraldo",
}

# ---------------------------------------------------------------------------
# Etiquetas
# ---------------------------------------------------------------------------

ETIQUETAS = [
    ("backend", "1d76db", "Django / API / banco de dados"),
    ("frontend", "5319e7", "React / telas"),
    ("infra", "0e8a16", "Docker, CI, repositório"),
    ("dados", "fbca04", "Fontes de dados, importação, enriquecimento"),
    ("pesquisa", "c5def5", "Levantamento de informações, sem código"),
    ("documentação", "0075ca", "README e documentos do projeto"),
    ("dupla", "d93f0b", "Fazer os dois juntos (chamada ou presencial)"),
    ("prioridade: alta", "b60205", "Bloqueia outras tarefas"),
    ("opcional", "cccccc", "Fazer só se houver tempo ou necessidade"),
    ("dono: marcos", "bfd4f2", "Responsável: Marcos André"),
    ("dono: pedro", "f9d0c4", "Responsável: Pedro Esmeraldo"),
]

# ---------------------------------------------------------------------------
# Fases (milestones)
# ---------------------------------------------------------------------------

FASES = {
    "F0": ("Fase 0 — Base e combinados",
           "Corrigir a base, organizar o repositório e levantar as informações de negócio."),
    "F1": ("Fase 1 — Modelo de dados",
           "Definir juntos o modelo e o contrato da API, e implementar."),
    "F2": ("Fase 2 — Base da Receita e filtros",
           "Importar empresas do DF a partir da base aberta do CNPJ e navegar por elas."),
    "F3": ("Fase 3 — Importação e exportação",
           "Importar CSV, exportar no formato da Redrive e controlar o funil."),
    "F4": ("Fase 4 — Enriquecimento",
           "Distância até a Asa Norte, resumo e mensagem personalizada."),
    "F5": ("Fase 5 — Score de prioridade",
           "Usar o histórico da PCI para priorizar os leads."),
}

# ---------------------------------------------------------------------------
# Issues
#   chave:     identificador interno (usado nas dependências)
#   fase:      F0..F5
#   dono:      "marcos", "pedro" ou "dupla"
#   depende:   chaves de issues que precisam estar prontas antes
#   corpo:     Markdown. As seções "Conexões" são geradas automaticamente.
# ---------------------------------------------------------------------------

ISSUES: list[dict] = [
    # ------------------------------------------------------------------ Guia
    {
        "chave": "guia",
        "fase": "F0",
        "titulo": "Leia primeiro: como vamos trabalhar juntos",
        "dono": "dupla",
        "etiquetas": ["documentação"],
        "depende": [],
        "corpo": """
            ## Como dividimos

            O trabalho está dividido **por funcionalidade**: cada um é dono de funcionalidades
            completas (banco + API + tela). Assim os dois conhecem o sistema inteiro e ninguém
            fica esperando "a parte do outro" para ver algo funcionando.

            ## Nossos combinados

            1. **Toda issue tem um dono e um revisor.** O revisor é sempre o outro. Nenhum PR entra
               na `develop` sem aprovação do revisor.
            2. **Contrato primeiro.** Qualquer mudança no modelo de dados ou no formato da API
               é registrada em `docs/modelo-de-dados.md` e avisada ao outro antes do PR.
            3. **Issues com a etiqueta `dupla` são feitas juntos**, em chamada ou presencialmente.
               São as decisões que afetam o projeto inteiro.
            4. **PRs pequenos.** Um PR por issue; se ficar grande, quebre em partes.
            5. **Revisão em até 24h.** Se não der, avise na própria issue.
            6. **Travou? Comente na issue e marque o outro** (`@usuario`). A conversa fica registrada.
            7. **Sincronização rápida 2x por semana** (15 min): o que fiz, o que vou fazer, onde travei.
            8. Branches e mensagens de commit seguem o padrão do README.

            ## Ao terminar uma issue

            - [ ] PR aberto apontando para `develop`, com `Closes #<número>` na descrição
            - [ ] Revisor marcado
            - [ ] README ou `docs/` atualizados, se algo mudou para quem usa o sistema
            - [ ] Issues que dependiam desta foram avisadas com um comentário

            ## Mapa das tarefas

            {MAPA}
        """,
    },

    # ------------------------------------------------------------------ Fase 0
    {
        "chave": "f0-build",
        "fase": "F0",
        "titulo": "Corrigir o build do frontend",
        "dono": "pedro",
        "etiquetas": ["frontend", "prioridade: alta"],
        "depende": [],
        "corpo": """
            ## Objetivo

            Hoje `npm run dev` funciona, mas `npm run build` falha com 2 erros de TypeScript.
            O build precisa passar para podermos ter CI e fazer deploy.

            ## O que fazer

            - [ ] Em `src/components/SearchForm.tsx`, trocar o import para
                  `import { useState, type FormEvent } from "react";`
            - [ ] Criar `src/vite-env.d.ts` com `/// <reference types="vite/client" />`
                  (resolve o erro de `import.meta.env`)
            - [ ] Mover `@vitejs/plugin-react`, `tailwindcss` e `@tailwindcss/vite` para `devDependencies`
            - [ ] Gerar e versionar o `package-lock.json` (o CI vai precisar dele)

            ## Critérios de aceite

            - [ ] `docker compose exec frontend npm run build` termina sem erros
            - [ ] A tela inicial continua funcionando em `npm run dev`
        """,
    },
    {
        "chave": "f0-docker",
        "fase": "F0",
        "titulo": "Versionar migrações e esperar o PostgreSQL no Docker",
        "dono": "marcos",
        "etiquetas": ["infra", "backend", "prioridade: alta"],
        "depende": [],
        "corpo": """
            ## Objetivo

            Hoje as migrações não estão no repositório e o backend pode subir antes do banco
            estar pronto, causando erro na primeira execução.

            ## O que fazer

            - [ ] Gerar `apps/leads/migrations/0001_initial.py` e versionar
            - [ ] Adicionar `healthcheck` com `pg_isready` no serviço `database` do `docker-compose.yml`
            - [ ] Trocar o `depends_on` do backend para `condition: service_healthy`
            - [ ] Rodar `migrate` automaticamente ao subir o backend
                  (ex.: `command: sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"`)
            - [ ] Atualizar a seção "Como rodar o projeto" do README

            ## Critérios de aceite

            - [ ] `docker compose down -v && docker compose up --build` sobe tudo na primeira tentativa
            - [ ] As tabelas são criadas sem precisar rodar comandos à mão
        """,
    },
    {
        "chave": "f0-repo",
        "fase": "F0",
        "titulo": "Organizar o repositório: branches, proteção e templates",
        "dono": "marcos",
        "etiquetas": ["infra", "documentação"],
        "depende": [],
        "corpo": """
            ## Objetivo

            Deixar o GitHub pronto para trabalharmos em paralelo sem atropelar o código um do outro.

            ## O que fazer

            - [ ] Garantir que o Pedro é colaborador do repositório
            - [ ] Criar a branch `develop` a partir da `main`
            - [ ] Proteger `main` e `develop`: exigir PR e 1 aprovação para fazer merge
            - [ ] Criar `.github/pull_request_template.md` com: o que mudou, como testar, issue relacionada (`Closes #`)
            - [ ] Criar templates de issue em `.github/ISSUE_TEMPLATE/` (tarefa e bug)
            - [ ] Criar um GitHub Project (quadro) e adicionar todas as issues
                  (colunas: A fazer, Fazendo, Em revisão, Feito)

            ## Critérios de aceite

            - [ ] Não é possível dar push direto na `main`
            - [ ] Ao abrir um PR, o template aparece preenchido
        """,
    },
    {
        "chave": "f0-ci",
        "fase": "F0",
        "titulo": "CI no GitHub Actions: testes do backend e build do frontend",
        "dono": "pedro",
        "etiquetas": ["infra"],
        "depende": ["f0-build", "f0-docker"],
        "corpo": """
            ## Objetivo

            Todo PR roda os testes automaticamente. Assim a revisão do outro foca na lógica,
            não em descobrir se o código quebra.

            ## O que fazer

            - [ ] Criar `.github/workflows/ci.yml` rodando em `pull_request` e `push` para `main`/`develop`
            - [ ] Job **backend**: serviço PostgreSQL, `pip install -r requirements.txt`, `python manage.py test`
            - [ ] Job **frontend**: `npm ci` e `npm run build`
            - [ ] Exigir o CI verde para fazer merge (proteção de branch)

            ## Critérios de aceite

            - [ ] Um PR com teste quebrado fica vermelho e não pode ser mergeado
        """,
    },
    {
        "chave": "f0-auth",
        "fase": "F0",
        "titulo": "Autenticação: login na API e tela de login",
        "dono": "pedro",
        "etiquetas": ["backend", "frontend", "prioridade: alta"],
        "depende": ["f0-build"],
        "corpo": """
            ## Objetivo

            O sistema vai guardar dados de pessoas (sócios, telefones). Antes disso, só usuários
            da PCI podem acessar.

            ## O que fazer

            **Backend**
            - [ ] Trocar `AllowAny` por `IsAuthenticated` como padrão no DRF
            - [ ] Autenticação por token (sugestão: `TokenAuthentication` do DRF, mais simples;
                  ou `djangorestframework-simplejwt`)
            - [ ] Endpoint de login (`/api/auth/login/`) e de usuário atual (`/api/auth/me/`)

            **Frontend**
            - [ ] Instalar `react-router-dom` e criar as rotas base
            - [ ] Tela de login
            - [ ] Interceptor do Axios enviando o token e redirecionando para o login em caso de 401
            - [ ] Botão de sair no `Header`

            ## Critérios de aceite

            - [ ] Sem login, a API responde 401 e o frontend mostra a tela de login
            - [ ] Com login, tudo funciona como antes
        """,
    },
    {
        "chave": "f0-redrive",
        "fase": "F0",
        "titulo": "Demonstração da Redrive e formato de importação",
        "dono": "marcos",
        "etiquetas": ["pesquisa", "prioridade: alta"],
        "depende": [],
        "corpo": """
            ## Objetivo

            Descobrir exatamente o que a Redrive faz e em que formato ela recebe os leads.
            A exportação do sistema (Fase 3) depende dessas respostas.

            ## Perguntas para a Redrive

            - [ ] Aceita importar CSV, XLSX ou Google Sheets? Com quais colunas obrigatórias?
            - [ ] Permite variáveis por contato na mensagem (ex.: `{nome_contato}`, `{mensagem}`)?
            - [ ] Tem API ou webhook para devolver status de envio e respostas?
            - [ ] Usa a API oficial do WhatsApp? Qual o limite seguro de envios por dia?
            - [ ] A captação própria dela (Google Maps, base de CNPJ) filtra por CNAE e bairro?
                  O que ela já faz que não precisamos construir?

            ## Entregável

            - [ ] `docs/redrive.md` com as respostas
            - [ ] Uma planilha de exemplo no formato aceito pela Redrive (sem dados reais)
            - [ ] Comentário nesta issue resumindo o que muda no plano, marcando o Pedro
        """,
    },
    {
        "chave": "f0-historico",
        "fase": "F0",
        "titulo": "Levantar o histórico de prospecções da PCI",
        "dono": "pedro",
        "etiquetas": ["pesquisa", "prioridade: alta"],
        "depende": [],
        "corpo": """
            ## Objetivo

            O score de prioridade (Fase 5) só funciona se soubermos quais leads fecharam negócio
            no passado. Esta tarefa reúne esse histórico.

            ## O que fazer

            - [ ] Descobrir onde está o histórico (planilhas, CRM, Notion, conversas com diretoria)
            - [ ] Consolidar numa planilha com, se possível: empresa, CNPJ, ramo, bairro,
                  como chegou até a PCI, data do contato, respondeu?, teve reunião?, fechou?, valor do projeto
            - [ ] Contar quantos registros existem e quantos têm resultado conhecido (fechou / não fechou)

            ## Entregável

            - [ ] `docs/historico.md` descrevendo as colunas, a quantidade de registros e onde a planilha está
            - [ ] **A planilha com dados reais não vai para o repositório** (fica no Drive da PCI)

            ## Dica

            Mesmo que existam poucos registros, já ajuda: os primeiros critérios do score podem
            ser definidos com a experiência de quem já prospectou na PCI.
        """,
    },

    # ------------------------------------------------------------------ Fase 1
    {
        "chave": "f1-modelo",
        "fase": "F1",
        "titulo": "Desenhar juntos o modelo de dados e o contrato da API",
        "dono": "dupla",
        "etiquetas": ["dupla", "backend", "documentação", "prioridade: alta"],
        "depende": ["f0-docker"],
        "corpo": """
            ## Objetivo

            É a tarefa que conecta todo o resto. Definimos juntos **como os dados são guardados**
            e **o formato do JSON da API**. Depois disso, cada um implementa sua parte sem esperar
            o outro, porque o contrato já está combinado.

            ## O que decidir

            - [ ] Entidades e campos: Empresa, Sócio, Telefone, Lead, LoteImportacao, Ramo / CnaeRamo
            - [ ] Um lead pode existir sem CNPJ? (ex.: veio de um CSV do Google Maps) → `cnpj` opcional e único
            - [ ] Status do funil: novo → exportado → contatado → respondeu → reunião → fechou / perdido
            - [ ] Como representar a origem do lead (Receita, CSV, Google Places, manual)
            - [ ] Formato das respostas da API: lista (resumida) e detalhe (completo)

            ## Entregável

            - [ ] `docs/modelo-de-dados.md` com diagrama (Mermaid `erDiagram`), campos e tipos
            - [ ] Exemplos de JSON da lista e do detalhe de um lead
            - [ ] Interfaces TypeScript correspondentes descritas no documento

            ## Referência

            Campos da base aberta do CNPJ:
            https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf
        """,
    },
    {
        "chave": "f1-empresa",
        "fase": "F1",
        "titulo": "Implementar os modelos Empresa, Sócio e Telefone",
        "dono": "marcos",
        "etiquetas": ["backend", "dados"],
        "depende": ["f1-modelo"],
        "corpo": """
            ## Objetivo

            Criar as tabelas que guardam os dados cadastrais das empresas, conforme
            `docs/modelo-de-dados.md`.

            ## O que fazer

            - [ ] Criar um app `empresas` (ou o nome combinado)
            - [ ] **Empresa:** CNPJ, razão social, nome fantasia, CNAE principal e secundários,
                  natureza jurídica, porte, capital social, data de abertura, situação cadastral,
                  opção Simples/MEI, endereço, bairro, CEP, UF, e-mail, latitude/longitude
            - [ ] **Sócio:** nome, qualificação, faixa etária, data de entrada
            - [ ] **Telefone:** DDD, número, número em formato E.164, é celular?, origem
            - [ ] Registro no Django Admin com busca e filtros
            - [ ] Migrações e testes dos modelos

            ## Critérios de aceite

            - [ ] É possível cadastrar uma empresa completa pelo Admin
            - [ ] `python manage.py test` passa
        """,
    },
    {
        "chave": "f1-lead",
        "fase": "F1",
        "titulo": "Implementar os modelos Lead, Lote de importação e Ramo",
        "dono": "pedro",
        "etiquetas": ["backend", "dados"],
        "depende": ["f1-modelo"],
        "corpo": """
            ## Objetivo

            Criar as tabelas do processo de prospecção, conforme `docs/modelo-de-dados.md`.

            ## O que fazer

            - [ ] Substituir o modelo `Lead` atual (ainda não há dados reais)
            - [ ] **Lead:** empresa, status do funil, score, origem, resumo, mensagem,
                  observações, não contatar (opt-out), datas de criação e atualização
            - [ ] **LoteImportacao:** origem, arquivo, data, quem importou, totais (criados, atualizados, ignorados)
            - [ ] **Ramo** e **CnaeRamo:** tabela que traduz CNAE para o ramo da PCI
            - [ ] Carga inicial dos ramos-alvo (migração de dados ou fixture). Exemplos:
                  `9602-5/01` Salão / Barbearia, `4761-0/03` Papelaria,
                  `9609-2/08` Pet shop (banho e tosa), `4789-0/04` Pet shop (comércio)
            - [ ] Registro no Admin e testes

            ## Critérios de aceite

            - [ ] Os ramos-alvo aparecem no Admin após `migrate`
            - [ ] `python manage.py test` passa
        """,
    },
    {
        "chave": "f1-api",
        "fase": "F1",
        "titulo": "API de leads com os dados da empresa",
        "dono": "marcos",
        "etiquetas": ["backend"],
        "depende": ["f1-empresa", "f1-lead"],
        "corpo": """
            ## Objetivo

            Expor os novos modelos na API exatamente no formato combinado em `docs/modelo-de-dados.md`.

            ## O que fazer

            - [ ] `GET /api/leads/` — lista resumida
            - [ ] `GET /api/leads/{id}/` — detalhe com empresa, sócios e telefones
            - [ ] `PATCH /api/leads/{id}/` — alterar status, observações e "não contatar"
            - [ ] `GET /api/ramos/` — lista de ramos
            - [ ] Testes dos endpoints (`APITestCase`)

            ## Critérios de aceite

            - [ ] O JSON retornado bate com os exemplos do documento
            - [ ] Testes cobrindo lista, detalhe e atualização
        """,
    },
    {
        "chave": "f1-front",
        "fase": "F1",
        "titulo": "Frontend: tipos, serviços da API e navegação",
        "dono": "pedro",
        "etiquetas": ["frontend"],
        "depende": ["f1-modelo", "f0-auth"],
        "corpo": """
            ## Objetivo

            Preparar o frontend para as próximas telas, usando o contrato da API.
            Pode começar **antes** da API ficar pronta, usando os exemplos de JSON do documento.

            ## O que fazer

            - [ ] Atualizar `src/types/` com as interfaces do documento (Lead, Empresa, Sócio, Telefone, Ramo)
            - [ ] Atualizar `src/services/api.ts` com as novas chamadas
            - [ ] Layout com menu: Leads, Importar, Exportar
            - [ ] Rotas para as páginas (mesmo que algumas ainda mostrem "em construção")

            ## Critérios de aceite

            - [ ] `npm run build` passa
            - [ ] Navegação entre as páginas funcionando
        """,
    },

    # ------------------------------------------------------------------ Fase 2
    {
        "chave": "f2-telefone",
        "fase": "F2",
        "titulo": "Serviço de normalização de telefones e remoção de duplicados",
        "dono": "pedro",
        "etiquetas": ["backend", "dados", "prioridade: alta"],
        "depende": ["f1-empresa", "f1-lead"],
        "corpo": """
            ## Objetivo

            Funções reutilizáveis que **todas** as fontes de dados usam: a importação da Receita
            (Marcos) e a importação de CSV (Pedro). Por isso precisa sair cedo e bem testada.

            ## O que fazer

            - [ ] Instalar a biblioteca `phonenumbers`
            - [ ] `normalizar_telefone(texto)` → DDD, número, formato E.164, é celular?
            - [ ] Regra de celular: DDD 61 + 9 dígitos começando com 9
            - [ ] Tratar números antigos de celular com 8 dígitos (sem o 9 na frente)
            - [ ] `encontrar_duplicado(...)`: procura por CNPJ; sem CNPJ, por telefone;
                  sem os dois, por nome normalizado + CEP
            - [ ] Testes com vários formatos reais: `(61) 99999-9999`, `61999999999`,
                  `+55 61 9 9999-9999`, `3333-3333`, vazio, texto inválido

            ## Critérios de aceite

            - [ ] Testes cobrindo todos os formatos acima
            - [ ] Funções documentadas, para o Marcos usar na importação da Receita
        """,
    },
    {
        "chave": "f2-receita",
        "fase": "F2",
        "titulo": "Importar empresas do DF a partir da base aberta do CNPJ",
        "dono": "marcos",
        "etiquetas": ["backend", "dados", "prioridade: alta"],
        "depende": ["f1-empresa", "f1-lead", "f2-telefone"],
        "corpo": """
            ## Objetivo

            Ter no banco as empresas **ativas** do **DF** dos **ramos-alvo**, com sócios e telefones.
            É a principal fonte de leads do sistema.

            ## O que fazer

            - [ ] Comando `python manage.py importar_receita`
            - [ ] Baixar os arquivos de Estabelecimentos, Empresas, Sócios e Simples do portal de dados abertos
            - [ ] Ler em partes (os arquivos têm vários GB): CSV com `;`, sem cabeçalho, codificação `latin-1`
            - [ ] Filtrar: UF = DF, situação cadastral ativa, CNAE principal presente na tabela `CnaeRamo`
            - [ ] Juntar empresas, sócios e Simples/MEI pelo CNPJ básico (8 primeiros dígitos)
            - [ ] Usar `normalizar_telefone` e `encontrar_duplicado` para criar ou atualizar (sem duplicar)
            - [ ] Registrar um `LoteImportacao` com os totais

            ## Critérios de aceite

            - [ ] Rodar duas vezes seguidas não duplica nada
            - [ ] Teste automatizado com um arquivo de amostra pequeno (poucas linhas, em `tests/`)

            ## Dicas

            - Os arquivos baixados ficam numa pasta `data/` que deve estar no `.gitignore`
            - Desenvolva com uma amostra pequena antes de rodar a base inteira
            - Layout dos arquivos: https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf
        """,
    },
    {
        "chave": "f2-filtros",
        "fase": "F2",
        "titulo": "Filtros, ordenação e paginação na API de leads",
        "dono": "pedro",
        "etiquetas": ["backend"],
        "depende": ["f1-api"],
        "corpo": """
            ## Objetivo

            Permitir encontrar rapidamente os leads certos entre milhares de registros.

            ## O que fazer

            - [ ] Instalar `django-filter`
            - [ ] Filtros: ramo, bairro, porte, MEI, só celular, DDD 61, status, não contatar,
                  busca por nome ou CNPJ
            - [ ] Ordenação: score, distância, nome, data de abertura, data de criação
            - [ ] Paginação de 25 itens por página
            - [ ] Atualizar os exemplos de JSON em `docs/modelo-de-dados.md` (agora a lista é paginada)
            - [ ] Testes dos filtros

            ## Critérios de aceite

            - [ ] `GET /api/leads/?ramo=1&so_celular=true&ordering=-score&page=2` funciona
        """,
    },
    {
        "chave": "f2-lista",
        "fase": "F2",
        "titulo": "Tela de lista de leads com filtros e paginação",
        "dono": "marcos",
        "etiquetas": ["frontend"],
        "depende": ["f1-front", "f2-filtros"],
        "corpo": """
            ## Objetivo

            A tela principal do sistema: ver, filtrar e ordenar os leads.

            ## O que fazer

            - [ ] Tabela com: empresa, ramo, bairro, telefone, porte, status, score
            - [ ] Painel de filtros (os mesmos da API)
            - [ ] Filtros guardados na URL, para poder compartilhar uma busca com o outro
            - [ ] Paginação e ordenação clicando no cabeçalho
            - [ ] Estados de carregando, vazio e erro
            - [ ] Clicar numa linha abre o detalhe do lead

            ## Critérios de aceite

            - [ ] Recarregar a página mantém os filtros
            - [ ] Funciona bem com milhares de leads
        """,
    },
    {
        "chave": "f2-detalhe",
        "fase": "F2",
        "titulo": "Tela de detalhe do lead",
        "dono": "pedro",
        "etiquetas": ["frontend"],
        "depende": ["f1-front", "f1-api"],
        "corpo": """
            ## Objetivo

            Tudo sobre uma empresa numa tela só, para quem vai fazer o contato.

            ## O que fazer

            - [ ] Dados da empresa: nomes, CNPJ, ramo, CNAE, porte, MEI/Simples, abertura, endereço
            - [ ] Sócios: nome, qualificação, faixa etária
            - [ ] Telefones, com botão de copiar e link para WhatsApp (`https://wa.me/55...`)
            - [ ] Alterar status, observações e "não contatar"
            - [ ] Espaço reservado para resumo, mensagem e score (Fases 4 e 5)

            ## Critérios de aceite

            - [ ] Alterar o status na tela reflete na lista
        """,
    },

    # ------------------------------------------------------------------ Fase 3
    {
        "chave": "f3-import",
        "fase": "F3",
        "titulo": "Importação de CSV (Instant Data Scraper e outras fontes)",
        "dono": "pedro",
        "etiquetas": ["backend", "frontend", "dados"],
        "depende": ["f2-telefone", "f1-front"],
        "corpo": """
            ## Objetivo

            Trazer leads de qualquer planilha (por exemplo, exportada pelo Instant Data Scraper)
            para dentro do sistema, sem duplicar o que já existe.

            ## O que fazer

            **Backend**
            - [ ] Endpoint de upload que lê o CSV/XLSX e devolve as colunas e uma prévia
            - [ ] Endpoint de confirmação que recebe o mapeamento (coluna do arquivo → campo do sistema)
            - [ ] Usar `normalizar_telefone` e `encontrar_duplicado`
            - [ ] Criar um `LoteImportacao` com o relatório: criados, atualizados, ignorados e o motivo

            **Frontend**
            - [ ] Tela de upload
            - [ ] Mapeamento de colunas com selects e prévia das 10 primeiras linhas
            - [ ] Relatório final da importação

            ## Critérios de aceite

            - [ ] Importar um CSV real do Instant Data Scraper funciona de ponta a ponta
            - [ ] Importar o mesmo arquivo duas vezes não duplica leads
        """,
    },
    {
        "chave": "f3-export",
        "fase": "F3",
        "titulo": "Exportação de leads no formato da Redrive",
        "dono": "marcos",
        "etiquetas": ["backend", "frontend", "dados"],
        "depende": ["f0-redrive", "f2-filtros", "f2-lista"],
        "corpo": """
            ## Objetivo

            Gerar a planilha que vai para a Redrive, com os leads filtrados na tela.

            ## O que fazer

            **Backend**
            - [ ] Endpoint de exportação que aceita os mesmos filtros da lista
            - [ ] CSV e XLSX (`openpyxl`) com as colunas definidas em `docs/redrive.md`
            - [ ] Exportar só telefones celulares com DDD 61
            - [ ] Nunca exportar leads marcados como "não contatar"
            - [ ] Marcar os leads exportados (status "exportado" e data)

            **Frontend**
            - [ ] Botão "Exportar para Redrive" na lista, mostrando quantos leads serão exportados

            ## Critérios de aceite

            - [ ] O arquivo gerado é aceito pela Redrive sem ajustes manuais
        """,
    },
    {
        "chave": "f3-funil",
        "fase": "F3",
        "titulo": "Funil de prospecção, histórico de status e opt-out",
        "dono": "pedro",
        "etiquetas": ["backend", "frontend"],
        "depende": ["f1-api", "f2-detalhe"],
        "corpo": """
            ## Objetivo

            Registrar o que acontece com cada lead depois do disparo. Esses registros viram,
            com o tempo, o **histórico que alimenta o score** (Fase 5).

            ## O que fazer

            - [ ] Modelo `HistoricoStatus`: lead, status anterior, novo status, data, quem alterou
            - [ ] Gravar automaticamente a cada mudança de status
            - [ ] Mostrar a linha do tempo no detalhe do lead
            - [ ] "Não contatar": motivo e data; lead some das exportações
            - [ ] Alterar o status de vários leads de uma vez na lista (ex.: marcar como "contatado")

            ## Critérios de aceite

            - [ ] Toda mudança de status fica registrada com data e usuário
        """,
    },
    {
        "chave": "f3-sheets",
        "fase": "F3",
        "titulo": "Enviar a exportação direto para o Google Sheets",
        "dono": "marcos",
        "etiquetas": ["backend", "opcional"],
        "depende": ["f3-export"],
        "corpo": """
            ## Objetivo

            Se o time trabalhar no Google Sheets, evitar baixar e subir arquivos.

            ## O que fazer

            - [ ] Conta de serviço do Google e biblioteca `gspread`
            - [ ] Credenciais no `.env` (nunca no repositório)
            - [ ] Opção "Enviar para o Google Sheets" ao lado do botão de exportar

            ## Critérios de aceite

            - [ ] A planilha é criada ou atualizada com as mesmas colunas do CSV
        """,
    },

    # ------------------------------------------------------------------ Fase 4
    {
        "chave": "f4-distancia",
        "fase": "F4",
        "titulo": "Distância até a Asa Norte",
        "dono": "marcos",
        "etiquetas": ["backend", "dados"],
        "depende": ["f2-receita"],
        "corpo": """
            ## Objetivo

            Priorizar empresas mais próximas da Asa Norte.

            ## O que fazer

            - [ ] Definir o ponto de referência (ex.: sede da PCI) e guardar nas configurações
            - [ ] Geocodificar o endereço (Nominatim/OpenStreetMap, gratuito, máx. 1 requisição por segundo;
                  ou Google Geocoding) e guardar latitude/longitude, para não repetir a consulta
            - [ ] Calcular a distância em km (fórmula de Haversine)
            - [ ] Plano B quando o endereço não for encontrado: estimar pelo bairro / região administrativa
            - [ ] Comando para geocodificar em lote
            - [ ] Filtro e ordenação por distância na API

            ## Critérios de aceite

            - [ ] Ordenar a lista por distância mostra primeiro as empresas da Asa Norte
        """,
    },
    {
        "chave": "f4-resumo",
        "fase": "F4",
        "titulo": "Resumo da empresa gerado por IA",
        "dono": "pedro",
        "etiquetas": ["backend", "frontend", "dados"],
        "depende": ["f2-receita", "f2-detalhe"],
        "corpo": """
            ## Objetivo

            Um parágrafo curto explicando o que a empresa faz, para quem vai prospectar.

            ## O que fazer

            - [ ] Escolher o provedor de IA e guardar a chave no `.env`
            - [ ] Serviço `gerar_resumo(lead)` usando nome, ramo, descrição do CNAE, bairro, porte,
                  tempo de empresa e site/Instagram, se houver
            - [ ] O resumo deve dizer só o que os dados mostram, sem inventar informações
            - [ ] Botão "Gerar resumo" no detalhe e geração em lote para os leads filtrados
            - [ ] Controle de custo: não gerar de novo se já existir (a não ser que peçam)

            ## Critérios de aceite

            - [ ] Resumo aparece no detalhe e pode ser editado à mão
        """,
    },
    {
        "chave": "f4-mensagem",
        "fase": "F4",
        "titulo": "Mensagem de prospecção personalizada por lead",
        "dono": "marcos",
        "etiquetas": ["backend", "frontend", "dados"],
        "depende": ["f4-resumo", "f3-export"],
        "corpo": """
            ## Objetivo

            Cada lead sai com uma mensagem pronta, personalizada, que vai numa coluna da exportação.

            ## O que fazer

            - [ ] Modelos de mensagem por ramo, com variáveis: `{nome_contato}`, `{empresa}`, `{ramo}`, `{bairro}`
            - [ ] Tela para criar e editar os modelos
            - [ ] Personalização opcional por IA a partir do resumo (serviço do Pedro)
            - [ ] Prévia da mensagem no detalhe do lead
            - [ ] Coluna "mensagem" na exportação para a Redrive
            - [ ] Nome do contato: primeiro nome do sócio administrador, quando houver

            ## Critérios de aceite

            - [ ] A exportação sai com a mensagem de cada lead preenchida
        """,
    },
    {
        "chave": "f4-places",
        "fase": "F4",
        "titulo": "Completar dados com a API do Google Places",
        "dono": "pedro",
        "etiquetas": ["backend", "dados", "opcional"],
        "depende": ["f2-receita"],
        "corpo": """
            ## Objetivo

            A Receita às vezes tem telefone antigo ou do contador. O Google costuma ter dados mais atuais.

            ## O que fazer

            - [ ] Buscar a empresa por nome + endereço (Text Search)
            - [ ] Pedir só os campos necessários (*field mask*) para não pagar a mais
            - [ ] Guardar telefone, site, avaliação e coordenadas, indicando a origem "Google"
            - [ ] Respeitar a cota gratuita mensal; contador de uso

            ## Critérios de aceite

            - [ ] Leads enriquecidos mostram os dados do Google, identificados como tal
        """,
    },
    {
        "chave": "f4-celery",
        "fase": "F4",
        "titulo": "Processar importações e enriquecimento em segundo plano",
        "dono": "marcos",
        "etiquetas": ["backend", "infra", "opcional"],
        "depende": ["f2-receita"],
        "corpo": """
            ## Objetivo

            Importações e chamadas de IA/geocodificação podem demorar minutos. Elas não devem
            travar a tela.

            ## O que fazer

            - [ ] Avaliar se é necessário (se tudo roda bem por comandos, pode ficar para depois)
            - [ ] Redis + Celery no `docker-compose.yml`
            - [ ] Transformar importação, geocodificação e geração de resumo em tarefas
            - [ ] Mostrar o andamento na tela

            ## Critérios de aceite

            - [ ] Uma importação grande roda sem travar o navegador
        """,
    },

    # ------------------------------------------------------------------ Fase 5
    {
        "chave": "f5-criterios",
        "fase": "F5",
        "titulo": "Analisar juntos o histórico e definir os critérios do score",
        "dono": "dupla",
        "etiquetas": ["dupla", "dados", "pesquisa"],
        "depende": ["f0-historico", "f3-funil"],
        "corpo": """
            ## Objetivo

            Descobrir quais características fazem uma empresa ter mais chance de fechar com a PCI.

            ## O que fazer

            - [ ] Taxa de conversão por ramo, porte, MEI, tempo de empresa e região
            - [ ] Conversar com quem já prospectou na PCI para validar os números
            - [ ] Definir os pesos do score (começar simples: regras com pontos)
            - [ ] Definir quando revisar os pesos (ex.: a cada 100 novos resultados no funil)

            ## Entregável

            - [ ] `docs/score.md` com a análise, os critérios e os pesos

            ## Observação

            Com poucos dados, um score por regras é mais confiável do que um modelo estatístico.
            Um modelo só vale a pena com algumas centenas de resultados registrados.
        """,
    },
    {
        "chave": "f5-score",
        "fase": "F5",
        "titulo": "Implementar o score de prioridade",
        "dono": "pedro",
        "etiquetas": ["backend", "frontend"],
        "depende": ["f5-criterios", "f2-filtros"],
        "corpo": """
            ## Objetivo

            Cada lead recebe uma nota de 0 a 100 e os motivos dela.

            ## O que fazer

            - [ ] Serviço `calcular_score(lead)` seguindo `docs/score.md`, retornando nota e motivos
            - [ ] Recalcular ao importar e com o comando `python manage.py recalcular_score`
            - [ ] Mostrar a nota na lista e os motivos no detalhe
            - [ ] Ordenação padrão da lista: maior score primeiro
            - [ ] Testes com leads de exemplo

            ## Critérios de aceite

            - [ ] Dá para explicar a nota de qualquer lead olhando os motivos
        """,
    },
    {
        "chave": "f5-dashboard",
        "fase": "F5",
        "titulo": "Painel de métricas da prospecção",
        "dono": "marcos",
        "etiquetas": ["backend", "frontend"],
        "depende": ["f3-funil"],
        "corpo": """
            ## Objetivo

            Mostrar para a PCI como a prospecção está indo.

            ## O que fazer

            - [ ] Endpoint de métricas: leads por ramo e status, exportados por semana, conversão por etapa do funil
            - [ ] Tela com os números principais e gráficos simples
            - [ ] Conversão por ramo (ajuda a revisar os pesos do score)

            ## Critérios de aceite

            - [ ] Os números batem com os dados da lista
        """,
    },
]

MARCADOR = "<!-- pci-leads:{chave} -->"
PENDENTE = "<!-- pci-leads:pendente -->"


# ---------------------------------------------------------------------------
# Execução de comandos
# ---------------------------------------------------------------------------

class Gh:
    def __init__(self, dry_run: bool):
        self.dry_run = dry_run
        self.exe = shutil.which("gh")
        if not self.exe and not dry_run:
            sys.exit(
                "ERRO: o GitHub CLI (gh) não foi encontrado.\n"
                "Instale em https://cli.github.com e rode `gh auth login`."
            )

    def run(self, args: list[str], entrada: str | None = None, leitura: bool = False,
            pode_falhar: bool = False) -> subprocess.CompletedProcess | None:
        """leitura=True executa mesmo no dry-run (comandos que não alteram nada)."""
        if self.dry_run and not leitura:
            print("  [dry-run] gh " + " ".join(_curto(a) for a in args))
            return None
        if not self.exe:
            return None
        resultado = subprocess.run(
            [self.exe, *args], input=entrada, capture_output=True,
            text=True, encoding="utf-8",
        )
        if resultado.returncode != 0 and not pode_falhar:
            print(f"\nERRO ao executar: gh {' '.join(_curto(a) for a in args)}")
            print(resultado.stderr.strip())
            sys.exit(1)
        return resultado


def _curto(texto: str) -> str:
    texto = texto.replace("\n", " ")
    if " " in texto:
        texto = f'"{texto}"'
    return texto if len(texto) <= 70 else texto[:67] + '..."'


# ---------------------------------------------------------------------------
# Montagem do corpo das issues
# ---------------------------------------------------------------------------

def nome_dono(dono: str) -> str:
    return "Marcos André e Pedro Esmeraldo (dupla)" if dono == "dupla" else PESSOAS[dono]


def nome_revisor(dono: str) -> str:
    if dono == "dupla":
        return "um revisa o PR do outro"
    return PESSOAS["pedro" if dono == "marcos" else "marcos"]


def referencia(chave: str, numeros: dict[str, int], por_chave: dict[str, dict]) -> str:
    numero = numeros.get(chave)
    titulo = por_chave[chave]["titulo"]
    return f"#{numero}" if numero else f"{titulo} (ainda não criada)"


def montar_corpo(issue: dict, numeros: dict[str, int], por_chave: dict[str, dict],
                 libera: dict[str, list[str]], final: bool) -> str:
    corpo = textwrap.dedent(issue["corpo"]).strip()

    if "{MAPA}" in corpo:
        corpo = corpo.replace("{MAPA}", montar_mapa(numeros, por_chave))

    depende = issue["depende"]
    liberadas = libera.get(issue["chave"], [])
    conexoes = [
        "## Conexões",
        "",
        f"- **Dono:** {nome_dono(issue['dono'])}",
        f"- **Revisor:** {nome_revisor(issue['dono'])}",
    ]
    if depende:
        conexoes.append("- **Depende de:** " + ", ".join(
            referencia(c, numeros, por_chave) for c in depende))
    if liberadas:
        conexoes.append("- **Libera:** " + ", ".join(
            referencia(c, numeros, por_chave) for c in liberadas))

    partes = [corpo]
    if issue["chave"] != "guia":
        partes.append("\n".join(conexoes))
    partes.append(MARCADOR.format(chave=issue["chave"]))
    if not final:
        partes.append(PENDENTE)
    return "\n\n".join(partes) + "\n"


def montar_mapa(numeros: dict[str, int], por_chave: dict[str, dict]) -> str:
    linhas = []
    for codigo, (titulo_fase, _) in FASES.items():
        itens = [i for i in ISSUES if i["fase"] == codigo and i["chave"] != "guia"]
        if not itens:
            continue
        linhas += [f"### {titulo_fase}", "", "| Issue | Dono |", "|---|---|"]
        for i in itens:
            ref = referencia(i["chave"], numeros, por_chave)
            dono = "Dupla" if i["dono"] == "dupla" else PESSOAS[i["dono"]].split()[0]
            linhas.append(f"| {ref} {i['titulo'] if ref.startswith('#') else ''} | {dono} |")
        linhas.append("")
    return "\n".join(linhas).strip()


# ---------------------------------------------------------------------------
# Passos
# ---------------------------------------------------------------------------

def validar() -> None:
    chaves = [i["chave"] for i in ISSUES]
    assert len(chaves) == len(set(chaves)), "chaves duplicadas"
    for i in ISSUES:
        assert i["fase"] in FASES, i["chave"]
        assert i["dono"] in ("marcos", "pedro", "dupla"), i["chave"]
        for d in i["depende"]:
            assert d in chaves, f"{i['chave']} depende de {d}, que não existe"
        for e in i["etiquetas"]:
            assert e in {n for n, _, _ in ETIQUETAS}, f"etiqueta desconhecida: {e}"


def criar_etiquetas(gh: Gh) -> None:
    print("\n1/4 Etiquetas")
    for nome, cor, descricao in ETIQUETAS:
        gh.run(["label", "create", nome, "--color", cor, "--description", descricao, "--force"])
        print(f"  ok  {nome}")


def criar_fases(gh: Gh) -> None:
    print("\n2/4 Fases (milestones)")
    existentes: set[str] = set()
    r = gh.run(["api", "repos/{owner}/{repo}/milestones?state=all&per_page=100"],
               leitura=True, pode_falhar=gh.dry_run)
    if r is not None and r.returncode == 0:
        existentes = {m["title"] for m in json.loads(r.stdout or "[]")}
    for titulo, descricao in FASES.values():
        if titulo in existentes:
            print(f"  já existe  {titulo}")
            continue
        gh.run(["api", "repos/{owner}/{repo}/milestones", "--method", "POST",
                "-f", f"title={titulo}", "-f", f"description={descricao}"])
        print(f"  ok  {titulo}")


def issues_existentes(gh: Gh) -> dict[str, dict]:
    r = gh.run(["issue", "list", "--state", "all", "--limit", "500",
                "--json", "number,body"], leitura=True, pode_falhar=gh.dry_run)
    if r is None or r.returncode != 0:
        return {}
    encontradas = {}
    for item in json.loads(r.stdout or "[]"):
        m = re.search(r"<!-- pci-leads:([\w-]+) -->", item.get("body") or "")
        if m and m.group(1) != "pendente":
            encontradas[m.group(1)] = {
                "numero": item["number"],
                "pendente": PENDENTE in (item.get("body") or ""),
            }
    return encontradas


def criar_issues(gh: Gh, usuarios: dict[str, str]) -> dict[str, int]:
    print("\n3/4 Issues")
    por_chave = {i["chave"]: i for i in ISSUES}
    libera: dict[str, list[str]] = {}
    for i in ISSUES:
        for d in i["depende"]:
            libera.setdefault(d, []).append(i["chave"])

    existentes = issues_existentes(gh)
    numeros = {c: v["numero"] for c, v in existentes.items()}
    para_atualizar = [c for c, v in existentes.items() if v["pendente"]]
    numero_falso = 1000

    for issue in ISSUES:
        chave = issue["chave"]
        if chave in numeros:
            print(f"  já existe  #{numeros[chave]} {issue['titulo']}")
            continue

        donos = ["marcos", "pedro"] if issue["dono"] == "dupla" else [issue["dono"]]
        etiquetas = list(issue["etiquetas"]) + [f"dono: {d}" for d in donos]
        args = ["issue", "create", "--title", issue["titulo"],
                "--milestone", FASES[issue["fase"]][0], "--body-file", "-"]
        for e in etiquetas:
            args += ["--label", e]
        logins = [usuarios[d] for d in donos if usuarios.get(d)]
        args_com_responsavel = args + sum((["--assignee", u] for u in logins), [])

        corpo = montar_corpo(issue, numeros, por_chave, libera, final=False)
        r = gh.run(args_com_responsavel, entrada=corpo, pode_falhar=True)
        if r is not None and r.returncode != 0 and logins:
            print(f"  aviso: não consegui atribuir a {', '.join(logins)} "
                  "(a pessoa é colaboradora do repositório?). Criando sem responsável.")
            r = gh.run(args, entrada=corpo)
        elif r is not None and r.returncode != 0:
            print(r.stderr.strip())
            sys.exit(1)

        if r is None:  # dry-run
            numero_falso += 1
            numeros[chave] = numero_falso
        else:
            numeros[chave] = int(r.stdout.strip().rstrip("/").split("/")[-1])
        para_atualizar.append(chave)
        print(f"  ok  #{numeros[chave]} {issue['titulo']}")

    print("\n4/4 Ligando as issues entre si (Depende de / Libera)")
    for chave in para_atualizar:
        if chave not in por_chave:
            continue
        corpo = montar_corpo(por_chave[chave], numeros, por_chave, libera, final=True)
        gh.run(["issue", "edit", str(numeros[chave]), "--body-file", "-"], entrada=corpo)
        print(f"  ok  #{numeros[chave]}")

    if "guia" in numeros:
        gh.run(["issue", "pin", str(numeros["guia"])], pode_falhar=True)
    return numeros


def resumo(numeros: dict[str, int]) -> None:
    print("\nDivisão final:")
    for dono in ("marcos", "pedro", "dupla"):
        itens = [i for i in ISSUES if i["dono"] == dono]
        nome = "Dupla" if dono == "dupla" else PESSOAS[dono]
        print(f"\n  {nome} ({len(itens)} issues)")
        for i in itens:
            print(f"    #{numeros.get(i['chave'], '?'):<5} [{i['fase']}] {i['titulo']}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows
    except Exception:
        pass

    p = argparse.ArgumentParser(description="Cria as issues do PCI-LEADS no GitHub.")
    p.add_argument("--marcos", help="usuário do GitHub do Marcos André")
    p.add_argument("--pedro", help="usuário do GitHub do Pedro Esmeraldo")
    p.add_argument("--repo", help="dono/repositorio (se não estiver dentro da pasta do repo)")
    p.add_argument("--dry-run", action="store_true", help="só mostra o que seria feito")
    a = p.parse_args()

    if a.repo:
        os.environ["GH_REPO"] = a.repo

    validar()
    gh = Gh(a.dry_run)
    if not a.dry_run:
        r = gh.run(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                   leitura=True)
        print(f"Repositório: {r.stdout.strip()}")
        if not (a.marcos and a.pedro):
            print("Aviso: sem --marcos/--pedro as issues ficam sem responsável "
                  "(as etiquetas 'dono: ...' continuam indicando quem faz).")

    criar_etiquetas(gh)
    criar_fases(gh)
    numeros = criar_issues(gh, {"marcos": a.marcos, "pedro": a.pedro})
    resumo(numeros)
    print("\nPronto!" if not a.dry_run else "\nDry-run concluído: nada foi alterado no GitHub.")


if __name__ == "__main__":
    main()