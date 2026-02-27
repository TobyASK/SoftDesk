# Exemples d'Utilisation - SoftDesk API

Guide pratique avec des exemples curl pour tous les cas d'usage de l'API SoftDesk.

---

## 📋 Table des matières

1. [Authentification](#authentification)
2. [Gestion des Projets](#gestion-des-projets)
3. [Gestion des Issues](#gestion-des-issues)
4. [Gestion des Commentaires](#gestion-des-commentaires)
5. [Gestion des Contributeurs](#gestion-des-contributeurs)
6. [Erreurs Courantes](#erreurs-courantes)

---

## 🔐 Authentification

### 1. S'inscrire (Registration)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePassword123",
    "age": 25,
    "can_be_contacted": true,
    "can_data_be_shared": false
  }'
```

**Réponse (200 Created)** :
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "age": 25,
  "can_be_contacted": true,
  "can_data_be_shared": false
}
```

**⚠️ Erreur si âge < 15** :
```json
{
  "age": ["L'utilisateur doit avoir au moins 15 ans."]
}
```

---

### 2. Obtenir un JWT Token (Login)

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePassword123"
  }'
```

**Réponse (200 OK)** :
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

**📌 À partir de maintenant, utilise le token `access` dans les requêtes** :
```bash
-H "Authorization: Bearer <access_token>"
```

---

### 3. Rafraîchir le Token (Refresh)

Quand ton token `access` expire :

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Réponse (200 OK)** :
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 📁 Gestion des Projets

### 1. Créer un Projet

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MonApp Mobile",
    "description": "Application mobile iOS/Android",
    "type": "mobile"
  }'
```

**Réponse (201 Created)** :
```json
{
  "id": 1,
  "name": "MonApp Mobile",
  "description": "Application mobile iOS/Android",
  "type": "mobile",
  "author": {
    "id": 1,
    "username": "alice"
  },
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-02-27T15:30:00Z"
}
```

**📌 Après création, tu es automatiquement contributeur du projet !**

---

### 2. Lister tes Projets

```bash
curl http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Réponse (200 OK)** :
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "MonApp Mobile",
      "type": "mobile",
      "author": { "id": 1, "username": "alice" }
    },
    {
      "id": 2,
      "name": "Backend API",
      "type": "backend",
      "author": { "id": 2, "username": "bob" }
    }
  ]
}
```

**📌 Tu ne vois que les projets où tu es contributeur !**

---

### 3. Voir les Détails d'un Projet

```bash
curl http://localhost:8000/api/v1/projects/1/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Réponse (200 OK)** :
```json
{
  "id": 1,
  "name": "MonApp Mobile",
  "description": "Application mobile iOS/Android",
  "type": "mobile",
  "author": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
  },
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-02-27T15:30:00Z"
}
```

---

### 4. Modifier un Projet (Seul l'auteur peut)

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/ \
  -H "Authorization: Bearer <TOKEN_ALICE>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Application mobile iOS/Android avec backend"
  }'
```

**Réponse (200 OK)** :
```json
{
  "id": 1,
  "name": "MonApp Mobile",
  "description": "Application mobile iOS/Android avec backend",
  "type": "mobile",
  "author": { "id": 1, "username": "alice" }
}
```

**❌ Si tu n'es pas l'auteur** :
```json
{
  "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

---

### 5. Supprimer un Projet (Seul l'auteur peut)

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (204 No Content)** : Rien (projet supprimé)

---

## 👥 Gestion des Contributeurs

### 1. Ajouter un Contributeur au Projet

**⚠️ Seul l'auteur du projet peut ajouter des contributeurs**

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/contributors/ \
  -H "Authorization: Bearer <TOKEN_ALICE>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'
```

**Réponse (201 Created)** :
```json
{
  "id": 1,
  "user": {
    "id": 2,
    "username": "bob",
    "email": "bob@example.com"
  },
  "project": 1,
  "role": "contributor"
}
```

Bob peut maintenant voir et contribuer au projet ! 🎯

---

### 2. Lister les Contributeurs d'un Projet

```bash
curl http://localhost:8000/api/v1/projects/1/contributors/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (200 OK)** :
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": { "id": 1, "username": "alice" },
      "role": "contributor"
    },
    {
      "id": 2,
      "user": { "id": 2, "username": "bob" },
      "role": "contributor"
    }
  ]
}
```

---

### 3. Supprimer un Contributeur

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1/contributors/2/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (204 No Content)** : Bob n'a plus accès au projet

---

## 🐛 Gestion des Issues

### 1. Créer une Issue dans un Projet

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/issues/ \
  -H "Authorization: Bearer <TOKEN_ALICE>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug: Crash au login",
    "description": "L'\''app crash quand on entre un mot de passe incorrect",
    "priority": "HIGH",
    "tag": "BUG",
    "status": "To Do",
    "assignee_id": 2
  }'
```

**Réponse (201 Created)** :
```json
{
  "id": 1,
  "title": "Bug: Crash au login",
  "description": "L'app crash quand on entre un mot de passe incorrect",
  "priority": "HIGH",
  "tag": "BUG",
  "status": "To Do",
  "assignee": {
    "id": 2,
    "username": "bob"
  },
  "author": {
    "id": 1,
    "username": "alice"
  },
  "created_at": "2026-02-27T16:00:00Z"
}
```

**Priority valides** : `LOW`, `MEDIUM`, `HIGH`
**Tags valides** : `BUG`, `FEATURE`, `TASK`
**Status valides** : `To Do`, `In Progress`, `Finished`

---

### 2. ⚠️ Erreur : Assigné non contributeur

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/issues/ \
  -H "Authorization: Bearer <TOKEN_ALICE>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Feature: Nouveau dashboard",
    "description": "Ajouter un dashboard pour les stats",
    "priority": "MEDIUM",
    "tag": "FEATURE",
    "assignee_id": 99
  }'
```

**❌ Réponse (400 Bad Request)** :
```json
{
  "assignee": ["L'assigné doit être un contributeur du projet."]
}
```

---

### 3. Lister les Issues d'un Projet

```bash
curl http://localhost:8000/api/v1/projects/1/issues/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (200 OK)** :
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/v1/projects/1/issues/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Bug: Crash au login",
      "priority": "HIGH",
      "status": "To Do",
      "assignee": { "id": 2, "username": "bob" },
      "author": { "id": 1, "username": "alice" }
    },
    {
      "id": 2,
      "title": "Feature: Nouveau dashboard",
      "priority": "MEDIUM",
      "status": "To Do",
      "assignee": null,
      "author": { "id": 1, "username": "alice" }
    }
  ]
}
```

---

### 4. Voir les Détails d'une Issue

```bash
curl http://localhost:8000/api/v1/projects/1/issues/1/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (200 OK)** :
```json
{
  "id": 1,
  "title": "Bug: Crash au login",
  "description": "L'app crash quand on entre un mot de passe incorrect",
  "priority": "HIGH",
  "tag": "BUG",
  "status": "To Do",
  "assignee": { "id": 2, "username": "bob" },
  "author": { "id": 1, "username": "alice" },
  "created_at": "2026-02-27T16:00:00Z",
  "updated_at": "2026-02-27T16:00:00Z"
}
```

---

### 5. Modifier une Issue (Seul l'auteur peut)

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/issues/1/ \
  -H "Authorization: Bearer <TOKEN_ALICE>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Progress",
    "priority": "CRITICAL"
  }'
```

**Réponse (200 OK)** :
```json
{
  "id": 1,
  "title": "Bug: Crash au login",
  "status": "In Progress",
  "priority": "CRITICAL",
  "assignee": { "id": 2, "username": "bob" }
}
```

---

### 6. Supprimer une Issue (Seul l'auteur peut)

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1/issues/1/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (204 No Content)** : Issue supprimée

---

## 💬 Gestion des Commentaires

### 1. Ajouter un Commentaire à une Issue

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/issues/1/comments/ \
  -H "Authorization: Bearer <TOKEN_BOB>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "J'\''ai reproché le bug. C'\''est causé par une validation manquante du password."
  }'
```

**Réponse (201 Created)** :
```json
{
  "id": 1,
  "description": "J'ai reproché le bug. C'est causé par une validation manquante du password.",
  "author": {
    "id": 2,
    "username": "bob"
  },
  "issue": 1,
  "created_at": "2026-02-27T16:30:00Z"
}
```

---

### 2. Lister les Commentaires d'une Issue

```bash
curl http://localhost:8000/api/v1/projects/1/issues/1/comments/ \
  -H "Authorization: Bearer <TOKEN_ALICE>"
```

**Réponse (200 OK)** :
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "description": "J'ai reproché le bug. C'est causé par une validation manquante du password.",
      "author": { "id": 2, "username": "bob" },
      "created_at": "2026-02-27T16:30:00Z"
    },
    {
      "id": 2,
      "description": "Bonne catch ! Je vais le corriger aujourd'hui.",
      "author": { "id": 1, "username": "alice" },
      "created_at": "2026-02-27T17:00:00Z"
    }
  ]
}
```

---

### 3. Modifier un Commentaire (Seul l'auteur peut)

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/issues/1/comments/1/ \
  -H "Authorization: Bearer <TOKEN_BOB>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "J'\''ai reproché le bug. C'\''est causé par une validation manquante du password. Correction en cours."
  }'
