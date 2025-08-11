# 🔧 Solução: Container sem Imagem e Porta

## Problema Identificado
Você está vendo um container `webprice-analyz` sem imagem e sem porta no Docker Desktop. Isso indica que há containers órfãos ou mal configurados.

## ✅ Solução Rápida

### Passo 1: Pare todos os containers
```bash
docker-compose down
```

### Passo 2: Remove o container problemático
```bash
docker rm -f webprice-analyz
```

### Passo 3: Limpe imagens órfãs
```bash
docker image prune -f
```

### Passo 4: Reconstrua tudo
```bash
docker-compose up --build -d
```

## 🚀 Solução Automática

Execute o script que criamos:
```bash
chmod +x restart-docker.sh
./restart-docker.sh
```

## 📋 Verificação

Após executar os comandos, você deve ver:

```bash
docker-compose ps
```

**Resultado esperado:**
```
NAME                   IMAGE                    COMMAND                  SERVICE    CREATED         STATUS         PORTS
webprice-adminer       adminer:4-standalone     "entrypoint.sh php -…"   adminer    2 minutes ago   Up 2 minutes   0.0.0.0:8080->8080/tcp
webprice-backend       webprice-analyzer-backend   "gunicorn --bind 0.0…"   backend    2 minutes ago   Up 2 minutes   0.0.0.0:5000->5000/tcp
webprice-database      postgres:15-alpine       "docker-entrypoint.s…"   database   2 minutes ago   Up 2 minutes   0.0.0.0:5432->5432/tcp
webprice-frontend      webprice-analyzer-frontend  "/docker-entrypoint.…"   frontend   2 minutes ago   Up 2 minutes   0.0.0.0:80->80/tcp
webprice-redis         redis:7-alpine           "docker-entrypoint.s…"   redis      2 minutes ago   Up 2 minutes   0.0.0.0:6379->6379/tcp
```

## 🌐 Acessos

Após a correção, você terá acesso a:

- **Aplicação Principal**: http://localhost
- **API Backend**: http://localhost:5000
- **Administrador do Banco**: http://localhost:8080
  - Servidor: `database`
  - Usuário: `webprice_user`
  - Senha: `webprice_password`
  - Banco: `webprice_db`

## 🔍 Diagnóstico

Se ainda houver problemas:

```bash
# Ver logs detalhados
docker-compose logs -f

# Ver apenas logs do backend
docker-compose logs backend

# Ver apenas logs do frontend  
docker-compose logs frontend
```

## 💡 Prevenção

Para evitar esse problema no futuro:
1. Sempre use `docker-compose down` antes de fazer mudanças
2. Use `docker-compose up --build -d` para reconstruir
3. Evite usar `docker run` diretamente para este projeto
