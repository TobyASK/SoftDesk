# SoftDesk - API de Suivi de Projets

Une API simple et professionnelle pour gérer des projets, des problèmes et des commentaires avec **Django REST Framework**, authentification JWT, respect RGPD, et tests complets.

## Fonctionnalités

✅ **Gestion des utilisateurs** - Modèle CustomUser avec validation d'âge (>= 15 ans)  
✅ **Authentification JWT** - Token d'accès et refresh tokens  
✅ **Gestion de projets** - Créer des projets et ajouter des contributeurs  
✅ **Suivi des problèmes** - Créer, modifier, assigner les problèmes  
✅ **Commentaires** - Ajouter des commentaires aux problèmes  
✅ **Permissions granulaires** - Seuls les contributeurs et auteurs ont accès  
✅ **Pagination** - Listes paginées (10 éléments par page)  
✅ **Optimisations ORM** - `select_related` et `prefetch_related`  
✅ **Tests complets** - 36+ tests couvrant tous les cas  
✅ **Conformité RGPD** - Validation d'âge et champs de consentement  

## Pré-requis

- **Python** : 3.9 ou supérieur
- **Poetry** : Gestionnaire de dépendances
- **Git** : Contrôle de version

## Installation

### 1. Cloner le dépôt

```bash
git clone <repository-url>
cd softdesk
```

### 2. Créer le fichier d'environnement

```bash
cp .env.example .env
```

Éditez `.env` et configurez votre `SECRET_KEY` :

```
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Installer les dépendances avec Poetry

```bash
poetry install
```

### 4. Appliquer les migrations

```bash
poetry run python manage.py migrate
```

### 5. (Optionnel) Créer un superutilisateur

```bash
poetry run python manage.py createsuperuser
```

### 6. Lancer le serveur de développement

```bash
poetry run python manage.py runserver
```

Le serveur sera disponible à `http://localhost:8000`  
Panneau admin : `http://localhost:8000/admin/`

## Points d'accès API

**URL de base** : `http://localhost:8000/api/v1/`

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/auth/register/` | Créer un compte utilisateur |
| `POST` | `/auth/token/` | Obtenir access et refresh tokens |
| `POST` | `/auth/token/refresh/` | Rafraîchir le token d'accès |
| `GET` | `/auth/users/profile/me/` | Profil utilisateur actuel |
| `PUT` | `/auth/users/{id}/` | Modifier le profil utilisateur |

### Projets

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/projects/` | Lister les projets |
| `POST` | `/projects/` | Créer un projet |
| `GET` | `/projects/{id}/` | Détails du projet |
| `PUT` | `/projects/{id}/` | Modifier le projet (auteur uniquement) |
| `DELETE` | `/projects/{id}/` | Supprimer le projet (auteur uniquement) |
| `POST` | `/projects/{id}/contributor/` | Ajouter un contributeur |

### Problèmes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/projects/{project_id}/issues/` | Lister les problèmes |
| `POST` | `/projects/{project_id}/issues/` | Créer un problème |
| `PUT` | `/projects/{project_id}/issues/{id}/` | Modifier (auteur uniquement) |
| `DELETE` | `/projects/{project_id}/issues/{id}/` | Supprimer (auteur uniquement) |

### Commentaires

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/projects/{project_id}/issues/{issue_id}/comments/` | Lister les commentaires |
| `POST` | `/projects/{project_id}/issues/{issue_id}/comments/` | Ajouter un commentaire |
| `PUT` | `/projects/{project_id}/issues/{issue_id}/comments/{uuid}/` | Modifier (auteur uniquement) |
| `DELETE` | `/projects/{project_id}/issues/{issue_id}/comments/{uuid}/` | Supprimer (auteur uniquement) |

## Exemples d'utilisation

Tous les endpoints (sauf `/auth/register/` et `/auth/token/`) requièrent l'authentification JWT :

```bash
Authorization: Bearer <access_token>
```

### 1. Créer un compte utilisateur

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Dupont",
    "age": 25,
    "password": "securepass123",
    "password_confirm": "securepass123",
    "can_be_contacted": true,
    "can_data_be_shared": false
  }'
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "first_name": "Alice",
  "age": 25,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Erreur** : Âge < 15 ans
```json
{
  "age": ["L'utilisateur doit avoir au moins 15 ans pour s'inscrire."]
}
```

### 2. Obtenir les tokens JWT

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "securepass123"
  }'
```

**Réponse** : `200 OK`
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Créer un projet

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mon Application",
    "description": "Une application web responsive",
    "type": "front-end"
  }'
```

**Réponse** : `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Mon Application",
  "description": "Une application web responsive",
  "type": "front-end",
  "author": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
  },
  "contributors_count": 1,
  "created_time": "2024-01-15T10:35:00Z"
}
```

### 4. Ajouter un contributeur au projet

```bash
curl -X POST http://localhost:8000/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/contributor/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'
```

**Réponse** : `201 Created`

### 5. Créer un problème

```bash
curl -X POST http://localhost:8000/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/issues/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Corriger le design responsive",
    "description": "Le layout se casse sur mobile",
    "priority": "HIGH",
    "tag": "BUG",
    "status": "To Do",
    "assignee_id": 2
  }'
