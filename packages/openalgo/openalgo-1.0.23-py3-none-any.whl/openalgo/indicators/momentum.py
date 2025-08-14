# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Momentum Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


@jit(nopython=True)
def _calculate_ema_for_macd(data: np.ndarray, period: int) -> np.ndarray:
    """EMA calculation optimized for MACD"""
    n = len(data)
    ema = np.empty(n)
    alpha = 2.0 / (period + 1)
    
    # Initialize with first value
    ema[0] = data[0]
    
    # Calculate EMA
    for i in range(1, n):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
    
    return ema


class RSI(BaseIndicator):
    """
    Relative Strength Index
    
    RSI is a momentum oscillator that measures the speed and magnitude of price changes.
    It oscillates between 0 and 100, with readings above 70 indicating overbought conditions
    and readings below 30 indicating oversold conditions.
    
    Formula: RSI = 100 - (100 / (1 + RS))
    Where: RS = Average Gain / Average Loss
    """
    
    def __init__(self):
        super().__init__("RSI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rsi(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized RSI calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        if n < period + 1:
            return result
        
        # Calculate price changes
        deltas = np.diff(data)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate initial average gain and loss
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        # Calculate first RSI value
        if avg_loss == 0:
            result[period] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[period] = 100.0 - (100.0 / (1.0 + rs))
        
        # Calculate subsequent RSI values using Wilder's smoothing
        for i in range(period, n - 1):
            gain = gains[i] if i < len(gains) else 0
            loss = losses[i] if i < len(losses) else 0
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                result[i + 1] = 100.0
            else:
                rs = avg_gain / avg_loss
                result[i + 1] = 100.0 - (100.0 / (1.0 + rs))
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Relative Strength Index
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for RSI calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            RSI values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_rsi(validated_data, period)
        return self.format_output(result, input_type, index)


class MACD(BaseIndicator):
    """
    Moving Average Convergence Divergence
    
    MACD is a trend-following momentum indicator that shows the relationship between
    two exponential moving averages of prices.
    
    Components:
    - MACD Line: 12-day EMA - 26-day EMA
    - Signal Line: 9-day EMA of MACD Line
    - MACD Histogram: MACD Line - Signal Line
    """
    
    def __init__(self):
        super().__init__("MACD")
    
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_macd(data: np.ndarray, fast_period: int, slow_period: int, 
                       signal_period: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Numba optimized MACD calculation"""
        # Calculate EMAs
        ema_fast = _calculate_ema_for_macd(data, fast_period)
        ema_slow = _calculate_ema_for_macd(data, slow_period)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = _calculate_ema_for_macd(macd_line, signal_period)
        
        # MACD histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], 
                 fast_period: int = 12, slow_period: int = 26, 
                 signal_period: int = 9) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate MACD
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast_period : int, default=12
            Period for fast EMA
        slow_period : int, default=26
            Period for slow EMA
        signal_period : int, default=9
            Period for signal line EMA
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (macd_line, signal_line, histogram) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Validate periods
        if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
            raise ValueError("All periods must be positive")
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
        
        results = self._calculate_macd(validated_data, fast_period, slow_period, signal_period)
        return self.format_multiple_outputs(results, input_type, index)


class Stochastic(BaseIndicator):
    """
    Stochastic Oscillator
    
    The Stochastic Oscillator compares a security's closing price to its price range
    over a given time period. It consists of two lines: %K and %D.
    
    Formula:
    %K = 100 × (Current Close - Lowest Low) / (Highest High - Lowest Low)
    %D = 3-period SMA of %K
    """
    
    def __init__(self):
        super().__init__("Stochastic")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                             k_period: int, d_period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Stochastic calculation"""
        n = len(close)
        k_percent = np.full(n, np.nan)
        d_percent = np.full(n, np.nan)
        
        # Calculate %K
        for i in range(k_period - 1, n):
            highest_high = high[i - k_period + 1:i + 1].max()
            lowest_low = low[i - k_period + 1:i + 1].min()
            
            if highest_high != lowest_low:
                k_percent[i] = 100 * (close[i] - lowest_low) / (highest_high - lowest_low)
            else:
                k_percent[i] = 50.0  # Default when range is zero
        
        # Calculate %D (SMA of %K)
        for i in range(k_period + d_period - 2, n):
            d_sum = 0.0
            count = 0
            for j in range(d_period):
                idx = i - j
                if idx >= 0 and not np.isnan(k_percent[idx]):
                    d_sum += k_percent[idx]
                    count += 1
            if count > 0:
                d_percent[i] = d_sum / count
        
        return k_percent, d_percent
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 k_period: int = 14, d_period: int = 3) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Stochastic Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        k_period : int, default=14
            Period for %K calculation
        d_period : int, default=3
            Period for %D calculation (SMA of %K)
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (k_percent, d_percent) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        # Validate periods
        self.validate_period(k_period, len(close_data))
        if d_period <= 0:
            raise ValueError(f"d_period must be positive, got {d_period}")
        
        results = self._calculate_stochastic(high_data, low_data, close_data, k_period, d_period)
        return self.format_multiple_outputs(results, input_type, index)


class CCI(BaseIndicator):
    """
    Commodity Channel Index
    
    CCI measures the current price level relative to an average price level over a given period.
    It is used to identify cyclical trends in commodities, equities, and currencies.
    
    Formula: CCI = (Typical Price - SMA of TP) / (0.015 × Mean Deviation)
    Where: Typical Price = (High + Low + Close) / 3
    """
    
    def __init__(self):
        super().__init__("CCI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_cci(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                      period: int) -> np.ndarray:
        """Numba optimized CCI calculation"""
        n = len(close)
        cci = np.full(n, np.nan)
        
        # Calculate Typical Price
        typical_price = (high + low + close) / 3.0
        
        # Calculate CCI
        for i in range(period - 1, n):
            # SMA of typical price
            sma_tp = np.mean(typical_price[i - period + 1:i + 1])
            
            # Mean deviation
            mean_dev = 0.0
            for j in range(period):
                mean_dev += abs(typical_price[i - period + 1 + j] - sma_tp)
            mean_dev = mean_dev / period
            
            # CCI calculation
            if mean_dev != 0:
                cci[i] = (typical_price[i] - sma_tp) / (0.015 * mean_dev)
            else:
                cci[i] = 0.0
        
        return cci
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Commodity Channel Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=20
            Number of periods for CCI calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            CCI values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_cci(high_data, low_data, close_data, period)
        return self.format_output(result, input_type, index)


class WilliamsR(BaseIndicator):
    """
    Williams %R
    
    Williams %R is a momentum indicator that measures overbought and oversold levels.
    It is similar to the Stochastic Oscillator but is plotted on a negative scale from 0 to -100.
    
    Formula: %R = (Highest High - Close) / (Highest High - Lowest Low) × -100
    """
    
    def __init__(self):
        super().__init__("Williams %R")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_williams_r(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                             period: int) -> np.ndarray:
        """Numba optimized Williams %R calculation"""
        n = len(close)
        williams_r = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            highest_high = high[i - period + 1:i + 1].max()
            lowest_low = low[i - period + 1:i + 1].min()
            
            if highest_high != lowest_low:
                williams_r[i] = -100 * (highest_high - close[i]) / (highest_high - lowest_low)
            else:
                williams_r[i] = -50.0  # Default when range is zero
        
        return williams_r
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Williams %R
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Number of periods for Williams %R calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Williams %R values (range: 0 to -100) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_williams_r(high_data, low_data, close_data, period)
        return self.format_output(result, input_type, index)


class BalanceOfPower(BaseIndicator):
    """
    Balance of Power (BOP)
    
    Balance of Power measures the strength of buyers versus sellers by assessing
    the ability of each side to drive prices to an extreme level.
    
    Formula: BOP = (Close - Open) / (High - Low)
    """
    
    def __init__(self):
        super().__init__("BOP")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_bop(open_prices: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
        """Numba optimized BOP calculation"""
        n = len(close)
        bop = np.full(n, np.nan)
        
        for i in range(n):
            if high[i] != low[i]:
                bop[i] = (close[i] - open_prices[i]) / (high[i] - low[i])
            else:
                bop[i] = 0.0
        
        return bop
    
    def calculate(self, open_prices: Union[np.ndarray, pd.Series, list],
                 high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Balance of Power
        
        Parameters:
        -----------
        open_prices : Union[np.ndarray, pd.Series, list]
            Opening prices
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            BOP values in the same format as input
        """
        open_data, input_type, index = self.validate_input(open_prices)
        high_data, _, _ = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        open_data, high_data, low_data, close_data = self.align_arrays(open_data, high_data, low_data, close_data)
        
        result = self._calculate_bop(open_data, high_data, low_data, close_data)
        return self.format_output(result, input_type, index)


class ElderRayIndex(BaseIndicator):
    """
    Elder Ray Index (Bull/Bear Power)
    
    Elder Ray Index consists of two indicators:
    - Bull Power = High - EMA
    - Bear Power = Low - EMA
    
    They measure the ability of bulls and bears to drive prices above or below an EMA.
    """
    
    def __init__(self):
        super().__init__("Elder Ray")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.empty(n)
        alpha = 2.0 / (period + 1)
        
        result[0] = data[0]
        for i in range(1, n):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 13) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Elder Ray Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=13
            Period for EMA calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (bull_power, bear_power) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        # Calculate EMA of close
        ema = self._calculate_ema(close_data, period)
        
        # Calculate Bull and Bear Power
        bull_power = high_data - ema
        bear_power = low_data - ema
        
        results = (bull_power, bear_power)
        return self.format_multiple_outputs(results, input_type, index)


class FisherTransform(BaseIndicator):
    """
    Fisher Transform
    
    The Fisher Transform converts prices into a Gaussian normal distribution.
    The Fisher Transform is used to highlight when prices have moved to an extreme.
    
    Formula: Fisher = 0.5 * ln((1 + x) / (1 - x))
    Where x = 2 * ((price - min) / (max - min)) - 1
    """
    
    def __init__(self):
        super().__init__("Fisher Transform")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_fisher(data: np.ndarray, period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Fisher Transform calculation"""
        n = len(data)
        fisher = np.full(n, np.nan)
        trigger = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Get window data
            window = data[i - period + 1:i + 1]
            min_val = np.min(window)
            max_val = np.max(window)
            
            if max_val != min_val:
                # Normalize to -1 to 1
                normalized = 2 * ((data[i] - min_val) / (max_val - min_val)) - 1
                
                # Constrain to avoid division by zero
                normalized = max(-0.9999, min(0.9999, normalized))
                
                # Calculate Fisher Transform
                fisher[i] = 0.5 * np.log((1 + normalized) / (1 - normalized))
            else:
                fisher[i] = 0.0
            
            # Calculate trigger (previous Fisher value)
            if i > 0:
                trigger[i] = fisher[i - 1] if not np.isnan(fisher[i - 1]) else 0.0
        
        return fisher, trigger
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 period: int = 10) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Fisher Transform
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically (high + low) / 2)
        period : int, default=10
            Period for min/max calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (fisher, trigger) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        fisher, trigger = self._calculate_fisher(validated_data, period)
        
        results = (fisher, trigger)
        return self.format_multiple_outputs(results, input_type, index)


class ConnorsRSI(BaseIndicator):
    """
    Connors RSI (CRSI)
    
    Connors RSI is a composite momentum oscillator consisting of three components:
    1. RSI of price
    2. RSI of streak (consecutive up/down days)
    3. Percent rank of rate of change
    
    Formula: CRSI = (RSI(Close, 3) + RSI(Streak, 2) + ROC(Close, 100)) / 3
    """
    
    def __init__(self):
        super().__init__("Connors RSI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rsi(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate RSI"""
        n = len(data)
        result = np.full(n, np.nan)
        
        if n < period + 1:
            return result
        
        deltas = np.diff(data)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            result[period] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[period] = 100.0 - (100.0 / (1.0 + rs))
        
        for i in range(period + 1, n):
            gain = gains[i - 1]
            loss = losses[i - 1]
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                result[i] = 100.0
            else:
                rs = avg_gain / avg_loss
                result[i] = 100.0 - (100.0 / (1.0 + rs))
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_streak(data: np.ndarray) -> np.ndarray:
        """Calculate streak of consecutive up/down days"""
        n = len(data)
        streak = np.zeros(n)
        
        for i in range(1, n):
            if data[i] > data[i-1]:
                if streak[i-1] > 0:
                    streak[i] = streak[i-1] + 1
                else:
                    streak[i] = 1
            elif data[i] < data[i-1]:
                if streak[i-1] < 0:
                    streak[i] = streak[i-1] - 1
                else:
                    streak[i] = -1
            else:
                streak[i] = 0
        
        return streak
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_percent_rank(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate percent rank"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            window = data[i - period + 1:i + 1]
            current_val = data[i]
            
            count_below = 0
            for j in range(len(window)):
                if window[j] < current_val:
                    count_below += 1
            
            result[i] = (count_below / period) * 100
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 rsi_period: int = 3, streak_period: int = 2, 
                 roc_period: int = 100) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Connors RSI
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        rsi_period : int, default=3
            Period for price RSI
        streak_period : int, default=2
            Period for streak RSI
        roc_period : int, default=100
            Period for ROC percent rank
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Connors RSI values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(max(rsi_period, streak_period, roc_period), len(validated_data))
        
        # Calculate components
        price_rsi = self._calculate_rsi(validated_data, rsi_period)
        
        streak = self._calculate_streak(validated_data)
        streak_rsi = self._calculate_rsi(streak, streak_period)
        
        # Calculate ROC
        roc = np.full_like(validated_data, np.nan)
        for i in range(roc_period, len(validated_data)):
            if validated_data[i - roc_period] != 0:
                roc[i] = ((validated_data[i] - validated_data[i - roc_period]) / validated_data[i - roc_period]) * 100
        
        roc_percentrank = self._calculate_percent_rank(roc, roc_period)
        
        # Calculate Connors RSI
        crsi = np.full_like(validated_data, np.nan)
        for i in range(len(validated_data)):
            if not np.isnan(price_rsi[i]) and not np.isnan(streak_rsi[i]) and not np.isnan(roc_percentrank[i]):
                crsi[i] = (price_rsi[i] + streak_rsi[i] + roc_percentrank[i]) / 3
        
        return self.format_output(crsi, input_type, index)