"""Core logic for Ask360: intent routing, data generation, and handlers."""

import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from typing import Dict, List, Any
from pathlib import Path


# Synthetic data generation
def _generate_facts() -> pd.DataFrame:
    """Generate monthly sales facts for 2023-2024."""
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='MS')
    markets = ['US', 'UK', 'DE', 'IN', 'BR']
    channels = ['retail', 'ecommerce']
    packs = ['single', 'multipack']
    
    rows = []
    np.random.seed(42)  # Reproducible
    
    for date in dates:
        for market in markets:
            for channel in channels:
                for pack in packs:
                    # 2024 baseline, 2023 is 0.8x with noise
                    base = 100000 if market == 'US' else 50000
                    multiplier = 1.0 if date.year == 2024 else 0.8
                    channel_mult = 1.2 if channel == 'ecommerce' else 1.0
                    pack_mult = 1.1 if pack == 'multipack' else 1.0
                    
                    sales_usd = base * multiplier * channel_mult * pack_mult * (1 + np.random.normal(0, 0.1))
                    units = sales_usd / 3.5  # Approx price per unit
                    
                    rows.append({
                        'date': date,
                        'market': market,
                        'channel': channel,
                        'product': 'yogurt',
                        'pack': pack,
                        'sales_usd': max(0, sales_usd),
                        'units': max(0, units)
                    })
    
    return pd.DataFrame(rows)


def _generate_segments() -> pd.DataFrame:
    """Generate segment repeat/trial rates by age bucket and market."""
    markets = ['US', 'UK', 'DE', 'IN', 'BR']
    age_buckets = ['18-34', '35-54', '55+']
    year = 2024
    
    rows = []
    np.random.seed(42)
    
    for market in markets:
        for age in age_buckets:
            # Deterministic but varied rates
            base_trial = 0.15 + hash(f"{market}{age}") % 20 / 100
            base_repeat = 0.35 + hash(f"{market}{age}") % 30 / 100
            rows.append({
                'year': year,
                'market': market,
                'age_bucket': age,
                'trial_rate': min(1.0, base_trial + np.random.normal(0, 0.02)),
                'repeat_rate': min(1.0, base_repeat + np.random.normal(0, 0.03))
            })
    
    return pd.DataFrame(rows)


def _get_occasions() -> List[tuple]:
    """Return consumption occasions with shares."""
    return [
        ("breakfast", 0.45),
        ("post-workout", 0.18),
        ("snack", 0.27),
        ("late-night", 0.10)
    ]


