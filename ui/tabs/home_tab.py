"""
Onglet d'accueil - Page principale avec dashboard et onboarding
Architecture professionnelle pour chercheurs et universitaires
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

# Import du design system
from ui.design_system import (
    Colors, Typography, Spacing, Effects,
    create_divider
)


def render_hero_status():
    """
    Section Hero avec statut des endpoints et résumé de la dernière session
    """

    # Statut des endpoints (sans logo central)
    st.markdown(f"""
    <div style="
        text-align: center;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Typography.SIZE_H5};
        font-weight: {Typography.WEIGHT_MEDIUM};
        margin-bottom: {Spacing.LG};
    ">État des Endpoints</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Virtuoso status
    with col1:
        virtuoso_status = st.session_state.get('virtuoso_connected', None)

        if virtuoso_status is True:
            status_color = Colors.SUCCESS
            status_icon = "✓"
            status_text = "Connecté"
        elif virtuoso_status is False:
            status_color = Colors.ERROR
            status_icon = "✗"
            status_text = "Déconnecté"
        else:
            status_color = Colors.GRAY_400
            status_icon = "○"
            status_text = "Non testé"

        st.markdown(f"""
        <div style="
            background: {Colors.BG_CARD};
            border: {Effects.BORDER_THIN} solid {Colors.GRAY_200};
            border-left: {Effects.BORDER_THICK} solid {status_color};
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            box-shadow: {Effects.SHADOW_SM};
            text-align: center;
        ">
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: {Spacing.SM};
            ">Virtuoso</div>
            <div style="
                color: {status_color};
                font-size: {Typography.SIZE_H3};
                font-weight: {Typography.WEIGHT_BOLD};
                margin-bottom: {Spacing.SM};
            ">{status_icon} {status_text}</div>
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-family: monospace;
            ">{st.session_state.get('virtuoso_endpoint', 'localhost:8890/sparql')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Fuseki status
    with col2:
        fuseki_status = st.session_state.get('fuseki_connected', None)

        if fuseki_status is True:
            status_color = Colors.SUCCESS
            status_icon = "✓"
            status_text = "Connecté"
        elif fuseki_status is False:
            status_color = Colors.ERROR
            status_icon = "✗"
            status_text = "Déconnecté"
        else:
            status_color = Colors.GRAY_400
            status_icon = "○"
            status_text = "Non testé"

        st.markdown(f"""
        <div style="
            background: {Colors.BG_CARD};
            border: {Effects.BORDER_THIN} solid {Colors.GRAY_200};
            border-left: {Effects.BORDER_THICK} solid {status_color};
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            box-shadow: {Effects.SHADOW_SM};
            text-align: center;
        ">
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: {Spacing.SM};
            ">Jena Fuseki</div>
            <div style="
                color: {status_color};
                font-size: {Typography.SIZE_H3};
                font-weight: {Typography.WEIGHT_BOLD};
                margin-bottom: {Spacing.SM};
            ">{status_icon} {status_text}</div>
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-family: monospace;
            ">{st.session_state.get('fuseki_endpoint', 'localhost:3030/dataset/query')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Résumé de la dernière session (si disponible)
    results_df = st.session_state.get('results_df', None)
    last_session = st.session_state.get('last_session_timestamp', None)

    if results_df is not None and not results_df.empty:
        # Calculer les métriques
        virtuoso_df = results_df[results_df['engine'] == 'Virtuoso']
        fuseki_df = results_df[results_df['engine'] == 'Jena Fuseki']

        v_avg = virtuoso_df['execution_time'].mean() * 1000 if not virtuoso_df.empty else 0
        f_avg = fuseki_df['execution_time'].mean() * 1000 if not fuseki_df.empty else 0
        num_queries = len(results_df) // 2 if len(results_df) > 0 else 0

        st.markdown(f"""
        <div style="
            background: {Colors.PRIMARY_PALE};
            border: {Effects.BORDER_THIN} solid {Colors.PRIMARY};
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            margin: {Spacing.XL} 0;
        ">
            <div style="
                color: {Colors.PRIMARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: {Spacing.SM};
            ">Dernière Session</div>
            <div style="
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.SIZE_BODY};
                line-height: {Typography.LINE_HEIGHT_RELAXED};
            ">
                <strong>{num_queries}</strong> requêtes •
                Dataset: <strong>{st.session_state.get('dataset_type', 'LUBM')}</strong> •
                Itérations: <strong>{st.session_state.get('num_iterations', 5)}</strong>
                <br>
                <span style="color: {Colors.VIRTUOSO};">▪</span> Virtuoso: <strong>{v_avg:.1f}ms</strong> moyenne •
                <span style="color: {Colors.FUSEKI};">▪</span> Fuseki: <strong>{f_avg:.1f}ms</strong> moyenne
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Boutons d'action principaux
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Lancer un nouveau benchmark", use_container_width=True, type="primary"):
            st.session_state['active_tab'] = 'Configuration & Tests'
            st.rerun()

    with col2:
        if results_df is not None and not results_df.empty:
            if st.button("← Reprendre la dernière session", use_container_width=True, type="secondary"):
                st.session_state['active_tab'] = 'Résultats & Analyses'
                st.rerun()
        else:
            st.button("← Reprendre la dernière session", use_container_width=True, type="secondary", disabled=True)


def render_onboarding_guide():
    """
    Guide de démarrage rapide avec les 4 étapes du workflow
    Réutilise la fonction render_guide() existante
    """
    from main import render_guide

    st.markdown(f"""
    <div style="
        text-align: center;
        margin: {Spacing.XXL} 0 {Spacing.XL} 0;
    ">
        <div style="
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.SIZE_H2};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
        ">Guide de Démarrage Rapide</div>
        <div style="
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.SIZE_BODY};
            margin-top: {Spacing.SM};
        ">Suivez ces 4 étapes pour réaliser votre premier benchmark</div>
    </div>
    """, unsafe_allow_html=True)

    # Appeler le guide existant sans le bouton de retour (on est déjà sur la page d'accueil)
    render_guide(show_back_button=False)


def render_global_stats():
    """
    Statistiques globales de la plateforme (optionnel, si données disponibles)
    """

    # Vérifier si on a des données à afficher
    results_df = st.session_state.get('results_df', None)

    if results_df is None or results_df.empty:
        return  # Ne rien afficher si pas de données

    create_divider()

    st.markdown(f"""
    <div style="
        text-align: center;
        margin: {Spacing.XL} 0 {Spacing.LG} 0;
    ">
        <div style="
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.SIZE_H3};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
        ">Statistiques de la Plateforme</div>
    </div>
    """, unsafe_allow_html=True)

    # Calcul des métriques
    total_tests = len(results_df)
    num_sessions = st.session_state.get('session_count', 1)
    datasets_used = set([st.session_state.get('dataset_type', 'LUBM')])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="
            background: {Colors.BG_CARD};
            border: {Effects.BORDER_THIN} solid {Colors.PRIMARY};
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            text-align: center;
        ">
            <div style="
                color: {Colors.PRIMARY};
                font-size: {Typography.SIZE_H1};
                font-weight: {Typography.WEIGHT_BOLD};
            ">{total_tests}</div>
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-top: {Spacing.SM};
            ">Tests Effectués</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: {Colors.BG_CARD};
            border: {Effects.BORDER_THIN} solid {Colors.SECONDARY};
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            text-align: center;
        ">
            <div style="
                color: {Colors.SECONDARY};
                font-size: {Typography.SIZE_H1};
                font-weight: {Typography.WEIGHT_BOLD};
            ">{num_sessions}</div>
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-top: {Spacing.SM};
            ">Sessions Enregistrées</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
            background: {Colors.BG_CARD};
            border: {Effects.BORDER_THIN} solid {Colors.SUCCESS};
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            text-align: center;
        ">
            <div style="
                color: {Colors.SUCCESS};
                font-size: {Typography.SIZE_H1};
                font-weight: {Typography.WEIGHT_BOLD};
            ">{len(datasets_used)}</div>
            <div style="
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-top: {Spacing.SM};
            ">Datasets Utilisés</div>
        </div>
        """, unsafe_allow_html=True)


