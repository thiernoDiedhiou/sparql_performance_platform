# Test du Système de Gestion des Datasets

## ✅ L'onglet "Datasets" est maintenant disponible !

### Comment accéder à l'onglet Datasets

1. **Démarrer l'application** :
   ```bash
   streamlit run main_v2.py
   ```

2. **Cliquer sur l'onglet "📦 Datasets"** (2ème onglet)

3. **Vous devriez voir** :
   - Une vue d'ensemble des datasets disponibles
   - Des sélecteurs pour choisir le dataset et la taille
   - Des informations détaillées (taille fichier, temps estimé, mémoire)
   - Des boutons pour charger dans Virtuoso/Fuseki/Les deux
   - Une section de statistiques des datasets chargés

## 🧪 Tests à effectuer

### Test 1: Vérifier que l'onglet s'affiche
- [ ] Lancer `streamlit run main_v2.py`
- [ ] L'onglet "📦 Datasets" apparaît en 2ème position
- [ ] Cliquer dessus ne provoque pas d'erreur

### Test 2: Charger un dataset simple
- [ ] Sélectionner "Generic" et "10K"
- [ ] Vérifier les informations affichées
- [ ] Cliquer sur "Charger dans Virtuoso" (ou Fuseki si Virtuoso n'est pas démarré)
- [ ] Observer la barre de progression
- [ ] Vérifier le message de succès

### Test 3: Vérifier les métadonnées
- [ ] Après chargement, vérifier que `datasets_metadata.json` a été créé à la racine
- [ ] Ouvrir le fichier et vérifier son contenu
- [ ] Vérifier que le fichier `.env` a été mis à jour avec la section "CONFIGURATION DES DATASETS CHARGÉS"

### Test 4: Consulter les statistiques
- [ ] Faire défiler jusqu'à la section "Datasets actuellement chargés"
- [ ] Vérifier que les informations du dataset chargé sont affichées
- [ ] Vérifier que le nombre de triplets est correct

### Test 5: Supprimer un dataset
- [ ] Cliquer sur le bouton "🗑️ Effacer" à côté du moteur
- [ ] Vérifier le message de confirmation
- [ ] Vérifier que les statistiques sont mises à jour
- [ ] Vérifier que `datasets_metadata.json` a été mis à jour

## 🔧 Si vous rencontrez des problèmes

### Erreur: "Module datasets_tab non disponible"
**Solution** : Le fichier `ui/tabs/datasets_tab.py` existe déjà, vérifiez qu'il n'y a pas d'erreur de syntaxe :
```bash
python -c "from ui.tabs.datasets_tab import render_datasets_tab; print('OK')"
```

### Erreur: "Dossier datasets non trouvé"
**Solution** : Créez la structure de dossiers :
```bash
mkdir -p datasets/DBpedia datasets/LUBM datasets/Generic
```

### Erreur: "Aucun dataset trouvé"
**Solution** : Placez vos fichiers .ttl dans les bons dossiers :
```
datasets/
├── DBpedia/
│   ├── 10K.ttl
│   └── 100K.ttl
├── LUBM/
│   ├── 10K.ttl
│   └── 100K.ttl
└── Generic/
    └── 10K.ttl
```

### Erreur lors du chargement dans Virtuoso
**Solution** : Vérifiez que Virtuoso est démarré et accessible :
```bash
curl http://localhost:8890/sparql
```

### Erreur de permissions SPARQL_UPDATE
**Solution** : Connectez-vous à Virtuoso et donnez les permissions :
```sql
isql 1111 dba dba
GRANT SPARQL_UPDATE TO "SPARQL";
```

## 📊 Résultat attendu

Après avoir suivi ces tests, vous devriez avoir :

1. ✅ L'onglet "📦 Datasets" fonctionnel
2. ✅ Un dataset chargé dans Virtuoso et/ou Fuseki
3. ✅ Le fichier `datasets_metadata.json` créé avec les infos
4. ✅ Le fichier `.env` mis à jour
5. ✅ Les statistiques affichées correctement
6. ✅ La capacité de supprimer les datasets

## 🎉 Si tout fonctionne

Félicitations ! Votre système de gestion des datasets est opérationnel. Vous pouvez maintenant :

- Charger différents datasets pour vos tests
- Comparer les performances de Virtuoso vs Fuseki
- Consulter l'historique des datasets chargés
- Nettoyer facilement les données

## 📚 Documentation complète

Pour plus d'informations, consultez :
- [README_DATASETS.md](README_DATASETS.md) - Guide rapide
- [DATASETS_MANAGEMENT.md](DATASETS_MANAGEMENT.md) - Guide complet
- [CHANGELOG_DATASETS.md](CHANGELOG_DATASETS.md) - Liste des changements

## 🆘 Support

Si vous rencontrez un problème non couvert ici :
1. Consultez les logs : `logs/sparql_platform.log`
2. Vérifiez la documentation complète
3. Relisez les messages d'erreur affichés dans Streamlit

---

**Note** : Ce fichier de test peut être supprimé une fois que vous avez vérifié que tout fonctionne correctement.