# SQL query generation
def _generate_sql_query(intent: str, metadata: Dict[str, Any]) -> str:
    """
    Generate a SQL-like query string based on intent and metadata.
    
    Returns a string like "SELECT ... FROM ... WHERE ..."
    """
    data_source = metadata.get('data_sources', [])
    time_range = metadata.get('time_range', '')
    regions = metadata.get('regions', [])
    filters = metadata.get('filters', [])
    
    # Determine table name based on intent
    if intent in ['trend', 'growth_markets', 'channel_pack']:
        table = 'sales_facts'
        if intent == 'trend':
            select = 'SELECT date, SUM(sales_usd) as total_sales'
            group_by = 'GROUP BY date'
        elif intent == 'growth_markets':
            select = 'SELECT market, SUM(sales_usd) as total_sales'
            group_by = 'GROUP BY market'
        else:  # channel_pack
            select = 'SELECT channel, pack, SUM(sales_usd) as total_sales'
            group_by = 'GROUP BY channel, pack'
    elif intent == 'segment_repeat':
        table = 'segment_analytics'
        select = 'SELECT age_bucket, AVG(repeat_rate) as avg_repeat_rate'
        group_by = 'GROUP BY age_bucket'
    else:  # occasions
        table = 'consumer_research'
        select = 'SELECT occasion, share'
        group_by = ''
    
    # Build WHERE clause
    where_clauses = []
    
    # Time range filters
    if time_range:
        if '2024' in time_range and '2023' not in time_range:
            where_clauses.append("date >= '2024-01-01' AND date < '2025-01-01'")
        elif '2023' in time_range and '2024' not in time_range:
            where_clauses.append("date >= '2023-01-01' AND date < '2024-01-01'")
        elif 'Last 12 months' in time_range:
            where_clauses.append("date >= DATE_SUB(CURRENT_DATE, INTERVAL 12 MONTH)")
        elif 'YoY' in time_range:
            where_clauses.append("date >= '2023-01-01' AND date < '2025-01-01'")
    
    # Region/market filters
    if regions and 'All markets' not in str(regions[0]):
        market_list = ', '.join([f"'{r}'" for r in regions])
        where_clauses.append(f"market IN ({market_list})")
    
    # Channel filters
    channel_filters = [f for f in filters if 'Channel' in f]
    if channel_filters:
        if 'E-commerce' in channel_filters[0]:
            where_clauses.append("channel = 'ecommerce'")
        elif 'Retail' in channel_filters[0]:
            where_clauses.append("channel = 'retail'")
    
    # Pack filters
    pack_filters = [f for f in filters if 'Pack' in f]
    if pack_filters:
        if 'Multipack' in pack_filters[0]:
            where_clauses.append("pack = 'multipack'")
        elif 'Single' in pack_filters[0]:
            where_clauses.append("pack = 'single'")
    
    # Age filters (for segment_repeat)
    age_filters = [f for f in filters if 'Age' in f]
    if age_filters:
        age_values = [f.split(':')[1].strip() for f in age_filters]
        age_list = ', '.join([f"'{a}'" for a in age_values])
        where_clauses.append(f"age_bucket IN ({age_list})")
    
    # Product filter (always yogurt in this demo)
    if intent in ['trend', 'growth_markets', 'channel_pack']:
        where_clauses.append("product = 'yogurt'")
    
    # Build final query
    query = f"{select}\nFROM {table}"
    if where_clauses:
        query += f"\nWHERE {' AND '.join(where_clauses)}"
    if group_by:
        query += f"\n{group_by}"
    
    if intent == 'growth_markets':
        query += "\nORDER BY total_sales DESC\nLIMIT 3"
    elif intent == 'occasions':
        query += "\nORDER BY share DESC"
    
    return query


