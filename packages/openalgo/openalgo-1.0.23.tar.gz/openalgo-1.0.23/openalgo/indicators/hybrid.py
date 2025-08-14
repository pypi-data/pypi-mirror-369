# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Hybrid and Advanced Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class ADX(BaseIndicator):
    """
    Average Directional Index
    
    ADX measures the strength of a trend, regardless of direction.
    
    Components: +DI, -DI, ADX
    """
    
    def __init__(self):
        super().__init__("ADX")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_adx(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      period: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Numba optimized ADX calculation"""
        n = len(high)
        
        # Initialize arrays
        tr = np.empty(n)
        dm_plus = np.empty(n)
        dm_minus = np.empty(n)
        
        # Calculate True Range and Directional Movement
        tr[0] = high[0] - low[0]
        dm_plus[0] = 0
        dm_minus[0] = 0
        
        for i in range(1, n):
            # True Range
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr[i] = max(hl, hc, lc)
            
            # Directional Movement
            up_move = high[i] - high[i-1]
            down_move = low[i-1] - low[i]
            
            if up_move > down_move and up_move > 0:
                dm_plus[i] = up_move
            else:
                dm_plus[i] = 0
                
            if down_move > up_move and down_move > 0:
                dm_minus[i] = down_move
            else:
                dm_minus[i] = 0
        
        # Calculate smoothed values
        atr = np.full(n, np.nan)
        di_plus = np.full(n, np.nan)
        di_minus = np.full(n, np.nan)
        adx = np.full(n, np.nan)
        dx = np.full(n, np.nan)  # store DX values separately for proper ADX seed
        
        # Initial smoothed values
        if n >= period:
            atr[period-1] = np.mean(tr[:period])
            sm_dm_plus = np.mean(dm_plus[:period])
            sm_dm_minus = np.mean(dm_minus[:period])
            
            if atr[period-1] > 0:
                di_plus[period-1] = (sm_dm_plus / atr[period-1]) * 100
                di_minus[period-1] = (sm_dm_minus / atr[period-1]) * 100
            
            # Calculate subsequent values
            for i in range(period, n):
                # Smoothed TR
                atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
                
                # Smoothed DM
                sm_dm_plus = (sm_dm_plus * (period - 1) + dm_plus[i]) / period
                sm_dm_minus = (sm_dm_minus * (period - 1) + dm_minus[i]) / period
                
                # DI calculations
                if atr[i] > 0:
                    di_plus[i] = (sm_dm_plus / atr[i]) * 100
                    di_minus[i] = (sm_dm_minus / atr[i]) * 100
                
                # DX calculation (store for later ADX seed)
                di_sum = di_plus[i] + di_minus[i]
                if di_sum > 0:
                    dx[i] = abs(di_plus[i] - di_minus[i]) / di_sum * 100
        
            # ---- ADX Seed & Smoothing ----
            first_adx_pos = period * 2 - 1
            if n > first_adx_pos:
                # Average of DX over the first 'period' values to seed ADX
                adx[first_adx_pos] = np.nanmean(dx[period:first_adx_pos + 1])
                # Continue smoothing ADX for remaining periods
                for i in range(first_adx_pos + 1, n):
                    if not np.isnan(dx[i]):
                        adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period
        
        return di_plus, di_minus, adx
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Average Directional Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Period for ADX calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (+DI, -DI, ADX) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        results = self._calculate_adx(high_data, low_data, close_data, period)
        return self.format_multiple_outputs(results, input_type, index)


class Aroon(BaseIndicator):
    """
    Aroon Indicator
    
    Aroon indicators measure the time since the highest high and lowest low.
    
    Formula: 
    Aroon Up = ((period - periods since highest high) / period) × 100
    Aroon Down = ((period - periods since lowest low) / period) × 100
    """
    
    def __init__(self):
        super().__init__("Aroon")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_aroon(high: np.ndarray, low: np.ndarray, period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Aroon calculation"""
        n = len(high)
        aroon_up = np.full(n, np.nan)
        aroon_down = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Find highest high and lowest low positions in the window
            high_window = high[i - period + 1:i + 1]
            low_window = low[i - period + 1:i + 1]
            
            # Find positions of highest high and lowest low
            highest_pos = 0
            lowest_pos = 0
            
            for j in range(len(high_window)):
                if high_window[j] >= high_window[highest_pos]:
                    highest_pos = j
                if low_window[j] <= low_window[lowest_pos]:
                    lowest_pos = j
            
            # Calculate Aroon values
            periods_since_high = period - 1 - highest_pos
            periods_since_low = period - 1 - lowest_pos
            
            aroon_up[i] = ((period - periods_since_high) / period) * 100
            aroon_down[i] = ((period - periods_since_low) / period) * 100
        
        return aroon_up, aroon_down
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 period: int = 25) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Aroon Indicator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        period : int, default=25
            Period for Aroon calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (aroon_up, aroon_down) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        self.validate_period(period, len(high_data))
        
        results = self._calculate_aroon(high_data, low_data, period)
        return self.format_multiple_outputs(results, input_type, index)


