# PCI-LEADS

Sistema de prospecção de leads.

## Stack

- Backend: Python + Django + Django REST Framework
- Frontend: React + TypeScript + Vite + Tailwind CSS
- Banco: PostgreSQL
- Ambiente: Docker + Docker Compose

## Subir o projeto

Na raiz do projeto:

```bash
docker compose up --build
```

Frontend:

http://localhost:5173

Backend:

http://localhost:8000

Admin:

http://localhost:8000/admin/

## Migrações

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

## Criar usuário administrador

```bash
docker compose exec backend python manage.py createsuperuser
```

## Parar

```bash
docker compose down
```

## Próximas etapas

1. Implementar providers de busca.
2. Normalizar dados.
3. Remover leads duplicados.
4. Criar score de qualificação.
5. Adicionar autenticação.
6. Adicionar filtros e paginação.
7. Adicionar exportação CSV.
8. Avaliar Redis + Celery para buscas assíncronas.
