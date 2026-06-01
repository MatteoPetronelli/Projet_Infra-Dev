# Projet Ymmo - Infrastructure et Développement B2

![Statut](https://img.shields.io/badge/Statut-Terminé-success)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Niveau](https://img.shields.io/badge/Niveau-Bachelor_2-orange)
![Docker](https://img.shields.io/badge/Docker-Containerisé-2496ED?logo=docker\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi\&logoColor=white)
![Svelte](https://img.shields.io/badge/SvelteKit-Frontend-FF3E00?logo=svelte\&logoColor=white)

---

## Présentation du Projet

**Ymmo** est une plateforme moderne et sécurisée de gestion et d'estimation immobilière développée dans le cadre du module **Infrastructure & Développement – Bachelor 2 (Ynov Campus)**.

L'objectif principal du projet est de démontrer la capacité à concevoir une application full-stack complète, sécurisée et conteneurisée intégrant des problématiques réelles liées :

* au développement web moderne,
* à la sécurisation des accès,
* à l'analyse de données,
* à l'automatisation des déploiements,
* et à l'intégration d'un modèle d'Intelligence Artificielle.

L'application combine plusieurs fonctionnalités métier :

* Un catalogue interactif de biens immobiliers.
* Un simulateur d'estimation basé sur un modèle IA entraîné avec les données DVF.
* Une gestion des accès avancée avec système RBAC.
* Une infrastructure entièrement conteneurisée via Docker.
* Une API REST documentée automatiquement via Swagger/OpenAPI.

---

## Objectifs Pédagogiques

Ce projet permet de valider plusieurs compétences du référentiel Bachelor 2 :

* Conception d'une architecture full-stack moderne.
* Développement d'une API sécurisée.
* Mise en place d'une infrastructure reproductible.
* Gestion des rôles et sécurisation des accès.
* Exploitation de pipelines de données et Machine Learning.
* Industrialisation du développement via Docker.

---

# Stack Technique

## Frontend (Interface Utilisateur)

* **SvelteKit / Svelte 5** : Framework moderne réactif et performant.
* **Tailwind CSS** : Framework CSS utilitaire pour une interface responsive.
* **TypeScript** : Typage statique et robustesse du code.
* **Fetch API** : Communication avec le backend FastAPI.

## Backend (API & Logique Métier)

* **FastAPI (Python)** : API REST asynchrone haute performance.
* **Pydantic** : Validation stricte des données entrantes.
* **JWT** : Authentification sécurisée basée sur des tokens.
* **Argon2** : Hachage cryptographique sécurisé des mots de passe.
* **Uvicorn** : Serveur ASGI pour l'exécution de FastAPI.

## Base de Données & Data Science

* **DuckDB** : Base de données analytique légère et performante.
* **Pandas** : Manipulation et nettoyage des datasets.
* **Parquet** : Format optimisé pour les traitements massifs.
* **XGBoost** : Modèle de Machine Learning pour la prédiction immobilière.
* **DVF Open Data** : Base gouvernementale des ventes foncières.

## Infrastructure & DevOps

* **Docker** : Conteneurisation des services.
* **Docker Compose** : Orchestration multi-services.
* **Volumes Docker** : Persistance des données.
* **Variables d'environnement** : Gestion de la configuration.

---

# Arborescence Détaillée du Projet

```text
projet_infra-dev/
├── docker-compose.yml
├── dev/
│   ├── backend/
│   │   ├── main.py
│   │   ├── test_main.py
│   │   ├── exceptions.py
│   │   ├── dependencies.py
│   │   ├── schemas.py
│   │   ├── core/
│   │   │   └── logger.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   └── predict_service.py
│   │   └── Dockerfile
│   │
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   │   ├── +layout.svelte
│   │   │   │   ├── +page.svelte
│   │   │   │   ├── layout.css
│   │   │   │   ├── admin/
│   │   │   │   │   └── +page.svelte
│   │   │   │   ├── catalogue/
│   │   │   │   │   └── +page.svelte
│   │   │   │   ├── estimer/
│   │   │   │   │   └── +page.svelte
│   │   │   │   └── login/
│   │   │   │       └── +page.svelte
│   │   │   └── app.html
│   │   ├── static/
│   │   │   └── carte_prix_immobiliers.html
│   │   └── Dockerfile
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── init_log_db.py
│   │   ├── seed_db.py
│   │   ├── seed_users.py
│   │   ├── seed_biens.py
│   │   └── ymmo_analytics.duckdb
│   │
│   └── data_analysis/
│       ├── import_dvf.py
│       ├── clean_dvf.py
│       ├── generate_plots.py
│       ├── convert_to_parquet.py
│       ├── train_model.py
│       ├── data/
│           ├── raw/
│           │   └── valeursfoncieres-2025.csv
│           └── processed/
│               ├── dvf_clean.parquet
│               └── modele_ymmo.pkl

```

---

# Installation et Lancement

## Prérequis

Avant de démarrer le projet, assurez-vous d'avoir installé :

* Docker Engine
* Docker Compose
* Git

---

## Clonage du dépôt

```bash
git clone https://github.com/MatteoPetronelli/Projet_Infra-Dev.git
cd Projet_Infra-Dev
```

---

## ▶Démarrage de l'infrastructure

Depuis la racine du projet :

```bash
docker compose up --build
```

Cette commande :

* construit les images Docker,
* initialise les dépendances,
* démarre le frontend et le backend,
* configure automatiquement les services.

---

## Arrêt des conteneurs

```bash
docker compose down
```

Pour supprimer également les volumes :

```bash
docker compose down -v
```

---

# Accès aux Services

| Service                    | URL                                |
| -------------------------- | ---------------------------------- |
| Frontend SvelteKit         | http://localhost:5173              |
| Backend FastAPI            | http://localhost:8000              |
| Swagger UI                 | http://localhost:8000/docs         |
| Documentation OpenAPI JSON | http://localhost:8000/openapi.json |

> Swagger UI permet de tester les endpoints directement depuis le navigateur.

---

# Gestion des Accès et Sécurité (RBAC)

Le projet applique une stratégie de sécurité basée sur le principe du **moindre privilège** et de la **défense en profondeur**.

Les contrôles sont réalisés :

* côté frontend (interface dynamique),
* côté backend (validation serveur obligatoire),
* et via des vérifications en base de données.

## Mécanismes de sécurité implémentés

* Authentification JWT.
* Hachage des mots de passe via Argon2.
* Validation stricte des permissions.
* Vérification des rôles à chaque requête sensible.
* Protection contre l'escalade de privilèges.
* Gestion des erreurs HTTP sécurisée.
* Séparation des responsabilités utilisateur.

---

## Comptes de démonstration

### Direction (Administrateur Supérieur)

* **Email** : `directeur@ymmo.fr`
* **Mot de passe** : `admin123`

Permissions :

* Gestion complète des utilisateurs.
* Ajout / suppression des biens.
* Accès aux fonctionnalités d'administration avancées.

---

### IT & Support (Administrateur Délégué)

* **Email** : `it@ymmo.fr`
* **Mot de passe** : `itpass1%`

Permissions :

* Gestion du catalogue.
* Gestion des utilisateurs standards.
* Impossible de modifier les droits de la Direction.

---

### Utilisateur Standard

* **Email** : `user@gmail.com`
* **Mot de passe** : `FirstUser01`

Permissions :

* Consultation du catalogue.
* Utilisation du simulateur IA.
* Aucun accès aux routes d'administration.

---

# Pipeline IA et Data

Le modèle d'estimation immobilière repose sur un pipeline complet de traitement des données :

1. Import des données DVF.
2. Nettoyage et normalisation.
3. Conversion en format Parquet.
4. Entraînement du modèle XGBoost.
5. Intégration du modèle dans l'API FastAPI.

Le pipeline permet d'obtenir des estimations cohérentes basées sur des données réelles de transactions immobilières françaises.

---

# Bonnes Pratiques Techniques

Le projet applique plusieurs bonnes pratiques professionnelles :

* Architecture modulaire.
* Séparation des responsabilités.
* Code typé et maintenable.
* Validation des données.
* Conteneurisation complète.
* Gestion des erreurs API.
* Documentation automatique.
* Sécurité renforcée.