```

**Réponse** : `201 Created`

**Erreur** : L'assigné doit être contributeur
```json
{
  "assignee": ["L'assigné doit être un contributeur du projet."]
}
```

### 6. Ajouter un commentaire

```bash
curl -X POST http://localhost:8000/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/issues/550e8400-e29b-41d4-a716-446655440003/comments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Je peux corriger ça en ajustant les media queries CSS"
  }'
```

**Réponse** : `201 Created`

### 7. Rafraîchir le token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

**Réponse** : `200 OK` avec nouveau `access` token

## Pagination

Les listes sont paginées (10 éléments par défaut) :

```bash
curl "http://localhost:8000/api/v1/projects/?page=1&page_size=5" \
  -H "Authorization: Bearer <access_token>"
```

**Réponse** :
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/projects/?page=2",
  "previous": null,
  "results": [...]
}
```

## Tests

### Exécuter tous les tests

```bash
poetry run pytest
```

### Exécuter un fichier spécifique

```bash
poetry run pytest tests/test_accounts.py -v
```

### Avec rapport de couverture

```bash
poetry run pytest --cov=. --cov-report=html
```

### Tests clés couverts

✅ Enregistrement avec validation d'âge (< 15 = rejeté)  
✅ Obtention et rafraîchissement des tokens JWT  
✅ Authentification requise sur tous les endpoints  
✅ Accès aux projets uniquement si contributeur  
✅ Modification/suppression réservée à l'auteur  
✅ L'assigné du problème doit être contributeur  
✅ Pagination fonctionnelle  
✅ Conformité RGPD (âge, consentement)  

## Permissions et sécurité

### Règles de permissions

- **Projets** : Seuls les contributeurs peuvent les voir
- **Modification** : Seul l'auteur peut modifier/supprimer
- **Commentaires** : Seul l'auteur peut les modifier
- **Assignation** : L'assigné doit être contributeur du projet

### Conformité RGPD

- Validation d'âge >= 15 ans obligatoire
- Champs de consentement (`can_be_contacted`, `can_data_be_shared`)
- Suppression d'utilisateur en cascade

## Architecture

```
softdesk/
├── accounts/              # Gestion des utilisateurs
│   ├── models.py         # CustomUser avec validation d'âge
│   ├── serializers.py    # Sérialisation des utilisateurs
│   ├── views.py          # Endpoints d'authentification
│   ├── permissions.py    # Permissions personnalisées
│   └── urls.py
├── tracker/               # Suivi des projets
│   ├── models.py         # Project, Contributor, Issue, Comment
│   ├── serializers.py    # Sérialisation des ressources
│   ├── views.py          # ViewSets CRUD
│   ├── permissions.py    # Contrôle d'accès
│   ├── pagination.py     # Pagination (10 items/page)
│   └── urls.py
├── tests/                # Suite de tests (36+ tests)
│   ├── conftest.py
│   ├── test_accounts.py
│   └── test_tracker.py
├── pyproject.toml        # Dépendances Poetry
├── .env.example          # Modèle de configuration
└── README.md
```

## Modèles de données

### CustomUser
- Prénom, nom, email, nom d'utilisateur
- Âge (validation >= 15)
- Champs de consentement RGPD

### Project
- Nom, description, type
- Auteur (créateur)
- Contributeurs (relation M2M)

### Issue
- Titre, description
- Priorité (LOW, MEDIUM, HIGH)
- Statut (To Do, In Progress, Finished)
- Auteur et assigné
- Commentaires associés

### Comment
- Texte du commentaire
- Auteur
- Associé à un problème

## Dépendances principales

- **Django 4.2** - Framework web
- **Django REST Framework 3.14** - API REST
- **djangorestframework-simplejwt 5.3** - Authentification JWT
- **pytest 7.4** - Framework de test
- **python-decouple 3.8** - Configuration d'environnement

## Optimisations ORM

- `select_related` : Charge les relations ForeignKey en une seule requête
- `prefetch_related` : Optimise les requêtes pour les relations M2M
- Réduit les requêtes N+1

## Variables d'environnement

```
DEBUG=True                           # Mode debug
SECRET_KEY=your-secret-key          # Clé secrète Django
ALLOWED_HOSTS=localhost,127.0.0.1   # Hôtes autorisés
SECURE_SSL_REDIRECT=False           # Forcer HTTPS (True en production)
```

## Dépannage

**"L'utilisateur n'est pas contributeur"**  
→ Ajouter l'utilisateur comme contributeur au projet d'abord

**Erreurs de migration**  
```bash
poetry run python manage.py migrate
```

**Permission refusée sur modification/suppression**  
→ Seul l'auteur peut modifier. Utiliser le bon token utilisateur

**Token expiré**  
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## Postman

Une collection Postman est fournie : `SoftDesk_API.postman_collection.json`

Importez-la dans Postman pour tester tous les endpoints avec des exemples pré-configurés.

