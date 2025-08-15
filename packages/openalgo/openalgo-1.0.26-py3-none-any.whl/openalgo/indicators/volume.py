# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Volume Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class OBV(BaseIndicator):
    """
    On Balance Volume
    
    OBV is a momentum indicator that uses volume flow to predict changes in stock price.
    It adds volume on up days and subtracts volume on down days.
    
    Formula:
    If Close > Previous Close: OBV = Previous OBV + Volume
    If Close < Previous Close: OBV = Previous OBV - Volume  
    If Close = Previous Close: OBV = Previous OBV
    """
    
    def __init__(self):
        super().__init__("OBV")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized OBV calculation"""
        n = len(close)
        # Seed baseline with first volume (TA-Lib behaviour)
        obv = np.empty(n)
        obv[0] = volume[0]
        
        # Calculate OBV
        for i in range(1, n):
            if close[i] > close[i-1]:
                obv[i] = obv[i-1] + volume[i]
            elif close[i] < close[i-1]:
                obv[i] = obv[i-1] - volume[i]
            else:
                obv[i] = obv[i-1]
        
        return obv
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate On Balance Volume
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            OBV values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_obv(close_data, volume_data)
        return self.format_output(result, input_type, index)


class VWAP(BaseIndicator):
    """
    Volume Weighted Average Price
    
    VWAP is the average price a security has traded at throughout the day, 
    based on both volume and price. It gives more weight to prices with higher volume.
    
    Formula: VWAP = Σ(Typical Price × Volume) / Σ(Volume)
    Where: Typical Price = (High + Low + Close) / 3
    """
    
    def __init__(self):
        super().__init__("VWAP")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                       volume: np.ndarray, period: int = 0) -> np.ndarray:
        """Numba optimized VWAP calculation"""
        n = len(close)
        vwap = np.empty(n)
        
        # Calculate typical price
        typical_price = (high + low + close) / 3.0
        
        if period == 0:  # Cumulative VWAP
            cumulative_pv = 0.0
            cumulative_volume = 0.0
            
            for i in range(n):
                pv = typical_price[i] * volume[i]
                cumulative_pv += pv
                cumulative_volume += volume[i]
                
                if cumulative_volume > 0:
                    vwap[i] = cumulative_pv / cumulative_volume
                else:
                    vwap[i] = typical_price[i]
        else:  # Rolling VWAP
            vwap[:period-1] = np.nan
            
            for i in range(period - 1, n):
                sum_pv = 0.0
                sum_volume = 0.0
                
                for j in range(period):
                    idx = i - period + 1 + j
                    pv = typical_price[idx] * volume[idx]
                    sum_pv += pv
                    sum_volume += volume[idx]
                
                if sum_volume > 0:
                    vwap[i] = sum_pv / sum_volume
                else:
                    vwap[i] = typical_price[i]
        
        return vwap
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int = 0) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Weighted Average Price
        
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
        period : int, default=0
            Period for rolling VWAP. If 0, calculates cumulative VWAP
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            VWAP values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        
        if period > 0:
            self.validate_period(period, len(close_data))
        
        result = self._calculate_vwap(high_data, low_data, close_data, volume_data, period)
        return self.format_output(result, input_type, index)


class MFI(BaseIndicator):
    """
    Money Flow Index
    
    MFI is a momentum indicator that uses both price and volume to measure 
    buying and selling pressure. It is also known as Volume-Weighted RSI.
    
    Formula:
    1. Typical Price = (High + Low + Close) / 3
    2. Raw Money Flow = Typical Price × Volume
    3. Positive/Negative Money Flow based on Typical Price comparison
    4. Money Ratio = Positive Money Flow / Negative Money Flow
    5. MFI = 100 - (100 / (1 + Money Ratio))
    """
    
    def __init__(self):
        super().__init__("MFI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_mfi(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized MFI aligned with TA-Lib"""
        n = len(close)
        result = np.full(n, np.nan)
        
        tp = (high + low + close) / 3.0
        rmf = tp * volume  # raw money flow
        
        # Pre-compute positive / negative flows per bar
        pos_raw = np.zeros(n)
        neg_raw = np.zeros(n)
        for i in range(1, n):
            if tp[i] > tp[i - 1]:
                pos_raw[i] = rmf[i]
            elif tp[i] < tp[i - 1]:
                neg_raw[i] = rmf[i]
        
        # Rolling window sums
        pos_sum = 0.0
        neg_sum = 0.0
        for i in range(1, n):
            pos_sum += pos_raw[i]
            neg_sum += neg_raw[i]
            
            if i >= period:
                pos_sum -= pos_raw[i - period]
                neg_sum -= neg_raw[i - period]
            
            if i >= period - 1:
                if neg_sum == 0:
                    result[i] = 100.0
                else:
                    m_ratio = pos_sum / neg_sum
                    result[i] = 100.0 - (100.0 / (1.0 + m_ratio))
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Money Flow Index
        
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
        period : int, default=14
            Number of periods for MFI calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            MFI values (range: 0 to 100) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_mfi(high_data, low_data, close_data, volume_data, period)
        return self.format_output(result, input_type, index)


