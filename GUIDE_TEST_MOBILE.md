# 📱 GUIDE DE TEST MOBILE - ALORIA AGENCY

## Vue d'Ensemble

Ce guide vous permet de tester l'application ALORIA sur différents appareils mobiles pour garantir une expérience utilisateur optimale.

---

## 🎯 Objectifs des Tests

- ✅ Vérifier le responsive sur tous les écrans mobiles
- ✅ Tester la navigation et l'ergonomie
- ✅ Valider les fonctionnalités principales
- ✅ S'assurer de la performance (temps de chargement)

---

## 📱 Appareils de Test Recommandés

### Smartphones iOS

| Appareil | Résolution | Priorité |
|----------|------------|----------|
| iPhone SE (2020) | 375 x 667 | ⭐⭐⭐ Haute |
| iPhone 12/13 | 390 x 844 | ⭐⭐⭐ Haute |
| iPhone 14 Pro Max | 430 x 932 | ⭐⭐ Moyenne |

### Smartphones Android

| Appareil | Résolution | Priorité |
|----------|------------|----------|
| Samsung Galaxy S21 | 360 x 800 | ⭐⭐⭐ Haute |
| Google Pixel 5 | 393 x 851 | ⭐⭐ Moyenne |
| OnePlus 9 | 412 x 915 | ⭐ Basse |

---

## ✅ CHECKLIST DE TEST - LANDING PAGE

### Hero Section

- [ ] **Titre visible** : "Votre Rêve d'Immigration Devient Réalité"
- [ ] **Badge orange** : Pas de débordement, texte lisible
- [ ] **Texte descriptif** : Visible et lisible (pas coupé)
- [ ] **Bouton "Commencer Maintenant"** : Bien visible et cliquable
- [ ] **Statistiques** : "98% Succès", "500+ Succès", "Support 24/7" visibles
- [ ] **Pas de scroll horizontal** : Pas de débordement

**Actions à tester :**
1. Cliquer sur **"Commencer Maintenant"**
   - ✅ Doit scroller automatiquement vers le calculateur CRS
   - ✅ Animation smooth (pas de saut brutal)

### Calculateur CRS

- [ ] **Section visible** après scroll
- [ ] **Formulaire** : Tous les champs visibles et utilisables
- [ ] **Dropdowns** : Fonctionnent correctement (pas de débordement)
- [ ] **Bouton "Calculer"** : Visible et cliquable
- [ ] **Résultat** : S'affiche correctement

### Autres Sections

- [ ] **Services** : Cards alignées verticalement, texte lisible
- [ ] **Processus** : Timeline visible et claire
- [ ] **Témoignages** : Cards lisibles, navigation fonctionne
- [ ] **FAQ** : Questions/réponses s'ouvrent correctement
- [ ] **Contact** : Formulaire fonctionnel, champs visibles

---

## ✅ CHECKLIST DE TEST - CONNEXION

### Page de Login

- [ ] **Logo ALORIA** : Visible et centré
- [ ] **Titre "Connexion"** : Visible
- [ ] **Champ Email** : 
  - [ ] Visible
  - [ ] Clavier email (avec @) s'ouvre sur mobile
  - [ ] Pas de zoom automatique (iOS)
- [ ] **Champ Password** : 
  - [ ] Visible
  - [ ] Icône œil pour afficher/masquer fonctionne
- [ ] **Bouton "Se connecter"** : 
  - [ ] Pleine largeur
  - [ ] Cliquable
  - [ ] Feedback visuel au clic
- [ ] **Lien "Mot de passe oublié"** : Visible et cliquable

**Actions à tester :**
1. Entrer email invalide
   - ✅ Message d'erreur visible
2. Entrer mot de passe incorrect
   - ✅ Message d'erreur clair
3. Se connecter avec credentials valides
   - ✅ Redirection vers dashboard

### Reset Mot de Passe

- [ ] **Dialogue "Mot de passe oublié"** : S'ouvre correctement
- [ ] **Champ email** : Fonctionnel
- [ ] **Bouton "Réinitialiser"** : Cliquable
- [ ] **Message de succès** : Visible et clair

---

## ✅ CHECKLIST DE TEST - DASHBOARD CLIENT

### Navigation

- [ ] **Menu hamburger** : S'ouvre/ferme correctement
- [ ] **Liens du menu** : Tous cliquables
- [ ] **Logo ALORIA** : Cliquable (retour dashboard)

### Dashboard Principal

- [ ] **Statistiques** : 4 cards visibles et lisibles
- [ ] **Dossier Actif** : Card bien affichée
  - [ ] Nom du pays
  - [ ] Type de visa
  - [ ] Barre de progression
  - [ ] Statut
- [ ] **Étape Actuelle** : Informations visibles
- [ ] **Paiements** : Section visible
  - [ ] Bouton "Déclarer un Paiement"
  - [ ] Historique des paiements

### Déclaration de Paiement

- [ ] **Dialogue** : S'ouvre en plein écran (mobile)
- [ ] **Champs du formulaire** : 
  - [ ] Montant (clavier numérique)
  - [ ] Devise (dropdown fonctionne)
  - [ ] Méthode de paiement (dropdown fonctionne)
  - [ ] Description (optionnel)