def render_resources_footer():
    """
    Footer avec liens vers documentation et ressources
    """

    create_divider()

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: {Spacing.XL} 0;
        background: {Colors.GRAY_50};
        border-radius: {Effects.RADIUS_LG};
        margin-top: {Spacing.XXL};
    ">
        <div style="
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.SIZE_BODY_SMALL};
            font-weight: {Typography.WEIGHT_MEDIUM};
            margin-bottom: {Spacing.MD};
        ">Ressources & Documentation</div>
        <div style="
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.SIZE_BODY_SMALL};
        ">
            <a href="#" style="color: {Colors.PRIMARY}; text-decoration: none; margin: 0 {Spacing.MD};">Documentation</a> •
            <a href="#" style="color: {Colors.PRIMARY}; text-decoration: none; margin: 0 {Spacing.MD};">Guide Utilisateur</a> •
            <a href="#" style="color: {Colors.PRIMARY}; text-decoration: none; margin: 0 {Spacing.MD};">Support</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_home_tab():
    """
    Point d'entrée principal pour l'onglet d'accueil
    """

    # Section 1: Hero + Status
    render_hero_status()

    create_divider()

    # Section 2: Guide de démarrage
    render_onboarding_guide()

    # Section 3: Statistiques (optionnel)
    render_global_stats()

    # Section 4: Footer ressources
    render_resources_footer()


if __name__ == "__main__":
    # Test de la page d'accueil
    render_home_tab()
