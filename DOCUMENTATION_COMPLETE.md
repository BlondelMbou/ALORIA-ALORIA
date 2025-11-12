# 📚 DOCUMENTATION COMPLÈTE - ALORIA AGENCY

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Technique](#architecture-technique)
3. [Fonctionnalités par Rôle](#fonctionnalités-par-rôle)
4. [Workflows Métier](#workflows-métier)
5. [Guide Utilisateur](#guide-utilisateur)
6. [Guide Développeur](#guide-développeur)
7. [API Documentation](#api-documentation)
8. [Guide de Déploiement](#guide-de-déploiement)
9. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Vue d'Ensemble

### Présentation

**ALORIA AGENCY** est une plateforme digitale complète de gestion d'agence d'immigration pour le Canada et la France. L'application permet de gérer l'ensemble du cycle de vie d'un prospect jusqu'à la finalisation de son dossier d'immigration.

### Objectifs

- ✅ Digitaliser la gestion des dossiers d'immigration
- ✅ Automatiser les workflows de prospects et clients
- ✅ Assurer la transparence et la traçabilité
- ✅ Optimiser la gestion financière et des paiements
- ✅ Faciliter la collaboration entre équipes

### Caractéristiques Clés

- 🌍 **Multi-pays:** Canada et France
- 👥 **Multi-rôles:** SuperAdmin, Manager, Employee, Consultant, Client
- 💰 **Gestion financière:** Paiements, consultations (50,000 CFA), retraits
- 📊 **Dashboards personnalisés** par rôle
- 🔐 **Sécurité:** JWT Authentication, Role-Based Access Control
- 🎨 **UI/UX:** Thème "Bleu Nuit" cohérent, interface en français
- 📧 **Notifications:** Email automatiques (SendGrid)
- 📄 **Documents:** Génération de factures PDF

---

## Architecture Technique

### Stack Technologique

#### Frontend
- **Framework:** React.js 18
- **UI Library:** Tailwind CSS + Shadcn UI
- **State Management:** React Context (AuthContext)
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Real-time:** Socket.IO Client
- **Animations:** CSS animations avec IntersectionObserver

#### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Database:** MongoDB
- **Authentication:** JWT (JSON Web Tokens)
- **Real-time:** Python-SocketIO
- **Email Service:** SendGrid
- **PDF Generation:** ReportLab
- **Data Validation:** Pydantic

#### Infrastructure
- **Hosting:** Kubernetes
- **Reverse Proxy:** Ingress (routes /api → backend:8001)
- **Environment:** Docker containers
- **Process Manager:** Supervisor

### Architecture Applicative

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │SuperAdmin│  │ Manager  │  │ Employee │  │  Client  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│              ┌─────────────────────────┐                    │
│              │   Consultant Dashboard  │                    │
│              └─────────────────────────┘                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │   API    │  │ WebSocket│  │  Email   │   │
│  │ (JWT)    │  │ Endpoints│  │  Server  │  │ Service  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (MongoDB)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  users   │  │ clients  │  │  cases   │  │prospects │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ payments │  │activities│  │ visitors │  │withdrawals│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Hiérarchie des Rôles

```
SUPERADMIN (Niveau 4)
    ↓
MANAGER (Niveau 3)
    ↓
CONSULTANT (Niveau 2.5)
    ↓
EMPLOYEE (Niveau 2)
    ↓
CLIENT (Niveau 1)
```

**Règles de Création:**
- SUPERADMIN peut créer: MANAGER, CONSULTANT, EMPLOYEE
- MANAGER peut créer: EMPLOYEE, CLIENT
- EMPLOYEE peut créer: CLIENT
- CONSULTANT ne peut créer personne

---

## Fonctionnalités par Rôle

### 👑 SUPERADMIN

**Dashboard: 6 Onglets**

#### 1. Vue d'Ensemble
- **Stats Globales:**
  - Utilisateurs totaux (Managers, Employees, Clients)
  - Dossiers totaux et actifs
  - Paiements confirmés
  - Connexions 24h
- **Stats Consultations:**
  - Nombre de paiements consultation (50,000 CFA)
  - Revenus totaux consultations
- **Notifications:** Paiements consultation reçus

#### 2. Utilisateurs
- **Liste complète:** 132+ utilisateurs
- **Recherche:** Par nom, email, rôle
- **Tri:** Date création, nom, rôle, email
- **Actions:**
  - 👁️ Voir détails utilisateur
  - 🎭 Impersonner (se connecter en tant que)
- **Informations:** Avatar, nom, rôle (badge), email, statut, dernière connexion

#### 3. Activités
- **Historique complet:** 100+ activités
- **Filtres:**
  - Recherche par action (payment, login, client, etc.)
  - ID Utilisateur spécifique
  - Limite d'affichage (50 par défaut)
- **Export:** Bouton "Exporter CSV"
- **Types d'activités:**
  - Connexions (login)
  - Créations (client_created, create_user, case_created)
  - Paiements (consultation_payment_confirmed, payment_confirmed)
  - Prospects (prospect_assigned, prospect_consultant_assignment)
  - Retraits (withdrawal_created)
  - Cas (case_updated, case_status_changed)

#### 4. Prospects
- **Vue globale:** TOUS les prospects (28+)
- **Stats par statut:**
  - 🆕 Nouveau: 12
  - 📝 Assigné: 1
  - 💰 Payé 50k: 1
  - ✅ Convertis: 7
- **Actions:**
  - **Assigner** prospect à Manager/Employee
    - Dropdown avec 38 employés disponibles
    - Sélection employé/manager
    - Confirmation assignation
  - **Ajouter notes consultant**
  - Voir détails complets

#### 5. Créer Utilisateur
- **Rôles disponibles:**
  - Manager
  - Consultant ⭐
  - Employé
- **Champs:**
  - Nom complet
  - Email
- **Génération automatique:**
  - Mot de passe temporaire (ex: `Xk9$mP2vL@7n`)
  - Email de bienvenue
- **Modal confirmation:**
  - Affichage email + mot de passe
  - 👁️ Révéler/Masquer mot de passe
  - 📋 Copier mot de passe

#### 6. Solde & Finances
- **Component:** BalanceMonitor
- **Fonctionnalités:**
  - Suivi retraits Manager
  - Approbation/Rejet retraits
  - Historique financier

---

### 👔 MANAGER

**Dashboard: 7 Onglets**

#### 1. Clients (107+ clients)
- **Liste complète** avec recherche/tri
- **Actions:**
  - 👁️ Voir détails client
  - 🔄 **Réassigner** client à autre employé
    - Dropdown employés disponibles
    - Confirmation réassignation
- **Informations:**
  - Nom client
  - Pays/Visa
  - Employé assigné
  - Statut dossier

#### 2. Équipe
- **Liste employés** sous sa responsabilité
- **Statistiques:**
  - Nombre de clients par employé
  - Dossiers actifs par employé
- **Actions:**
  - Voir détails employé
  - Performance tracking

#### 3. Dossiers
- **Tous les dossiers** de ses équipes
- **Filtres:**
  - Par statut (Actif, Terminé, En attente)
  - Par pays (Canada, France)
  - Par employé assigné
- **Progression:** Visualisation étapes workflow

#### 4. Visiteurs
- **Liste TOUS les visiteurs** (pas filtré par employé)
- **Enregistrement nouveau visiteur:**
  - Nom visiteur
  - Organisation
  - Email
  - Téléphone
  - Objet visite
  - Numéro CNI
- **Actions:**
  - Marquer départ (checkout)
- **Stats:** Visiteurs présents vs partis

#### 5. Prospects ⭐
- **Component:** MyProspects
- **Stats:**
  - 📞 À Contacter
  - 💼 Chez Consultant
  - ✅ Convertis
- **Liste:** Prospects assignés au manager
- **Auto-refresh:** Toutes les 30 secondes

**Actions par Statut:**

**Status: `assigne_employe` (Assigné)**
- 🔶 **Bouton 1: "Affecter au Consultant"**
  - Modal paiement 50,000 CFA
  - Champs:
    - Méthode: Cash, Mobile Money, Virement
    - Référence transaction (optionnelle)
  - Enregistrement paiement automatique
  - Génération facture (CONS-YYYYMMDD-UUID)
  - Notification SuperAdmin
  - Changement statut → `paiement_50k`

- 🔵 **Bouton 2: "Convertir en Client"**
  - Conversion directe sans consultation
  - Création compte CLIENT
  - Création dossier immigration
  - Changement statut → `converti_client`

**Status: `paiement_50k` (Chez Consultant)**
- Badge: "Chez le consultant" (vert)
- 🔵 **Bouton: "Convertir en Client"**

**Status: `en_consultation`**
- Badge: "En consultation" (orange)
- 🔵 **Bouton: "Convertir en Client"**

**Status: `converti_client`**
- Badge: "Client créé" (émeraude)
- Aucune action (terminé)

#### 6. Paiements
- **Paiements en attente:** Liste des paiements clients à confirmer
- **Actions:**
  - ✅ Confirmer paiement (avec code)
  - ❌ Rejeter paiement (avec raison)
- **Historique:** Tous les paiements confirmés/rejetés

#### 7. Retraits ⭐
- **Component:** WithdrawalManager
- **Demande retrait:**
  - Montant CFA
  - Méthode (Mobile Money, Virement, Cash)
  - Motif
- **Suivi demandes:**
  - En attente
  - Approuvées
  - Rejetées
- **Historique complet**

---

### 💼 EMPLOYEE

**Dashboard: 4 Onglets**

#### 1. Mes Dossiers
- **Dossiers assignés** à l'employé
- **Progression workflow:**
  - Étapes complétées (bleu)
  - Étape actuelle (orange)
  - Étapes à venir (gris)
- **Actions:**
  - Voir détails dossier
  - Mettre à jour étape
  - Ajouter documents
- **Stats:**
  - Dossiers actifs
  - Dossiers terminés
  - En attente

#### 2. Mes Clients
- **Liste clients** assignés (13+)
- **Création nouveau client:**
  - Formulaire complet
  - Assignation automatique à l'employé
  - Création compte utilisateur
  - Email bienvenue
- **Actions:**
  - Voir/Éditer profil client
  - Voir dossiers client
  - Historique communications

#### 3. Visiteurs
- **Liste TOUS les visiteurs** (50+)
- **Enregistrement:** Même formulaire que Manager
- **Actions:** Checkout visiteurs

#### 4. Prospects ⭐
- **Identique à Manager**
- **Prospects assignés** à l'employé uniquement
- **Mêmes 2 boutons d'action** selon statut
- **Auto-refresh 30s**

---

### 🎓 CONSULTANT

**Dashboard: 1 Vue Principale**

#### Prospects Payants
- **Affichage:** Prospects avec status `paiement_50k` uniquement
- **Accès:** Aucune erreur 403 ✅
- **Stats:**
  - Total prospects consultations
  - Consultations payées
  - Montant total (ex: 200,000 CFA)
- **Informations prospect:**
  - Nom, email, téléphone
  - Pays, type de visa
  - Lead score (coloré)
  - Badge: "💰 50,000 CFA Payé"
- **Actions:**
  - ✏️ **Ajouter une Note**
    - Zone texte pour notes consultation
    - Enregistrement en base
    - Changement statut → `en_consultation`
  - 🔵 **Convertir en Client**
    - Si prospect prêt après consultation
    - Création compte client direct
- **Recherche & Tri:**
  - Par nom, score, pays, date
  - Ordre ascendant/descendant

#### Connexion Consultant
**Email:** (créé par SuperAdmin)
**Mot de passe:** Temporaire fourni lors de création

---

### 👤 CLIENT

**Dashboard: Vue Personnalisée**

#### Mon Dossier
- **Informations personnelles:**
  - Nom, email, pays, visa
  - Employé assigné
- **Progression dossier:**
  - Workflow visuel avec étapes
  - Documents requis par étape
  - Statut actuel
- **Historique:** Toutes les mises à jour

#### Mes Paiements
- **Déclarer paiement:**
  - Montant
  - Méthode
  - Preuve (upload)
- **Historique:**
  - Paiements en attente
  - Paiements confirmés
  - Factures téléchargeables (PDF)

#### Communications
- **Chat:** Avec employé assigné
- **Notifications:** Mises à jour dossier

---

## Workflows Métier

### 🔄 Workflow Prospect → Client

#### Étape 1: Création Prospect
**Acteur:** Visiteur (Landing Page)
**Action:** Formulaire de contact
**Champs:**
- Nom complet
- Email
- Téléphone
- Pays destination (Canada/France)
- Type de visa
- Comment avez-vous connu Aloria?
**Résultat:** 
- Status: `nouveau`
- Notification SuperAdmin

#### Étape 2: Assignation SuperAdmin → Manager/Employee
**Acteur:** SuperAdmin
**Action:** Dashboard Prospects → Bouton "Assigner"
**Process:**
1. Sélectionner prospect
2. Cliquer "Assigner"
3. Choisir Manager ou Employee (dropdown 38 disponibles)
4. Confirmer
**Résultat:**
- Status: `assigne_employe`
- Email notification à assigné
- Activity log créée

#### Étape 3: Contact & Paiement 50k CFA
**Acteur:** Manager/Employee
**Action:** Contacter prospect
**Process:**
1. Manager/Employee appelle prospect
2. Prospect veut consultation → Paie 50,000 CFA
3. Manager/Employee: Dashboard Prospects → "Affecter au Consultant"
4. Modal paiement:
   - Méthode: Cash/Mobile Money/Virement
   - Référence transaction
5. Confirmer
**Résultat:**
- Status: `paiement_50k`
- Paiement enregistré DB (collection `payments`)
- Facture PDF générée (CONS-20251111-XXXXXXXX)
- Notification SuperAdmin: "💰 Paiement Consultation 50,000 CFA"
- Email confirmation prospect
- Activity log: `consultation_payment_confirmed`

#### Étape 4: Consultation
**Acteur:** Consultant
**Action:** Dashboard Consultant
**Process:**
1. Voir prospect dans liste
2. Consultation (hors plateforme)
3. Ajouter notes consultation
**Résultat:**
- Status: `en_consultation`
- Notes enregistrées
- Activity log

#### Étape 5A: Conversion Client (Après Consultation)
**Acteur:** Manager/Employee OU Consultant
**Action:** Bouton "Convertir en Client"
**Process:**
1. Confirmation
2. Création automatique:
   - Compte USER (role: CLIENT)
   - Profil CLIENT
   - Dossier (CASE) initial
3. Email bienvenue avec credentials
**Résultat:**
- Status: `converti_client`
- CLIENT créé et actif
- Redirection vers gestion client

#### Étape 5B: Conversion Client (Directe, Sans Consultation)
**Acteur:** Manager/Employee
**Action:** Depuis status `assigne_employe` → Bouton "Convertir en Client"
**Process:** Identique à 5A
**Note:** Skip consultation si prospect déjà décidé

---

### 💰 Workflow Paiement Client

#### 1. Déclaration Paiement
**Acteur:** Client
**Action:** Dashboard → Mes Paiements → Déclarer
**Champs:**
- Montant CFA
- Méthode paiement
- Upload preuve
**Résultat:**
- Status: `PENDING`
- Notification Manager

#### 2. Confirmation/Rejet
**Acteur:** Manager
**Action:** Dashboard → Paiements
**Options:**
- ✅ **Confirmer:**
  - Entrer code paiement
  - Génération facture PDF
  - Progression dossier client
  - Status: `CONFIRMED`
- ❌ **Rejeter:**
  - Raison rejet
  - Notification client
  - Status: `REJECTED`

---

### 💸 Workflow Retrait Manager

#### 1. Demande Retrait
**Acteur:** Manager
**Action:** Dashboard → Retraits → Nouvelle Demande
**Champs:**
- Montant CFA
- Méthode (Mobile Money, Virement, Cash)
- Motif
**Résultat:**
- Status: `PENDING`
- Notification SuperAdmin

#### 2. Traitement SuperAdmin
**Acteur:** SuperAdmin
**Action:** Dashboard → Solde & Finances
**Options:**
- ✅ **Approuver:**
  - Validation solde disponible
  - Status: `APPROVED`
  - Activity log
- ❌ **Rejeter:**
  - Raison rejet
  - Status: `REJECTED`
  - Notification Manager

---

## Guide Utilisateur

### 🚀 Première Connexion

#### Pour SuperAdmin
1. URL: `http://localhost:3000/login`
2. Email: `superadmin@aloria.com`
3. Mot de passe: `SuperAdmin123!`
4. Redirection automatique: `/superadmin`

#### Pour Utilisateurs Créés
1. Email reçu avec credentials:
   - Email: (votre email)
   - Mot de passe temporaire: `Xk9$mP2vL@7n` (exemple)
2. Première connexion → Changement mot de passe recommandé
3. Redirection selon rôle:
   - Manager → `/manager`
   - Employee → `/employee`
   - Consultant → `/consultant`
   - Client → `/client`

### 📱 Navigation Générale

#### Header (Tous dashboards)
- **Logo ALORIA** (coin gauche)
- **Titre dashboard** (ex: "Tableau de Bord SuperAdmin")
- **Notifications** 🔔 (coin droit)
  - Badge nombre non lues
  - Dropdown avec liste
- **User Menu:**
  - Nom utilisateur
  - Déconnexion

#### Onglets
- Navigation horizontale
- Onglet actif: Gradient orange
- Compteurs dynamiques (ex: "Utilisateurs (132)")

### 🎨 Thème & Design

**Couleurs Principales:**
- **Background:** #0F172A (Slate-900 - Bleu Nuit)
- **Cards:** #1E293B (Slate-800)
- **Borders:** #334155 (Slate-700)
- **Texte:** Blanc (#FFFFFF) / Slate-300 (#CBD5E1)
- **Primary Action:** Orange (#F97316)
- **Secondary:** Blue (#3B82F6)
- **Success:** Emerald (#10B981)

**Typography:**
- Titres: Font-bold, text-white
- Labels: text-slate-300
- Descriptions: text-slate-400

---

## Guide Développeur

### 📂 Structure des Dossiers

```
/app/
├── backend/
│   ├── server.py              # Application FastAPI principale
│   ├── email_service.py       # Service emails (SendGrid)
│   ├── requirements.txt       # Dépendances Python
│   ├── .env                   # Variables environnement backend
│   └── invoices/              # Factures PDF générées
│
├── frontend/
│   ├── public/
│   │   └── ALORIA Logo.png    # Logo application
│   ├── src/
│   │   ├── index.js           # Point d'entrée React
│   │   ├── App.js             # Router principal
│   │   ├── App.css            # Styles globaux + animations
│   │   ├── components/
│   │   │   ├── ui/            # Composants Shadcn UI
│   │   │   ├── SearchAndSort.js
│   │   │   ├── MyProspects.js
│   │   │   ├── ProspectManagement.js
│   │   │   ├── HierarchicalUserCreation.js
│   │   │   ├── WithdrawalManager.js
│   │   │   ├── BalanceMonitor.js
│   │   │   ├── ActivityHistory.js
│   │   │   ├── ChatWidget.js
│   │   │   ├── NotificationBell.js
│   │   │   └── AloriaLogo.js
│   │   ├── context/
│   │   │   └── AuthContext.js # État authentification global
│   │   ├── hooks/
│   │   │   ├── use-toast.js
│   │   │   └── useSocket.js
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── LoginPage.js
│   │   │   ├── SuperAdminDashboard.js
│   │   │   ├── ManagerDashboard.js
│   │   │   ├── EmployeeDashboard.js
│   │   │   ├── ConsultantDashboard.js
│   │   │   └── ClientDashboard.js
│   │   └── utils/
│   │       └── api.js         # Axios instance configurée
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env                   # Variables environnement frontend
│
├── test_result.md             # Résultats tests & protocole
└── DOCUMENTATION_COMPLETE.md  # Ce fichier
```

### 🔧 Configuration Environnement

#### Backend `.env`
```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017/aloria_db

# JWT
SECRET_KEY=your-secret-key-here-change-in-production

# SendGrid Email
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SENDER_EMAIL=contact@aloria-agency.com

# Server
PORT=8001
```

#### Frontend `.env`
```bash
# Backend URL (DO NOT MODIFY - configured for production)
REACT_APP_BACKEND_URL=https://your-domain.com

# Environment
NODE_ENV=production
```

### 🛠️ Installation & Démarrage

#### Prérequis
- Python 3.9+
- Node.js 16+
- MongoDB 5.0+
- Yarn

#### Backend
```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Démarrer via Supervisor (production)
sudo supervisorctl restart backend

# OU manuel (dev)
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend
```bash
cd frontend

# Installer dépendances
yarn install

# Démarrer via Supervisor (production)
sudo supervisorctl restart frontend

# OU manuel (dev)
yarn start
```

#### Vérifier Services
```bash
# Status tous les services
sudo supervisorctl status

# Logs backend
tail -f /var/log/supervisor/backend.*.log

# Logs frontend
tail -f /var/log/supervisor/frontend.*.log
```

### 🔐 Authentification & Sécurité

#### JWT Token Flow
```python
# Backend: Génération token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Frontend: Stockage
localStorage.setItem('token', token)

# Frontend: Utilisation
api.defaults.headers.common['Authorization'] = `Bearer ${token}`
```

#### Middleware Protection
```python
# Dépendance FastAPI pour routes protégées
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401)
```

#### Role-Based Access
```python
# Vérification hiérarchie
def can_create_role(creator_role: str, target_role: str) -> bool:
    creator_level = ROLE_HIERARCHY.get(creator_role, 0)
    target_level = ROLE_HIERARCHY.get(target_role, 0)
    return creator_level > target_level

# Exemple utilisation
if current_user["role"] != "SUPERADMIN":
    raise HTTPException(status_code=403, detail="Accès interdit")
```

### 📊 Base de Données

#### Collections MongoDB

**users**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "email": "user@example.com",
  "password": "hashed_password",
  "full_name": "John Doe",
  "role": "MANAGER", // SUPERADMIN, MANAGER, EMPLOYEE, CONSULTANT, CLIENT
  "is_active": true,
  "created_by": "creator_user_id",
  "created_at": "2024-11-11T10:00:00Z",
  "last_login": "2024-11-11T15:30:00Z"
}
```

**contact_messages (Prospects)**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "name": "Prospect Name",
  "email": "prospect@example.com",
  "phone": "+237XXXXXXXXX",
  "country": "Canada",
  "visa_type": "Visa Travail",
  "how_did_you_know": "Google",
  "message": "Description...",
  "status": "paiement_50k", // nouveau, assigne_employe, paiement_50k, en_consultation, converti_client
  "lead_score": 75,
  "assigned_to": "employee_user_id",
  "assigned_by": "superadmin_user_id",
  "payment_50k_amount": 50000,
  "payment_50k_date": "2024-11-11T12:00:00Z",
  "payment_50k_id": "payment_uuid",
  "payment_50k_method": "Mobile Money",
  "consultant_notes": "Notes de consultation...",
  "created_at": "2024-11-11T10:00:00Z",
  "updated_at": "2024-11-11T14:00:00Z"
}
```

**payments**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "invoice_number": "CONS-20241111-ABC123",
  "type": "consultation", // consultation, case_payment
  "amount": 50000,
  "currency": "CFA",
  "payment_method": "Mobile Money",
  "transaction_reference": "MTN-123456789",
  "status": "CONFIRMED", // PENDING, CONFIRMED, REJECTED
  "prospect_id": "prospect_uuid", // pour consultations
  "client_id": "client_uuid", // pour paiements dossiers
  "confirmed_by": "manager_user_id",
  "confirmed_by_name": "Manager Name",
  "confirmed_at": "2024-11-11T12:00:00Z",
  "created_at": "2024-11-11T11:30:00Z"
}
```

**clients**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "user_id": "user_uuid",
  "full_name": "Client Name",
  "email": "client@example.com",
  "phone": "+237XXXXXXXXX",
  "country": "Canada",
  "visa_type": "Visa Étudiant",
  "assigned_employee_id": "employee_uuid",
  "assigned_employee_name": "Employee Name",
  "created_by": "manager_uuid",
  "created_at": "2024-11-11T10:00:00Z"
}
```

**cases**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "client_id": "client_uuid",
  "client_name": "Client Name",
  "country": "Canada",
  "visa_type": "Visa Travail",
  "status": "In Progress", // New, In Progress, Documents Review, Interview, Approved, Rejected, Terminated
  "current_step_index": 2,
  "workflow_steps": [
    {
      "title": "Consultation initiale",
      "description": "Évaluation du profil",
      "documents": ["Passeport", "CV"],
      "completed": true
    },
    // ... autres étapes
  ],
  "assigned_employee_id": "employee_uuid",
  "created_at": "2024-11-11T10:00:00Z",
  "updated_at": "2024-11-11T15:00:00Z"
}
```

**user_activities**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "user_id": "user_uuid",
  "user_name": "John Doe",
  "user_role": "MANAGER",
  "action": "client_created", // login, create_user, client_created, consultation_payment_confirmed, etc.
  "details": {
    "client_name": "Client Name",
    "amount": 50000,
    // ... autres détails selon action
  },
  "ip_address": "192.168.1.1",
  "timestamp": "2024-11-11T10:00:00Z"
}
```

**visitors**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "name": "Visitor Name",
  "organization": "Company XYZ",
  "email": "visitor@example.com",
  "phone_number": "+237XXXXXXXXX",
  "purpose": "Consultation initiale",
  "other_purpose": "",
  "cni_number": "1234567890",
  "arrival_time": "2024-11-11T09:00:00Z",
  "departure_time": "2024-11-11T11:00:00Z", // null si encore présent
  "registered_by": "employee_uuid",
  "registered_by_name": "Employee Name"
}
```

**withdrawals**
```javascript
{
  "_id": ObjectId,
  "id": "uuid",
  "amount": 100000,
  "currency": "CFA",
  "method": "Mobile Money",
  "reason": "Salaire mensuel",
  "status": "PENDING", // PENDING, APPROVED, REJECTED
  "requested_by": "manager_uuid",
  "requested_by_name": "Manager Name",
  "processed_by": "superadmin_uuid",
  "processed_at": "2024-11-11T16:00:00Z",
  "rejection_reason": "",
  "created_at": "2024-11-11T15:00:00Z"
}
```

### 🔄 API Endpoints Principaux

#### Authentication
```
POST   /api/auth/login          # Login utilisateur
POST   /api/auth/logout         # Logout
GET    /api/auth/me             # Utilisateur courant
```

#### Users
```
POST   /api/users/create        # Créer utilisateur (hierarchical)
GET    /api/admin/users         # Liste tous users (SuperAdmin)
GET    /api/users/{user_id}     # Détails user
PATCH  /api/users/{user_id}     # Update user
```

#### Prospects (Contact Messages)
```
POST   /api/contact-messages                        # Créer prospect
GET    /api/contact-messages                        # Liste prospects (filtered by role)
PATCH  /api/contact-messages/{id}/assign           # Assigner à employee
PATCH  /api/contact-messages/{id}/assign-consultant # Affecter au consultant (paiement 50k)
PATCH  /api/contact-messages/{id}/consultant-notes # Ajouter notes consultant
POST   /api/contact-messages/{id}/convert-to-client # Convertir en client
```

#### Clients
```
POST   /api/clients             # Créer client
GET    /api/clients             # Liste clients
GET    /api/clients/{id}        # Détails client
PATCH  /api/clients/{id}/reassign # Réassigner à autre employee
```

#### Cases (Dossiers)
```
POST   /api/cases               # Créer dossier
GET    /api/cases               # Liste dossiers
GET    /api/cases/{id}          # Détails dossier
PATCH  /api/cases/{id}/status   # Mettre à jour statut
PATCH  /api/cases/{id}/step     # Progresser étape workflow
```

#### Payments
```
POST   /api/payments            # Déclarer paiement (client)
GET    /api/payments            # Liste paiements
PATCH  /api/payments/{id}/confirm # Confirmer/Rejeter (manager)
GET    /api/payments/consultations # Paiements consultation (SuperAdmin)
GET    /api/payments/{id}/invoice/pdf # Télécharger facture
```

#### Visitors
```
POST   /api/visitors            # Enregistrer visiteur
GET    /api/visitors            # Liste tous visiteurs
PATCH  /api/visitors/{id}/checkout # Marquer départ
```

#### Withdrawals
```
POST   /api/withdrawals         # Demander retrait (manager)
GET    /api/withdrawals         # Liste retraits
PATCH  /api/withdrawals/{id}/approve # Approuver/Rejeter (SuperAdmin)
```

#### Activities
```
GET    /api/admin/activities    # Historique activités (SuperAdmin)
```

#### Dashboard Stats
```
GET    /api/admin/dashboard-stats # Stats globales (SuperAdmin)
GET    /api/dashboard-stats      # Stats utilisateur courant
```

### 📧 Email Notifications

**Service:** SendGrid

**Templates Disponibles:**
1. **Bienvenue User:** Envoyé lors création compte
2. **Bienvenue Client:** Envoyé lors conversion prospect
3. **Assignation Prospect:** Notifie employee assigné
4. **Rendez-vous Consultant:** Confirme paiement 50k
5. **Changement Statut Dossier:** Informe client
6. **Paiement Confirmé:** Facture attachée
7. **Retrait Approuvé/Rejeté:** Notification manager

**Configuration:**
```python
# email_service.py
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'contact@aloria-agency.com')
```

### 🎨 Composants Réutilisables

#### SearchAndSort
```jsx
<SearchAndSort
  data={items}
  searchFields={['name', 'email', 'status']}
  sortOptions={[
    { value: 'created_at', label: 'Date' },
    { value: 'name', label: 'Nom' }
  ]}
  onFilteredDataChange={setFilteredItems}
  placeholder="Rechercher..."
/>
```

#### AloriaLogo
```jsx
<AloriaLogo className="h-12" />
```

#### NotificationBell
```jsx
<NotificationBell />
```

#### ChatWidget
```jsx
<ChatWidget userRole="MANAGER" />
```

### 🧪 Testing

**Backend Testing:**
```bash
# Via testing agent
deep_testing_backend_v2
```

**Frontend Testing:**
```bash
# Via testing agent
auto_frontend_testing_agent
```

**Protocole:** Voir `test_result.md`

---

## API Documentation

### Authentication Headers

Toutes les requêtes API (sauf login) nécessitent:
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Response Format

**Success:**
```json
{
  "message": "Opération réussie",
  "data": { /* ... */ },
  "id": "uuid",
  "invoice_number": "CONS-20241111-ABC123"
}
```

**Error:**
```json
{
  "detail": "Message d'erreur explicite"
}
```

### Status Codes

- `200` OK - Requête réussie
- `201` Created - Ressource créée
- `400` Bad Request - Validation échouée
- `401` Unauthorized - Token invalide/expiré
- `403` Forbidden - Permissions insuffisantes
- `404` Not Found - Ressource inexistante
- `500` Internal Server Error - Erreur serveur

### Exemples Requêtes

#### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@test.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "manager@test.com",
    "full_name": "Test Manager",
    "role": "MANAGER"
  }
}
```

#### Créer Prospect
```bash
curl -X POST http://localhost:3000/api/contact-messages \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jean Dupont",
    "email": "jean@example.com",
    "phone": "+237690000000",
    "country": "Canada",
    "visa_type": "Visa Travail",
    "how_did_you_know": "Google",
    "message": "Je souhaite immigrer au Canada"
  }'
```

#### Assigner Prospect
```bash
curl -X PATCH http://localhost:3000/api/contact-messages/{prospect_id}/assign \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_to": "employee_uuid"
  }'
```

#### Paiement Consultation 50k
```bash
curl -X PATCH http://localhost:3000/api/contact-messages/{prospect_id}/assign-consultant \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "Mobile Money",
    "transaction_reference": "MTN-123456789"
  }'
```

Response:
```json
{
  "message": "Prospect affecté au consultant avec succès",
  "payment_50k_amount": 50000,
  "payment_id": "payment_uuid",
  "invoice_number": "CONS-20241111-10EE3ZAF"
}
```

---

## Guide de Déploiement

### 🚀 Production Checklist

#### Pré-déploiement
- [ ] Tester en local complètement
- [ ] Mettre à jour `requirements.txt` et `package.json`
- [ ] Vérifier `.env` avec valeurs production
- [ ] Changer `SECRET_KEY` JWT
- [ ] Configurer SendGrid API key réelle
- [ ] Vérifier MongoDB connection string
- [ ] Tester backup/restore MongoDB

#### Backend
```bash
# 1. Build
cd backend
pip install -r requirements.txt

# 2. Vérifier configuration
cat .env

# 3. Test sanity
curl http://localhost:8001/api/health

# 4. Restart service
sudo supervisorctl restart backend
```

#### Frontend
```bash
# 1. Build production
cd frontend
yarn build

# 2. Vérifier build
ls -lh build/

# 3. Restart service
sudo supervisorctl restart frontend
```

#### Post-déploiement
- [ ] Vérifier tous services: `sudo supervisorctl status`
- [ ] Test login SuperAdmin
- [ ] Test création utilisateur
- [ ] Test workflow prospect complet
- [ ] Vérifier emails envoyés
- [ ] Test paiements
- [ ] Monitorer logs: `tail -f /var/log/supervisor/*.log`

### 🔒 Sécurité Production

**Variables Sensibles:**
```bash
# NE JAMAIS committer
SECRET_KEY=<générer-256-bits-random>
SENDGRID_API_KEY=<real-sendgrid-key>
MONGO_URL=<secure-mongodb-connection>
```

**Recommandations:**
- HTTPS obligatoire (Let's Encrypt)
- CORS configuré strictement
- Rate limiting API
- MongoDB authentification activée
- Logs rotations configurées
- Backups quotidiens MongoDB

### 📊 Monitoring

**Logs à surveiller:**
```bash
# Backend errors
tail -f /var/log/supervisor/backend.err.log

# Backend output
tail -f /var/log/supervisor/backend.out.log

# Frontend errors
tail -f /var/log/supervisor/frontend.err.log
```

**Métriques importantes:**
- Temps réponse API (<200ms)
- Taux erreur (<1%)
- Uptime (>99.9%)
- Utilisation mémoire
- Connexions MongoDB

---

## FAQ & Troubleshooting

### Questions Fréquentes

#### Q: Comment réinitialiser mot de passe utilisateur?
**R:** SuperAdmin doit:
1. Aller dans Utilisateurs
2. Cliquer "Voir" sur l'utilisateur
3. Utiliser fonction "Réinitialiser mot de passe"
4. Nouveau mot de passe temporaire généré
5. Communiquer au user

#### Q: Prospect ne reçoit pas email après assignation?
**R:** Vérifier:
1. SendGrid API key configurée
2. Sender email vérifié dans SendGrid
3. Logs backend: `grep "Email" /var/log/supervisor/backend.out.log`
4. Tester SendGrid API directement

#### Q: Liste activités vide?
**R:** Problème résolu! Vérifier:
1. Endpoint correct: `/api/admin/activities` ✅
2. Backend retourne données: `curl` endpoint
3. Frontend component: `ActivityHistory.js` ligne 40 ✅

#### Q: Dropdown employés vide dans assignation?
**R:** Problème résolu! Utilisation `<select>` HTML natif au lieu de Shadcn UI `<Select>` ✅

#### Q: Comment se connecter en tant que Consultant?
**R:**
1. SuperAdmin crée consultant
2. Noter mot de passe temporaire affiché
3. Login avec email + mot de passe temporaire
4. Redirection automatique `/consultant`

#### Q: Client ne voit pas son dossier?
**R:** Vérifier:
1. Client bien créé (table `clients`)
2. Case créé et lié au client (`client_id`)
3. Client assigné à employee (`assigned_employee_id`)

### Problèmes Courants

#### Erreur: "Maximum update depth exceeded"
**Cause:** Boucle infinie React (useEffect)
**Solution:**
1. Utiliser `useCallback` pour callbacks
2. Vérifier dependencies array useEffect
3. Éviter setState dans render
✅ **Résolu:** SearchAndSort utilise `useMemo` + callbacks stables

#### Erreur: "403 Forbidden"
**Cause:** Permissions insuffisantes
**Solution:**
1. Vérifier rôle utilisateur courant
2. Vérifier hiérarchie ROLE_HIERARCHY
3. Logs backend pour détails

#### Erreur: "Connection refused MongoDB"
**Cause:** MongoDB non démarré ou mauvais URL
**Solution:**
```bash
# Vérifier MongoDB
sudo systemctl status mongod

# Démarrer si arrêté
sudo systemctl start mongod

# Vérifier connexion
mongo --eval "db.adminCommand('ping')"
```

#### Erreur: "WebSocket connection failed"
**Cause:** Normal - Chat non critique
**Solution:** Ignorer ou désactiver si non utilisé

### Logs Utiles

```bash
# Tous les logs backend
tail -f /var/log/supervisor/backend.*.log

# Filtrer erreurs uniquement
tail -f /var/log/supervisor/backend.err.log | grep ERROR

# Activités loggées
grep "Activity logged" /var/log/supervisor/backend.out.log

# Emails envoyés
grep "Email.*sent" /var/log/supervisor/backend.out.log

# Erreurs 500
grep "500" /var/log/supervisor/backend.out.log
```

---

## Annexes

### Glossaire

- **Prospect:** Personne ayant rempli formulaire contact, pas encore client
- **Consultation:** Rendez-vous avec consultant après paiement 50k CFA
- **Dossier (Case):** Ensemble documents/étapes pour immigration client
- **Workflow:** Séquence d'étapes pour traiter dossier
- **Lead Score:** Score automatique qualité prospect (0-100)
- **Retrait:** Demande manager pour retirer fonds
- **Activity Log:** Historique actions utilisateurs système

### Acronymes

- **JWT:** JSON Web Token (authentification)
- **RBAC:** Role-Based Access Control
- **CFA:** Franc CFA (devise Cameroun)
- **API:** Application Programming Interface
- **CRUD:** Create, Read, Update, Delete
- **E2E:** End-to-End (tests)
- **UUID:** Universal Unique Identifier

### Ressources Externes

- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **MongoDB:** https://www.mongodb.com/docs/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Shadcn UI:** https://ui.shadcn.com/
- **SendGrid:** https://docs.sendgrid.com/

---

## 📝 Historique des Versions

### Version 1.0 (Novembre 2024)
- ✅ MVP complet
- ✅ 5 rôles utilisateurs
- ✅ Workflow prospects → clients
- ✅ Paiements consultation 50k CFA
- ✅ Dashboards personnalisés
- ✅ System activités loggées
- ✅ Génération factures PDF
- ✅ Email notifications
- ✅ UI dark theme cohérent

### Améliorations Futures Suggérées

1. **Fonctionnalités:**
   - Chat en temps réel (WebSocket opérationnel)
   - Upload documents clients (S3 ou local)
   - Calendrier rendez-vous
   - Rapports analytics avancés
   - Multi-langue (EN, FR)

2. **Technique:**
   - Tests unitaires (Jest, Pytest)
   - CI/CD pipeline
   - Docker Compose pour dev
   - Monitoring (Prometheus/Grafana)
   - Logs centralisés (ELK Stack)

3. **Sécurité:**
   - 2FA (Two-Factor Authentication)
   - Audit trail complet
   - Encryption documents sensibles
   - Rate limiting API
   - GDPR compliance tools

---

## 📞 Support & Contact

**Équipe Développement:**
- **Email:** support@aloria-agency.com
- **Documentation:** Ce fichier + `test_result.md`

**En cas de problème:**
1. Consulter FAQ ci-dessus
2. Vérifier logs backend/frontend
3. Tester avec curl (voir exemples API)
4. Consulter `test_result.md` pour protocole tests

---

**Document créé:** Novembre 2024
**Dernière mise à jour:** 11 Novembre 2024
**Version:** 1.0
**Statut:** Production Ready ✅

---

*ALORIA AGENCY - Plateforme de Gestion d'Immigration*
*Tous droits réservés © 2024*
