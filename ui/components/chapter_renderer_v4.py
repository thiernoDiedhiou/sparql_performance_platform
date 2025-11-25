"""
Renderer VRAIMENT fonctionnel pour l'affichage des chapitres
Version 4.0 - Utilise les composants natifs Streamlit pour garantir que TOUT fonctionne

Différence avec v3.0:
- v3.0 utilisait beaucoup de HTML/CSS qui ne s'affichait pas correctement
- v4.0 utilise les composants NATIFS Streamlit (st.expander, st.columns, etc.)
- Toutes les fonctionnalités sont RÉELLEMENT visibles

Auteur: Assistant Claude (Anthropic)
Date: 2025-10-25
Version: 4.0
"""

import streamlit as st
from pathlib import Path
import markdown
import re


class FunctionalChapterRenderer:
    """Renderer 100% fonctionnel utilisant les composants natifs Streamlit."""

    @staticmethod
    def render_chapter(chapter_num, chapter_info, chapters_dir, all_chapters):
        """Affiche un chapitre avec TOUTES les fonctionnalités réellement visibles."""
        chapter_file = chapters_dir / chapter_info['file']

        if not chapter_file.exists():
            st.error(f"❌ Chapitre {chapter_num} introuvable : {chapter_file}")
            return

        try:
            # Lire le contenu
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. HEADER avec gradient (CSS inline fonctionne)
            FunctionalChapterRenderer._render_header(chapter_num, chapter_info)

            # 2. TABLE DES MATIÈRES avec st.expander (natif Streamlit)
            toc = FunctionalChapterRenderer._extract_toc(content)
            if toc:
                FunctionalChapterRenderer._render_toc(toc)

            # 3. CONTENU avec sections
            FunctionalChapterRenderer._render_content(content, chapters_dir)

            # 4. NAVIGATION avec st.columns (natif Streamlit)
            FunctionalChapterRenderer._render_navigation(chapter_num, all_chapters)

            # 5. FOOTER
            FunctionalChapterRenderer._render_footer()

        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du chapitre : {e}")
            import traceback
            st.code(traceback.format_exc())

    @staticmethod
    def _render_header(chapter_num, chapter_info):
        """Header avec gradient - CSS inline fonctionne dans Streamlit."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <h1 style="margin: 0 0 15px 0; font-size: 2.5em;">
                {chapter_info['icon']} Chapitre {chapter_num} : {chapter_info['title']}
            </h1>
            <p style="font-size: 1.2em; opacity: 0.95; margin-bottom: 20px;">
                {chapter_info['description']}
            </p>
            <div style="display: flex; gap: 15px; flex-wrap: wrap; font-size: 0.95em;">
                <span style="background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 15px;">
                    📄 {chapter_info['sections']} sections
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 15px;">
                    📖 ~{chapter_info['pages_estimate']} pages
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 15px;">
                    📅 M2 Génie Logiciel
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def _extract_toc(content):
        """Extrait la table des matières."""
        toc = []
        lines = content.split('\n')

        for line in lines:
            # Chercher les sections Markdown standard (## Titre)
            if line.startswith('## '):
                title = line[3:].strip()
                toc.append(title)
            # Chercher aussi les sections avec numérotation (1. Titre, 1.1. Titre)
            elif re.match(r'^\d+(\.\d+)*\.?\s+\w', line):
                title = line.strip()
                toc.append(title)

        return toc

    @staticmethod
    def _render_toc(toc):
        """Table des matières avec st.expander (natif Streamlit)."""
        with st.expander("📑 **Table des Matières**", expanded=False):
            st.markdown("""
            <style>
            .toc-item {
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
                font-size: 1.05em;
            }
            .toc-item:last-child {
                border-bottom: none;
            }
            </style>
            """, unsafe_allow_html=True)

            for i, item in enumerate(toc, 1):
                st.markdown(f"""
                <div class="toc-item">
                    {i}. {item}
                </div>
                """, unsafe_allow_html=True)

    @staticmethod
    def _render_content(content, chapters_dir):
        """Affiche le contenu avec highlight boxes et styles."""
        # Traiter les images d'abord
        content_parts = FunctionalChapterRenderer._split_content_with_images(content)

        for part in content_parts:
            if part['type'] == 'image':
                # Afficher l'image avec st.image
                FunctionalChapterRenderer._display_image(part, chapters_dir)
            else:
                # Afficher le texte
                FunctionalChapterRenderer._render_section(part['content'], chapters_dir)

    @staticmethod
    def _split_content_with_images(content):
        """Sépare le contenu en sections texte et images."""
        parts = []
        current_text = []
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # Détecter les images markdown: ![alt](path)
            img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)

            if img_match:
                # Sauvegarder le texte accumulé
                if current_text:
                    parts.append({
                        'type': 'text',
                        'content': '\n'.join(current_text)
                    })
                    current_text = []

                # Chercher la légende (ligne précédente souvent)
                caption = ""
                if i > 0 and lines[i-1].startswith('**'):
                    caption = lines[i-1].strip('*').strip()

                # Ajouter l'image
                parts.append({
                    'type': 'image',
                    'alt': img_match.group(1),
                    'path': img_match.group(2),
                    'caption': caption
                })
            else:
                current_text.append(line)

            i += 1

        # Ajouter le reste du texte
        if current_text:
            parts.append({
                'type': 'text',
                'content': '\n'.join(current_text)
            })

        return parts

    @staticmethod
    def _display_image(image_part, chapters_dir):
        """Affiche une image avec st.image."""
        img_path = image_part['path']

        # Construire le chemin complet
        if img_path.startswith('images/'):
            full_path = chapters_dir / img_path
        else:
            full_path = chapters_dir / 'images' / img_path

        caption = image_part.get('caption') or image_part.get('alt', '')

        if full_path.exists():
            st.image(str(full_path), caption=caption, use_container_width=True)
        else:
            st.warning(f"⚠️ Image introuvable : {img_path}")
            st.caption(f"Légende : {caption}")

    @staticmethod
    def _render_section(section_text, chapters_dir):
        """Affiche une section avec les bons styles."""
        if not section_text.strip():
            return

        # Normaliser le format : convertir les titres numérotés en Markdown
        section_text = FunctionalChapterRenderer._normalize_markdown(section_text)

        # Détecter les highlight boxes
        if '**Validation expérimentale' in section_text or '**Validation Expérimentale' in section_text:
            st.success("✅ **Section avec validation expérimentale**")

        if '**Note :' in section_text or '**Note:**' in section_text:
            st.info("ℹ️ Cette section contient des notes importantes")

        if '**Important :' in section_text or '**Important:**' in section_text:
            st.warning("⚠️ Cette section contient des informations importantes")

        # Container avec style pour la section
        with st.container():
            st.markdown("""
            <style>
            .chapter-section {
                background: white;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                max-width: 900px;
                margin-left: auto;
                margin-right: auto;
            }
            .chapter-section h2 {
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 12px;
                padding-top: 20px;
                margin-top: 40px;
                margin-bottom: 25px;
                font-size: 1.8em;
                font-weight: 600;
            }
            .chapter-section h2:first-child {
                margin-top: 0;
            }
            .chapter-section h3 {
                color: #764ba2;
                margin-top: 30px;
                margin-bottom: 18px;
                border-left: 5px solid #764ba2;
                padding-left: 15px;
                padding-top: 5px;
                padding-bottom: 5px;
                background: linear-gradient(to right, rgba(118, 75, 162, 0.05), transparent);
                font-size: 1.4em;
                font-weight: 500;
            }
            .chapter-section h4 {
                color: #667eea;
                margin-top: 25px;
                margin-bottom: 15px;
                font-size: 1.2em;
                font-weight: 500;
            }
            .chapter-section p {
                line-height: 1.8;
                font-size: 1.05em;
                text-align: justify;
                margin-bottom: 18px;
                color: #333;
            }
            .chapter-section ul, .chapter-section ol {
                line-height: 1.9;
                margin: 20px 0;
                padding-left: 30px;
            }
            .chapter-section li {
                margin-bottom: 10px;
            }
            .chapter-section hr {
                border: none;
                border-top: 2px solid #e0e0e0;
                margin: 35px 0;
            }
            .chapter-section table {
                margin: 25px 0;
                border-collapse: collapse;
                width: 100%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }
            .chapter-section table th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px;
                text-align: left;
                font-weight: 600;
            }
            .chapter-section table td {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }
            .chapter-section table tr:last-child td {
                border-bottom: none;
            }
            .chapter-section table tr:hover {
                background-color: #f8f9fa;
            }
            .chapter-section code {
                background-color: #f4f4f4;
                padding: 3px 8px;
                border-radius: 4px;
                color: #e83e8c;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.95em;
            }
            .chapter-section pre {
                background-color: #2d2d2d;
                color: #f8f8f2;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                overflow-x: auto;
                margin: 25px 0;
            }
            .chapter-section pre code {
                background: none;
                color: inherit;
                padding: 0;
            }
            .chapter-section blockquote {
                border-left: 5px solid #667eea;
                padding: 18px 25px;
                background: #f8f9ff;
                margin: 25px 0;
                border-radius: 0 8px 8px 0;
                font-style: italic;
                color: #555;
            }
            .chapter-section strong {
                color: #667eea;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)

            # Convertir Markdown en HTML
            html_content = markdown.markdown(
                section_text,
                extensions=['extra', 'nl2br', 'tables', 'fenced_code', 'codehilite']
            )

            # Afficher avec un cadre
            st.markdown(f'<div class="chapter-section">{html_content}</div>', unsafe_allow_html=True)

    @staticmethod
    def _normalize_markdown(text):
        """Normalise le texte pour un meilleur rendu Markdown."""
        lines = text.split('\n')
        normalized = []

        for i, line in enumerate(lines):
            # Convertir les titres numérotés en titres Markdown avec séparation
            # Format: "1. Titre" ou "1.1. Titre" → "## 1. Titre" ou "### 1.1. Titre"
            if re.match(r'^\d+\.\s+[A-Z]', line):
                # Titre de niveau 2 (1., 2., 3.)
                # Ajouter une ligne vide avant pour la séparation
                if i > 0 and normalized and normalized[-1].strip():
                    normalized.append('')
                    normalized.append('---')  # Séparateur horizontal
                    normalized.append('')
                normalized.append(f"## {line}")
                normalized.append('')  # Ligne vide après le titre
            elif re.match(r'^\d+\.\d+\.?\s+[A-Z]', line):
                # Titre de niveau 3 (1.1., 1.2.)
                if i > 0 and normalized and normalized[-1].strip():
                    normalized.append('')  # Ligne vide avant
                normalized.append(f"### {line}")
                normalized.append('')  # Ligne vide après
            elif re.match(r'^\d+\.\d+\.\d+\.?\s+[A-Z]', line):
                # Titre de niveau 4 (1.1.1.)
                if i > 0 and normalized and normalized[-1].strip():
                    normalized.append('')  # Ligne vide avant
                normalized.append(f"#### {line}")
                normalized.append('')  # Ligne vide après
            else:
                # Ajouter des espaces après les paragraphes pour meilleure lisibilité
                if line.strip() and i < len(lines) - 1:
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    # Si la ligne suivante est un nouveau paragraphe, ajouter un espace
                    if next_line.strip() and not next_line.startswith(('##', '###', '####', '-', '*', '1.', '2.', '3.', '![', '**Figure')):
                        normalized.append(line)
                        # Ajouter espace uniquement si le paragraphe est complet (> 100 chars)
                        if len(line) > 100 and not line.endswith((',', ';', 'et', 'ou', 'des', 'les', 'ces')):
                            normalized.append('')
                    else:
                        normalized.append(line)
                else:
                    normalized.append(line)

        return '\n'.join(normalized)


    @staticmethod
    def _render_navigation(current_chapter, all_chapters):
        """Navigation avec st.columns (natif Streamlit)."""
        st.markdown("<br>", unsafe_allow_html=True)

        # Convertir en int pour calculs
        current_num = int(current_chapter) if isinstance(current_chapter, str) else current_chapter

        # Calculer prev/next
        prev_chapter = str(current_num - 1) if current_num > 1 else None
        next_chapter = str(current_num + 1) if current_num <= len(all_chapters) - 1 else None

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if prev_chapter and prev_chapter in all_chapters:
                if st.button(
                    f"← Chapitre {prev_chapter}",
                    key=f"nav_prev_{current_chapter}",
                    width='stretch',
                    type="secondary"
                ):
                    # Utiliser current_chapter (pas selected_chapter)
                    st.session_state.current_chapter = prev_chapter
                    st.session_state.current_view = 'read'
                    st.rerun()
            else:
                # Bouton désactivé
                st.button("← (Début)", disabled=True, width='stretch')

        with col2:
            # Info centrale
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; color: #666;">
                Chapitre {current_chapter} sur {len(all_chapters)}
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if next_chapter and next_chapter in all_chapters:
                if st.button(
                    f"Chapitre {next_chapter} →",
                    key=f"nav_next_{current_chapter}",
                    width='stretch',
                    type="secondary"
                ):
                    # Utiliser current_chapter (pas selected_chapter)
                    st.session_state.current_chapter = next_chapter
                    st.session_state.current_view = 'read'
                    st.rerun()
            else:
                # Bouton désactivé
                st.button("(Fin) →", disabled=True, width='stretch')

    @staticmethod
    def _render_footer():
        """Footer académique."""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p style="margin: 5px 0;"><strong>Mémoire de Master 2 - Informatique, Option Génie Logiciel</strong></p>
            <p style="margin: 5px 0;">Université Iba Der Thiam de Thiès • Année 2024-2025</p>
            <p style="margin: 15px 0 5px 0; font-size: 0.9em; opacity: 0.8;">
                Généré avec SPARQL Performance Platform v2.0
            </p>
        </div>
        """, unsafe_allow_html=True)


# Fonction helper pour afficher des highlight boxes manuellement
def render_highlight_box(box_type, title, content):
    """
    Affiche une highlight box.

    Args:
        box_type: 'info', 'success', 'warning', 'error'
        title: Titre de la box
        content: Contenu (peut être du markdown)
    """
    if box_type == 'info':
        st.info(f"**{title}**\n\n{content}")
    elif box_type == 'success':
        st.success(f"**{title}**\n\n{content}")
    elif box_type == 'warning':
        st.warning(f"**{title}**\n\n{content}")
    elif box_type == 'error':
        st.error(f"**{title}**\n\n{content}")