class PivotPoints(BaseIndicator):
    """
    Pivot Points
    
    Traditional pivot points used for support and resistance levels.
    
    Formula:
    Pivot = (High + Low + Close) / 3
    R1 = 2 * Pivot - Low
    S1 = 2 * Pivot - High
    R2 = Pivot + (High - Low)
    S2 = Pivot - (High - Low)
    R3 = High + 2 * (Pivot - Low)
    S3 = Low - 2 * (High - Pivot)
    """
    
    def __init__(self):
        super().__init__("Pivot Points")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_pivot_points(high: np.ndarray, low: np.ndarray, 
                               close: np.ndarray) -> Tuple[np.ndarray, ...]:
        """Numba optimized Pivot Points calculation"""
        n = len(high)
        
        pivot = np.empty(n)
        r1 = np.empty(n)
        s1 = np.empty(n)
        r2 = np.empty(n)
        s2 = np.empty(n)
        r3 = np.empty(n)
        s3 = np.empty(n)
        
        for i in range(n):
            # Calculate pivot point
            pivot[i] = (high[i] + low[i] + close[i]) / 3
            
            # Calculate resistance and support levels
            r1[i] = 2 * pivot[i] - low[i]
            s1[i] = 2 * pivot[i] - high[i]
            r2[i] = pivot[i] + (high[i] - low[i])
            s2[i] = pivot[i] - (high[i] - low[i])
            r3[i] = high[i] + 2 * (pivot[i] - low[i])
            s3[i] = low[i] - 2 * (high[i] - pivot[i])
        
        return pivot, r1, s1, r2, s2, r3, s3
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list]) -> Union[Tuple[np.ndarray, ...], Tuple[pd.Series, ...]]:
        """
        Calculate Pivot Points
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
            
        Returns:
        --------
        Union[Tuple[np.ndarray, ...], Tuple[pd.Series, ...]]
            (pivot, r1, s1, r2, s2, r3, s3) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        results = self._calculate_pivot_points(high_data, low_data, close_data)
        return self.format_multiple_outputs(results, input_type, index)


class SAR(BaseIndicator):
    """
    Parabolic SAR (Stop and Reverse)
    
    SAR is a trend-following indicator that provides potential reversal points.
    
    Formula: SAR = SAR[prev] + AF × (EP - SAR[prev])
    Where: AF = Acceleration Factor, EP = Extreme Point
    """
    
    def __init__(self):
        super().__init__("Parabolic SAR")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sar(high: np.ndarray, low: np.ndarray, 
                      acceleration: float, maximum: float) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized SAR calculation"""
        n = len(high)
        sar = np.empty(n)
        trend = np.empty(n)  # 1 for uptrend, -1 for downtrend
        
        # Initialize
        sar[0] = low[0]
        trend[0] = 1
        af = acceleration
        ep = high[0]  # Extreme point
        
        for i in range(1, n):
            prev_sar = sar[i-1]
            prev_trend = trend[i-1]
            
            # Calculate new SAR
            sar[i] = prev_sar + af * (ep - prev_sar)
            
            # Determine trend
            if prev_trend == 1:  # Uptrend
                if low[i] <= sar[i]:
                    # Trend reversal to downtrend
                    trend[i] = -1
                    sar[i] = ep  # Set SAR to previous EP
                    ep = low[i]  # New EP for downtrend
                    af = acceleration  # Reset AF
                else:
                    # Continue uptrend
                    trend[i] = 1
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + acceleration, maximum)
                    
                    # SAR should not exceed previous two lows
                    if i >= 2:
                        sar[i] = min(sar[i], low[i-1], low[i-2])
                    elif i >= 1:
                        sar[i] = min(sar[i], low[i-1])
            else:  # Downtrend
                if high[i] >= sar[i]:
                    # Trend reversal to uptrend
                    trend[i] = 1
                    sar[i] = ep  # Set SAR to previous EP
                    ep = high[i]  # New EP for uptrend
                    af = acceleration  # Reset AF
                else:
                    # Continue downtrend
                    trend[i] = -1
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + acceleration, maximum)
                    
                    # SAR should not fall below previous two highs
                    if i >= 2:
                        sar[i] = max(sar[i], high[i-1], high[i-2])
                    elif i >= 1:
                        sar[i] = max(sar[i], high[i-1])
        
        return sar, trend
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 acceleration: float = 0.02, maximum: float = 0.2) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Parabolic SAR
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        acceleration : float, default=0.02
            Acceleration factor
        maximum : float, default=0.2
            Maximum acceleration factor
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (sar_values, trend_direction) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        
        if acceleration <= 0 or maximum <= 0:
            raise ValueError("Acceleration and maximum must be positive")
        if acceleration > maximum:
            raise ValueError("Acceleration cannot be greater than maximum")
        
        results = self._calculate_sar(high_data, low_data, acceleration, maximum)
        return self.format_multiple_outputs(results, input_type, index)


