"""
Baseline Forecasting Models

Simple, interpretable forecasting methods that often perform surprisingly well.
These should always be your starting point before moving to complex models.

Models included:
1. Naive Forecast (last value)
2. Seasonal Naive (same day last week/year)
3. Moving Average (7-day, 30-day)
4. Exponential Smoothing
5. Day-of-Week Average
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


class NaiveForecast:
    """
    Simplest possible forecast: tomorrow will be like today
    
    Surprisingly effective baseline for comparison.
    """
    
    def __init__(self):
        self.last_value = None
        self.name = "Naive (Last Value)"
    
    def fit(self, data: pd.Series):
        """Store the last observed value"""
        self.last_value = data.iloc[-1]
        return self
    
    def predict(self, horizon: int) -> np.ndarray:
        """Return last value repeated"""
        return np.array([self.last_value] * horizon)
    
    def __repr__(self):
        return f"NaiveForecast(last_value={self.last_value:.2f})"


class SeasonalNaiveForecast:
    """
    Use the same day from last week/month/year as the forecast
    
    Effective when strong seasonal patterns exist.
    Example: Next Monday's sales = Last Monday's sales
    """
    
    def __init__(self, season_length: int = 7):
        """
        Parameters:
        -----------
        season_length : int
            7 for weekly seasonality (default)
            30 for monthly
            365 for yearly
        """
        self.season_length = season_length
        self.seasonal_values = None
        self.name = f"Seasonal Naive (period={season_length})"
    
    def fit(self, data: pd.Series):
        """Store the last complete season"""
        self.seasonal_values = data.iloc[-self.season_length:].values
        return self
    
    def predict(self, horizon: int) -> np.ndarray:
        """Repeat the seasonal pattern"""
        # Repeat the pattern as many times as needed
        n_repeats = int(np.ceil(horizon / self.season_length))
        forecast = np.tile(self.seasonal_values, n_repeats)
        return forecast[:horizon]
    
    def __repr__(self):
        return f"SeasonalNaiveForecast(season_length={self.season_length})"


class MovingAverageForecast:
    """
    Average of the last N values
    
    Smooths out short-term fluctuations, good for stable demand.
    """
    
    def __init__(self, window: int = 7):
        """
        Parameters:
        -----------
        window : int
            Number of periods to average (default 7 days)
        """
        self.window = window
        self.moving_avg = None
        self.name = f"Moving Average ({window}-day)"
    
    def fit(self, data: pd.Series):
        """Calculate moving average from recent data"""
        self.moving_avg = data.iloc[-self.window:].mean()
        return self
    
    def predict(self, horizon: int) -> np.ndarray:
        """Return constant forecast"""
        return np.array([self.moving_avg] * horizon)
    
    def __repr__(self):
        return f"MovingAverageForecast(window={self.window}, avg={self.moving_avg:.2f})"


class ExponentialSmoothingForecast:
    """
    Weighted average giving more weight to recent observations
    
    Good for data with trend but no seasonality.
    Alpha controls how much weight to give recent vs. historical data.
    """
    
    def __init__(self, alpha: float = 0.3):
        """
        Parameters:
        -----------
        alpha : float
            Smoothing parameter (0-1)
            Higher = more weight to recent observations
        """
        if not 0 < alpha < 1:
            raise ValueError("Alpha must be between 0 and 1")
        
        self.alpha = alpha
        self.level = None
        self.name = f"Exponential Smoothing (α={alpha})"
    
    def fit(self, data: pd.Series):
        """Calculate the smoothed level"""
        # Simple exponential smoothing
        values = data.values
        self.level = values[0]
        
        for value in values[1:]:
            self.level = self.alpha * value + (1 - self.alpha) * self.level
        
        return self
    
    def predict(self, horizon: int) -> np.ndarray:
        """Return constant forecast at current level"""
        return np.array([self.level] * horizon)
    
    def __repr__(self):
        return f"ExponentialSmoothingForecast(alpha={self.alpha}, level={self.level:.2f})"


class DayOfWeekForecast:
    """
    Use average for each day of the week
    
    Effective when day-of-week patterns are strong (retail, restaurants)
    Example: Saturdays average $5,000, so forecast $5,000 for next Saturday
    """
    
    def __init__(self, apply_trend: bool = False):
        """
        Parameters:
        -----------
        apply_trend : bool
            If True, adjust forecasts by recent trend
        """
        self.dow_averages = None
        self.trend_factor = 1.0
        self.apply_trend = apply_trend
        self.name = "Day-of-Week Average" + (" + Trend" if apply_trend else "")
    
    def fit(self, data: pd.DataFrame):
        """
        Calculate average for each day of week
        
        Parameters:
        -----------
        data : pd.DataFrame
            Must have 'sales' and 'day_of_week' columns
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("DayOfWeekForecast requires DataFrame with 'day_of_week' column")
        
        # Calculate day-of-week averages
        self.dow_averages = data.groupby('day_of_week')['sales'].mean().to_dict()
        
        # Calculate trend if requested
        if self.apply_trend:
            # Compare last 30 days to previous 30 days
            recent_avg = data['sales'].tail(30).mean()
            prev_avg = data['sales'].tail(60).head(30).mean()
            self.trend_factor = recent_avg / prev_avg if prev_avg > 0 else 1.0
        
        return self
    
    def predict(self, start_date: pd.Timestamp, horizon: int) -> np.ndarray:
        """
        Generate forecast for specified dates
        
        Parameters:
        -----------
        start_date : pd.Timestamp
            First date to forecast
        horizon : int
            Number of days to forecast
        """
        forecast_dates = pd.date_range(start=start_date, periods=horizon, freq='D')
        forecasts = []
        
        for date in forecast_dates:
            dow = date.dayofweek
            base_forecast = self.dow_averages[dow]
            forecast = base_forecast * self.trend_factor
            forecasts.append(forecast)
        
        return np.array(forecasts)
    
    def __repr__(self):
        return f"DayOfWeekForecast(apply_trend={self.apply_trend})"


