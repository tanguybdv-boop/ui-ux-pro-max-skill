# Participation SCOP

Petite application web (autonome) pour calculer la participation des salariés d'une SCOP.

## Fonctionnalités

- **Montant de base par salarié** : valeur de référence appliquée par défaut à chaque salarié.
- **Intérêts automatiques à 3 %** : le taux (modifiable) est calculé automatiquement sur le montant de base de chaque salarié.
- **Gestion des salariés** : ajout, suppression, montant de base personnalisable par personne.
- **Récapitulatif en temps réel** : total des montants de base, total des intérêts et participation totale (base + intérêts).
- **Sauvegarde locale** : les données sont conservées dans le navigateur (localStorage).

## Calcul

Pour chaque salarié :

```
Intérêts = Montant de base × Taux %
Total    = Montant de base + Intérêts
```

Exemple avec 1 000 € de base et 3 % :
`Intérêts = 30 €`, `Total = 1 030 €`.

## Utilisation

Ouvrir `index.html` dans n'importe quel navigateur. Aucune installation requise.
