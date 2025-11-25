"""
Onglet de visualisation des chapitres du mémoire dans l'interface Streamlit.
Permet de naviguer et consulter les chapitres 1, 2, 3 et 4 directement depuis la plateforme.

Auteur: Assistant Claude (Anthropic)
Date: 2025-10-24
Version: 2.0 - Design moderne inspiré du Chapitre 4
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import markdown
import sys

# Ajouter le chemin pour importer le nouveau renderer
sys.path.append(str(Path(__file__).parent.parent))
from components.chapter_renderer_v4 import FunctionalChapterRenderer


class ChaptersViewer:
    """Visualiseur de chapitres du mémoire."""

    CHAPTERS = {
        '1': {
            'title': 'Chapitre 1 : Fondements théoriques et état de l\'art',
            'file': 'CHAPITRE 1.md',
            'icon': '📚',
            'description': 'Web sémantique, RDF, SPARQL, moteurs, benchmarks',
            'sections': 4,
            'pages_estimate': 45
        },
        '2': {
            'title': 'Chapitre 2 : Méthodologie d\'évaluation',
            'file': 'CHAPITRE 2.md',
            'icon': '🔬',
            'description': 'Cadre d\'évaluation, datasets, requêtes, protocole',
            'sections': 4,
            'pages_estimate': 30
        },
        '3': {
            'title': 'Chapitre 3 : Mise en œuvre et expérimentations',
            'file': 'CHAPITRE 3.md',
            'icon': '⚙️',
            'description': 'Implémentation plateforme v2.0, tests, synchronisation',
            'sections': 3,
            'pages_estimate': 18
        },
        '4': {
            'title': 'Chapitre 4 : Analyse et résultats',
            'file': 'CHAPITRE 4.md',
            'icon': '📊',
            'description': 'Résultats expérimentaux, analyses statistiques, recommandations',
            'sections': 5,
            'pages_estimate': 22,
            'status': 'A générer après collecte données'
        }
    }

    def __init__(self):
        """Initialisation du visualiseur."""
        self.base_dir = Path(__file__).parent.parent.parent
        self.chapters_dir = self.base_dir / "chapitres_extraits"

    def render(self):
        """Affiche l'interface de visualisation des chapitres."""
        st.title("📖 Chapitres du mémoire M2")

        st.markdown("""
        <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;'>
            <h4 style='margin: 0; color: #1565c0;'>🎓 Mémoire M2 Informatique - Génie Logiciel</h4>
            <p style='margin: 10px 0 0 0; color: #424242;'>
                <strong>Sujet :</strong> Étude et comparaison de la performance des requêtes SPARQL
                dans des moteurs SPARQL (Virtuoso vs Jena Fuseki)
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Vue d'ensemble des chapitres
        self._show_chapters_overview()

        st.markdown("<br>", unsafe_allow_html=True)

        # Sélection du chapitre
        col1, col2 = st.columns([3, 1])

        with col1:
            selected_chapter = st.selectbox(
                "📑 Sélectionner un chapitre à consulter",
                options=list(self.CHAPTERS.keys()),
                format_func=lambda x: f"{self.CHAPTERS[x]['icon']} {self.CHAPTERS[x]['title']}"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Actualiser", width='stretch'):
                st.rerun()

        chapter_info = self.CHAPTERS[selected_chapter]

        # Carte d'information du chapitre
        self._show_chapter_card(selected_chapter, chapter_info)

        # Boutons d'action
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📖 Lire", key="read_btn", width='stretch'):
                st.session_state.current_chapter = selected_chapter
                st.session_state.current_view = 'read'
                st.rerun()

        with col2:
            if st.button("Statistiques", key="stats_btn", width='stretch'):
                st.session_state.current_chapter = selected_chapter
                st.session_state.current_view = 'stats'
                st.rerun()

        with col3:
            if st.button("📝 Corrections", key="corrections_btn", width='stretch'):
                st.session_state.current_chapter = selected_chapter
                st.session_state.current_view = 'corrections'
                st.rerun()

        with col4:
            if st.button("📥 Télécharger", key="download_btn", width='stretch'):
                st.session_state.current_chapter = selected_chapter
                st.session_state.current_view = 'download'
                st.rerun()

        # Zone de contenu
        st.markdown("<br>", unsafe_allow_html=True)

        if 'current_chapter' in st.session_state and 'current_view' in st.session_state:
            view = st.session_state.current_view
            chapter = st.session_state.current_chapter

            if view == 'read':
                self._render_chapter_content(chapter)
            elif view == 'stats':
                self._show_statistics(chapter)
            elif view == 'corrections':
                self._show_corrections(chapter)
            elif view == 'download':
                self._show_download_options(chapter)

    def _show_chapters_overview(self):
        """Affiche vue d'ensemble des chapitres."""
        st.subheader("📚 Vue d'ensemble des chapitres")

        cols = st.columns(4)

        for idx, (num, info) in enumerate(self.CHAPTERS.items()):
            with cols[idx]:
                status = info.get('status', 'Disponible')
                status_color = '#4caf50' if status == 'Disponible' else '#ff9800'
                status_icon = '✅' if status == 'Disponible' else '⏳'

                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    color: white;
                    min-height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                '>
                    <div style='font-size: 3em; margin-bottom: 10px;'>{info['icon']}</div>
                    <div style='font-weight: bold; font-size: 1.2em; margin-bottom: 10px;'>
                        Chapitre {num}
                    </div>
                    <div style='font-size: 0.9em; margin-bottom: 15px; line-height: 1.4;'>
                        {info['description']}
                    </div>
                    <div style='background-color: rgba(255,255,255,0.2); padding: 8px; border-radius: 5px;'>
                        {status_icon} {status}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    def _show_chapter_card(self, chapter_num, info):
        """Affiche carte d'information du chapitre."""
        st.markdown(f"""
        <div style='
            background-color: #f8f9fa;
            border-left: 5px solid #1f77b4;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        '>
            <h3 style='margin: 0 0 15px 0; color: #1f77b4;'>
                {info['icon']} {info['title']}
            </h3>
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 15px;'>
                <div>
                    <strong>📑 Sections principales :</strong> {info['sections']}
                </div>
                <div>
                    <strong>📄 Pages estimées :</strong> ~{info['pages_estimate']}
                </div>
                <div>
                    <strong>📅 Dernière mise à jour :</strong> 2025-10-24
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_chapter_content(self, chapter_num):
        """Affiche le contenu du chapitre avec design 100% fonctionnel (v4.0)."""
        chapter_info = self.CHAPTERS[chapter_num]

        # Utiliser le renderer v4 avec composants natifs Streamlit
        FunctionalChapterRenderer.render_chapter(
            chapter_num,
            chapter_info,
            self.chapters_dir,
            self.CHAPTERS  # Passer tous les chapitres pour la navigation
        )

        # Bouton retour
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Revenir à la sélection", width='stretch', type="primary"):
                st.session_state.current_view = None
                st.rerun()

        return  # Fin de la méthode

    def _render_chapter_content_OLD(self, chapter_num):
        """ANCIENNE VERSION - Affiche le contenu du chapitre avec design professionnel."""
        chapter_info = self.CHAPTERS[chapter_num]
        chapter_path = self.chapters_dir / chapter_info['file']

        # En-tête stylisé
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        '>
            <h1 style='margin: 0; font-size: 2.2em; font-weight: 700;'>
                {chapter_info['icon']} {chapter_info['title']}
            </h1>
            <p style='margin: 15px 0 0 0; font-size: 1.1em; opacity: 0.9;'>
                {chapter_info['description']}
            </p>
            <div style='margin-top: 20px; display: flex; gap: 20px; flex-wrap: wrap;'>
                <span style='background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px; font-size: 0.9em;'>
                    📄 ~{chapter_info['pages_estimate']} pages
                </span>
                <span style='background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px; font-size: 0.9em;'>
                    📑 {chapter_info['sections']} sections principales
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not chapter_path.exists():
            st.warning(f"""
            ⚠️ Le chapitre {chapter_num} n'est pas encore disponible dans le répertoire
            `chapitres_extraits/`.

            **Actions possibles :**
            - Vérifiez que les fichiers ont été extraits depuis les documents Word
            - Consultez le document `INTEGRATION_CHAPITRES_1_2_3.md` pour les instructions
            """)

            if chapter_num == '4':
                st.info("""
                **Chapitre 4 - Statut spécial**

                Le Chapitre 4 sera généré automatiquement après la collecte des données réelles.
                Consultez le fichier `PLAN_FINALISATION_MEMOIRE.md` pour plus d'informations.
                """)
            return

        # Lecture du contenu
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Style CSS personnalisé pour le contenu
            st.markdown("""
            <style>
            .chapter-content {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                max-width: 900px;
                margin: 0 auto;
                font-family: 'Georgia', 'Times New Roman', serif;
                line-height: 1.8;
                color: #2c3e50;
            }

            .chapter-content h1 {
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 15px;
                margin-top: 40px;
                margin-bottom: 25px;
                font-size: 2.2em;
                font-weight: 700;
            }

            .chapter-content h2 {
                color: #764ba2;
                margin-top: 35px;
                margin-bottom: 20px;
                font-size: 1.8em;
                font-weight: 600;
                border-left: 5px solid #764ba2;
                padding-left: 15px;
            }

            .chapter-content h3 {
                color: #5a67d8;
                margin-top: 25px;
                margin-bottom: 15px;
                font-size: 1.4em;
                font-weight: 500;
            }

            .chapter-content p {
                margin-bottom: 18px;
                text-align: justify;
                font-size: 1.05em;
            }

            .chapter-content ul, .chapter-content ol {
                margin: 20px 0;
                padding-left: 30px;
            }

            .chapter-content li {
                margin-bottom: 10px;
                line-height: 1.7;
            }

            .chapter-content code {
                background-color: #f7f7f9;
                padding: 3px 8px;
                border-radius: 4px;
                color: #e83e8c;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.9em;
            }

            .chapter-content pre {
                background-color: #282c34;
                color: #abb2bf;
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 25px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .chapter-content pre code {
                background: none;
                color: inherit;
                padding: 0;
            }

            .chapter-content table {
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border-radius: 8px;
                overflow: hidden;
            }

            .chapter-content th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                font-size: 1em;
            }

            .chapter-content td {
                padding: 12px 15px;
                border-bottom: 1px solid #e1e8ed;
            }

            .chapter-content tr:hover {
                background-color: #f8f9fa;
            }

            .chapter-content blockquote {
                border-left: 5px solid #667eea;
                margin: 25px 0;
                padding: 15px 20px;
                background-color: #f8f9fa;
                border-radius: 0 8px 8px 0;
                font-style: italic;
                color: #5a67d8;
            }

            .chapter-content a {
                color: #667eea;
                text-decoration: none;
                border-bottom: 1px dotted #667eea;
                transition: all 0.3s ease;
            }

            .chapter-content a:hover {
                color: #764ba2;
                border-bottom-color: #764ba2;
            }

            .chapter-content img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                margin: 25px auto;
                display: block;
            }

            /* Table des matières */
            .toc {
                background: #f8f9fa;
                border-left: 5px solid #667eea;
                padding: 20px 25px;
                margin: 30px 0;
                border-radius: 0 8px 8px 0;
            }

            .toc h4 {
                margin-top: 0;
                color: #667eea;
                font-size: 1.3em;
            }

            /* Sections numérotées */
            .section-number {
                color: #667eea;
                font-weight: 700;
                margin-right: 10px;
            }
            </style>
            """, unsafe_allow_html=True)

            # Contenu formaté dans un conteneur stylisé
            st.markdown('<div class="chapter-content">', unsafe_allow_html=True)

            # Traiter le contenu avec images
            import re
            images_dir = self.chapters_dir / "images"

            # Découper le contenu en sections texte et images
            parts = re.split(r'(!\[[^\]]*\]\([^\)]+\))', content)

            for part in parts:
                # Vérifier si c'est une image
                img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', part)

                if img_match:
                    alt_text = img_match.group(1)
                    img_path = img_match.group(2)

                    if img_path.startswith('images/'):
                        full_path = images_dir / img_path.replace('images/', '')
                        if full_path.exists():
                            # Afficher l'image avec st.image
                            st.markdown('</div>', unsafe_allow_html=True)  # Fermer div temporairement
                            st.image(str(full_path), caption=alt_text, use_container_width=True)
                            st.markdown('<div class="chapter-content">', unsafe_allow_html=True)  # Réouvrir
                        else:
                            st.warning(f"Image introuvable : {img_path}")
                    else:
                        # Image externe ou autre
                        html = markdown.markdown(part)
                        st.markdown(html, unsafe_allow_html=True)
                else:
                    # C'est du texte normal
                    if part.strip():
                        html = markdown.markdown(
                            part,
                            extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
                        )
                        st.markdown(html, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Bouton de navigation stylisé
            st.markdown("<br><br>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                if st.button("Revenir en haut", width='stretch', type="primary"):
                    st.session_state.current_view = None
                    st.rerun()

        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
            st.info("Vérifiez que le module 'markdown' est installé : `pip install markdown`")

    def _show_statistics(self, chapter_num):
        """Affiche statistiques du chapitre."""
        chapter_info = self.CHAPTERS[chapter_num]
        chapter_path = self.chapters_dir / chapter_info['file']

        st.markdown(f"## Statistiques : {chapter_info['title']}")

        if not chapter_path.exists():
            st.warning(f"Chapitre {chapter_num} non disponible.")
            return

        try:
            # Lecture et analyse
            with open(chapter_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Calcul des statistiques
            stats = {
                'caracteres': len(content),
                'mots': len(content.split()),
                'lignes': content.count('\n'),
                'paragraphes': content.count('\n\n'),
                'titres_h1': content.count('\n# '),
                'titres_h2': content.count('\n## '),
                'titres_h3': content.count('\n### '),
                'blocs_code': content.count('```') // 2,
                'tableaux': content.count('|---'),
                'listes': content.count('\n- ') + content.count('\n* '),
                'liens': content.count('[') and content.count(']('),
                'images': content.count('!['),
            }

            # Estimations
            pages_estimate = stats['mots'] // 250
            temps_lecture = stats['mots'] // 200  # 200 mots/minute

            # Affichage en colonnes
            st.subheader("Métriques générales")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📝 Mots", f"{stats['mots']:,}")
                st.metric("📄 Caractères", f"{stats['caracteres']:,}")

            with col2:
                st.metric("📑 Lignes", f"{stats['lignes']:,}")
                st.metric("¶ Paragraphes", f"{stats['paragraphes']:,}")

            with col3:
                st.metric("📖 Pages estimées", f"~{pages_estimate}")
                st.metric("Temps lecture", f"~{temps_lecture} min")

            with col4:
                st.metric("Tableaux", stats['tableaux'])
                st.metric("Blocs de code", stats['blocs_code'])

            # Structure du document
            st.subheader("Structure du document")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Hiérarchie des titres**")
                st.markdown(f"- Titres H1 : **{stats['titres_h1']}**")
                st.markdown(f"- Titres H2 : **{stats['titres_h2']}**")
                st.markdown(f"- Titres H3 : **{stats['titres_h3']}**")

            with col2:
                st.markdown("**Éléments visuels**")
                st.markdown(f"- Listes : **{stats['listes']}**")
                st.markdown(f"- Liens : **{stats['liens']}**")
                st.markdown(f"- Images : **{stats['images']}**")

            # Graphique de distribution
            import plotly.graph_objects as go

            fig = go.Figure(data=[
                go.Bar(
                    x=['H1', 'H2', 'H3', 'Code', 'Tables', 'Listes'],
                    y=[
                        stats['titres_h1'],
                        stats['titres_h2'],
                        stats['titres_h3'],
                        stats['blocs_code'],
                        stats['tableaux'],
                        stats['listes']
                    ],
                    marker_color='#1f77b4'
                )
            ])

            fig.update_layout(
                title="Distribution des éléments structurels",
                xaxis_title="Type d'élément",
                yaxis_title="Nombre",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")

    def _show_corrections(self, chapter_num):
        """Éditeur interactif pour visualiser et modifier les chapitres."""
        st.markdown(f"## Éditeur de Chapitre {chapter_num}")

        st.info("""
        **Mode Éditeur** : Visualisez et modifiez directement le contenu du chapitre.
        Les modifications sont sauvegardées automatiquement dans le fichier Markdown.
        """)

        # Charger le contenu actuel du chapitre
        chapter_info = self.CHAPTERS.get(chapter_num)
        if not chapter_info:
            st.error(f"Chapitre {chapter_num} non trouvé.")
            return

        chapter_file = self.chapters_dir / chapter_info['file']

        if not chapter_file.exists():
            st.error(f"Fichier {chapter_info['file']} introuvable dans {self.chapters_dir}")
            return

        try:
            # Lire le contenu actuel
            with open(chapter_file, 'r', encoding='utf-8') as f:
                current_content = f.read()

            # Statistiques du chapitre
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Lignes", len(current_content.splitlines()))
            with col2:
                st.metric("Mots", len(current_content.split()))
            with col3:
                st.metric("Caractères", len(current_content))
            with col4:
                pages_est = len(current_content.split()) // 250
                st.metric("Pages estimées", pages_est)

            st.divider()

            # Tabs pour éditeur et aperçu
            edit_tab, preview_tab = st.tabs(["Édition", "Aperçu"])

            with edit_tab:
                st.markdown("### Mode Édition")

                # Zone de texte pour éditer le contenu
                edited_content = st.text_area(
                    "Contenu du chapitre (Markdown)",
                    value=current_content,
                    height=600,
                    key=f"editor_{chapter_num}",
                    help="Modifiez le contenu en Markdown. Les modifications seront sauvegardées en cliquant sur 'Enregistrer'."
                )

                # Boutons d'action
                col_save, col_reset, col_export = st.columns([1, 1, 2])

                with col_save:
                    if st.button("💾 Enregistrer", type="primary", width='stretch'):
                        try:
                            # Sauvegarder les modifications
                            with open(chapter_file, 'w', encoding='utf-8') as f:
                                f.write(edited_content)

                            st.success(f"✅ Chapitre {chapter_num} sauvegardé avec succès !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur lors de la sauvegarde : {str(e)}")

                with col_reset:
                    if st.button("Annuler", width='stretch'):
                        st.info("Rechargement de la version sauvegardée...")
                        st.rerun()

                with col_export:
                    # Export en fichier
                    st.download_button(
                        label="📥 Télécharger .md",
                        data=edited_content,
                        file_name=f"CHAPITRE_{chapter_num}_modifie.md",
                        mime="text/markdown",
                        width='stretch'
                    )

                # Afficher les différences si modifié
                if edited_content != current_content:
                    st.warning(f"⚠️ **{abs(len(edited_content) - len(current_content))} caractères** modifiés (non sauvegardés)")

                    # Statistiques des modifications
                    words_diff = len(edited_content.split()) - len(current_content.split())
                    if words_diff > 0:
                        st.info(f"➕ {words_diff} mots ajoutés")
                    elif words_diff < 0:
                        st.info(f"➖ {abs(words_diff)} mots supprimés")

            with preview_tab:
                st.markdown("### Aperçu du rendu")

                # Afficher l'aperçu HTML
                try:
                    html_content = markdown.markdown(
                        edited_content,
                        extensions=['extra', 'codehilite', 'tables', 'toc', 'fenced_code']
                    )

                    # Style CSS pour l'aperçu
                    st.markdown("""
                    <style>
                        .preview-content {
                            font-family: 'Georgia', serif;
                            line-height: 1.6;
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                            background: white;
                            border-radius: 8px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }
                        .preview-content h1 { color: #1f3a93; margin-top: 1.5em; }
                        .preview-content h2 { color: #2e5cb8; margin-top: 1.3em; }
                        .preview-content h3 { color: #4a76c9; margin-top: 1.1em; }
                        .preview-content code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
                        .preview-content pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
                        .preview-content table { border-collapse: collapse; width: 100%; margin: 1em 0; }
                        .preview-content table th, .preview-content table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        .preview-content table th { background: #f2f2f2; font-weight: bold; }
                    </style>
                    """, unsafe_allow_html=True)

                    st.markdown(f'<div class="preview-content">{html_content}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Erreur lors de la génération de l'aperçu : {str(e)}")
                    st.code(edited_content, language='markdown')

        except Exception as e:
            st.error(f"Erreur lors du chargement du chapitre : {str(e)}")

    def _show_download_options(self, chapter_num):
        """Affiche options de téléchargement."""
        st.markdown(f"## 📥 Téléchargement - Chapitre {chapter_num}")

        chapter_info = self.CHAPTERS[chapter_num]
        chapter_path = self.chapters_dir / chapter_info['file']

        if not chapter_path.exists():
            st.warning(f"Chapitre {chapter_num} non disponible pour téléchargement.")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📄 Markdown")
            st.markdown("Format source éditable")

            try:
                with open(chapter_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

                st.download_button(
                    label="Télécharger MD",
                    data=markdown_content,
                    file_name=f"chapitre_{chapter_num}.md",
                    mime="text/markdown",
                    width='stretch'
                )
            except Exception as e:
                st.error(f"Erreur : {e}")

        with col2:
            st.markdown("### 📝 Texte brut")
            st.markdown("Format texte simple")

            st.download_button(
                label="Télécharger TXT",
                data="Fonctionnalité à venir...",
                file_name=f"chapitre_{chapter_num}.txt",
                mime="text/plain",
                width='stretch',
                disabled=True
            )

        with col3:
            st.markdown("### 📕 PDF")
            st.markdown("Format imprimable")

            st.download_button(
                label="Télécharger PDF",
                data="Fonctionnalité à venir...",
                file_name=f"chapitre_{chapter_num}.pdf",
                mime="application/pdf",
                width='stretch',
                disabled=True
            )

        st.info("""
        **Note** : La conversion PDF sera implémentée prochainement.
        En attendant, utilisez le format Markdown et convertissez avec Pandoc :

        ```bash
        pandoc chapitre_1.md -o chapitre_1.pdf --pdf-engine=xelatex
        ```
        """)


def show_chapters_tab():
    """Point d'entrée pour l'onglet chapitres."""
    viewer = ChaptersViewer()
    viewer.render()
