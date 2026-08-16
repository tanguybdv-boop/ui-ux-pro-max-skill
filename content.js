/* ============================================================
   CONTENU DU SITE — modifie uniquement ce fichier.
   N'importe quel texte entre guillemets " " peut être changé.
   Pour AJOUTER un service, un témoignage, un lien de menu, etc. :
   duplique le bloc { ... } correspondant dans le tableau [ ],
   ajoute une virgule après, et remplis le nouveau bloc.
   Pour SUPPRIMER un élément : supprime son bloc { ... } (et la virgule en trop).
   ============================================================ */

window.SITE_CONTENT = {

  // Informations générales du site
  site: {
    name: "Mon Entreprise",
    logoLetter: "M",              // 1ère lettre affichée dans le logo
    tagline: "Votre activité en une phrase percutante",
  },

  // Menu de navigation (en haut de page)
  nav: [
    { label: "Services", href: "#services" },
    { label: "À propos", href: "#about" },
    { label: "Avis clients", href: "#testimonials" },
    { label: "Contact", href: "#contact" },
  ],

  // Section principale (tout en haut de la page)
  hero: {
    badge: "Nouveau — précise ici une actualité si tu veux",
    title: "Le titre principal qui donne envie de rester",
    titleHighlight: "et qui donne envie d'agir",   // affiché en couleur
    subtitle: "Une ou deux phrases qui expliquent simplement ce que tu proposes et à qui.",
    ctaPrimaryText: "Demander un devis",
    ctaPrimaryHref: "#contact",
    ctaSecondaryText: "En savoir plus",
    ctaSecondaryHref: "#about",
  },

  // Section "À propos"
  about: {
    title: "Qui sommes-nous",
    text: "Présente ici ton activité, ton histoire, ce qui te différencie. Deux à quatre phrases suffisent pour rassurer le visiteur.",
    stats: [
      { number: "10+", label: "années d'expérience" },
      { number: "200+", label: "clients satisfaits" },
      { number: "100%", label: "sur-mesure" },
    ],
  },

  // Section "Services" — ajoute/supprime des blocs pour changer le nombre de cartes
  servicesTitle: "Nos services",
  servicesSubtitle: "Ce que nous proposons",
  services: [
    {
      icon: "⚡",
      title: "Nom du service 1",
      description: "Décris ici en une phrase ce qu'apporte ce service au client.",
    },
    {
      icon: "🎯",
      title: "Nom du service 2",
      description: "Décris ici en une phrase ce qu'apporte ce service au client.",
    },
    {
      icon: "🤝",
      title: "Nom du service 3",
      description: "Décris ici en une phrase ce qu'apporte ce service au client.",
    },
  ],

  // Section "Avis clients" — ajoute/supprime des blocs pour changer le nombre d'avis
  testimonialsTitle: "Ce que disent nos clients",
  testimonials: [
    {
      text: "Un exemple de témoignage client, à remplacer par un vrai retour d'expérience.",
      author: "Prénom Nom",
      role: "Fonction, Entreprise",
    },
    {
      text: "Un deuxième témoignage pour renforcer la confiance des visiteurs.",
      author: "Prénom Nom",
      role: "Fonction, Entreprise",
    },
  ],

  // Section "Contact"
  contact: {
    title: "Parlons de votre projet",
    subtitle: "Une question, un projet ? Contactez-nous, réponse sous 24h.",
    email: "contact@monentreprise.fr",
    phone: "+33 1 23 45 67 89",
    address: "12 rue Exemple, 75000 Paris",
  },

  // Pied de page — liens sociaux (laisse href: "" pour masquer un lien)
  footer: {
    text: "Tous droits réservés.",
    social: [
      { label: "LinkedIn", href: "" },
      { label: "Instagram", href: "" },
      { label: "Facebook", href: "" },
    ],
  },
};