class EnsembleBaseline:
    """
    Combine multiple baseline methods
    
    Often performs better than any single method.
    Simple average or weighted average of predictions.
    """
    
    def __init__(self, models: list = None, weights: list = None):
        """
        Parameters:
        -----------
        models : list
            List of fitted forecast models
        weights : list
            Optional weights for each model (default: equal weights)
        """
        self.models = models or []
        self.weights = weights
        self.name = "Ensemble Baseline"
        
        if self.weights is not None:
            if len(self.weights) != len(self.models):
                raise ValueError("Number of weights must match number of models")
            if not np.isclose(sum(self.weights), 1.0):
                raise ValueError("Weights must sum to 1.0")
    
    def add_model(self, model):
        """Add a model to the ensemble"""
        self.models.append(model)
        return self
    
    def predict(self, horizon: int, **kwargs) -> np.ndarray:
        """
        Generate ensemble forecast
        
        Takes average (or weighted average) of all model predictions
        """
        if not self.models:
            raise ValueError("No models in ensemble")
        
        predictions = []
        for model in self.models:
            # Handle different predict signatures
            if isinstance(model, DayOfWeekForecast) and 'start_date' in kwargs:
                pred = model.predict(kwargs['start_date'], horizon)
            else:
                pred = model.predict(horizon)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Apply weights if provided
        if self.weights is not None:
            weights = np.array(self.weights).reshape(-1, 1)
            forecast = np.sum(predictions * weights, axis=0)
        else:
            # Equal weights
            forecast = np.mean(predictions, axis=0)
        
        return forecast
    
    def __repr__(self):
        model_names = [m.name for m in self.models]
        return f"EnsembleBaseline(models={model_names})"