class ADL(BaseIndicator):
    """
    Accumulation/Distribution Line
    
    ADL is a volume-based indicator designed to measure the cumulative flow 
    of money into and out of a security.
    
    Formula: ADL = Previous ADL + Money Flow Volume
    Where: Money Flow Volume = Volume × ((Close - Low) - (High - Close)) / (High - Low)
    """
    
    def __init__(self):
        super().__init__("ADL")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_adl(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      volume: np.ndarray) -> np.ndarray:
        """Numba optimized ADL calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        result[0] = 0.0  # Seed baseline at 0 as per common definition
        
        for i in range(1, n):
            if high[i] != low[i]:
                mfm = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])
            else:
                mfm = 0.0
            
            mfv = mfm * volume[i]
            result[i] = result[i - 1] + mfv
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Accumulation/Distribution Line
        
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
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ADL values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        
        result = self._calculate_adl(high_data, low_data, close_data, volume_data)
        return self.format_output(result, input_type, index)


class CMF(BaseIndicator):
    """
    Chaikin Money Flow
    
    CMF is the sum of Money Flow Volume over a period divided by the sum of volume.
    
    Formula: CMF = Sum(Money Flow Volume, n) / Sum(Volume, n)
    """
    
    def __init__(self):
        super().__init__("CMF")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_cmf(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized CMF calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            sum_mfv = 0.0
            sum_volume = 0.0
            
            for j in range(period):
                idx = i - period + 1 + j
                
                if high[idx] != low[idx]:
                    mfm = ((close[idx] - low[idx]) - (high[idx] - close[idx])) / (high[idx] - low[idx])
                else:
                    mfm = 0
                
                mfv = mfm * volume[idx]
                sum_mfv += mfv
                sum_volume += volume[idx]
            
            if sum_volume > 0:
                result[i] = sum_mfv / sum_volume
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Chaikin Money Flow
        
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
        period : int, default=20
            Number of periods for CMF calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            CMF values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_cmf(high_data, low_data, close_data, volume_data, period)
        return self.format_output(result, input_type, index)


class EMV(BaseIndicator):
    """
    Ease of Movement - matches TradingView exactly
    
    EMV relates price change to volume and is particularly useful 
    for assessing the strength of a trend. TradingView version includes
    automatic SMA smoothing.
    
    TradingView Formula: EMV = SMA(div * change(hl2) * (high - low) / volume, length)
    Where: hl2 = (high + low) / 2
           change(hl2) = current hl2 - previous hl2
    """
    
    def __init__(self):
        super().__init__("EMV")
    
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
    def _calculate_emv_raw(high: np.ndarray, low: np.ndarray, volume: np.ndarray,
                          divisor: float) -> np.ndarray:
        """Calculate raw EMV values before smoothing - matches TradingView formula"""
        n = len(high)
        result = np.full(n, np.nan)
        
        for i in range(1, n):
            # Calculate hl2 (typical price)
            hl2_current = (high[i] + low[i]) / 2
            hl2_previous = (high[i-1] + low[i-1]) / 2
            
            # Change in hl2 (ta.change(hl2) in TradingView)
            change_hl2 = hl2_current - hl2_previous
            
            # High - Low range
            high_low_range = high[i] - low[i]
            
            # TradingView formula: div * change(hl2) * (high - low) / volume
            if volume[i] > 0 and high_low_range > 0:
                result[i] = divisor * change_hl2 * high_low_range / volume[i]
            else:
                result[i] = 0.0
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 length: int = 14, divisor: int = 10000) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Ease of Movement - matches TradingView exactly
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        length : int, default=14
            Period for SMA smoothing (TradingView default)
        divisor : int, default=10000
            Divisor for scaling EMV values (TradingView default)
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            EMV values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, volume_data = self.align_arrays(high_data, low_data, volume_data)
        self.validate_period(length, len(high_data))
        
        if divisor <= 0:
            raise ValueError(f"Divisor must be positive, got {divisor}")
        
        # Calculate raw EMV values
        raw_emv = self._calculate_emv_raw(high_data, low_data, volume_data, float(divisor))
        
        # Apply SMA smoothing (TradingView always smooths)
        smoothed_emv = self._calculate_sma(raw_emv, length)
        
        return self.format_output(smoothed_emv, input_type, index)


class FI(BaseIndicator):
    """
    Elder Force Index - matches TradingView exactly
    
    The Elder Force Index (EFI) combines price and volume to assess the power 
    used to move the price of an asset. TradingView version applies EMA smoothing
    to reduce noise.
    
    TradingView Formula: EFI = EMA(volume * change(close), length)
    Where: change(close) = close - close[1]
    """
    
    def __init__(self):
        super().__init__("Elder Force Index")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.full(n, np.nan)
        alpha = 2.0 / (period + 1)
        
        # Find first valid (non-NaN) value
        first_valid = -1
        for i in range(n):
            if not np.isnan(data[i]):
                first_valid = i
                result[i] = data[i]
                break
        
        if first_valid == -1:
            return result
        
        # Calculate EMA
        for i in range(first_valid + 1, n):
            if not np.isnan(data[i]):
                result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_raw_fi(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Calculate raw Force Index values"""
        n = len(close)
        result = np.full(n, np.nan)
        
        for i in range(1, n):
            # TradingView: ta.change(close) * volume
            price_change = close[i] - close[i-1]
            result[i] = volume[i] * price_change
        
        return result
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 length: int = 13) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Elder Force Index - matches TradingView exactly
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        length : int, default=13
            Period for EMA smoothing (TradingView default)
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Elder Force Index values in the same format as input
            
        Raises:
        -------
        ValueError
            If no volume is provided by the data vendor (cumulative volume is zero)
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        self.validate_period(length, len(close_data))
        
        # TradingView volume validation: check if cumulative volume is zero
        cumulative_volume = np.nansum(volume_data)
        if cumulative_volume == 0:
            raise ValueError("No volume is provided by the data vendor.")
        
        # Calculate raw Force Index: volume * change(close)
        raw_fi = self._calculate_raw_fi(close_data, volume_data)
        
        # Apply EMA smoothing (TradingView: ta.ema(raw_fi, length))
        smoothed_fi = self._calculate_ema(raw_fi, length)
        
        return self.format_output(smoothed_fi, input_type, index)