# Metadata extraction
def _extract_metadata(question: str, intent: str, handler_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata about data sources, time range, regions, and filters.
    
    Returns a dict with:
    - data_sources: List[str] - Data sources used
    - time_range: str - Time range detected
    - regions: List[str] - Regions/markets filtered
    - filters: List[str] - Other filters applied
    """
    q_lower = question.lower()
    metadata = {
        'data_sources': [],
        'time_range': None,
        'regions': [],
        'filters': []
    }
    
    # Determine data sources based on intent
    if intent in ['trend', 'growth_markets', 'channel_pack']:
        metadata['data_sources'].append('Insights360 - Sales Facts')
    elif intent == 'segment_repeat':
        metadata['data_sources'].append('Insights360 - Segment Analytics')
    elif intent == 'occasions':
        metadata['data_sources'].append('Past Projects - Consumer Research')
    
    # Extract time range from query
    if re.search(r'last\s+12\s+months|12\s+months', q_lower):
        metadata['time_range'] = 'Last 12 months'
    elif re.search(r'2024|twenty\s+twenty\s+four', q_lower):
        metadata['time_range'] = '2024'
    elif re.search(r'2023|twenty\s+twenty\s+three', q_lower):
        metadata['time_range'] = '2023'
    elif re.search(r'last\s+year|yoy|year\s+over\s+year', q_lower):
        metadata['time_range'] = '2023-2024 (YoY)'
    elif re.search(r'year\s+to\s+date|ytd', q_lower):
        metadata['time_range'] = 'Year to date'
    
    # Set default time ranges based on intent if not detected
    if not metadata['time_range']:
        if intent == 'trend':
            metadata['time_range'] = '2024'
        elif intent in ['growth_markets', 'channel_pack']:
            metadata['time_range'] = '2023-2024 (YoY)'
        elif intent == 'segment_repeat':
            metadata['time_range'] = '2024'
        elif intent == 'occasions':
            metadata['time_range'] = 'Current'
    
    # Extract regions/markets from query
    # Use more specific patterns to avoid false positives
    market_patterns = [
        (r'\b(united\s+states|us\b)(?!\w)', 'US'),
        (r'\b(united\s+kingdom|uk\b)(?!\w)', 'UK'),
        (r'\b(germany|de\b)(?!\w)', 'DE'),
        (r'\b(india|in\s+market|in\s+region|india\s+market)(?!\w)', 'IN'),  # Avoid matching "in" as preposition
        (r'\b(brazil|br\b)(?!\w)', 'BR')
    ]
    detected_markets = []
    for pattern, market_code in market_patterns:
        if re.search(pattern, q_lower):
            if market_code not in detected_markets:
                detected_markets.append(market_code)
    
    # If no specific market mentioned, check if handler result shows all markets
    if not detected_markets:
        if intent in ['trend', 'growth_markets', 'channel_pack']:
            metadata['regions'] = ['All markets (US, UK, DE, IN, BR)']
        elif intent == 'segment_repeat':
            metadata['regions'] = ['All markets (US, UK, DE, IN, BR)']
        else:
            metadata['regions'] = ['Global']
    else:
        metadata['regions'] = detected_markets
    
    # Extract filters from query
    if re.search(r'e-?commerce|ecommerce', q_lower):
        metadata['filters'].append('Channel: E-commerce')
    if re.search(r'retail', q_lower):
        metadata['filters'].append('Channel: Retail')
    if re.search(r'multipack|multi\s+pack', q_lower):
        metadata['filters'].append('Pack: Multipack')
    if re.search(r'single\s+pack|single', q_lower):
        metadata['filters'].append('Pack: Single')
    if re.search(r'18-34|18\s+to\s+34', q_lower):
        metadata['filters'].append('Age: 18-34')
    if re.search(r'35-54|35\s+to\s+54', q_lower):
        metadata['filters'].append('Age: 35-54')
    if re.search(r'55\+|55\s+plus', q_lower):
        metadata['filters'].append('Age: 55+')
    
    # Add filters based on handler result
    if intent == 'channel_pack':
        if not any('Channel' in f for f in metadata['filters']):
            metadata['filters'].append('Channel: All (E-commerce, Retail)')
        if not any('Pack' in f for f in metadata['filters']):
            metadata['filters'].append('Pack: All (Single, Multipack)')
    
    return metadata


# Intent routing
def _route_intent(question: str) -> str:
    """Route question to intent using regex patterns."""
    q_lower = question.lower()
    
    if re.search(r'trend|last\s+12\s+months|monthly|how\s+is\s+yogurt\s+doing', q_lower):
        return 'trend'
    elif re.search(r'top\s+3.*growth|which.*growth\s+markets|fastest\s+growing', q_lower):
        return 'growth_markets'
    elif re.search(r'repeat\s+rate|trial\s+vs\s+repeat|18-34|35-54', q_lower):
        return 'segment_repeat'
    elif re.search(r'occasion|consumption\s+occasions|when\s+do\s+people\s+consume', q_lower):
        return 'occasions'
    elif re.search(r'(e-?commerce|retail).*(single|multi|multipack)|channel\s+grew\s+faster', q_lower):
        return 'channel_pack'
    else:
        return 'trend'  # Default


# Handlers
def _handle_trend() -> Dict[str, Any]:
    """Handle trend intent: monthly sales for 2024."""
    facts = _generate_facts()
    facts_2024 = facts[facts['date'].dt.year == 2024].copy()
    monthly = facts_2024.groupby('date')['sales_usd'].sum().reset_index()
    monthly = monthly.sort_values('date')
    
    start_val = monthly.iloc[0]['sales_usd']
    end_val = monthly.iloc[-1]['sales_usd']
    pct_change = ((end_val - start_val) / start_val) * 100
    
    # Generate chart
    chart_path = Path('trend.png')
    plt.figure(figsize=(10, 6))
    plt.plot(monthly['date'], monthly['sales_usd'] / 1e6, marker='o')
    plt.title('Monthly Sales Trend - 2024')
    plt.xlabel('Month')
    plt.ylabel('Sales (Million USD)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return {
        'intent': 'trend',
        'kpis': [
            {'label': 'Start (Jan 2024)', 'value': f'${start_val/1e6:.2f}M'},
            {'label': 'End (Dec 2024)', 'value': f'${end_val/1e6:.2f}M'},
            {'label': 'Change', 'value': f'{pct_change:+.1f}%'}
        ],
        'text': [
            f"Yogurt sales in 2024 started at ${start_val/1e6:.2f}M in January.",
            f"By December, sales reached ${end_val/1e6:.2f}M.",
            f"This represents a {pct_change:+.1f}% change over the year."
        ],
        'table': [
            {
                'date': row['date'].strftime('%Y-%m-%d'),
                'sales_usd': round(row['sales_usd'], 2)
            }
            for _, row in monthly.iterrows()
        ],
        'chart_path': str(chart_path)
    }


def _handle_growth_markets() -> Dict[str, Any]:
    """Handle growth_markets intent: YoY% by market, top 3."""
    facts = _generate_facts()
    
    # Compute YoY by market
    facts_2023 = facts[facts['date'].dt.year == 2023].groupby('market')['sales_usd'].sum()
    facts_2024 = facts[facts['date'].dt.year == 2024].groupby('market')['sales_usd'].sum()
    
    yoy = ((facts_2024 - facts_2023) / facts_2023 * 100).sort_values(ascending=False)
    top3 = yoy.head(3)
    
    table_data = [
        {'market': m, 'yoy_growth_pct': f'{v:.1f}%'} 
        for m, v in top3.items()
    ]
    
    return {
        'intent': 'growth_markets',
        'kpis': [
            {'label': 'Top Market', 'value': f'{top3.index[0]} ({top3.iloc[0]:.1f}%)'},
            {'label': '2nd Market', 'value': f'{top3.index[1]} ({top3.iloc[1]:.1f}%)'},
            {'label': '3rd Market', 'value': f'{top3.index[2]} ({top3.iloc[2]:.1f}%)'}
        ],
        'text': [
            f"The top 3 growth markets for yogurt are:",
            f"1. {top3.index[0]} with {top3.iloc[0]:+.1f}% YoY growth",
            f"2. {top3.index[1]} with {top3.iloc[1]:+.1f}% YoY growth",
            f"3. {top3.index[2]} with {top3.iloc[2]:+.1f}% YoY growth"
        ],
        'table': table_data
    }


def _handle_segment_repeat() -> Dict[str, Any]:
    """Handle segment_repeat intent: repeat_rate by age_bucket."""
    segments = _generate_segments()
    avg_repeat = segments.groupby('age_bucket')['repeat_rate'].mean().sort_values(ascending=False)
    
    highest = avg_repeat.index[0]
    highest_val = avg_repeat.iloc[0]
    
    table_data = [
        {'age_bucket': age, 'avg_repeat_rate': f'{rate:.1%}'}
        for age, rate in avg_repeat.items()
    ]
    
    return {
        'intent': 'segment_repeat',
        'kpis': [
            {'label': 'Highest Repeat Rate', 'value': f'{highest} ({highest_val:.1%})'}
        ],
        'text': [
            f"Average repeat rates by age segment:",
            f"- {avg_repeat.index[0]}: {avg_repeat.iloc[0]:.1%}",
            f"- {avg_repeat.index[1]}: {avg_repeat.iloc[1]:.1%}",
            f"- {avg_repeat.index[2]}: {avg_repeat.iloc[2]:.1%}",
            f"The {highest} segment has the highest repeat rate at {highest_val:.1%}."
        ],
        'table': table_data
    }


def _handle_occasions() -> Dict[str, Any]:
    """Handle occasions intent: list occasions by share."""
    occasions = _get_occasions()
    sorted_occasions = sorted(occasions, key=lambda x: x[1], reverse=True)
    
    table_data = [
        {'occasion': occ, 'share': f'{share:.1%}'}
        for occ, share in sorted_occasions
    ]
    
    return {
        'intent': 'occasions',
        'kpis': [
            {'label': 'Top Occasion', 'value': f'{sorted_occasions[0][0]} ({sorted_occasions[0][1]:.1%})'}
        ],
        'text': [
            "Top consumption occasions for shelf-stable yogurt:",
            f"1. {sorted_occasions[0][0]}: {sorted_occasions[0][1]:.1%}",
            f"2. {sorted_occasions[1][0]}: {sorted_occasions[1][1]:.1%}",
            f"3. {sorted_occasions[2][0]}: {sorted_occasions[2][1]:.1%}",
            f"4. {sorted_occasions[3][0]}: {sorted_occasions[3][1]:.1%}"
        ],
        'table': table_data
    }


def _handle_channel_pack() -> Dict[str, Any]:
    """Handle channel_pack intent: YoY% growth by (channel×pack)."""
    facts = _generate_facts()
    
    # Compute YoY by channel and pack
    facts_2023 = facts[facts['date'].dt.year == 2023].groupby(['channel', 'pack'])['sales_usd'].sum()
    facts_2024 = facts[facts['date'].dt.year == 2024].groupby(['channel', 'pack'])['sales_usd'].sum()
    
    yoy = ((facts_2024 - facts_2023) / facts_2023 * 100).sort_values(ascending=False)
    fastest = yoy.index[0]
    fastest_val = yoy.iloc[0]
    
    table_data = [
        {'channel': ch, 'pack': pk, 'yoy_growth_pct': f'{v:.1f}%'}
        for (ch, pk), v in yoy.items()
    ]
    
    return {
        'intent': 'channel_pack',
        'kpis': [
            {'label': 'Fastest Growing', 'value': f'{fastest[0]}-{fastest[1]} ({fastest_val:.1f}%)'}
        ],
        'text': [
            f"YoY growth by channel and pack:",
            f"- {yoy.index[0][0]} {yoy.index[0][1]}: {yoy.iloc[0]:+.1f}%",
            f"- {yoy.index[1][0]} {yoy.index[1][1]}: {yoy.iloc[1]:+.1f}%",
            f"- {yoy.index[2][0]} {yoy.index[2][1]}: {yoy.iloc[2]:+.1f}%",
            f"- {yoy.index[3][0]} {yoy.index[3][1]}: {yoy.iloc[3]:+.1f}%",
            f"The fastest growing combination is {fastest[0]} {fastest[1]} with {fastest_val:+.1f}% growth."
        ],
        'table': table_data
    }


# Main entry point
def answer(question: str) -> Dict[str, Any]:
    """
    Answer a natural-language question about FreshFoods yogurt.
    
    Returns a dict with:
    - intent: str
    - kpis: List[Dict[str, str]] (optional)
    - text: List[str]
    - table: List[Dict] (optional)
    - chart_path: str (optional)
    - metadata: Dict[str, Any] - Data sources, time range, regions, filters
    """
    intent = _route_intent(question)
    
    handlers = {
        'trend': _handle_trend,
        'growth_markets': _handle_growth_markets,
        'segment_repeat': _handle_segment_repeat,
        'occasions': _handle_occasions,
        'channel_pack': _handle_channel_pack
    }
    
    handler = handlers.get(intent, _handle_trend)
    result = handler()
    
    # Ensure all keys exist
    result.setdefault('kpis', [])
    result.setdefault('table', [])
    result.setdefault('chart_path', None)
    
    # Extract and add metadata
    metadata = _extract_metadata(question, intent, result)
    result['metadata'] = metadata
    
    # Generate SQL query
    sql_query = _generate_sql_query(intent, metadata)
    result['sql_query'] = sql_query
    
    return result

