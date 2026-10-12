# NexusAI ⚡ — 🚧 En desarrollo

![Estado](https://img.shields.io/badge/estado-en_desarrollo-FF79C6?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-BD93F9?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-BD93F9?style=flat-square&logo=fastapi&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-BD93F9?style=flat-square)](LICENSE)

> **Proyecto en construcción.** El objetivo es un backend de generación de contenido con IA (FastAPI + PostgreSQL + Redis + OpenAI).
> Hoy el repositorio contiene **solo una parte del código** y **todavía no se puede ejecutar**: faltan los módulos de `app/` (configuración, sesión de BD, servicios, schemas, middleware) y el `Dockerfile`.

## Qué hay hoy en el repo

| Archivo | Contenido | Estado |
|---------|-----------|--------|
| `main.py` | App FastAPI: `lifespan`, CORS, GZip, middleware de rate limit, manejo de errores | importa módulos que aún no existen |
| `generation.py` | Endpoints `/generate` (crear, listar, obtener, borrar, streaming) | depende de servicios pendientes |
| `models.py` | Modelos SQLAlchemy 2.0: usuarios, generaciones, hilos de conversación, API keys y jobs | ✔ definidos |
| `test_api.py` | Tests de integración con `httpx` + SQLite en memoria | no ejecutables hasta completar `app/` |
| `docker-compose.yml` | API, worker y beat de Celery, Flower, PostgreSQL y Redis | falta `docker/Dockerfile` |

## Roadmap

Planificado, **todavía no implementado** en este repo:

- [ ] Estructura `app/` completa (`core/config`, `db/session`, `schemas`, `services`, `middleware`) para que `main.py` arranque
- [ ] Autenticación JWT (access + refresh) con contraseñas BCrypt
- [ ] RBAC (roles Admin / User) en endpoints protegidos
- [ ] Generación de texto, código, análisis y resúmenes vía OpenAI
- [ ] Streaming de respuestas (SSE y WebSocket)
- [ ] Hilos de conversación con memoria persistente
- [ ] Cuotas de tokens por plan y rate limiting por ventana deslizante
- [ ] API keys para acceso programático
- [ ] Jobs en segundo plano con Celery (resets mensuales, digests)
- [ ] `docker/Dockerfile` y stack de Compose funcionando de punta a punta
- [ ] Tests de integración pasando en CI

## Configuración (cuando el stack esté completo)

Las credenciales van en `.env` (ver `.env.example`). `docker-compose.yml` **no trae contraseñas por defecto**: si falta `POSTGRES_PASSWORD`, Compose se detiene con un error claro. PostgreSQL y Redis se exponen solo en `127.0.0.1`.

## Qué estoy aprendiendo

- Arquitectura asíncrona con FastAPI y SQLAlchemy 2.0.
- Diseño de una API con cuotas, rate limiting y roles.
- A no publicar como "listo para producción" algo que todavía no corre.

## Licencia

[MIT](LICENSE) © 2026 Fernanda (Fernandamv96)