class NVI(BaseIndicator):
    """
    Negative Volume Index
    
    NVI focuses on days when volume decreases from the previous day.
    
    Formula: If Volume < Previous Volume: NVI = Previous NVI × (1 + PCR)
             Else: NVI = Previous NVI
    Where: PCR = (Close - Previous Close) / Previous Close
    """
    
    def __init__(self):
        super().__init__("NVI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_nvi(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized NVI calculation"""
        n = len(close)
        result = np.empty(n)
        
        result[0] = 1000  # Start with base value
        
        for i in range(1, n):
            if volume[i] < volume[i-1]:
                pcr = (close[i] - close[i-1]) / close[i-1] if close[i-1] != 0 else 0
                result[i] = result[i-1] * (1 + pcr)
            else:
                result[i] = result[i-1]
        
        return result
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Negative Volume Index
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            NVI values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_nvi(close_data, volume_data)
        return self.format_output(result, input_type, index)


class PVI(BaseIndicator):
    """
    Positive Volume Index
    
    PVI focuses on days when volume increases from the previous day.
    
    Formula: If Volume > Previous Volume: PVI = Previous PVI × (1 + PCR)
             Else: PVI = Previous PVI
    Where: PCR = (Close - Previous Close) / Previous Close
    """
    
    def __init__(self):
        super().__init__("PVI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_pvi(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized PVI calculation"""
        n = len(close)
        result = np.empty(n)
        
        result[0] = 1000  # Start with base value
        
        for i in range(1, n):
            if volume[i] > volume[i-1]:
                pcr = (close[i] - close[i-1]) / close[i-1] if close[i-1] != 0 else 0
                result[i] = result[i-1] * (1 + pcr)
            else:
                result[i] = result[i-1]
        
        return result
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Positive Volume Index
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            PVI values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_pvi(close_data, volume_data)
        return self.format_output(result, input_type, index)


class VOLOSC(BaseIndicator):
    """
    Volume Oscillator
    
    Volume Oscillator shows the relationship between two moving averages of volume.
    
    Formula: VO = ((Short MA - Long MA) / Long MA) × 100
    """
    
    def __init__(self):
        super().__init__("VO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, volume: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 5, slow_period: int = 10) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Oscillator
        
        Parameters:
        -----------
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        fast_period : int, default=5
            Fast moving average period
        slow_period : int, default=10
            Slow moving average period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Volume Oscillator values in the same format as input
        """
        validated_volume, input_type, index = self.validate_input(volume)
        
        # Calculate moving averages
        fast_ma = self._calculate_sma(validated_volume, fast_period)
        slow_ma = self._calculate_sma(validated_volume, slow_period)
        
        # Calculate Volume Oscillator
        vo = np.empty_like(validated_volume)
        for i in range(len(validated_volume)):
            if slow_ma[i] != 0:
                vo[i] = ((fast_ma[i] - slow_ma[i]) / slow_ma[i]) * 100
            else:
                vo[i] = 0
        
        return self.format_output(vo, input_type, index)


class VROC(BaseIndicator):
    """
    Volume Rate of Change
    
    VROC measures the rate of change in volume.
    
    Formula: VROC = ((Volume - Volume[n periods ago]) / Volume[n periods ago]) × 100
    """
    
    def __init__(self):
        super().__init__("VROC")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vroc(volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized VROC calculation"""
        n = len(volume)
        result = np.full(n, np.nan)
        
        for i in range(period, n):
            if volume[i - period] != 0:
                result[i] = ((volume[i] - volume[i - period]) / volume[i - period]) * 100
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, volume: Union[np.ndarray, pd.Series, list], period: int = 25) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Rate of Change
        
        Parameters:
        -----------
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int, default=25
            Number of periods to look back
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            VROC values in the same format as input
        """
        validated_volume, input_type, index = self.validate_input(volume)
        self.validate_period(period, len(validated_volume))
        
        result = self._calculate_vroc(validated_volume, period)
        return self.format_output(result, input_type, index)


class KlingerVolumeOscillator(BaseIndicator):
    """
    Klinger Volume Oscillator (KVO) - matches TradingView exactly
    
    The KVO is designed to predict price reversals in a market by comparing 
    volume to price movement.
    
    TradingView Formula:
    xTrend = iff(hlc3 > hlc3[1], volume * 100, -volume * 100)
    xFast = ema(xTrend, FastX)
    xSlow = ema(xTrend, SlowX)
    xKVO = xFast - xSlow
    xTrigger = ema(xKVO, TrigLen)
    """
    
    def __init__(self):
        super().__init__("KVO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_kvo_tv(high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray,
                         trig_len: int, fast_x: int, slow_x: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate KVO using exact TradingView logic
        TradingView formula:
        xTrend = iff(hlc3 > hlc3[1], volume * 100, -volume * 100)
        xFast = ema(xTrend, FastX)
        xSlow = ema(xTrend, SlowX)
        xKVO = xFast - xSlow
        xTrigger = ema(xKVO, TrigLen)
        """
        n = len(close)
        
        # Calculate hlc3 (typical price)
        hlc3 = (high + low + close) / 3.0
        
        # Calculate xTrend using TradingView logic
        # xTrend = iff(hlc3 > hlc3[1], volume * 100, -volume * 100)
        x_trend = np.zeros(n)  # Initialize with zeros instead of NaN
        x_trend[0] = volume[0] * 100.0  # First value assumes positive
        
        for i in range(1, n):
            if hlc3[i] > hlc3[i - 1]:
                x_trend[i] = volume[i] * 100.0
            else:
                x_trend[i] = -volume[i] * 100.0
        
        # Calculate EMAs using TradingView logic
        # xFast = ema(xTrend, FastX)
        x_fast = np.zeros(n)
        fast_alpha = 2.0 / (fast_x + 1)
        
        # Initialize EMA with first value
        x_fast[0] = x_trend[0]
        for i in range(1, n):
            x_fast[i] = fast_alpha * x_trend[i] + (1 - fast_alpha) * x_fast[i - 1]
        
        # xSlow = ema(xTrend, SlowX)
        x_slow = np.zeros(n)
        slow_alpha = 2.0 / (slow_x + 1)
        
        # Initialize EMA with first value
        x_slow[0] = x_trend[0]
        for i in range(1, n):
            x_slow[i] = slow_alpha * x_trend[i] + (1 - slow_alpha) * x_slow[i - 1]
        
        # xKVO = xFast - xSlow
        x_kvo = x_fast - x_slow
        
        
        # xTrigger = ema(xKVO, TrigLen)
        x_trigger = np.zeros(n)
        trig_alpha = 2.0 / (trig_len + 1)
        
        # Initialize trigger EMA with first KVO value
        x_trigger[0] = x_kvo[0]
        for i in range(1, n):
            x_trigger[i] = trig_alpha * x_kvo[i] + (1 - trig_alpha) * x_trigger[i - 1]
        
        return x_kvo, x_trigger
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 trig_len: int = 13, fast_x: int = 34, slow_x: int = 55) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Calculate Klinger Volume Oscillator - matches TradingView exactly
        
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
        trig_len : int, default=13
            Trigger line EMA period (TradingView: TrigLen)
        fast_x : int, default=34
            Fast EMA period (TradingView: FastX)
        slow_x : int, default=55
            Slow EMA period (TradingView: SlowX)
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (kvo, trigger) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        
        # Validate parameters
        for param, name in [(trig_len, "trig_len"), (fast_x, "fast_x"), (slow_x, "slow_x")]:
            if param <= 0:
                raise ValueError(f"{name} must be positive, got {param}")
        
        kvo, trigger = self._calculate_kvo_tv(high_data, low_data, close_data, volume_data, trig_len, fast_x, slow_x)
        
        results = (kvo, trigger)
        return self.format_multiple_outputs(results, input_type, index)


class PriceVolumeTrend(BaseIndicator):
    """
    Price Volume Trend (PVT)
    
    PVT combines price and volume to show the cumulative volume based on 
    price changes.
    
    Formula: PVT = Previous PVT + (Volume × (Close - Previous Close) / Previous Close)
    """
    
    def __init__(self):
        super().__init__("PVT")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_pvt(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized PVT calculation"""
        n = len(close)
        pvt = np.zeros(n)
        
        for i in range(1, n):
            if close[i-1] != 0:
                price_change_ratio = (close[i] - close[i-1]) / close[i-1]
                pvt[i] = pvt[i-1] + (volume[i] * price_change_ratio)
            else:
                pvt[i] = pvt[i-1]
        
        return pvt
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Price Volume Trend
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            PVT values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_pvt(close_data, volume_data)
        return self.format_output(result, input_type, index)


class RVOL(BaseIndicator):
    """
    Relative Volume (RVOL)
    
    Compares current volume to average volume over a specified period.
    
    Formula: RVOL = Current Volume / Average Volume
    """
    
    def __init__(self):
        super().__init__("Relative Volume")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rvol(volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized RVOL calculation"""
        n = len(volume)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Calculate average volume over the period
            avg_volume = 0.0
            for j in range(i - period + 1, i + 1):
                avg_volume += volume[j]
            avg_volume = avg_volume / period
            
            # Avoid division by zero
            if avg_volume > 0:
                result[i] = volume[i] / avg_volume
            else:
                result[i] = 1.0  # Default to 1.0 when average volume is 0
        
        return result
    
    def calculate(self, volume: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Relative Volume
        
        Parameters:
        -----------
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int, default=20
            Period for average volume calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            RVOL values in the same format as input
        """
        volume_data, input_type, index = self.validate_input(volume)
        self.validate_period(period, len(volume_data))
        
        result = self._calculate_rvol(volume_data, period)
        return self.format_output(result, input_type, index)