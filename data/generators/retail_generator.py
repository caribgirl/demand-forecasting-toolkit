"""
Saskatchewan Retail Demand Data Generator

Generates realistic retail sales data incorporating Saskatchewan-specific patterns:
- Seasonal variations (harsh winters, summer peaks)
- Weather impacts (extreme cold affects foot traffic)
- Local events (Roughriders games, festivals, agricultural cycles)
- Day-of-week patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_saskatchewan_retail_data(
    start_date='2022-01-01',
    periods=730,  # 2 years default
    base_daily_sales=5000,
    seasonal_strength=0.3,
    trend_strength=0.02,
    add_promotions=True,
    add_weather_effect=True,
    add_events=True,
    random_seed=42
):
    """
    Generate realistic retail demand data for Saskatchewan context
    
    Parameters:
    -----------
    start_date : str
        Start date for data generation
    periods : int
        Number of days to generate
    base_daily_sales : float
        Average daily sales baseline
    seasonal_strength : float
        Strength of seasonal pattern (0-1)
    trend_strength : float
        Annual growth rate
    add_promotions : bool
        Include promotional events
    add_weather_effect : bool
        Include weather-based variations
    add_events : bool
        Include local events (Rider games, festivals)
    random_seed : int
        Random seed for reproducibility
        
    Returns:
    --------
    pd.DataFrame with columns:
        - date: Date
        - sales: Daily sales amount
        - temperature: Daily temperature (°C)
        - day_of_week: 0-6 (Monday-Sunday)
        - is_weekend: Boolean
        - is_promotion: Boolean
        - is_event: Boolean
        - month: 1-12
        - season: winter/spring/summer/fall
    """
    
    np.random.seed(random_seed)
    
    # Generate date range
    date_range = pd.date_range(start=start_date, periods=periods, freq='D')
    df = pd.DataFrame({'date': date_range})
    
    # Extract date features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['year'] = df['date'].dt.year
    
    # Saskatchewan seasons (harsher, longer winters)
    def get_season(month):
        if month in [12, 1, 2, 3]:  # Longer winter
            return 'winter'
        elif month in [4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:  # 9, 10, 11
            return 'fall'
    
    df['season'] = df['month'].apply(get_season)
    
    # Base sales (starting point)
    sales = np.ones(periods) * base_daily_sales
    
    # 1. TREND (growth over time)
    years_elapsed = np.arange(periods) / 365.25
    trend = base_daily_sales * (1 + trend_strength) ** years_elapsed
    sales = sales * (trend / base_daily_sales)
    
    # 2. SEASONAL PATTERNS (Saskatchewan-specific)
    # Strong December (holidays), August (back-to-school), Summer events
    seasonal_pattern = (
        1.0 +  # Baseline
        seasonal_strength * 0.4 * np.sin(2 * np.pi * df['day_of_year'] / 365) +  # Annual cycle
        seasonal_strength * 0.3 * (df['month'] == 12).astype(float) +  # Christmas boost
        seasonal_strength * 0.2 * (df['month'] == 8).astype(float) +   # Back to school
        seasonal_strength * 0.15 * (df['month'].isin([6, 7])).astype(float) -  # Summer increase
        seasonal_strength * 0.2 * (df['month'].isin([1, 2])).astype(float)  # Post-holiday drop
    )
    sales = sales * seasonal_pattern
    
    # 3. DAY OF WEEK PATTERNS
    dow_multipliers = {
        0: 0.85,  # Monday (slow)
        1: 0.90,  # Tuesday
        2: 0.95,  # Wednesday
        3: 1.00,  # Thursday
        4: 1.10,  # Friday (payday effect)
        5: 1.20,  # Saturday (peak)
        6: 1.05   # Sunday
    }
    dow_effect = df['day_of_week'].map(dow_multipliers)
    sales = sales * dow_effect
    
    # 4. WEATHER EFFECTS (Saskatchewan-specific: extreme cold impacts)
    if add_weather_effect:
        # Generate realistic Saskatchewan temperatures
        base_temp = 15 * np.sin(2 * np.pi * (df['day_of_year'] - 80) / 365)  # Seasonal baseline
        
        # Saskatchewan extremes: -40°C winter, +35°C summer
        temp_range = np.where(
            df['season'] == 'winter', 25,  # Wider range in winter
            np.where(df['season'] == 'summer', 15, 10)
        )
        df['temperature'] = base_temp + np.random.normal(0, temp_range / 3, periods)
        
        # Extreme cold reduces foot traffic
        weather_effect = np.where(
            df['temperature'] < -25, 0.70,  # Severe cold: -30% sales
            np.where(df['temperature'] < -15, 0.85,  # Very cold: -15% sales
            np.where(df['temperature'] < -5, 0.95,   # Cold: -5% sales
            np.where(df['temperature'] > 30, 0.90,   # Extreme heat: -10% sales
            1.0)))  # Normal
        )
        sales = sales * weather_effect
    else:
        df['temperature'] = 0
    
    # 5. PROMOTIONS (strategic timing)
    df['is_promotion'] = 0
    if add_promotions:
        # Black Friday (last Friday of November)
        black_friday_dates = []
        for year in df['year'].unique():
            november = df[(df['year'] == year) & (df['month'] == 11)]
            fridays = november[november['day_of_week'] == 4]
            if len(fridays) > 0:
                black_friday_dates.append(fridays.iloc[-1]['date'])
        
        # Add promotional periods
        promo_dates = []
        promo_dates.extend(black_friday_dates)  # Black Friday
        
        # Back to school (mid-August)
        for year in df['year'].unique():
            promo_dates.append(pd.Timestamp(f'{year}-08-15'))
        
        # Spring sale (early May)
        for year in df['year'].unique():
            promo_dates.append(pd.Timestamp(f'{year}-05-05'))
        
        # Convert to promotion periods (3-day events)
        for promo_date in promo_dates:
            if promo_date in df['date'].values:
                idx = df[df['date'] == promo_date].index[0]
                df.loc[idx:idx+2, 'is_promotion'] = 1
        
        # Promotions boost sales 30-50%
        promo_boost = 1 + (0.3 + 0.2 * np.random.random(periods)) * df['is_promotion']
        sales = sales * promo_boost
    
    # 6. LOCAL EVENTS (Saskatchewan-specific)
    df['is_event'] = 0
    if add_events:
        # Saskatchewan Roughriders home games (CFL season: June-November)
        # Assume games every 2 weeks on Saturdays
        for year in df['year'].unique():
            game_dates = pd.date_range(
                start=f'{year}-06-15',
                end=f'{year}-11-15',
                freq='14D'  # Every 2 weeks
            )
            for game_date in game_dates:
                if game_date in df['date'].values:
                    idx = df[df['date'] == game_date].index[0]
                    df.loc[idx, 'is_event'] = 1
        
        # Other events: Mosaic Stadium concerts, Exhibition, etc.
        event_dates = [
            ('07-28', 0.15),  # Regina Exhibition
            ('08-01', 0.15),  # Long weekend events
        ]
        
        for year in df['year'].unique():
            for date_str, boost in event_dates:
                event_date = pd.Timestamp(f'{year}-{date_str}')
                if event_date in df['date'].values:
                    idx = df[df['date'] == event_date].index[0]
                    df.loc[idx, 'is_event'] = 1
        
        # Events boost sales 10-20%
        event_boost = 1 + (0.1 + 0.1 * np.random.random(periods)) * df['is_event']
        sales = sales * event_boost
    
    # 7. RANDOM NOISE (real-world variability)
    noise = np.random.normal(1.0, 0.08, periods)  # 8% standard deviation
    sales = sales * noise
    
    # Ensure non-negative sales
    sales = np.maximum(sales, 100)
    
    # Round to realistic values
    df['sales'] = np.round(sales, 2)
    
    # Add derived business metrics
    df['revenue'] = df['sales'] * 1.0  # Assuming sales = revenue for simplicity
    df['units_sold'] = (df['sales'] / 45).round(0).astype(int)  # Avg item price ~$45
    
    # Reorder columns for better readability
    column_order = [
        'date', 'sales', 'revenue', 'units_sold',
        'temperature', 'day_of_week', 'is_weekend',
        'is_promotion', 'is_event', 'month', 'season'
    ]
    
    return df[column_order]


def add_data_quality_issues(df, missing_rate=0.02, outlier_rate=0.01, random_seed=42):
    """
    Add realistic data quality issues for demonstration purposes
    
    Parameters:
    -----------
    df : pd.DataFrame
        Clean generated data
    missing_rate : float
        Proportion of values to set as missing
    outlier_rate : float
        Proportion of outliers to introduce
    random_seed : int
        Random seed
        
    Returns:
    --------
    pd.DataFrame with introduced quality issues
    """
    np.random.seed(random_seed)
    df_dirty = df.copy()
    
    # Introduce missing values
    n_missing = int(len(df) * missing_rate)
    missing_indices = np.random.choice(df.index, n_missing, replace=False)
    df_dirty.loc[missing_indices, 'sales'] = np.nan
    
    # Introduce outliers (data entry errors)
    n_outliers = int(len(df) * outlier_rate)
    outlier_indices = np.random.choice(df.index, n_outliers, replace=False)
    df_dirty.loc[outlier_indices, 'sales'] = df_dirty.loc[outlier_indices, 'sales'] * np.random.choice([0.1, 10, 100], n_outliers)
    
    return df_dirty


if __name__ == "__main__":
    # Generate sample data
    print("Generating Saskatchewan retail demand data...")
    
    # Clean data
    df_clean = generate_saskatchewan_retail_data(
        start_date='2022-01-01',
        periods=730,
        base_daily_sales=5000
    )
    
    # Save clean version
    df_clean.to_csv('../sample_retail_sales.csv', index=False)
    print(f"✅ Clean data saved: {len(df_clean)} days")
    print(f"   Date range: {df_clean['date'].min()} to {df_clean['date'].max()}")
    print(f"   Avg daily sales: ${df_clean['sales'].mean():,.2f}")
    print(f"   Sales range: ${df_clean['sales'].min():,.2f} - ${df_clean['sales'].max():,.2f}")
    
    # Generate version with quality issues for teaching purposes
    df_dirty = add_data_quality_issues(df_clean)
    df_dirty.to_csv('../sample_retail_sales_with_issues.csv', index=False)
    print(f"\n✅ Data with quality issues saved (for teaching data cleaning)")
    
    # Display summary statistics
    print("\n" + "="*60)
    print("DATA SUMMARY")
    print("="*60)
    print(df_clean.describe())
    
    print("\n" + "="*60)
    print("SEASONAL PATTERNS")
    print("="*60)
    print(df_clean.groupby('season')['sales'].agg(['mean', 'std', 'min', 'max']))
    
    print("\n" + "="*60)
    print("DAY OF WEEK PATTERNS")
    print("="*60)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_stats = df_clean.groupby('day_of_week')['sales'].agg(['mean', 'std'])
    dow_stats.index = day_names
    print(dow_stats)