- [ ] **Boutons** : "Annuler" et "Soumettre" visibles
- [ ] **Validation** : Erreurs affichées clairement

**Actions à tester :**
1. Déclarer un paiement de test
   - ✅ Formulaire se soumet
   - ✅ Message de confirmation
   - ✅ Paiement apparaît dans l'historique avec statut "En attente"

---

## ✅ CHECKLIST DE TEST - DASHBOARD EMPLOYÉ

### Mes Clients

- [ ] **Liste des clients** : Cards affichées correctement
- [ ] **Barre de recherche** : Fonctionne sur mobile
- [ ] **Tri** : Dropdown fonctionne
- [ ] **Bouton "Voir Détails"** : Cliquable

### Créer un Client

- [ ] **Formulaire** : Tous les champs visibles
- [ ] **Champs obligatoires** : Marqués clairement
- [ ] **Validation** : Messages d'erreur clairs
- [ ] **Bouton "Créer"** : Pleine largeur et cliquable

---

## ✅ CHECKLIST DE TEST - DASHBOARD MANAGER

### Vue Globale

- [ ] **Statistiques** : 6 cards visibles
- [ ] **Onglets** : Tous accessibles et fonctionnels
  - [ ] Clients
  - [ ] Dossiers
  - [ ] Employés
  - [ ] Paiements
  - [ ] Retraits
  - [ ] Visiteurs

### Validation Paiements

- [ ] **Liste paiements en attente** : Cards lisibles
- [ ] **Boutons "Valider/Rejeter"** : Visibles et cliquables
- [ ] **Dialogue de confirmation** : Fonctionne correctement
- [ ] **Code de confirmation** : Champ visible et fonctionnel

---

## ⚡ TEST DE PERFORMANCE

### Temps de Chargement

| Page | Temps Acceptable | Cible |
|------|------------------|-------|
| Landing Page | < 3 secondes | < 2 secondes |
| Login | < 2 secondes | < 1 seconde |
| Dashboard | < 3 secondes | < 2 secondes |

**Comment tester :**
1. Ouvrir Chrome DevTools
2. Onglet "Network"
3. Activer "Disable cache"
4. Activer "Slow 3G" (simulation 3G)
5. Recharger la page
6. Noter le temps "Load"

### Interactions

- [ ] **Scroll smooth** : Pas de lag
- [ ] **Boutons** : Répondent instantanément
- [ ] **Animations** : Fluides (pas de saccades)
- [ ] **Formulaires** : Saisie réactive

---

## 🐛 SIGNALEMENT DE BUGS

### Template de Bug Report

```
**Appareil :** [iPhone 12, Galaxy S21, etc.]
**OS/Version :** [iOS 16, Android 13, etc.]
**Navigateur :** [Safari, Chrome, Firefox]
**Page concernée :** [Landing, Login, Dashboard, etc.]

**Description du problème :**
[Décrire le problème en détail]

**Étapes pour reproduire :**
1. [Étape 1]
2. [Étape 2]
3. [Étape 3]

**Résultat attendu :**
[Ce qui devrait se passer]

**Résultat observé :**
[Ce qui se passe réellement]

**Screenshot :**
[Joindre une capture d'écran si possible]

**Priorité :** [🔴 Critique / 🟠 Haute / 🟡 Moyenne / 🟢 Basse]
```

---

## 📊 RAPPORT DE TEST

### Template de Rapport

```
**Date du test :** [JJ/MM/AAAA]
**Testeur :** [Nom]
**Appareil(s) testé(s) :** [Liste]

**Résumé :**
- Pages testées : [X/Y]
- Fonctionnalités testées : [X/Y]
- Bugs trouvés : [X]
  - Critiques : [X]
  - Hauts : [X]
  - Moyens : [X]
  - Bas : [X]

**Bugs Critiques :**
1. [Description bug 1]
2. [Description bug 2]

**Recommandations :**
1. [Recommandation 1]
2. [Recommandation 2]

**Verdict :** [✅ Prêt pour production / ⚠️ Corrections mineures / ❌ Corrections majeures]
```

---

## 🎯 CRITÈRES D'ACCEPTATION

### Pour Validation Production

✅ **Obligatoire (100%) :**
- Toutes les pages se chargent sans erreur
- Pas de débordement horizontal
- Tous les boutons fonctionnels
- Formulaires utilisables
- Texte lisible sur tous les écrans

⚠️ **Important (80%) :**
- Performance acceptable (< 3s)
- Animations fluides
- Responsive parfait sur 3+ appareils

💡 **Nice-to-have (50%) :**
- Temps de chargement optimal (< 2s)
- Animations avancées
- Responsive parfait sur tous appareils

---

## 📞 CONTACTS SUPPORT

**Pour questions techniques :**
- Email : support@aloria-agency.com
- Téléphone : +237 6XX XX XX XX

**Pour signaler un bug critique :**
- Email urgent : bugs@aloria-agency.com
- Slack : #bugs-urgent

---

**ALORIA AGENCY**  
*Guide de Test Mobile - Version 1.0*

**Dernière mise à jour :** Janvier 2025