def evaluate_forecast(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics
    
    Returns:
    --------
    dict with metrics:
        - mae: Mean Absolute Error
        - mape: Mean Absolute Percentage Error
        - rmse: Root Mean Squared Error
        - accuracy: 100 - MAPE (business-friendly)
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    # Handle edge cases
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted must have same length")
    
    # Remove any NaN or infinite values
    mask = np.isfinite(actual) & np.isfinite(predicted) & (actual != 0)
    actual_clean = actual[mask]
    predicted_clean = predicted[mask]
    
    if len(actual_clean) == 0:
        return {'mae': np.nan, 'mape': np.nan, 'rmse': np.nan, 'accuracy': np.nan}
    
    # Calculate metrics
    errors = actual_clean - predicted_clean
    abs_errors = np.abs(errors)
    pct_errors = abs_errors / np.abs(actual_clean)
    
    mae = np.mean(abs_errors)
    mape = np.mean(pct_errors) * 100
    rmse = np.sqrt(np.mean(errors ** 2))
    accuracy = 100 - mape
    
    return {
        'mae': mae,
        'mape': mape,
        'rmse': rmse,
        'accuracy': accuracy,
        'n_predictions': len(actual_clean)
    }


def cross_validate_timeseries(
    data: pd.DataFrame,
    model_class,
    n_splits: int = 5,
    test_size: int = 7,
    **model_kwargs
) -> Tuple[list, pd.DataFrame]:
    """
    Time series cross-validation
    
    Performs walk-forward validation maintaining temporal order.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Time series data with 'sales' column
    model_class : class
        Forecasting model class to evaluate
    n_splits : int
        Number of train/test splits
    test_size : int
        Size of test set (forecast horizon)
    model_kwargs : dict
        Arguments to pass to model constructor
        
    Returns:
    --------
    scores : list
        List of accuracy scores for each split
    results_df : pd.DataFrame
        Detailed results for each split
    """
    results = []
    scores = []
    
    # Calculate split points
    total_size = len(data)
    min_train_size = 30  # Minimum training size
    
    for i in range(n_splits):
        # Calculate train/test split
        test_end = total_size - (n_splits - i - 1) * test_size
        test_start = test_end - test_size
        train_end = test_start
        
        if train_end < min_train_size:
            continue
        
        # Split data
        train = data.iloc[:train_end]
        test = data.iloc[test_start:test_end]
        
        # Fit model
        model = model_class(**model_kwargs)
        
        # Handle different fit signatures
        if isinstance(model, DayOfWeekForecast):
            model.fit(train)
            predictions = model.predict(test.iloc[0]['date'], len(test))
        else:
            model.fit(train['sales'])
            predictions = model.predict(len(test))
        
        # Evaluate
        metrics = evaluate_forecast(test['sales'].values, predictions)
        
        results.append({
            'split': i + 1,
            'train_size': len(train),
            'test_size': len(test),
            **metrics
        })
        
        scores.append(metrics['accuracy'])
    
    results_df = pd.DataFrame(results)
    
    return scores, results_df


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("BASELINE FORECASTING MODELS - Examples")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Simulate data with day-of-week pattern
    dow_pattern = [0.9, 0.95, 1.0, 1.05, 1.15, 1.25, 1.1]  # Mon-Sun
    sales = []
    base = 5000
    
    for i, date in enumerate(dates):
        dow_multiplier = dow_pattern[date.dayofweek]
        trend = 1 + (i / 1000)  # Slight upward trend
        noise = np.random.normal(1.0, 0.08)
        sales.append(base * dow_multiplier * trend * noise)
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'day_of_week': dates.dayofweek
    })
    
    # Split into train/test
    train = df.iloc[:-7]
    test = df.iloc[-7:]
    
    print(f"\nData: {len(df)} days | Train: {len(train)} | Test: {len(test)}")
    print(f"Average sales: ${df['sales'].mean():,.2f}")
    
    # Test each model
    models = [
        NaiveForecast(),
        SeasonalNaiveForecast(season_length=7),
        MovingAverageForecast(window=7),
        MovingAverageForecast(window=30),
        ExponentialSmoothingForecast(alpha=0.3),
        DayOfWeekForecast(apply_trend=False),
        DayOfWeekForecast(apply_trend=True)
    ]
    
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    
    results = []
    for model in models:
        # Fit
        if isinstance(model, DayOfWeekForecast):
            model.fit(train)
            predictions = model.predict(test.iloc[0]['date'], len(test))
        else:
            model.fit(train['sales'])
            predictions = model.predict(len(test))
        
        # Evaluate
        metrics = evaluate_forecast(test['sales'].values, predictions)
        
        results.append({
            'Model': model.name,
            'Accuracy': f"{metrics['accuracy']:.2f}%",
            'MAPE': f"{metrics['mape']:.2f}%",
            'MAE': f"${metrics['mae']:,.2f}"
        })
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("ENSEMBLE MODEL")
    print("=" * 60)
    
    # Create ensemble of top 3 models
    ensemble = EnsembleBaseline()
    ensemble.add_model(SeasonalNaiveForecast(season_length=7).fit(train['sales']))
    ensemble.add_model(MovingAverageForecast(window=7).fit(train['sales']))
    
    dow_model = DayOfWeekForecast(apply_trend=True).fit(train)
    ensemble.add_model(dow_model)
    
    ensemble_pred = ensemble.predict(len(test), start_date=test.iloc[0]['date'])
    ensemble_metrics = evaluate_forecast(test['sales'].values, ensemble_pred)
    
    print(f"Ensemble Accuracy: {ensemble_metrics['accuracy']:.2f}%")
    print(f"Ensemble MAPE: {ensemble_metrics['mape']:.2f}%")
    print(f"Ensemble MAE: ${ensemble_metrics['mae']:,.2f}")
    
    print("\n✅ All baseline models tested successfully!")
