# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Trend Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class SMA(BaseIndicator):
    """
    Simple Moving Average
    
    The SMA is calculated by adding the closing prices of a security for a period 
    and then dividing this total by the number of time periods.
    
    Formula: SMA = (P1 + P2 + ... + Pn) / n
    """
    
    def __init__(self):
        super().__init__("SMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized SMA calculation"""
        result = np.empty_like(data)
        result[:period-1] = np.nan
        
        # Calculate first SMA value
        sum_val = 0.0
        for i in range(period):
            sum_val += data[i]
        result[period-1] = sum_val / period
        
        # Calculate remaining values using rolling window
        for i in range(period, len(data)):
            sum_val = sum_val - data[i-period] + data[i]
            result[i] = sum_val / period
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Simple Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            SMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_sma(validated_data, period)
        return self.format_output(result, input_type, index)


class EMA(BaseIndicator):
    """
    Exponential Moving Average
    
    The EMA gives more weight to recent prices, making it more responsive to new information.
    
    Formula: EMA = (Close - Previous EMA) × Multiplier + Previous EMA
    Where: Multiplier = 2 / (Period + 1)
    """
    
    def __init__(self):
        super().__init__("EMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized EMA calculation"""
        result = np.empty_like(data)
        alpha = 2.0 / (period + 1)
        
        # Start with SMA for the first value
        result[:period-1] = np.nan
        
        # Calculate initial SMA
        sum_val = 0.0
        for i in range(period):
            sum_val += data[i]
        result[period-1] = sum_val / period
        
        # Calculate EMA for remaining values
        for i in range(period, len(data)):
            result[i] = alpha * data[i] + (1 - alpha) * result[i-1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            EMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_ema(validated_data, period)
        return self.format_output(result, input_type, index)


class WMA(BaseIndicator):
    """
    Weighted Moving Average
    
    The WMA assigns greater weight to recent data points.
    
    Formula: WMA = (P1×1 + P2×2 + ... + Pn×n) / (1 + 2 + ... + n)
    """
    
    def __init__(self):
        super().__init__("WMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_wma(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized WMA calculation"""
        result = np.empty_like(data)
        result[:period-1] = np.nan
        
        # Calculate weight sum: 1 + 2 + ... + period
        weight_sum = period * (period + 1) // 2
        
        for i in range(period-1, len(data)):
            weighted_sum = 0.0
            for j in range(period):
                weight = j + 1
                weighted_sum += data[i - period + 1 + j] * weight
            result[i] = weighted_sum / weight_sum
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Weighted Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            WMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_wma(validated_data, period)
        return self.format_output(result, input_type, index)


class DEMA(BaseIndicator):
    """
    Double Exponential Moving Average
    
    DEMA attempts to reduce the lag associated with traditional moving averages.
    
    Formula: DEMA = 2 × EMA(n) - EMA(EMA(n))
    """
    
    def __init__(self):
        super().__init__("DEMA")
        self._ema = EMA()
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Double Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            DEMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate first EMA
        ema1_data = self._ema._calculate_ema(validated_data, period)
        
        # For second EMA, skip NaN values from first EMA
        # Find first valid index in ema1
        first_valid = period - 1
        if first_valid >= len(ema1_data):
            result = np.full_like(validated_data, np.nan)
            return self.format_output(result, input_type, index)
        
        # Extract valid portion for second EMA calculation
        valid_ema1 = ema1_data[first_valid:]
        ema2_partial = self._ema._calculate_ema(valid_ema1, period)
        
        # Reconstruct full ema2 array
        ema2_data = np.full_like(validated_data, np.nan)
        second_valid_start = first_valid + period - 1
        if second_valid_start < len(ema2_data):
            valid_length = min(len(ema2_partial[period-1:]), len(ema2_data) - second_valid_start)
            ema2_data[second_valid_start:second_valid_start + valid_length] = ema2_partial[period-1:period-1 + valid_length]
        
        # DEMA = 2 * EMA - EMA(EMA)
        result = 2 * ema1_data - ema2_data
        return self.format_output(result, input_type, index)


class TEMA(BaseIndicator):
    """
    Triple Exponential Moving Average
    
    TEMA further reduces lag compared to DEMA.
    
    Formula: TEMA = 3×EMA(n) - 3×EMA(EMA(n)) + EMA(EMA(EMA(n)))
    """
    
    def __init__(self):
        super().__init__("TEMA")
        self._ema = EMA()
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Triple Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            TEMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate first EMA
        ema1_data = self._ema._calculate_ema(validated_data, period)
        
        # Calculate second EMA from valid portion of first EMA
        first_valid = period - 1
        if first_valid >= len(ema1_data):
            result = np.full_like(validated_data, np.nan)
            return self.format_output(result, input_type, index)
        
        valid_ema1 = ema1_data[first_valid:]
        ema2_partial = self._ema._calculate_ema(valid_ema1, period)
        
        # Reconstruct full ema2 array
        ema2_data = np.full_like(validated_data, np.nan)
        second_valid_start = first_valid + period - 1
        if second_valid_start < len(ema2_data):
            valid_length = min(len(ema2_partial[period-1:]), len(ema2_data) - second_valid_start)
            ema2_data[second_valid_start:second_valid_start + valid_length] = ema2_partial[period-1:period-1 + valid_length]
        
        # Calculate third EMA from valid portion of second EMA
        ema3_data = np.full_like(validated_data, np.nan)
        if second_valid_start < len(ema2_data):
            valid_ema2 = ema2_data[second_valid_start:]
            # Remove NaN values
            valid_ema2_clean = valid_ema2[~np.isnan(valid_ema2)]
            if len(valid_ema2_clean) >= period:
                ema3_partial = self._ema._calculate_ema(valid_ema2_clean, period)
                third_valid_start = second_valid_start + period - 1
                if third_valid_start < len(ema3_data):
                    valid_length = min(len(ema3_partial[period-1:]), len(ema3_data) - third_valid_start)
                    ema3_data[third_valid_start:third_valid_start + valid_length] = ema3_partial[period-1:period-1 + valid_length]
        
        # TEMA = 3 * EMA - 3 * EMA(EMA) + EMA(EMA(EMA))
        result = 3 * ema1_data - 3 * ema2_data + ema3_data
        return self.format_output(result, input_type, index)


@jit(nopython=True)
def _calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
    """Calculate Average True Range"""
    n = len(high)
    tr = np.empty(n)
    atr = np.empty(n)
    
    # First TR value
    tr[0] = high[0] - low[0]
    
    # Calculate True Range
    for i in range(1, n):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr[i] = max(hl, hc, lc)
    
    # Calculate ATR
    atr[:period-1] = np.nan
    
    # Initial ATR is simple average
    sum_tr = 0.0
    for i in range(period):
        sum_tr += tr[i]
    atr[period-1] = sum_tr / period
    
    # Subsequent ATR values use smoothed average
    for i in range(period, n):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    
    return atr


class Supertrend(BaseIndicator):
    """
    Supertrend Indicator
    
    The Supertrend indicator is a trend-following indicator that uses ATR (Average True Range) 
    to calculate dynamic support and resistance levels.
    
    Formula:
    Basic Upper Band = (HIGH + LOW) / 2 + Multiplier × ATR
    Basic Lower Band = (HIGH + LOW) / 2 - Multiplier × ATR
    """
    
    def __init__(self):
        super().__init__("Supertrend")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_supertrend(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                             period: int, multiplier: float) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Supertrend calculation - matches TradingView Pine Script logic"""
        n = len(close)
        
        # Calculate ATR
        atr = _calculate_atr(high, low, close, period)
        
        # Calculate basic bands (src = hl2 in Pine Script)
        hl_avg = (high + low) / 2.0
        upper_band = hl_avg + multiplier * atr
        lower_band = hl_avg - multiplier * atr
        
        # Initialize arrays
        final_upper = np.full(n, np.nan)
        final_lower = np.full(n, np.nan)
        supertrend = np.full(n, np.nan)
        direction = np.full(n, np.nan)
        
        first_valid = period - 1
        if first_valid < 0 or first_valid >= n:
            return supertrend, direction
        
        # Initialize first valid values
        final_upper[first_valid] = upper_band[first_valid]
        final_lower[first_valid] = lower_band[first_valid]
        # Pine Script: if na(atr[1]) _direction := 1 (first bar is downtrend)
        direction[first_valid] = 1.0  # downtrend (red in Pine Script)
        supertrend[first_valid] = final_upper[first_valid]
        
        # Pine Script logic for subsequent bars
        for i in range(first_valid + 1, n):
            # Final lower band: lowerBand > prevLowerBand or close[1] < prevLowerBand ? lowerBand : prevLowerBand
            if lower_band[i] > final_lower[i-1] or close[i-1] < final_lower[i-1]:
                final_lower[i] = lower_band[i]
            else:
                final_lower[i] = final_lower[i-1]
            
            # Final upper band: upperBand < prevUpperBand or close[1] > prevUpperBand ? upperBand : prevUpperBand  
            if upper_band[i] < final_upper[i-1] or close[i-1] > final_upper[i-1]:
                final_upper[i] = upper_band[i]
            else:
                final_upper[i] = final_upper[i-1]
            
            # Direction logic (Pine Script)
            # if prevSuperTrend == prevUpperBand
            #     _direction := close > upperBand ? -1 : 1
            # else
            #     _direction := close < lowerBand ? 1 : -1
            if supertrend[i-1] == final_upper[i-1]:
                # Previous was upper band (downtrend)
                if close[i] > final_upper[i]:
                    direction[i] = -1.0  # Change to uptrend (green)
                else:
                    direction[i] = 1.0   # Continue downtrend (red)
            else:
                # Previous was lower band (uptrend)
                if close[i] < final_lower[i]:
                    direction[i] = 1.0   # Change to downtrend (red)
                else:
                    direction[i] = -1.0  # Continue uptrend (green)
            
            # Supertrend assignment: _direction == -1 ? lowerBand : upperBand
            if direction[i] == -1.0:  # uptrend (green)
                supertrend[i] = final_lower[i]
            else:  # downtrend (red)
                supertrend[i] = final_upper[i]
                
        return supertrend, direction
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 10, multiplier: float = 3.0) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Supertrend Indicator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=10
            ATR period
        multiplier : float, default=3.0
            ATR multiplier
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (supertrend values, direction values) in the same format as input
            Direction: -1 for uptrend (green), 1 for downtrend (red) - matches TradingView
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        if multiplier <= 0:
            raise ValueError(f"Multiplier must be positive, got {multiplier}")
        
        supertrend_result, direction_result = self._calculate_supertrend(high_data, low_data, close_data, period, multiplier)
        return self.format_multiple_outputs((supertrend_result, direction_result), input_type, index)


class Ichimoku(BaseIndicator):
    """
    Ichimoku Cloud
    
    The Ichimoku Cloud is a comprehensive indicator that defines support and resistance, 
    identifies trend direction, gauges momentum, and provides trading signals.
    
    Components:
    - Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
    - Kijun-sen (Base Line): (26-period high + 26-period low) / 2
    - Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen) / 2, plotted 26 periods ahead
    - Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, plotted 26 periods ahead
    - Chikou Span (Lagging Span): Close plotted 26 periods behind
    """
    
    def __init__(self):
        super().__init__("Ichimoku")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ichimoku(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                           tenkan_period: int = 9, kijun_period: int = 26,
                           senkou_b_period: int = 52, displacement: int = 26) -> Tuple[np.ndarray, ...]:
        """Numba optimized Ichimoku calculation"""
        n = len(close)
        
        # Initialize arrays
        tenkan_sen = np.full(n, np.nan)
        kijun_sen = np.full(n, np.nan)
        senkou_span_a = np.full(n + displacement, np.nan)
        senkou_span_b = np.full(n + displacement, np.nan)
        chikou_span = np.full(n, np.nan)
        
        # Calculate Tenkan-sen (Conversion Line)
        for i in range(tenkan_period - 1, n):
            period_high = high[i - tenkan_period + 1:i + 1].max()
            period_low = low[i - tenkan_period + 1:i + 1].min()
            tenkan_sen[i] = (period_high + period_low) / 2
        
        # Calculate Kijun-sen (Base Line)
        for i in range(kijun_period - 1, n):
            period_high = high[i - kijun_period + 1:i + 1].max()
            period_low = low[i - kijun_period + 1:i + 1].min()
            kijun_sen[i] = (period_high + period_low) / 2
        
        # Calculate Senkou Span A (Leading Span A)
        for i in range(max(tenkan_period, kijun_period) - 1, n):
            senkou_span_a[i + displacement] = (tenkan_sen[i] + kijun_sen[i]) / 2
        
        # Calculate Senkou Span B (Leading Span B)
        for i in range(senkou_b_period - 1, n):
            period_high = high[i - senkou_b_period + 1:i + 1].max()
            period_low = low[i - senkou_b_period + 1:i + 1].min()
            senkou_span_b[i + displacement] = (period_high + period_low) / 2
        
        # Calculate Chikou Span (Lagging Span)
        chikou_span[displacement:] = close[:-displacement]
        
        # Trim arrays to original length
        senkou_span_a = senkou_span_a[:n]
        senkou_span_b = senkou_span_b[:n]
        
        return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 tenkan_period: int = 9, kijun_period: int = 26,
                 senkou_b_period: int = 52, displacement: int = 26) -> Union[Tuple[np.ndarray, ...], Tuple[pd.Series, ...]]:
        """
        Calculate Ichimoku Cloud
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        tenkan_period : int, default=9
            Period for Tenkan-sen calculation
        kijun_period : int, default=26
            Period for Kijun-sen calculation
        senkou_b_period : int, default=52
            Period for Senkou Span B calculation
        displacement : int, default=26
            Displacement for Senkou Spans and Chikou Span
            
        Returns:
        --------
        Union[Tuple[np.ndarray, ...], Tuple[pd.Series, ...]]
            (tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        # Validate periods
        for period, name in [(tenkan_period, "tenkan_period"), 
                            (kijun_period, "kijun_period"), 
                            (senkou_b_period, "senkou_b_period")]:
            if period <= 0:
                raise ValueError(f"{name} must be positive, got {period}")
        
        results = self._calculate_ichimoku(high_data, low_data, close_data, tenkan_period, 
                                          kijun_period, senkou_b_period, displacement)
        return self.format_multiple_outputs(results, input_type, index)


class HMA(BaseIndicator):
    """
    Hull Moving Average
    
    The Hull Moving Average (HMA) attempts to minimize lag and improve smoothing.
    
    Formula: HMA = WMA(2 × WMA(n/2) - WMA(n), sqrt(n))
    """
    
    def __init__(self):
        super().__init__("HMA")
        self._wma = WMA()
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Hull Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            HMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Step 1: Calculate WMA(n/2)
        wma_half = self._wma.calculate(validated_data, period // 2)
        
        # Step 2: Calculate WMA(n)
        wma_full = self._wma.calculate(validated_data, period)
        
        # Step 3: Calculate 2 * WMA(n/2) - WMA(n)
        diff = 2 * wma_half - wma_full
        
        # Step 4: Calculate HMA = WMA(diff, sqrt(n))
        sqrt_period = int(np.sqrt(period))
        result = self._wma.calculate(diff, sqrt_period)
        
        return self.format_output(result, input_type, index)


class VWMA(BaseIndicator):
    """
    Volume Weighted Moving Average
    
    VWMA gives more weight to periods with higher volume.
    
    Formula: VWMA = Σ(Price × Volume) / Σ(Volume)
    """
    
    def __init__(self):
        super().__init__("VWMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vwma(data: np.ndarray, volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized VWMA calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            sum_pv = 0.0
            sum_v = 0.0
            
            for j in range(period):
                idx = i - period + 1 + j
                sum_pv += data[idx] * volume[idx]
                sum_v += volume[idx]
            
            if sum_v > 0:
                result[i] = sum_pv / sum_v
            else:
                result[i] = data[i]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Weighted Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            VWMA values in the same format as input
        """
        data_validated, input_type, index = self.validate_input(data)
        volume_validated, _, _ = self.validate_input(volume)
        data_validated, volume_validated = self.align_arrays(data_validated, volume_validated)
        self.validate_period(period, len(data_validated))
        
        result = self._calculate_vwma(data_validated, volume_validated, period)
        return self.format_output(result, input_type, index)


class ALMA(BaseIndicator):
    """
    Arnaud Legoux Moving Average
    
    ALMA is a technical analysis indicator that combines the features of SMA and EMA.
    
    Formula: ALMA = Σ(w[i] × data[i]) / Σ(w[i])
    Where: w[i] = exp(-((i - m)^2) / (2 × s^2))
    """
    
    def __init__(self):
        super().__init__("ALMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_alma(data: np.ndarray, period: int, offset: float, sigma: float) -> np.ndarray:
        """Numba optimized ALMA calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # Calculate weights
        m = offset * (period - 1)
        s = period / sigma
        
        weights = np.empty(period)
        for i in range(period):
            weights[i] = np.exp(-((i - m) ** 2) / (2 * s * s))
        
        # Normalize weights
        weight_sum = np.sum(weights)
        weights = weights / weight_sum
        
        # Calculate ALMA
        for i in range(period - 1, n):
            alma_sum = 0.0
            for j in range(period):
                alma_sum += weights[j] * data[i - period + 1 + j]
            result[i] = alma_sum
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 period: int = 21, offset: float = 0.85, sigma: float = 6.0) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Arnaud Legoux Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=21
            Number of periods for the moving average
        offset : float, default=0.85
            Phase offset (0 to 1)
        sigma : float, default=6.0
            Smoothing factor
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ALMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        if not 0 <= offset <= 1:
            raise ValueError(f"Offset must be between 0 and 1, got {offset}")
        if sigma <= 0:
            raise ValueError(f"Sigma must be positive, got {sigma}")
        
        result = self._calculate_alma(validated_data, period, offset, sigma)
        return self.format_output(result, input_type, index)


class KAMA(BaseIndicator):
    """
    Kaufman's Adaptive Moving Average
    
    KAMA is a moving average designed to account for market noise or volatility.
    
    Formula: KAMA = KAMA[prev] + SC × (Price - KAMA[prev])
    Where: SC = (ER × (fastest SC - slowest SC) + slowest SC)^2
    """
    
    def __init__(self):
        super().__init__("KAMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_kama(data: np.ndarray, period: int, fast_sc: float, slow_sc: float) -> np.ndarray:
        """Numba optimized KAMA calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # Initialize first value
        result[period - 1] = data[period - 1]
        
        for i in range(period, n):
            # Calculate direction
            direction = abs(data[i] - data[i - period])
            
            # Calculate volatility
            volatility = 0.0
            for j in range(period):
                volatility += abs(data[i - j] - data[i - j - 1])
            
            # Calculate efficiency ratio
            if volatility > 0:
                er = direction / volatility
            else:
                er = 0.0
            
            # Calculate smoothing constant
            sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
            
            # Calculate KAMA
            result[i] = result[i - 1] + sc * (data[i] - result[i - 1])
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 period: int = 10, fast_period: int = 2, slow_period: int = 30) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Kaufman's Adaptive Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=10
            Efficiency ratio period
        fast_period : int, default=2
            Fast EMA constant
        slow_period : int, default=30
            Slow EMA constant
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            KAMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        if fast_period <= 0 or slow_period <= 0:
            raise ValueError("Fast and slow periods must be positive")
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
        
        # Convert periods to smoothing constants
        fast_sc = 2.0 / (fast_period + 1)
        slow_sc = 2.0 / (slow_period + 1)
        
        result = self._calculate_kama(validated_data, period, fast_sc, slow_sc)
        return self.format_output(result, input_type, index)


class ZLEMA(BaseIndicator):
    """
    Zero Lag Exponential Moving Average
    
    ZLEMA is an EMA that attempts to minimize lag by using price momentum.
    
    Formula: ZLEMA = EMA(2 × Price - Price[lag])
    Where: lag = (period - 1) / 2
    """
    
    def __init__(self):
        super().__init__("ZLEMA")
        self._ema = EMA()
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Zero Lag Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ZLEMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate lag
        lag = (period - 1) // 2
        
        # Create lagged data
        adjusted_data = np.empty_like(validated_data)
        adjusted_data[:lag] = validated_data[:lag]
        
        for i in range(lag, len(validated_data)):
            adjusted_data[i] = 2 * validated_data[i] - validated_data[i - lag]
        
        # Calculate EMA of adjusted data
        result = self._ema.calculate(adjusted_data, period)
        return self.format_output(result, input_type, index)


class T3(BaseIndicator):
    """
    T3 Moving Average
    
    T3 is a type of moving average which is the result of applying EMA three times.
    
    Formula: T3 = GD(GD(GD(data)))
    Where: GD = Generalized DEMA
    """
    
    def __init__(self):
        super().__init__("T3")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_gd(data: np.ndarray, period: int, v_factor: float) -> np.ndarray:
        """Calculate Generalized DEMA"""
        alpha = 2.0 / (period + 1)
        
        # First EMA
        ema1 = np.empty_like(data)
        ema1[0] = data[0]
        for i in range(1, len(data)):
            ema1[i] = alpha * data[i] + (1 - alpha) * ema1[i - 1]
        
        # Second EMA
        ema2 = np.empty_like(data)
        ema2[0] = ema1[0]
        for i in range(1, len(data)):
            ema2[i] = alpha * ema1[i] + (1 - alpha) * ema2[i - 1]
        
        # Generalized DEMA
        gd = (1 + v_factor) * ema1 - v_factor * ema2
        return gd
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 period: int = 21, v_factor: float = 0.7) -> Union[np.ndarray, pd.Series]:
        """
        Calculate T3 Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=21
            Number of periods for the moving average
        v_factor : float, default=0.7
            Volume factor for T3 calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            T3 values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Apply GD three times
        gd1 = self._calculate_gd(validated_data, period, v_factor)
        gd2 = self._calculate_gd(gd1, period, v_factor)
        result = self._calculate_gd(gd2, period, v_factor)
        
        return self.format_output(result, input_type, index)


class FRAMA(BaseIndicator):
    """
    Fractal Adaptive Moving Average
    
    FRAMA adjusts its smoothing based on the fractal dimension of the price series.
    
    Formula: FRAMA = (2 - D) × Price + (D - 1) × FRAMA[prev]
    Where: D = fractal dimension
    """
    
    def __init__(self):
        super().__init__("FRAMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_frama(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized FRAMA calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # Initialize first value
        result[period - 1] = data[period - 1]
        
        for i in range(period, n):
            # Calculate fractal dimension
            n1 = period // 2
            n2 = period - n1
            
            # High and low for each half
            h1 = np.max(data[i - period + 1:i - n2 + 1])
            l1 = np.min(data[i - period + 1:i - n2 + 1])
            h2 = np.max(data[i - n2 + 1:i + 1])
            l2 = np.min(data[i - n2 + 1:i + 1])
            h3 = np.max(data[i - period + 1:i + 1])
            l3 = np.min(data[i - period + 1:i + 1])
            
            # Fractal dimension calculation
            if h1 - l1 > 0 and h2 - l2 > 0 and h3 - l3 > 0:
                d = (np.log(h1 - l1) + np.log(h2 - l2) - np.log(h3 - l3)) / np.log(2)
            else:
                d = 1.0
            
            # Ensure D is between 1 and 2
            d = max(1.0, min(2.0, d))
            
            # Calculate alpha
            alpha = 2.0 / (period + 1)
            
            # Adjust alpha based on fractal dimension
            w = np.log(2.0 / alpha) / np.log(2.0)
            alpha_adj = 2.0 / (w * d + 1)
            
            # Calculate FRAMA
            result[i] = alpha_adj * data[i] + (1 - alpha_adj) * result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 16) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Fractal Adaptive Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=16
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            FRAMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        if period < 4:
            raise ValueError("Period must be at least 4 for FRAMA calculation")
        
        result = self._calculate_frama(validated_data, period)
        return self.format_output(result, input_type, index)


class ChandeKrollStop(BaseIndicator):
    """
    Chande Kroll Stop
    
    The Chande Kroll Stop is a trailing stop-loss technique that combines 
    ATR-based calculations with highest highs and lowest lows.
    
    Formula:
    Long Stop = Highest(High, period) - ATR_multiplier * ATR(period)
    Short Stop = Lowest(Low, period) + ATR_multiplier * ATR(period)
    """
    
    def __init__(self):
        super().__init__("Chande Kroll Stop")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
        """Calculate ATR"""
        n = len(close)
        tr = np.empty(n)
        
        # Calculate True Range
        tr[0] = high[0] - low[0]
        for i in range(1, n):
            tr[i] = max(high[i] - low[i],
                       abs(high[i] - close[i-1]),
                       abs(low[i] - close[i-1]))
        
        # Calculate ATR using exponential moving average
        atr = np.empty(n)
        atr[0] = tr[0]
        alpha = 1.0 / period
        
        for i in range(1, n):
            atr[i] = alpha * tr[i] + (1 - alpha) * atr[i-1]
        
        return atr
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_chande_kroll_stop(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                                   period: int, atr_multiplier: float) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Chande Kroll Stop calculation"""
        n = len(close)
        long_stop = np.full(n, np.nan)
        short_stop = np.full(n, np.nan)
        
        # Calculate ATR
        atr = ChandeKrollStop._calculate_atr(high, low, close, period)
        
        for i in range(period - 1, n):
            # Calculate highest high and lowest low over the period
            highest_high = np.max(high[i - period + 1:i + 1])
            lowest_low = np.min(low[i - period + 1:i + 1])
            
            # Calculate stops
            long_stop[i] = highest_high - atr_multiplier * atr[i]
            short_stop[i] = lowest_low + atr_multiplier * atr[i]
        
        return long_stop, short_stop
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 10, atr_multiplier: float = 1.0) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Chande Kroll Stop
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=10
            Period for highest/lowest and ATR calculation
        atr_multiplier : float, default=1.0
            Multiplier for ATR in stop calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (long_stop, short_stop) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        long_stop, short_stop = self._calculate_chande_kroll_stop(high_data, low_data, close_data, period, atr_multiplier)
        
        results = (long_stop, short_stop)
        return self.format_multiple_outputs(results, input_type, index)


class TRIMA(BaseIndicator):
    """
    Triangular Moving Average
    
    TRIMA is a double-smoothed moving average that applies SMA twice.
    
    Formula: TRIMA = SMA(SMA(Close, n), n)
    Where n = (period + 1) / 2
    """
    
    def __init__(self):
        super().__init__("TRIMA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_trima(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized TRIMA calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # First, calculate n for SMA
        n1 = (period + 1) // 2
        n2 = period - n1 + 1
        
        # First SMA
        first_sma = np.full(n, np.nan)
        for i in range(n1 - 1, n):
            first_sma[i] = np.mean(data[i - n1 + 1:i + 1])
        
        # Second SMA on first SMA
        for i in range(n1 + n2 - 2, n):
            if not np.isnan(first_sma[i]):
                window_start = max(0, i - n2 + 1)
                window = first_sma[window_start:i + 1]
                valid_values = window[~np.isnan(window)]
                if len(valid_values) >= n2:
                    result[i] = np.mean(valid_values[-n2:])
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Triangular Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            TRIMA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_trima(validated_data, period)
        return self.format_output(result, input_type, index)


class McGinley(BaseIndicator):
    """
    McGinley Dynamic
    
    A moving average that adjusts automatically for market speed changes.
    
    Formula: MD[i] = MD[i-1] + (Close[i] - MD[i-1]) / (N * (Close[i]/MD[i-1])^4)
    """
    
    def __init__(self):
        super().__init__("McGinley Dynamic")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_mcginley(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized McGinley Dynamic calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        if n < period:
            return result
        
        # Initialize with SMA
        result[period - 1] = np.mean(data[:period])
        
        for i in range(period, n):
            if result[i - 1] != 0:
                ratio = data[i] / result[i - 1]
                factor = period * (ratio ** 4)
                result[i] = result[i - 1] + (data[i] - result[i - 1]) / factor
            else:
                result[i] = data[i]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Calculate McGinley Dynamic
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            McGinley Dynamic values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_mcginley(validated_data, period)
        return self.format_output(result, input_type, index)


class VIDYA(BaseIndicator):
    """
    Variable Index Dynamic Average (VIDYA)
    
    VIDYA uses the Chande Momentum Oscillator (CMO) to adjust the smoothing constant of an EMA.
    
    Formula: VIDYA[i] = VIDYA[i-1] + alpha * |CMO[i]| / 100 * (Close[i] - VIDYA[i-1])
    """
    
    def __init__(self):
        super().__init__("VIDYA")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_cmo(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Chande Momentum Oscillator"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # Calculate price changes
        changes = np.diff(data)
        
        for i in range(period, n):
            sum_up = 0.0
            sum_down = 0.0
            
            for j in range(period):
                change = changes[i - period + j]
                if change > 0:
                    sum_up += change
                elif change < 0:
                    sum_down += abs(change)
            
            total_movement = sum_up + sum_down
            if total_movement > 0:
                result[i] = 100 * (sum_up - sum_down) / total_movement
            else:
                result[i] = 0.0
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vidya(data: np.ndarray, period: int, alpha: float) -> np.ndarray:
        """Numba optimized VIDYA calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # Calculate CMO inline
        cmo = np.full(n, np.nan)
        
        for i in range(period, n):
            gains = 0.0
            losses = 0.0
            
            for j in range(i - period + 1, i + 1):
                if j > 0:
                    diff = data[j] - data[j - 1]
                    if diff > 0:
                        gains += diff
                    elif diff < 0:
                        losses += abs(diff)
            
            if gains + losses != 0:
                cmo[i] = 100 * (gains - losses) / (gains + losses)
            else:
                cmo[i] = 0.0
        
        # Initialize with first valid data point
        result[period] = data[period]
        
        for i in range(period + 1, n):
            if not np.isnan(cmo[i]):
                smoothing_constant = alpha * abs(cmo[i]) / 100
                result[i] = result[i - 1] + smoothing_constant * (data[i] - result[i - 1])
            else:
                result[i] = result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], 
                 period: int = 14, alpha: float = 0.2) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Variable Index Dynamic Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Period for CMO calculation
        alpha : float, default=0.2
            Alpha factor for smoothing
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            VIDYA values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period + 1, len(validated_data))
        result = self._calculate_vidya(validated_data, period, alpha)
        return self.format_output(result, input_type, index)


class Alligator(BaseIndicator):
    """
    Alligator (Bill Williams)
    
    The Alligator consists of three smoothed moving averages:
    - Jaw (blue line): 13-period SMMA, shifted 8 bars forward
    - Teeth (red line): 8-period SMMA, shifted 5 bars forward  
    - Lips (green line): 5-period SMMA, shifted 3 bars forward
    """
    
    def __init__(self):
        super().__init__("Alligator")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_smma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Smoothed Moving Average (SMMA)"""
        n = len(data)
        result = np.full(n, np.nan)
        
        if n < period:
            return result
        
        # Initialize with SMA
        result[period - 1] = np.mean(data[:period])
        
        # Calculate SMMA
        for i in range(period, n):
            result[i] = (result[i - 1] * (period - 1) + data[i]) / period
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _shift_series(data: np.ndarray, shift: int) -> np.ndarray:
        """Shift series forward by specified periods"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(shift, n):
            result[i] = data[i - shift]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 jaw_period: int = 13, jaw_shift: int = 8,
                 teeth_period: int = 8, teeth_shift: int = 5,
                 lips_period: int = 5, lips_shift: int = 3) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Alligator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically (high + low) / 2)
        jaw_period : int, default=13
            Period for Jaw line
        jaw_shift : int, default=8
            Forward shift for Jaw line
        teeth_period : int, default=8
            Period for Teeth line
        teeth_shift : int, default=5
            Forward shift for Teeth line
        lips_period : int, default=5
            Period for Lips line
        lips_shift : int, default=3
            Forward shift for Lips line
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (jaw, teeth, lips) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate SMMA for each line
        jaw_smma = self._calculate_smma(validated_data, jaw_period)
        teeth_smma = self._calculate_smma(validated_data, teeth_period)
        lips_smma = self._calculate_smma(validated_data, lips_period)
        
        # Apply shifts
        jaw = self._shift_series(jaw_smma, jaw_shift)
        teeth = self._shift_series(teeth_smma, teeth_shift)
        lips = self._shift_series(lips_smma, lips_shift)
        
        results = (jaw, teeth, lips)
        return self.format_multiple_outputs(results, input_type, index)


class MovingAverageEnvelopes(BaseIndicator):
    """
    Moving Average Envelopes
    
    Upper and lower envelopes around a moving average, calculated as percentage bands.
    
    Formula: 
    Upper = MA * (1 + percentage/100)
    Lower = MA * (1 - percentage/100)
    """
    
    def __init__(self):
        super().__init__("MA Envelopes")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
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
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 period: int = 20, percentage: float = 2.5,
                 ma_type: str = "SMA") -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Moving Average Envelopes
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=20
            Period for moving average calculation
        percentage : float, default=2.5
            Percentage for envelope calculation
        ma_type : str, default="SMA"
            Type of moving average ("SMA" or "EMA")
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (upper_envelope, middle_line, lower_envelope) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate moving average
        if ma_type.upper() == "SMA":
            ma = self._calculate_sma(validated_data, period)
        elif ma_type.upper() == "EMA":
            ma = self._calculate_ema(validated_data, period)
        else:
            raise ValueError(f"Unsupported MA type: {ma_type}")
        
        # Calculate envelopes
        multiplier = percentage / 100
        upper_envelope = ma * (1 + multiplier)
        lower_envelope = ma * (1 - multiplier)
        
        results = (upper_envelope, ma, lower_envelope)
        return self.format_multiple_outputs(results, input_type, index)