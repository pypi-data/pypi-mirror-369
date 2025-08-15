# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Oscillators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class ROC(BaseIndicator):
    """
    Rate of Change (Price Oscillator)
    
    ROC measures the percentage change in price from n periods ago.
    
    Formula: ROC = ((Price - Price[n periods ago]) / Price[n periods ago]) × 100
    """
    
    def __init__(self):
        super().__init__("ROC")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_roc(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized ROC calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period, n):
            if data[i - period] != 0:
                result[i] = ((data[i] - data[i - period]) / data[i - period]) * 100
            else:
                result[i] = 0.0
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 12) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Rate of Change
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=12
            Number of periods to look back
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ROC values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_roc(validated_data, period)
        return self.format_output(result, input_type, index)


class CMO(BaseIndicator):
    """
    Chande Momentum Oscillator
    
    CMO is a momentum oscillator developed by Tushar Chande.
    
    Formula: CMO = 100 × (Sum of Up Days - Sum of Down Days) / (Sum of Up Days + Sum of Down Days)
    """
    
    def __init__(self):
        super().__init__("CMO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_cmo(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized CMO calculation"""
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
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Chande Momentum Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for CMO calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            CMO values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period + 1, len(validated_data))  # +1 for diff
        result = self._calculate_cmo(validated_data, period)
        return self.format_output(result, input_type, index)


class TRIX(BaseIndicator):
    """
    TRIX - Triple Exponential Average
    
    TRIX is a momentum oscillator that displays the percentage rate of change 
    of a triple exponentially smoothed moving average.
    
    Formula: TRIX = % change of triple EMA
    """
    
    def __init__(self):
        super().__init__("TRIX")
    
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
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate TRIX
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for EMA calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            TRIX values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate triple EMA
        ema1 = self._calculate_ema(validated_data, period)
        ema2 = self._calculate_ema(ema1, period)
        ema3 = self._calculate_ema(ema2, period)
        
        # Calculate percentage change of triple EMA
        trix = np.full_like(ema3, np.nan)
        for i in range(1, len(ema3)):
            if ema3[i - 1] != 0:
                trix[i] = ((ema3[i] - ema3[i - 1]) / ema3[i - 1]) * 100  # ×100 to express percentage change
        
        return self.format_output(trix, input_type, index)