class DMI(BaseIndicator):
    """
    Directional Movement Index
    
    DMI is the same as ADX system but focuses on the directional indicators.
    """
    
    def __init__(self):
        super().__init__("DMI")
        self._adx = ADX()
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Directional Movement Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Period for DMI calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (+DI, -DI) in the same format as input
        """
        results = self._adx.calculate(high, low, close, period)
        # Return only the first two components (+DI, -DI), excluding ADX
        if isinstance(results[0], np.ndarray):
            return results[0], results[1]
        else:
            return results[0], results[1]


class PSAR(BaseIndicator):
    """
    Parabolic SAR (alias for SAR)
    """
    
    def __init__(self):
        super().__init__("PSAR")
        self._sar = SAR()
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 acceleration: float = 0.02, maximum: float = 0.2) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Parabolic SAR
        
        Returns only the SAR values (not the trend direction) in the same format as input
        """
        results = self._sar.calculate(high, low, acceleration, maximum)
        # Return only the first component (SAR values), excluding trend direction
        if isinstance(results[0], np.ndarray):
            return results[0]
        else:
            return results[0]


class HT_TRENDLINE(BaseIndicator):
    """
    Hilbert Transform - Instantaneous Trendline
    
    Uses Hilbert Transform to create a smoothed trendline.
    """
    
    def __init__(self):
        super().__init__("HT Trendline")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ht_trendline(data: np.ndarray) -> np.ndarray:
        """Simplified Hilbert Transform Trendline"""
        n = len(data)
        result = np.empty(n)
        
        # Initialize
        for i in range(7):
            result[i] = data[i]
        
        # Apply smoothing filter
        for i in range(7, n):
            # Simple approximation of Hilbert Transform
            result[i] = (4 * data[i] + 3 * data[i-1] + 2 * data[i-2] + data[i-3] + 
                        data[i-4] + data[i-5] + data[i-6]) / 13
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Hilbert Transform Trendline
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Trendline values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        result = self._calculate_ht_trendline(validated_data)
        return self.format_output(result, input_type, index)


