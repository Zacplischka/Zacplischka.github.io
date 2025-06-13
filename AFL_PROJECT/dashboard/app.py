#!/usr/bin/env python3
"""
AFL Player Stats Dashboard

A Streamlit dashboard for exploring AFL player statistics from the database.
Provides interactive filters and visualizations for data exploration.

Author: AFL Project
Date: June 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add the parent directory to the path to import db_connect
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_scripts.data_processing.db_connect import connect_to_database_raw

# Page configuration
st.set_page_config(
    page_title="AFL Player Stats Dashboard", 
    page_icon="🏈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data_from_db(query):
    """
    Fetch data from the database using the provided SQL query.
    """
    try:
        conn = connect_to_database_raw()
        if conn is None:
            st.error("Could not connect to database")
            return None
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
        
        conn.close()
        return pd.DataFrame(data, columns=columns)
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

@st.cache_data
def load_player_stats():
    """Load player stats with essential columns"""
    query = """
    SELECT 
        player_id,
        player_first_name,
        player_last_name,
        player_team,
        player_position,
        match_date,
        match_round,
        venue_name,
        match_home_team,
        match_away_team,
        goals,
        behinds,
        kicks,
        handballs,
        disposals,
        marks,
        tackles,
        hitouts,
        rebounds,
        inside_fifties,
        clearances,
        clangers,
        free_kicks_for,
        free_kicks_against,
        brownlow_votes,
        contested_possessions,
        uncontested_possessions,
        contested_marks,
        marks_inside_fifty,
        one_percenters,
        bounces,
        goal_assists,
        time_on_ground_percentage,
        afl_fantasy_score,
        supercoach_score,
        metres_gained,
        turnovers,
        intercepts
    FROM player_stats 
    WHERE player_first_name IS NOT NULL 
    AND player_last_name IS NOT NULL
    ORDER BY match_date DESC
    """
    return get_data_from_db(query)

@st.cache_data
def get_teams():
    """Get unique teams"""
    query = "SELECT DISTINCT player_team FROM player_stats WHERE player_team IS NOT NULL ORDER BY player_team"
    result = get_data_from_db(query)
    return result['player_team'].tolist() if result is not None else []

@st.cache_data
def get_seasons():
    """Get unique seasons"""
    query = """
    SELECT DISTINCT EXTRACT(YEAR FROM match_date::date) as season 
    FROM player_stats 
    WHERE match_date IS NOT NULL 
    ORDER BY season DESC
    """
    result = get_data_from_db(query)
    return result['season'].astype(int).tolist() if result is not None else []

def main():
    # Header
    st.markdown('<h1 class="main-header">🏈 AFL Player Stats Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading player statistics..."):
        df = load_player_stats()
    
    if df is None or df.empty:
        st.error("No data available. Please check your database connection.")
        return
    
    # Convert date column
    df['match_date'] = pd.to_datetime(df['match_date'])
    df['season'] = df['match_date'].dt.year
    df['player_name'] = df['player_first_name'] + ' ' + df['player_last_name']
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Team filter
    teams = get_teams()
    selected_teams = st.sidebar.multiselect(
        "Select Teams", 
        options=teams,
        default=teams[:5] if len(teams) > 5 else teams
    )
    
    # Season filter
    seasons = get_seasons()
    if seasons:
        season_range = st.sidebar.slider(
            "Season Range",
            min_value=min(seasons),
            max_value=max(seasons),
            value=(max(seasons)-2, max(seasons))
        )
    else:
        season_range = (2023, 2025)
    
    # Position filter
    positions = df['player_position'].dropna().unique()
    selected_positions = st.sidebar.multiselect(
        "Select Positions",
        options=sorted(positions),
        default=list(positions)
    )
    
    # Apply filters
    filtered_df = df[
        (df['player_team'].isin(selected_teams) if selected_teams else True) &
        (df['season'].between(season_range[0], season_range[1])) &
        (df['player_position'].isin(selected_positions) if selected_positions else True)
    ]
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overview", "🏆 Top Performers", "📈 Team Analysis", "👤 Player Deep Dive", "🎯 Custom Analysis", "🎉 Fun Stats"])
    
    with tab1:
        show_overview(filtered_df)
    
    with tab2:
        show_top_performers(filtered_df)
    
    with tab3:
        show_team_analysis(filtered_df)
    
    with tab4:
        show_player_deep_dive(filtered_df)
    
    with tab5:
        show_custom_analysis(filtered_df)
    
    with tab6:
        show_fun_stats(filtered_df)

def show_overview(df):
    """Show overview statistics"""
    st.header("📊 Dataset Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Games", f"{len(df):,}")
    
    with col2:
        st.metric("Unique Players", f"{df['player_id'].nunique():,}")
    
    with col3:
        st.metric("Teams", f"{df['player_team'].nunique()}")
    
    with col4:
        st.metric("Date Range", f"{df['season'].min()}-{df['season'].max()}")
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Games per season
        season_games = df.groupby('season').size().reset_index(name='games')
        fig = px.bar(season_games, x='season', y='games', 
                    title="Games per Season",
                    color='games',
                    color_continuous_scale='blues')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Games per team
        team_games = df['player_team'].value_counts().head(10).reset_index()
        team_games.columns = ['team', 'games']
        fig = px.bar(team_games, x='team', y='games',
                    title="Top 10 Teams by Games Played",
                    color='games',
                    color_continuous_scale='oranges')
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_top_performers(df):
    """Show top performers across different statistics"""
    st.header("🏆 Top Performers")
    
    # Stat selection
    stat_options = {
        'goals': 'Goals',
        'kicks': 'Kicks', 
        'handballs': 'Handballs',
        'disposals': 'Disposals',
        'marks': 'Marks',
        'tackles': 'Tackles',
        'hitouts': 'Hit Outs',
        'afl_fantasy_score': 'AFL Fantasy Score',
        'supercoach_score': 'SuperCoach Score'
    }
    
    selected_stat = st.selectbox("Select Statistic", options=list(stat_options.keys()), 
                                format_func=lambda x: stat_options[x])
    
    # Aggregate by player
    player_stats = df.groupby(['player_name', 'player_team']).agg({
        selected_stat: ['sum', 'mean', 'max'],
        'match_date': 'count'
    }).round(2)
    
    player_stats.columns = ['Total', 'Average', 'Best', 'Games']
    player_stats = player_stats.reset_index()
    player_stats = player_stats[player_stats['Games'] >= 5]  # Minimum 5 games
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Top 15 by Total {stat_options[selected_stat]}")
        top_total = player_stats.nlargest(15, 'Total')
        
        fig = px.bar(top_total, x='Total', y='player_name',
                    orientation='h',
                    color='Total',
                    color_continuous_scale='viridis',
                    title=f"Total {stat_options[selected_stat]}")
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(top_total[['player_name', 'player_team', 'Total', 'Games']], 
                    use_container_width=True)
    
    with col2:
        st.subheader(f"Top 15 by Average {stat_options[selected_stat]}")
        top_avg = player_stats.nlargest(15, 'Average')
        
        fig = px.bar(top_avg, x='Average', y='player_name',
                    orientation='h',
                    color='Average',
                    color_continuous_scale='plasma',
                    title=f"Average {stat_options[selected_stat]} per Game")
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(top_avg[['player_name', 'player_team', 'Average', 'Games']], 
                    use_container_width=True)

def show_team_analysis(df):
    """Show team-level analysis"""
    st.header("📈 Team Analysis")
    
    # Team performance metrics
    team_stats = df.groupby('player_team').agg({
        'goals': 'mean',
        'disposals': 'mean',
        'marks': 'mean',
        'tackles': 'mean',
        'afl_fantasy_score': 'mean',
        'supercoach_score': 'mean',
        'match_date': 'count'
    }).round(2)
    
    team_stats.columns = ['Avg Goals', 'Avg Disposals', 'Avg Marks', 'Avg Tackles', 
                         'Avg Fantasy', 'Avg SuperCoach', 'Total Games']
    team_stats = team_stats.reset_index()
    
    # Team comparison radar chart
    st.subheader("Team Performance Comparison")
    
    selected_teams_radar = st.multiselect(
        "Select teams for comparison (max 5)",
        options=team_stats['player_team'].tolist(),
        default=team_stats.nlargest(3, 'Total Games')['player_team'].tolist(),
        max_selections=5
    )
    
    if selected_teams_radar:
        radar_data = team_stats[team_stats['player_team'].isin(selected_teams_radar)]
        
        fig = go.Figure()
        
        categories = ['Avg Goals', 'Avg Disposals', 'Avg Marks', 'Avg Tackles', 'Avg Fantasy']
        
        for _, team in radar_data.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[team[cat] for cat in categories],
                theta=categories,
                fill='toself',
                name=team['player_team'],
                line=dict(width=2)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, None])
            ),
            showlegend=True,
            title="Team Performance Radar Chart",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Team stats table
    st.subheader("Team Statistics Summary")
    st.dataframe(team_stats.sort_values('Avg Fantasy', ascending=False), use_container_width=True)

def show_player_deep_dive(df):
    """Show detailed analysis for individual players"""
    st.header("👤 Player Deep Dive")
    
    # Player selection
    players = df.groupby('player_name')['match_date'].count().sort_values(ascending=False)
    selected_player = st.selectbox(
        "Select Player",
        options=players.index.tolist(),
        help="Players with most games are shown first"
    )
    
    if selected_player:
        player_data = df[df['player_name'] == selected_player].copy()
        player_data = player_data.sort_values('match_date')
        
        # Player info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Games", len(player_data))
        
        with col2:
            st.metric("Team(s)", player_data['player_team'].nunique())
        
        with col3:
            st.metric("Position(s)", player_data['player_position'].nunique())
        
        with col4:
            st.metric("Career Span", f"{player_data['season'].min()}-{player_data['season'].max()}")
        
        # Performance over time
        st.subheader(f"{selected_player} - Performance Over Time")
        
        metrics = ['goals', 'disposals', 'marks', 'tackles', 'afl_fantasy_score']
        selected_metrics = st.multiselect(
            "Select metrics to display",
            options=metrics,
            default=['disposals', 'afl_fantasy_score']
        )
        
        if selected_metrics:
            fig = make_subplots(
                rows=len(selected_metrics), cols=1,
                subplot_titles=selected_metrics,
                shared_xaxes=True,
                vertical_spacing=0.05
            )
            
            for i, metric in enumerate(selected_metrics, 1):
                fig.add_trace(
                    go.Scatter(
                        x=player_data['match_date'],
                        y=player_data[metric],
                        mode='lines+markers',
                        name=metric,
                        line=dict(width=2)
                    ),
                    row=i, col=1
                )
            
            fig.update_layout(
                height=150 * len(selected_metrics) + 100,
                title=f"{selected_player} Performance Timeline",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent games table
        st.subheader("Recent Games")
        recent_games = player_data.tail(10)[['match_date', 'player_team', 'match_home_team', 'match_away_team', 
                                           'goals', 'disposals', 'marks', 'tackles', 'afl_fantasy_score']]
        st.dataframe(recent_games, use_container_width=True)

def show_custom_analysis(df):
    """Show custom analysis options"""
    st.header("🎯 Custom Analysis")
    
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Correlation Analysis", "Statistical Distributions", "Performance Trends", "Head-to-Head Comparison"]
    )
    
    if analysis_type == "Correlation Analysis":
        st.subheader("📊 Statistical Correlations")
        
        numeric_cols = ['goals', 'kicks', 'handballs', 'disposals', 'marks', 'tackles', 
                       'hitouts', 'rebounds', 'inside_fifties', 'clearances', 'afl_fantasy_score']
        
        correlation_data = df[numeric_cols].corr()
        
        fig = px.imshow(
            correlation_data,
            title="Correlation Matrix of Player Statistics",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show strongest correlations
        st.subheader("Strongest Correlations")
        corr_pairs = []
        for i in range(len(correlation_data.columns)):
            for j in range(i+1, len(correlation_data.columns)):
                corr_pairs.append({
                    'Stat 1': correlation_data.columns[i],
                    'Stat 2': correlation_data.columns[j],
                    'Correlation': correlation_data.iloc[i, j]
                })
        
        corr_df = pd.DataFrame(corr_pairs)
        corr_df = corr_df.reindex(corr_df['Correlation'].abs().sort_values(ascending=False).index)
        
        st.dataframe(corr_df.head(10), use_container_width=True)
    
    elif analysis_type == "Statistical Distributions":
        st.subheader("📈 Statistical Distributions")
        
        stat_for_dist = st.selectbox(
            "Select statistic",
            ['goals', 'disposals', 'marks', 'tackles', 'afl_fantasy_score']
        )
        
        fig = px.histogram(
            df, 
            x=stat_for_dist,
            nbins=50,
            title=f"Distribution of {stat_for_dist.title()}",
            marginal='box'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        summary_stats = df[stat_for_dist].describe()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean", f"{summary_stats['mean']:.2f}")
        with col2:
            st.metric("Median", f"{summary_stats['50%']:.2f}")
        with col3:
            st.metric("Std Dev", f"{summary_stats['std']:.2f}")
        with col4:
            st.metric("Max", f"{summary_stats['max']:.2f}")

def show_fun_stats(df):
    """Show fun and interesting statistics"""
    st.header("🎉 Fun Stats & Records")
    
    # Goal drought analysis
    st.subheader("🥅 Goal Drought Analysis")
    
    # Calculate consecutive games without goals for each player
    player_droughts = []
    
    for player in df['player_name'].unique():
        player_data = df[df['player_name'] == player].sort_values('match_date')
        
        if len(player_data) < 5:  # Skip players with few games
            continue
            
        current_drought = 0
        max_drought = 0
        games_without_goal = []
        
        for _, game in player_data.iterrows():
            if game['goals'] == 0:
                current_drought += 1
                max_drought = max(max_drought, current_drought)
            else:
                if current_drought > 0:
                    games_without_goal.append(current_drought)
                current_drought = 0
        
        # Add final drought if player ended without scoring
        if current_drought > 0:
            games_without_goal.append(current_drought)
            
        if max_drought > 0:
            player_droughts.append({
                'player_name': player,
                'team': player_data['player_team'].iloc[-1],
                'max_drought': max_drought,
                'current_drought': current_drought,
                'total_games': len(player_data),
                'total_goals': player_data['goals'].sum()
            })
    
    drought_df = pd.DataFrame(player_droughts)
    
    if not drought_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏜️ Longest Goal Droughts (All Time)**")
            top_droughts = drought_df.nlargest(10, 'max_drought')
            
            # Create horizontal bar chart
            fig = px.bar(
                top_droughts, 
                x='max_drought', 
                y='player_name',
                orientation='h',
                color='max_drought',
                color_continuous_scale='reds',
                title="Longest Streaks Without a Goal",
                labels={'max_drought': 'Games Without Goal'}
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            display_cols = ['player_name', 'team', 'max_drought', 'total_goals', 'total_games']
            st.dataframe(
                top_droughts[display_cols].rename(columns={
                    'player_name': 'Player',
                    'team': 'Team', 
                    'max_drought': 'Max Drought',
                    'total_goals': 'Career Goals',
                    'total_games': 'Career Games'
                }), 
                use_container_width=True
            )
        
        with col2:
            st.markdown("**🔥 Currently on Goal Drought**")
            current_droughts = drought_df[drought_df['current_drought'] > 0].nlargest(10, 'current_drought')
            
            if not current_droughts.empty:
                # Create horizontal bar chart for current droughts
                fig = px.bar(
                    current_droughts, 
                    x='current_drought', 
                    y='player_name',
                    orientation='h',
                    color='current_drought',
                    color_continuous_scale='oranges',
                    title="Current Goal Droughts",
                    labels={'current_drought': 'Current Games Without Goal'}
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Display table
                display_cols = ['player_name', 'team', 'current_drought', 'total_goals']
                st.dataframe(
                    current_droughts[display_cols].rename(columns={
                        'player_name': 'Player',
                        'team': 'Team',
                        'current_drought': 'Current Drought',
                        'total_goals': 'Career Goals'
                    }), 
                    use_container_width=True
                )
            else:
                st.info("No players currently on significant goal droughts!")
    
    # Consistency analysis
    st.subheader("🎯 Mr. Reliable - Most Consistent Performers")
    
    # Calculate coefficient of variation (lower = more consistent)
    consistency_stats = []
    
    for player in df['player_name'].unique():
        player_data = df[df['player_name'] == player]
        
        if len(player_data) < 10:  # Need at least 10 games
            continue
            
        # Calculate consistency for key stats
        disposals_cv = player_data['disposals'].std() / player_data['disposals'].mean() if player_data['disposals'].mean() > 0 else float('inf')
        fantasy_cv = player_data['afl_fantasy_score'].std() / player_data['afl_fantasy_score'].mean() if player_data['afl_fantasy_score'].mean() > 0 else float('inf')
        
        consistency_stats.append({
            'player_name': player,
            'team': player_data['player_team'].iloc[-1],
            'games': len(player_data),
            'avg_disposals': player_data['disposals'].mean(),
            'disposals_cv': disposals_cv,
            'avg_fantasy': player_data['afl_fantasy_score'].mean(),
            'fantasy_cv': fantasy_cv,
            'consistency_score': 1 / (disposals_cv + fantasy_cv) if (disposals_cv + fantasy_cv) > 0 else 0
        })
    
    consistency_df = pd.DataFrame(consistency_stats)
    
    if not consistency_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Most Consistent Disposal Winners**")
            top_consistent_disposals = consistency_df[consistency_df['avg_disposals'] >= 15].nsmallest(10, 'disposals_cv')
            
            fig = px.bar(
                top_consistent_disposals,
                x='disposals_cv',
                y='player_name',
                orientation='h',
                color='avg_disposals',
                color_continuous_scale='greens',
                title="Lowest Disposal Variation (Most Consistent)",
                labels={'disposals_cv': 'Coefficient of Variation', 'avg_disposals': 'Avg Disposals'}
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**⭐ Most Consistent Fantasy Scorers**")
            top_consistent_fantasy = consistency_df[consistency_df['avg_fantasy'] >= 60].nsmallest(10, 'fantasy_cv')
            
            fig = px.bar(
                top_consistent_fantasy,
                x='fantasy_cv',
                y='player_name',
                orientation='h',
                color='avg_fantasy',
                color_continuous_scale='purples',
                title="Lowest Fantasy Score Variation",
                labels={'fantasy_cv': 'Coefficient of Variation', 'avg_fantasy': 'Avg Fantasy'}
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Biggest single-game performances
    st.subheader("💥 Record Breaking Performances")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🥅 Most Goals in a Game**")
        top_goal_games = df.nlargest(5, 'goals')[['player_name', 'player_team', 'match_date', 'goals', 'match_home_team', 'match_away_team']]
        
        for _, game in top_goal_games.iterrows():
            st.markdown(f"**{game['goals']} goals** - {game['player_name']} ({game['player_team']})")
            st.caption(f"{game['match_home_team']} vs {game['match_away_team']} - {game['match_date'].strftime('%d/%m/%Y')}")
    
    with col2:
        st.markdown("**🏃 Most Disposals in a Game**")
        top_disposal_games = df.nlargest(5, 'disposals')[['player_name', 'player_team', 'match_date', 'disposals', 'match_home_team', 'match_away_team']]
        
        for _, game in top_disposal_games.iterrows():
            st.markdown(f"**{game['disposals']} disposals** - {game['player_name']} ({game['player_team']})")
            st.caption(f"{game['match_home_team']} vs {game['match_away_team']} - {game['match_date'].strftime('%d/%m/%Y')}")
    
    with col3:
        st.markdown("**⭐ Highest Fantasy Scores**")
        top_fantasy_games = df.nlargest(5, 'afl_fantasy_score')[['player_name', 'player_team', 'match_date', 'afl_fantasy_score', 'match_home_team', 'match_away_team']]
        
        for _, game in top_fantasy_games.iterrows():
            st.markdown(f"**{game['afl_fantasy_score']} points** - {game['player_name']} ({game['player_team']})")
            st.caption(f"{game['match_home_team']} vs {game['match_away_team']} - {game['match_date'].strftime('%d/%m/%Y')}")
    
    # Player verification section for debugging
    with st.expander("🔍 Verify Player Stats (Debug)", expanded=False):
        debug_player = st.selectbox("Check specific player's goal stats:", 
                                   options=sorted(df['player_name'].unique()),
                                   key="debug_player")
        
        if debug_player:
            debug_data = df[df['player_name'] == debug_player].sort_values('match_date')
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Career Goals", debug_data['goals'].sum())
                st.metric("Games Played", len(debug_data))
                st.metric("Goals per Game", f"{debug_data['goals'].mean():.2f}")
            
            with col2:
                goals_by_year = debug_data.groupby('season')['goals'].sum().reset_index()
                st.write("**Goals by Season:**")
                for _, row in goals_by_year.iterrows():
                    st.write(f"{int(row['season'])}: {int(row['goals'])} goals")
            
            # Show goal-scoring games
            goal_games = debug_data[debug_data['goals'] > 0][['match_date', 'goals', 'match_home_team', 'match_away_team']]
            if not goal_games.empty:
                st.write("**Goal-scoring games:**")
                st.dataframe(goal_games, use_container_width=True)
            else:
                st.write("No goals scored in filtered data period")

    # Fun team stats
    st.subheader("🏆 Team Fun Facts")
    
    team_fun_stats = []
    for team in df['player_team'].unique():
        team_data = df[df['player_team'] == team]
        
        # Find team's best single game performance
        best_team_game = team_data.loc[team_data['afl_fantasy_score'].idxmax()]
        
        # Calculate team averages
        team_fun_stats.append({
            'team': team,
            'total_goals': team_data['goals'].sum(),
            'avg_goals_per_game': team_data['goals'].mean(),
            'best_single_performance': best_team_game['afl_fantasy_score'],
            'best_performer': best_team_game['player_name'],
            'most_consistent_scorer': team_data.groupby('player_name')['goals'].mean().idxmax(),
            'highest_avg_goals': team_data.groupby('player_name')['goals'].mean().max()
        })
    
    team_fun_df = pd.DataFrame(team_fun_stats)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🥅 Team Goal Statistics**")
        goal_stats = team_fun_df[['team', 'total_goals', 'avg_goals_per_game']].sort_values('total_goals', ascending=False)
        goal_stats.columns = ['Team', 'Total Goals', 'Avg Goals/Game']
        st.dataframe(goal_stats.head(10), use_container_width=True)
    
    with col2:
        st.markdown("**⭐ Team Record Holders**")
        record_stats = team_fun_df[['team', 'best_single_performance', 'best_performer']].sort_values('best_single_performance', ascending=False)
        record_stats.columns = ['Team', 'Best Fantasy Score', 'Record Holder']
        st.dataframe(record_stats.head(10), use_container_width=True)

if __name__ == "__main__":
    main()