```

**Réponse (200 OK)** :
```json
{
  "id": 1,
  "description": "J'ai reproché le bug. C'est causé par une validation manquante du password. Correction en cours.",
  "author": { "id": 2, "username": "bob" }
}
```

---

### 4. Supprimer un Commentaire (Seul l'auteur peut)

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1/issues/1/comments/1/ \
  -H "Authorization: Bearer <TOKEN_BOB>"
```

**Réponse (204 No Content)** : Commentaire supprimé

---

## ⚠️ Erreurs Courantes

### 1. Token Invalide ou Expiré

```bash
curl http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer invalid_token"
```

**Réponse (401 Unauthorized)** :
```json
{
  "detail": "Token invalide ou expiré."
}
```

**Solution** : Utilise un nouveau token avec `/auth/token/refresh/`

---

### 2. Pas d'Authentification

```bash
curl http://localhost:8000/api/v1/projects/
```

**Réponse (401 Unauthorized)** :
```json
{
  "detail": "Les identifiants d'authentification n'ont pas été fournis."
}
```

**Solution** : Ajoute le header `Authorization: Bearer <token>`

---

### 3. Permission Refusée (Non-auteur)

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1/ \
  -H "Authorization: Bearer <TOKEN_BOB>"
```

**Réponse (403 Forbidden)** :
```json
{
  "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

**Solution** : Seul l'auteur du projet peut le supprimer

---

### 4. Ressource Non Trouvée

```bash
curl http://localhost:8000/api/v1/projects/999/ \
  -H "Authorization: Bearer <TOKEN>"
```

**Réponse (404 Not Found)** :
```json
{
  "detail": "Non trouvé."
}
```

---

### 5. Validation Échouée

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "invalid-email",
    "password": "short",
    "age": 10
  }'
```

**Réponse (400 Bad Request)** :
```json
{
  "email": ["Entrez une adresse de messagerie valide."],
  "password": ["Le mot de passe est trop court."],
  "age": ["L'utilisateur doit avoir au moins 15 ans."]
}
```

---

## 📊 Pagination

L'API retourne les résultats par pages de **10 items** :

```bash
curl "http://localhost:8000/api/v1/projects/?page=2" \
  -H "Authorization: Bearer <TOKEN>"
```

**Réponse** :
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/projects/?page=3",
  "previous": "http://localhost:8000/api/v1/projects/?page=1",
  "results": [...]
}
```

---

## 🔑 Résumé des Règles de Sécurité

| Action | Qui peut ? |
|--------|-----------|
| Voir un projet | Seuls les contributeurs |
| Créer une issue | Contributeurs du projet |
| Modifier une issue | Seul l'auteur |
| Supprimer une issue | Seul l'auteur |
| Ajouter un contributeur | Seul l'auteur du projet |
| Modifier un commentaire | Seul l'auteur du commentaire |

---

**Besoin d'aide ?** Consulte le [README.md](./README.md) principal ! 📖