class UO(BaseIndicator):
    """
    Ultimate Oscillator
    
    The Ultimate Oscillator combines short, medium, and long-term price action 
    into one oscillator.
    
    Formula: UO = 100 × (4×AVG7 + 2×AVG14 + AVG28) / (4 + 2 + 1)
    Where: AVG = Average of (Close - TrueLow) / (TrueRange)
    """
    
    def __init__(self):
        super().__init__("UO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_uo(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                     period1: int, period2: int, period3: int) -> np.ndarray:
        """Numba optimized Ultimate Oscillator calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        # Calculate True Low and True Range
        true_low = np.empty(n)
        true_range = np.empty(n)
        buying_pressure = np.empty(n)
        
        true_low[0] = low[0]
        true_range[0] = high[0] - low[0]
        buying_pressure[0] = close[0] - true_low[0]
        
        for i in range(1, n):
            true_low[i] = min(low[i], close[i - 1])
            true_range[i] = max(high[i] - low[i], 
                               abs(high[i] - close[i - 1]), 
                               abs(low[i] - close[i - 1]))
            buying_pressure[i] = close[i] - true_low[i]
        
        # Calculate Ultimate Oscillator
        max_period = max(period1, period2, period3)
        for i in range(max_period - 1, n):
            # Calculate averages for each period
            bp1 = np.sum(buying_pressure[i - period1 + 1:i + 1])
            tr1 = np.sum(true_range[i - period1 + 1:i + 1])
            avg1 = bp1 / tr1 if tr1 > 0 else 0
            
            bp2 = np.sum(buying_pressure[i - period2 + 1:i + 1])
            tr2 = np.sum(true_range[i - period2 + 1:i + 1])
            avg2 = bp2 / tr2 if tr2 > 0 else 0
            
            bp3 = np.sum(buying_pressure[i - period3 + 1:i + 1])
            tr3 = np.sum(true_range[i - period3 + 1:i + 1])
            avg3 = bp3 / tr3 if tr3 > 0 else 0
            
            # Calculate Ultimate Oscillator
            result[i] = 100 * (4 * avg1 + 2 * avg2 + avg3) / 7
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period1: int = 7, period2: int = 14, period3: int = 28) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Ultimate Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period1 : int, default=7
            Short period
        period2 : int, default=14
            Medium period
        period3 : int, default=28
            Long period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Ultimate Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        result = self._calculate_uo(high_data, low_data, close_data, period1, period2, period3)
        return self.format_output(result, input_type, index)


class AO(BaseIndicator):
    """
    Awesome Oscillator
    
    The Awesome Oscillator is an indicator used to measure market momentum.
    
    Formula: AO = SMA(HL/2, 5) - SMA(HL/2, 34)
    Where: HL/2 = (High + Low) / 2
    """
    
    def __init__(self):
        super().__init__("AO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 5, slow_period: int = 34) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Awesome Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        fast_period : int, default=5
            Fast SMA period
        slow_period : int, default=34
            Slow SMA period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Awesome Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        
        # Calculate median price
        median_price = (high_data + low_data) / 2
        
        # Calculate SMAs
        fast_sma = self._calculate_sma(median_price, fast_period)
        slow_sma = self._calculate_sma(median_price, slow_period)
        
        # Calculate AO
        result = fast_sma - slow_sma
        return self.format_output(result, input_type, index)


class AC(BaseIndicator):
    """
    Accelerator Oscillator
    
    The Accelerator Oscillator measures acceleration and deceleration of momentum.
    
    Formula: AC = AO - SMA(AO, 5)
    Where: AO = Awesome Oscillator
    """
    
    def __init__(self):
        super().__init__("AC")
        self._ao = AO()
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 period: int = 5) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Accelerator Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        period : int, default=5
            SMA period for acceleration calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Accelerator Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        # Calculate Awesome Oscillator
        ao_raw = self._ao.calculate(high, low)
        
        # Ensure numpy array for numba SMA calculation
        if isinstance(ao_raw, pd.Series):
            ao_data = ao_raw.values.astype(np.float64)
        else:
            ao_data = ao_raw.astype(np.float64)
        
        # Calculate SMA of AO
        ao_sma = self._calculate_sma(ao_data, period)
        
        # Calculate AC (array diff)
        result_arr = ao_data - ao_sma
        return self.format_output(result_arr, input_type, index)


class PPO(BaseIndicator):
    """
    Percentage Price Oscillator
    
    PPO is a momentum oscillator that measures the difference between two 
    moving averages as a percentage of the larger moving average.
    
    Formula: PPO = ((Fast EMA - Slow EMA) / Slow EMA) × 100
    """
    
    def __init__(self):
        super().__init__("PPO")
    
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
                 fast_period: int = 12, slow_period: int = 26,
                 signal_period: int = 9) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Percentage Price Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast_period : int, default=12
            Fast EMA period
        slow_period : int, default=26
            Slow EMA period
        signal_period : int, default=9
            Signal line EMA period
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (ppo_line, signal_line, histogram) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(validated_data, fast_period)
        slow_ema = self._calculate_ema(validated_data, slow_period)
        
        # Calculate PPO line
        ppo_line = np.empty_like(validated_data)
        for i in range(len(validated_data)):
            if slow_ema[i] != 0:
                ppo_line[i] = ((fast_ema[i] - slow_ema[i]) / slow_ema[i]) * 100
            else:
                ppo_line[i] = 0
        
        # Calculate signal line
        signal_line = self._calculate_ema(ppo_line, signal_period)
        
        # Calculate histogram
        histogram = ppo_line - signal_line
        
        results = (ppo_line, signal_line, histogram)
        return self.format_multiple_outputs(results, input_type, index)


class PO(BaseIndicator):
    """
    Price Oscillator
    
    Price Oscillator shows the difference between two moving averages.
    
    Formula: PO = Fast MA - Slow MA
    """
    
    def __init__(self):
        super().__init__("PO")
    
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
                 fast_period: int = 10, slow_period: int = 20,
                 ma_type: str = "SMA") -> Union[np.ndarray, pd.Series]:
        """
        Calculate Price Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast_period : int, default=10
            Fast moving average period
        slow_period : int, default=20
            Slow moving average period
        ma_type : str, default="SMA"
            Type of moving average ("SMA" or "EMA")
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Price Oscillator values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        if ma_type.upper() == "SMA":
            fast_ma = self._calculate_sma(validated_data, fast_period)
            slow_ma = self._calculate_sma(validated_data, slow_period)
        elif ma_type.upper() == "EMA":
            fast_ma = self._calculate_ema(validated_data, fast_period)
            slow_ma = self._calculate_ema(validated_data, slow_period)
        else:
            raise ValueError(f"Unsupported MA type: {ma_type}")
        
        result = fast_ma - slow_ma
        return self.format_output(result, input_type, index)


class DPO(BaseIndicator):
    """
    Detrended Price Oscillator
    
    DPO attempts to eliminate the trend in prices by comparing a past price 
    to a moving average.
    
    Formula: DPO = Price[n/2 + 1 periods ago] - SMA(n)
    """
    
    def __init__(self):
        super().__init__("DPO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Detrended Price Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=20
            Period for SMA calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            DPO values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate SMA
        sma = self._calculate_sma(validated_data, period)
        
        # Calculate DPO
        dpo = np.full_like(validated_data, np.nan)
        offset = period // 2 + 1
        
        for i in range(offset, len(validated_data)):
            if not np.isnan(sma[i]):
                dpo[i] = validated_data[i - offset] - sma[i]
        
        return self.format_output(dpo, input_type, index)


class AROONOSC(BaseIndicator):
    """
    Aroon Oscillator
    
    The Aroon Oscillator is the difference between Aroon Up and Aroon Down.
    
    Formula: Aroon Oscillator = Aroon Up - Aroon Down
    """
    
    def __init__(self):
        super().__init__("Aroon Oscillator")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_aroon_osc(high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized Aroon Oscillator calculation"""
        n = len(high)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Find highest high and lowest low positions
            high_window = high[i - period + 1:i + 1]
            low_window = low[i - period + 1:i + 1]
            
            highest_pos = 0
            lowest_pos = 0
            
            for j in range(len(high_window)):
                if high_window[j] >= high_window[highest_pos]:
                    highest_pos = j
                if low_window[j] <= low_window[lowest_pos]:
                    lowest_pos = j
            
            # Calculate Aroon Up and Down
            aroon_up = ((period - (period - 1 - highest_pos)) / period) * 100
            aroon_down = ((period - (period - 1 - lowest_pos)) / period) * 100
            
            # Aroon Oscillator
            result[i] = aroon_up - aroon_down
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 period: int = 25) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Aroon Oscillator
        
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
        Union[np.ndarray, pd.Series]
            Aroon Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        self.validate_period(period, len(high_data))
        
        result = self._calculate_aroon_osc(high_data, low_data, period)
        return self.format_output(result, input_type, index)


class StochRSI(BaseIndicator):
    """
    Stochastic RSI
    
    The Stochastic RSI is an oscillator that uses RSI values instead of price values as inputs
    to the Stochastic formula.
    
    Formula: StochRSI = (RSI - Lowest(RSI, K)) / (Highest(RSI, K) - Lowest(RSI, K))
    """
    
    def __init__(self):
        super().__init__("StochRSI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rsi(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate RSI"""
        n = len(data)
        result = np.full(n, np.nan)
        
        if n < period + 1:
            return result
        
        # Calculate price changes
        deltas = np.diff(data)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        
        # Initial average gain and loss
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            result[period] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[period] = 100.0 - (100.0 / (1.0 + rs))
        
        # Calculate RSI for remaining periods
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
    def _calculate_stochrsi(data: np.ndarray, rsi_period: int, stoch_period: int, k_period: int, d_period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Stochastic RSI calculation"""
        # Calculate RSI inline
        n_data = len(data)
        rsi = np.full(n_data, np.nan)
        
        if n_data < rsi_period + 1:
            return rsi, rsi
        
        # Calculate price changes
        deltas = np.diff(data)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate initial average gain and loss
        avg_gain = np.mean(gains[:rsi_period])
        avg_loss = np.mean(losses[:rsi_period])
        
        # Calculate first RSI value
        if avg_loss == 0:
            rsi[rsi_period] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[rsi_period] = 100.0 - (100.0 / (1.0 + rs))
        
        # Calculate subsequent RSI values using Wilder's smoothing
        for i in range(rsi_period, n_data - 1):
            gain = gains[i] if i < len(gains) else 0
            loss = losses[i] if i < len(losses) else 0
            
            avg_gain = (avg_gain * (rsi_period - 1) + gain) / rsi_period
            avg_loss = (avg_loss * (rsi_period - 1) + loss) / rsi_period
            
            if avg_loss == 0:
                rsi[i + 1] = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi[i + 1] = 100.0 - (100.0 / (1.0 + rs))
        
        n = len(rsi)
        stoch_rsi = np.full(n, np.nan)
        
        # Calculate Stochastic RSI
        for i in range(stoch_period - 1, n):
            rsi_window = rsi[i - stoch_period + 1:i + 1]
            rsi_window_clean = rsi_window[~np.isnan(rsi_window)]
            
            if len(rsi_window_clean) > 0:
                rsi_high = np.max(rsi_window_clean)
                rsi_low = np.min(rsi_window_clean)
                
                if rsi_high != rsi_low:
                    stoch_rsi[i] = (rsi[i] - rsi_low) / (rsi_high - rsi_low) * 100
                else:
                    stoch_rsi[i] = 50.0
        
        # Calculate %K (SMA of StochRSI)
        k_values = np.full(n, np.nan)
        for i in range(k_period - 1, n):
            window = stoch_rsi[i - k_period + 1:i + 1]
            window_clean = window[~np.isnan(window)]
            if len(window_clean) > 0:
                k_values[i] = np.mean(window_clean)
        
        # Calculate %D (SMA of %K)
        d_values = np.full(n, np.nan)
        for i in range(d_period - 1, n):
            window = k_values[i - d_period + 1:i + 1]
            window_clean = window[~np.isnan(window)]
            if len(window_clean) > 0:
                d_values[i] = np.mean(window_clean)
        
        return k_values, d_values
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], 
                 rsi_period: int = 14, stoch_period: int = 14,
                 k_period: int = 3, d_period: int = 3) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Stochastic RSI
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        rsi_period : int, default=14
            Period for RSI calculation
        stoch_period : int, default=14
            Period for Stochastic calculation on RSI
        k_period : int, default=3
            Period for %K smoothing
        d_period : int, default=3
            Period for %D smoothing
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (%K, %D) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(rsi_period + stoch_period, len(validated_data))
        
        k_values, d_values = self._calculate_stochrsi(validated_data, rsi_period, stoch_period, k_period, d_period)
        
        results = (k_values, d_values)
        return self.format_multiple_outputs(results, input_type, index)


class RVI(BaseIndicator):
    """
    Relative Vigor Index (RVI Oscillator)
    
    The RVI compares the closing price to the trading range and smooths the result.
    
    Formula: RVI = SMA(Close - Open, period) / SMA(High - Low, period)
    """
    
    def __init__(self):
        super().__init__("RVI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rvi(open_prices: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized RVI calculation"""
        n = len(close)
        rvi = np.full(n, np.nan)
        signal = np.full(n, np.nan)
        
        # Calculate numerator and denominator
        numerator = close - open_prices
        denominator = high - low
        
        # Calculate RVI
        for i in range(period - 1, n):
            num_sum = np.sum(numerator[i - period + 1:i + 1])
            den_sum = np.sum(denominator[i - period + 1:i + 1])
            
            if den_sum != 0:
                rvi[i] = num_sum / den_sum
            else:
                rvi[i] = 0.0
        
        # Calculate signal line (4-period weighted moving average of RVI)
        for i in range(3, n):
            if not np.isnan(rvi[i]) and not np.isnan(rvi[i-1]) and not np.isnan(rvi[i-2]) and not np.isnan(rvi[i-3]):
                signal[i] = (rvi[i] + 2*rvi[i-1] + 2*rvi[i-2] + rvi[i-3]) / 6
        
        return rvi, signal
    
    def calculate(self, open_prices: Union[np.ndarray, pd.Series, list],
                 high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 10) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Relative Vigor Index
        
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
        period : int, default=10
            Period for RVI calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (rvi, signal) in the same format as input
        """
        open_data, input_type, index = self.validate_input(open_prices)
        high_data, _, _ = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        open_data, high_data, low_data, close_data = self.align_arrays(open_data, high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        rvi, signal = self._calculate_rvi(open_data, high_data, low_data, close_data, period)
        
        results = (rvi, signal)
        return self.format_multiple_outputs(results, input_type, index)


class CHO(BaseIndicator):
    """
    Chaikin Oscillator (Chaikin A/D Oscillator)
    
    The Chaikin Oscillator is the difference between the 3-day and 10-day EMAs
    of the Accumulation Distribution Line.
    
    Formula: Chaikin Osc = EMA(A/D Line, 3) - EMA(A/D Line, 10)
    """
    
    def __init__(self):
        super().__init__("Chaikin Oscillator")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_adl(high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Calculate Accumulation Distribution Line"""
        n = len(close)
        adl = np.zeros(n)
        
        for i in range(n):
            if high[i] != low[i]:
                clv = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])
            else:
                clv = 0.0
            
            mfv = clv * volume[i]
            
            if i == 0:
                adl[i] = mfv
            else:
                adl[i] = adl[i - 1] + mfv
        
        return adl
    
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
                 volume: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 3, slow_period: int = 10) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Chaikin Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        fast_period : int, default=3
            Fast EMA period
        slow_period : int, default=10
            Slow EMA period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Chaikin Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        
        # Calculate A/D Line
        adl = self._calculate_adl(high_data, low_data, close_data, volume_data)
        
        # Calculate EMAs of A/D Line
        fast_ema = self._calculate_ema(adl, fast_period)
        slow_ema = self._calculate_ema(adl, slow_period)
        
        # Calculate Chaikin Oscillator
        result = fast_ema - slow_ema
        
        return self.format_output(result, input_type, index)


class CHOP(BaseIndicator):
    """
    Choppiness Index
    
    The Choppiness Index measures whether the market is choppy (ranging) or trending.
    Values near 100 indicate a choppy market, while values near 0 indicate a trending market.
    
    Formula: CHOP = 100 * log10(sum(ATR, n) / (max(high, n) - min(low, n))) / log10(n)
    """
    
    def __init__(self):
        super().__init__("CHOP")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_atr_sum(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
        """Calculate sum of ATR over period"""
        n = len(close)
        atr_sum = np.full(n, np.nan)
        
        # Calculate True Range for each bar
        tr = np.full(n, np.nan)
        tr[0] = high[0] - low[0]
        
        for i in range(1, n):
            tr[i] = max(high[i] - low[i], 
                       abs(high[i] - close[i - 1]), 
                       abs(low[i] - close[i - 1]))
        
        # Calculate sum of ATR
        for i in range(period - 1, n):
            atr_sum[i] = np.sum(tr[i - period + 1:i + 1])
        
        return atr_sum
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_chop(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized CHOP calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        # Calculate sum of ATR inline
        atr_sum = np.full(n, np.nan)
        
        # Calculate True Range for each bar
        tr = np.full(n, np.nan)
        tr[0] = high[0] - low[0]
        
        for j in range(1, n):
            tr[j] = max(high[j] - low[j], 
                       abs(high[j] - close[j - 1]), 
                       abs(low[j] - close[j - 1]))
        
        # Calculate sum of ATR
        for j in range(period - 1, n):
            atr_sum[j] = np.sum(tr[j - period + 1:j + 1])
        
        for i in range(period - 1, n):
            # Calculate highest high and lowest low over period
            highest_high = np.max(high[i - period + 1:i + 1])
            lowest_low = np.min(low[i - period + 1:i + 1])
            
            range_val = highest_high - lowest_low
            
            if range_val > 0 and atr_sum[i] > 0:
                result[i] = 100 * np.log10(atr_sum[i] / range_val) / np.log10(period)
            else:
                result[i] = 50.0  # Default middle value
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Choppiness Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Period for CHOP calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            CHOP values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_chop(high_data, low_data, close_data, period)
        return self.format_output(result, input_type, index)


class KST(BaseIndicator):
    """
    Know Sure Thing (KST)
    
    KST is a momentum oscillator developed by Martin Pring based on the smoothed rate-of-change values.
    
    Formula: KST = (RCMA1 × 1) + (RCMA2 × 2) + (RCMA3 × 3) + (RCMA4 × 4)
    Where RCMA = SMA of ROC
    """
    
    def __init__(self):
        super().__init__("KST")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_roc(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Rate of Change"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period, n):
            if data[i - period] != 0:
                result[i] = ((data[i] - data[i - period]) / data[i - period]) * 100
            else:
                result[i] = 0.0
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            if not np.isnan(data[i]):
                window = data[i - period + 1:i + 1]
                valid_values = window[~np.isnan(window)]
                if len(valid_values) >= period:
                    result[i] = np.mean(valid_values[-period:])
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.full(n, np.nan)
        alpha = 2.0 / (period + 1)
        
        # Find first valid value
        first_valid = -1
        for i in range(n):
            if not np.isnan(data[i]):
                first_valid = i
                break
        
        if first_valid == -1:
            return result
        
        result[first_valid] = data[first_valid]
        
        for i in range(first_valid + 1, n):
            if not np.isnan(data[i]):
                result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
            else:
                result[i] = result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 roc1: int = 10, roc2: int = 15, roc3: int = 20, roc4: int = 30,
                 sma1: int = 10, sma2: int = 10, sma3: int = 10, sma4: int = 15,
                 signal: int = 9) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Know Sure Thing
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        roc1, roc2, roc3, roc4 : int
            ROC periods
        sma1, sma2, sma3, sma4 : int
            SMA periods for smoothing ROC
        signal : int, default=9
            Signal line period
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (kst, signal_line) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate ROCs
        roc_1 = self._calculate_roc(validated_data, roc1)
        roc_2 = self._calculate_roc(validated_data, roc2)
        roc_3 = self._calculate_roc(validated_data, roc3)
        roc_4 = self._calculate_roc(validated_data, roc4)
        
        # Calculate smoothed ROCs
        rcma_1 = self._calculate_sma(roc_1, sma1)
        rcma_2 = self._calculate_sma(roc_2, sma2)
        rcma_3 = self._calculate_sma(roc_3, sma3)
        rcma_4 = self._calculate_sma(roc_4, sma4)
        
        # Calculate KST
        kst = rcma_1 * 1 + rcma_2 * 2 + rcma_3 * 3 + rcma_4 * 4
        
        # Calculate signal line
        signal_line = self._calculate_ema(kst, signal)
        
        results = (kst, signal_line)
        return self.format_multiple_outputs(results, input_type, index)


class TSI(BaseIndicator):
    """
    True Strength Index (TSI)
    
    TSI is a momentum oscillator that uses moving averages of price changes.
    
    Formula: TSI = 100 * (Double Smoothed PC / Double Smoothed Absolute PC)
    Where PC = Price Change
    """
    
    def __init__(self):
        super().__init__("TSI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.full(n, np.nan)
        alpha = 2.0 / (period + 1)
        
        # Find first valid value
        first_valid = -1
        for i in range(n):
            if not np.isnan(data[i]):
                first_valid = i
                break
        
        if first_valid == -1:
            return result
        
        result[first_valid] = data[first_valid]
        
        for i in range(first_valid + 1, n):
            if not np.isnan(data[i]):
                result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
            else:
                result[i] = result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 long: int = 25, short: int = 13, signal: int = 13) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate True Strength Index
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        long : int, default=25
            Long period for first smoothing
        short : int, default=13
            Short period for second smoothing
        signal : int, default=13
            Signal line period
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (tsi, signal_line) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate price changes
        price_changes = np.diff(validated_data)
        price_changes = np.concatenate([np.array([0.0]), price_changes])
        
        # Calculate absolute price changes
        abs_price_changes = np.abs(price_changes)
        
        # First smoothing
        pc_smooth1 = self._calculate_ema(price_changes, long)
        apc_smooth1 = self._calculate_ema(abs_price_changes, long)
        
        # Second smoothing
        pc_smooth2 = self._calculate_ema(pc_smooth1, short)
        apc_smooth2 = self._calculate_ema(apc_smooth1, short)
        
        # Calculate TSI
        tsi = np.full_like(validated_data, np.nan)
        for i in range(len(validated_data)):
            if apc_smooth2[i] != 0:
                tsi[i] = 100 * (pc_smooth2[i] / apc_smooth2[i])
            else:
                tsi[i] = 0.0
        
        # Calculate signal line
        signal_line = self._calculate_ema(tsi, signal)
        
        results = (tsi, signal_line)
        return self.format_multiple_outputs(results, input_type, index)


class VI(BaseIndicator):
    """
    Vortex Indicator (VI+ and VI-)
    
    The Vortex Indicator identifies the start of a new trend or the continuation of an existing trend.
    
    Formula:
    VI+ = Sum(|Close - Prior Low|, n) / Sum(True Range, n)
    VI- = Sum(|Close - Prior High|, n) / Sum(True Range, n)
    """
    
    def __init__(self):
        super().__init__("VI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vi(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> Tuple[np.ndarray, np.ndarray]:
        """Numba optimized Vortex Indicator calculation"""
        n = len(close)
        vi_plus = np.full(n, np.nan)
        vi_minus = np.full(n, np.nan)
        
        for i in range(period, n):
            sum_vm_plus = 0.0
            sum_vm_minus = 0.0
            sum_tr = 0.0
            
            for j in range(period):
                idx = i - period + j + 1
                
                # Vortex Movement
                vm_plus = abs(close[idx] - low[idx - 1])
                vm_minus = abs(close[idx] - high[idx - 1])
                
                # True Range
                tr = max(high[idx] - low[idx],
                        abs(high[idx] - close[idx - 1]),
                        abs(low[idx] - close[idx - 1]))
                
                sum_vm_plus += vm_plus
                sum_vm_minus += vm_minus
                sum_tr += tr
            
            if sum_tr > 0:
                vi_plus[i] = sum_vm_plus / sum_tr
                vi_minus[i] = sum_vm_minus / sum_tr
            else:
                vi_plus[i] = 0.0
                vi_minus[i] = 0.0
        
        return vi_plus, vi_minus
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Vortex Indicator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Period for VI calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (vi_plus, vi_minus) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period + 1, len(close_data))
        
        vi_plus, vi_minus = self._calculate_vi(high_data, low_data, close_data, period)
        
        results = (vi_plus, vi_minus)
        return self.format_multiple_outputs(results, input_type, index)


class GatorOscillator(BaseIndicator):
    """
    Gator Oscillator (Bill Williams)
    
    The Gator Oscillator shows the convergence/divergence of the Alligator lines.
    
    Formula:
    Upper Histogram = |Jaw - Teeth|
    Lower Histogram = -|Teeth - Lips|
    """
    
    def __init__(self):
        super().__init__("Gator")
    
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
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 jaw_period: int = 13, teeth_period: int = 8, lips_period: int = 5) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Gator Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically (high + low) / 2)
        jaw_period : int, default=13
            Period for Jaw line
        teeth_period : int, default=8
            Period for Teeth line
        lips_period : int, default=5
            Period for Lips line
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (upper_histogram, lower_histogram) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate SMMA for each line
        jaw = self._calculate_smma(validated_data, jaw_period)
        teeth = self._calculate_smma(validated_data, teeth_period)
        lips = self._calculate_smma(validated_data, lips_period)
        
        # Calculate histograms
        upper_histogram = np.abs(jaw - teeth)
        lower_histogram = -np.abs(teeth - lips)
        
        results = (upper_histogram, lower_histogram)
        return self.format_multiple_outputs(results, input_type, index)


class STC(BaseIndicator):
    """
    Schaff Trend Cycle (STC)
    
    STC is a cyclical oscillator that combines slow stochastics and the MACD.
    
    Formula: Applies stochastic calculation twice - first to MACD values, then to the result.
    """
    
    def __init__(self):
        super().__init__("STC")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.full(n, np.nan)
        alpha = 2.0 / (period + 1)
        
        # Find first valid value
        first_valid = -1
        for i in range(n):
            if not np.isnan(data[i]):
                first_valid = i
                break
        
        if first_valid == -1:
            return result
        
        result[first_valid] = data[first_valid]
        
        for i in range(first_valid + 1, n):
            if not np.isnan(data[i]):
                result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
            else:
                result[i] = result[i - 1]
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _stochastic_calculation(data: np.ndarray, period: int, smooth: int) -> np.ndarray:
        """Apply stochastic calculation to any data series"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Find highest and lowest values in the period
            window = data[i - period + 1:i + 1]
            valid_window = window[~np.isnan(window)]
            
            if len(valid_window) > 0:
                highest = np.max(valid_window)
                lowest = np.min(valid_window)
                
                if highest != lowest:
                    result[i] = ((data[i] - lowest) / (highest - lowest)) * 100
                else:
                    result[i] = 50.0  # Middle value when no range
        
        # Smooth the result
        if smooth > 1:
            smoothed = np.full(n, np.nan)
            for i in range(smooth - 1, n):
                if not np.isnan(result[i]):
                    window = result[i - smooth + 1:i + 1]
                    valid_values = window[~np.isnan(window)]
                    if len(valid_values) >= smooth:
                        smoothed[i] = np.mean(valid_values[-smooth:])
            result = smoothed
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 fast: int = 23, slow: int = 50, cycle: int = 10, smooth1: int = 3, smooth2: int = 3) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Schaff Trend Cycle
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast : int, default=23
            Fast EMA period
        slow : int, default=50
            Slow EMA period
        cycle : int, default=10
            Cycle period for stochastic calculations
        smooth1 : int, default=3
            First smoothing period
        smooth2 : int, default=3
            Second smoothing period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            STC values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate MACD
        fast_ema = self._calculate_ema(validated_data, fast)
        slow_ema = self._calculate_ema(validated_data, slow)
        macd = fast_ema - slow_ema
        
        # First stochastic calculation on MACD
        stoch1 = self._stochastic_calculation(macd, cycle, smooth1)
        
        # Second stochastic calculation on the result
        stc = self._stochastic_calculation(stoch1, cycle, smooth2)
        
        return self.format_output(stc, input_type, index)