class ZigZag(BaseIndicator):
    """
    Zig Zag
    
    Zig Zag connects significant price swings and filters out smaller price movements.
    
    Formula: Connect swing highs and lows that exceed the deviation threshold.
    """
    
    def __init__(self):
        super().__init__("ZigZag")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_zigzag(high: np.ndarray, low: np.ndarray, close: np.ndarray, deviation: float) -> np.ndarray:
        """Numba optimized Zig Zag calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        if n < 3:
            return result
        
        # Find first significant point
        last_pivot_idx = 0
        last_pivot_price = close[0]
        last_pivot_type = 0  # 0 = unknown, 1 = high, -1 = low
        result[0] = close[0]
        
        current_high = high[0]
        current_low = low[0]
        current_high_idx = 0
        current_low_idx = 0
        
        for i in range(1, n):
            # Update current extremes
            if high[i] > current_high:
                current_high = high[i]
                current_high_idx = i
            if low[i] < current_low:
                current_low = low[i]
                current_low_idx = i
            
            # Check for reversal from high
            if last_pivot_type != -1:  # Not currently looking for high
                change_from_high = (current_high - low[i]) / current_high * 100
                if change_from_high >= deviation:
                    # Reversal from high - mark the high
                    result[current_high_idx] = current_high
                    last_pivot_idx = current_high_idx
                    last_pivot_price = current_high
                    last_pivot_type = 1
                    current_low = low[i]
                    current_low_idx = i
            
            # Check for reversal from low  
            if last_pivot_type != 1:  # Not currently looking for low
                if current_low > 0:
                    change_from_low = (high[i] - current_low) / current_low * 100
                    if change_from_low >= deviation:
                        # Reversal from low - mark the low
                        result[current_low_idx] = current_low
                        last_pivot_idx = current_low_idx
                        last_pivot_price = current_low
                        last_pivot_type = -1
                        current_high = high[i]
                        current_high_idx = i
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 deviation: float = 5.0) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Zig Zag
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        deviation : float, default=5.0
            Minimum percentage deviation for zig zag line
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Zig Zag values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        result = self._calculate_zigzag(high_data, low_data, close_data, deviation)
        return self.format_output(result, input_type, index)


class WilliamsFractals(BaseIndicator):
    """
    Williams Fractals
    
    Identifies turning points (fractals) in price action.
    
    Fractal Up: High[n] > High[n-2] and High[n] > High[n-1] and High[n] > High[n+1] and High[n] > High[n+2]
    Fractal Down: Low[n] < Low[n-2] and Low[n] < Low[n-1] and Low[n] < Low[n+1] and Low[n] < Low[n+2]
    """
    
    def __init__(self):
        super().__init__("Fractals")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_fractals(high: np.ndarray, low: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Williams Fractals calculation"""
        n = len(high)
        fractal_up = np.full(n, np.nan)
        fractal_down = np.full(n, np.nan)
        
        for i in range(2, n - 2):
            # Check for fractal up (peak)
            if (high[i] > high[i-1] and high[i] > high[i-2] and 
                high[i] > high[i+1] and high[i] > high[i+2]):
                fractal_up[i] = high[i]
            
            # Check for fractal down (trough)
            if (low[i] < low[i-1] and low[i] < low[i-2] and 
                low[i] < low[i+1] and low[i] < low[i+2]):
                fractal_down[i] = low[i]
        
        return fractal_up, fractal_down
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list]) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Williams Fractals
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (fractal_up, fractal_down) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        
        fractal_up, fractal_down = self._calculate_fractals(high_data, low_data)
        
        results = (fractal_up, fractal_down)
        return self.format_multiple_outputs(results, input_type, index)


class RandomWalkIndex(BaseIndicator):
    """
    Random Walk Index (RWI High/Low)
    
    Measures how much a security's price movement differs from a random walk.
    
    Formula:
    RWI High = (High - Low[n]) / (ATR * sqrt(n))
    RWI Low = (High[n] - Low) / (ATR * sqrt(n))
    """
    
    def __init__(self):
        super().__init__("RWI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
        """Calculate ATR"""
        n = len(close)
        tr = np.full(n, np.nan)
        atr = np.full(n, np.nan)
        
        # Calculate True Range
        tr[0] = high[0] - low[0]
        for i in range(1, n):
            tr[i] = max(high[i] - low[i], 
                       abs(high[i] - close[i - 1]), 
                       abs(low[i] - close[i - 1]))
        
        # Calculate ATR using simple moving average
        for i in range(period - 1, n):
            atr[i] = np.mean(tr[i - period + 1:i + 1])
        
        return atr
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rwi(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized RWI calculation"""
        n = len(close)
        rwi_high = np.full(n, np.nan)
        rwi_low = np.full(n, np.nan)
        
        # Calculate ATR
        atr = RandomWalkIndex._calculate_atr(high, low, close, period)
        
        for i in range(period - 1, n):
            if atr[i] > 0:
                # RWI High: (High - Low[n periods ago]) / (ATR * sqrt(n))
                rwi_high[i] = (high[i] - low[i - period + 1]) / (atr[i] * np.sqrt(period))
                
                # RWI Low: (High[n periods ago] - Low) / (ATR * sqrt(n))
                rwi_low[i] = (high[i - period + 1] - low[i]) / (atr[i] * np.sqrt(period))
            else:
                rwi_high[i] = 0.0
                rwi_low[i] = 0.0
        
        return rwi_high, rwi_low
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Random Walk Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Period for RWI calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (rwi_high, rwi_low) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        rwi_high, rwi_low = self._calculate_rwi(high_data, low_data, close_data, period)
        
        results = (rwi_high, rwi_low)
        return self.format_multiple_outputs(results, input_type, index)