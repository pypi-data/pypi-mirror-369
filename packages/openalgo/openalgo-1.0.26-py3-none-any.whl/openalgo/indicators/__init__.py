# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators Library

A high-performance technical analysis library with NumPy and Numba optimizations.
Provides TradingView-like syntax for easy use.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional

# Import all indicator classes
from .trend import (SMA, EMA, WMA, DEMA, TEMA, Supertrend, Ichimoku, HMA, VWMA, 
                   ALMA, KAMA, ZLEMA, T3, FRAMA, ChandeKrollStop, TRIMA, 
                   McGinley, VIDYA, Alligator, MovingAverageEnvelopes)
from .momentum import (RSI, MACD, Stochastic, CCI, WilliamsR, BOP, 
                      ElderRay, Fisher, CRSI)
from .volatility import (ATR, BollingerBands, Keltner, Donchian,
                        Chaikin, NATR, RVI as VolatilityRVI, ULTOSC, STDDEV, TRANGE, MASS,
                        BBPercent, BBWidth, ChandelierExit,
                        HistoricalVolatility, UlcerIndex, STARC)
from .volume import (OBV, VWAP, MFI, ADL, CMF, EMV, FI, NVI, PVI, VOLOSC, VROC,
                    KlingerVolumeOscillator, PriceVolumeTrend, RVOL)
from .oscillators import (ROC, CMO, TRIX, UO, AO, AC, PPO, PO, DPO, AROONOSC,
                         StochRSI, RVI, CHO, CHOP, KST, TSI, VI, 
                         GatorOscillator, STC)
from .statistics import (LINREG, LRSLOPE, CORREL, BETA, VAR, TSF, MEDIAN, MODE)
from .hybrid import (ADX, Aroon, PivotPoints, SAR, DMI, PSAR, HT,
                    ZigZag, WilliamsFractals, RWI)
from .utils import (crossover, crossunder, highest, lowest, change, roc, 
                   sma as utils_sma, ema as utils_ema, stdev, validate_input)


class TechnicalAnalysis:
    """
    Main technical analysis interface providing TradingView-like syntax
    
    Usage:
    ------
    from openalgo import ta
    
    # Trend indicators
    sma_20 = ta.sma(close, 20)
    ema_50 = ta.ema(close, 50)
    [supertrend, direction] = ta.supertrend(high, low, close, 10, 3)
    
    # Momentum indicators
    rsi_14 = ta.rsi(close, 14)
    [macd_line, signal_line, histogram] = ta.macd(close, 12, 26, 9)
    
    # Volatility indicators
    [upper, middle, lower] = ta.bbands(close, 20, 2)
    atr_14 = ta.atr(high, low, close, 14)
    
    # Volume indicators
    obv_values = ta.obv(close, volume)
    vwap_values = ta.vwap(high, low, close, volume)
    """
    
    def __init__(self):
        # Initialize all indicator classes
        # Trend indicators
        self._sma = SMA()
        self._ema = EMA()
        self._wma = WMA()
        self._dema = DEMA()
        self._tema = TEMA()
        self._hma = HMA()
        self._vwma = VWMA()
        self._alma = ALMA()
        self._kama = KAMA()
        self._zlema = ZLEMA()
        self._t3 = T3()
        self._frama = FRAMA()
        self._supertrend = Supertrend()
        self._ichimoku = Ichimoku()
        self._chande_kroll_stop = ChandeKrollStop()
        self._trima = TRIMA()
        self._mcginley_dynamic = McGinley()
        self._vidya = VIDYA()
        self._alligator = Alligator()
        self._ma_envelopes = MovingAverageEnvelopes()
        
        # Momentum indicators
        self._rsi = RSI()
        self._macd = MACD()
        self._stochastic = Stochastic()
        self._cci = CCI()
        self._williams_r = WilliamsR()
        self._balance_of_power = BOP()
        self._elder_ray = ElderRay()
        self._fisher_transform = Fisher()
        self._connors_rsi = CRSI()
        
        # Volatility indicators
        self._atr = ATR()
        self._bbands = BollingerBands()
        self._keltner = Keltner()
        self._donchian = Donchian()
        self._chaikin_volatility = Chaikin()
        self._natr = NATR()
        self._rvi = RVI()  # Oscillator RVI (Relative Vigor Index)
        self._rvol = RVOL()  # Relative Volume
        self._ultosc = ULTOSC()
        self._stddev = STDDEV()
        self._trange = TRANGE()
        self._mass = MASS()
        self._bbands_percent_b = BBPercent()
        self._bbands_bandwidth = BBWidth()
        self._chandelier_exit = ChandelierExit()
        self._hv = HistoricalVolatility()
        self._ulcer_index = UlcerIndex()
        self._starc_bands = STARC()
        
        # Volume indicators
        self._obv = OBV()
        self._vwap = VWAP()
        self._mfi = MFI()
        self._adl = ADL()
        self._cmf = CMF()
        self._emv = EMV()
        self._fi = FI()
        self._nvi = NVI()
        self._pvi = PVI()
        self._vo = VOLOSC()
        self._vroc = VROC()
        self._klinger_vo = KlingerVolumeOscillator()
        self._pvt = PriceVolumeTrend()
        
        # Oscillators
        self._roc = ROC()
        self._cmo = CMO()
        self._trix = TRIX()
        self._uo = UO()
        self._ao = AO()
        self._ac = AC()
        self._ppo = PPO()
        self._po = PO()
        self._dpo = DPO()
        self._aroonosc = AROONOSC()
        self._stoch_rsi = StochRSI()
        self._rvi_osc = RVI()
        self._chaikin_osc = CHO()
        self._chop = CHOP()
        self._kst = KST()
        self._tsi = TSI()
        self._vi = VI()
        self._stc = STC()
        self._gator_oscillator = GatorOscillator()
        
        # Statistical indicators
        self._linearreg = LINREG()
        self._linearreg_slope = LRSLOPE()
        self._correl = CORREL()
        self._beta = BETA()
        self._var = VAR()
        self._tsf = TSF()
        self._median = MEDIAN()
        self._mode = MODE()
        
        # Hybrid indicators
        self._adx = ADX()
        self._aroon = Aroon()
        self._pivot_points = PivotPoints()
        self._sar = SAR()
        self._dmi = DMI()
        self._psar = PSAR()
        self._ht_trendline = HT()
        self._zigzag = ZigZag()
        self._williams_fractals = WilliamsFractals()
        self._random_walk_index = RWI()
    
    # =================== TREND INDICATORS ===================
    
    def sma(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Simple Moving Average
        
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
        return self._sma.calculate(data, period)
    
    def ema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Exponential Moving Average
        
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
        return self._ema.calculate(data, period)
    
    def wma(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Weighted Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        np.ndarray
            Array of WMA values
        """
        return self._wma.calculate(data, period)
    
    def dema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Double Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        np.ndarray
            Array of DEMA values
        """
        return self._dema.calculate(data, period)
    
    def tema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Triple Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        np.ndarray
            Array of TEMA values
        """
        return self._tema.calculate(data, period)
    
    def supertrend(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   period: int = 10, multiplier: float = 3.0) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Supertrend Indicator
        
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
        """
        return self._supertrend.calculate(high, low, close, period, multiplier)
    
    def ichimoku(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 conversion_periods: int = 9, base_periods: int = 26,
                 lagging_span2_periods: int = 52, displacement: int = 26) -> Tuple[np.ndarray, ...]:
        """
        Ichimoku Cloud - matches TradingView exactly
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        conversion_periods : int, default=9
            Conversion Line Length (TradingView: conversionPeriods)
        base_periods : int, default=26
            Base Line Length (TradingView: basePeriods)
        lagging_span2_periods : int, default=52
            Leading Span B Length (TradingView: laggingSpan2Periods)
        displacement : int, default=26
            Lagging Span displacement (TradingView: displacement)
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            (conversion_line, base_line, leading_span_a, leading_span_b, lagging_span)
        """
        return self._ichimoku.calculate(high, low, close, conversion_periods, 
                                       base_periods, lagging_span2_periods, displacement)
    
    def hma(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """Hull Moving Average"""
        return self._hma.calculate(data, period)
    
    def vwma(self, data: Union[np.ndarray, pd.Series, list],
             volume: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """Volume Weighted Moving Average"""
        return self._vwma.calculate(data, volume, period)
    
    def alma(self, data: Union[np.ndarray, pd.Series, list], 
             period: int = 21, offset: float = 0.85, sigma: float = 6.0) -> np.ndarray:
        """Arnaud Legoux Moving Average"""
        return self._alma.calculate(data, period, offset, sigma)
    
    def kama(self, data: Union[np.ndarray, pd.Series, list],
             length: int = 14, fast_length: int = 2, slow_length: int = 30) -> np.ndarray:
        """Kaufman's Adaptive Moving Average - matches TradingView exactly"""
        return self._kama.calculate(data, length, fast_length, slow_length)
    
    def zlema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """Zero Lag Exponential Moving Average"""
        return self._zlema.calculate(data, period)
    
    def t3(self, data: Union[np.ndarray, pd.Series, list],
           period: int = 21, v_factor: float = 0.7) -> np.ndarray:
        """T3 Moving Average"""
        return self._t3.calculate(data, period, v_factor)
    
    def frama(self, high: Union[np.ndarray, pd.Series, list],
              low: Union[np.ndarray, pd.Series, list], period: int = 26) -> Union[np.ndarray, pd.Series]:
        """Fractal Adaptive Moving Average - matches TradingView exactly"""
        return self._frama.calculate(high, low, period)
    
    # =================== MOMENTUM INDICATORS ===================
    
    def rsi(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """
        Relative Strength Index
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for RSI calculation
            
        Returns:
        --------
        np.ndarray
            Array of RSI values
        """
        return self._rsi.calculate(data, period)
    
    def macd(self, data: Union[np.ndarray, pd.Series, list], 
             fast_period: int = 12, slow_period: int = 26, 
             signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Moving Average Convergence Divergence
        
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
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (macd_line, signal_line, histogram)
        """
        return self._macd.calculate(data, fast_period, slow_period, signal_period)
    
    def stochastic(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   k_period: int = 14, d_period: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Stochastic Oscillator
        
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
            Period for %D calculation
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray]
            (k_percent, d_percent)
        """
        return self._stochastic.calculate(high, low, close, k_period, d_period)
    
    def cci(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            period: int = 20) -> np.ndarray:
        """
        Commodity Channel Index
        
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
        np.ndarray
            Array of CCI values
        """
        return self._cci.calculate(high, low, close, period)
    
    def williams_r(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   period: int = 14) -> np.ndarray:
        """
        Williams %R
        
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
        np.ndarray
            Array of Williams %R values
        """
        return self._williams_r.calculate(high, low, close, period)
    
    # =================== VOLATILITY INDICATORS ===================
    
    def atr(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            period: int = 14) -> np.ndarray:
        """
        Average True Range
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Number of periods for ATR calculation
            
        Returns:
        --------
        np.ndarray
            Array of ATR values
        """
        return self._atr.calculate(high, low, close, period)
    
    def bbands(self, data: Union[np.ndarray, pd.Series, list],
               period: int = 20, std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Bollinger Bands
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=20
            Number of periods for moving average and standard deviation
        std_dev : float, default=2.0
            Number of standard deviations for the bands
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (upper_band, middle_band, lower_band)
        """
        return self._bbands.calculate(data, period, std_dev)
    
    def keltner(self, high: Union[np.ndarray, pd.Series, list],
                        low: Union[np.ndarray, pd.Series, list],
                        close: Union[np.ndarray, pd.Series, list],
                        ema_period: int = 20, atr_period: int = 10, 
                        multiplier: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Keltner Channel
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        ema_period : int, default=20
            Period for the EMA calculation
        atr_period : int, default=10
            Period for the ATR calculation
        multiplier : float, default=2.0
            Multiplier for the ATR
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (upper_channel, middle_line, lower_channel)
        """
        return self._keltner.calculate(high, low, close, ema_period, atr_period, multiplier)
    
    def donchian(self, high: Union[np.ndarray, pd.Series, list],
                         low: Union[np.ndarray, pd.Series, list],
                         period: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Donchian Channel
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        period : int, default=20
            Number of periods for the channel calculation
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (upper_channel, middle_line, lower_channel)
        """
        return self._donchian.calculate(high, low, period)
    
    def chaikin(self, high: Union[np.ndarray, pd.Series, list],
                          low: Union[np.ndarray, pd.Series, list],
                          ema_period: int = 10, roc_period: int = 10) -> np.ndarray:
        """Chaikin Volatility"""
        return self._chaikin_volatility.calculate(high, low, ema_period, roc_period)
    
    def natr(self, high: Union[np.ndarray, pd.Series, list],
             low: Union[np.ndarray, pd.Series, list],
             close: Union[np.ndarray, pd.Series, list],
             period: int = 14) -> np.ndarray:
        """Normalized Average True Range"""
        return self._natr.calculate(high, low, close, period)
    
    def rvol(self, volume: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """Relative Volume"""
        return self._rvol.calculate(volume, period)
    
    def ultimate_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                           low: Union[np.ndarray, pd.Series, list],
                           close: Union[np.ndarray, pd.Series, list],
                           period1: int = 7, period2: int = 14, period3: int = 28) -> np.ndarray:
        """Ultimate Oscillator"""
        return self._ultosc.calculate(high, low, close, period1, period2, period3)
    
    def stddev(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Standard Deviation"""
        return self._stddev.calculate(data, period)
    
    def true_range(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """True Range"""
        return self._trange.calculate(high, low, close)
    
    def massindex(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   fast_period: int = 9, slow_period: int = 25) -> np.ndarray:
        """Mass Index"""
        return self._mass.calculate(high, low, fast_period, slow_period)
    
    # =================== VOLUME INDICATORS ===================
    
    def obv(self, close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        On Balance Volume
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        np.ndarray
            Array of OBV values
        """
        return self._obv.calculate(close, volume)
    
    def vwap(self, high: Union[np.ndarray, pd.Series, list],
             low: Union[np.ndarray, pd.Series, list],
             close: Union[np.ndarray, pd.Series, list],
             volume: Union[np.ndarray, pd.Series, list],
             period: int = 0) -> np.ndarray:
        """
        Volume Weighted Average Price
        
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
        np.ndarray
            Array of VWAP values
        """
        return self._vwap.calculate(high, low, close, volume, period)
    
    def mfi(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            period: int = 14) -> np.ndarray:
        """
        Money Flow Index
        
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
        np.ndarray
            Array of MFI values
        """
        return self._mfi.calculate(high, low, close, volume, period)
    
    def adl(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Accumulation/Distribution Line"""
        return self._adl.calculate(high, low, close, volume)
    
    def cmf(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            period: int = 20) -> np.ndarray:
        """Chaikin Money Flow"""
        return self._cmf.calculate(high, low, close, volume, period)
    
    def emv(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            length: int = 14, divisor: int = 10000) -> Union[np.ndarray, pd.Series]:
        """Ease of Movement - matches TradingView exactly"""
        return self._emv.calculate(high, low, volume, length, divisor)
    
    def force_index(self, close: Union[np.ndarray, pd.Series, list],
                    volume: Union[np.ndarray, pd.Series, list],
                    length: int = 13) -> Union[np.ndarray, pd.Series]:
        """Elder Force Index - matches TradingView exactly"""
        return self._fi.calculate(close, volume, length)
    
    def nvi(self, close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Negative Volume Index"""
        return self._nvi.calculate(close, volume)
    
    def pvi(self, close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Positive Volume Index"""
        return self._pvi.calculate(close, volume)
    
    def volosc(self, volume: Union[np.ndarray, pd.Series, list],
                         fast_period: int = 5, slow_period: int = 10) -> np.ndarray:
        """Volume Oscillator"""
        return self._vo.calculate(volume, fast_period, slow_period)
    
    def vroc(self, volume: Union[np.ndarray, pd.Series, list], period: int = 25) -> np.ndarray:
        """Volume Rate of Change"""
        return self._vroc.calculate(volume, period)
    
    def kvo(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            trig_len: int = 13, fast_x: int = 34, slow_x: int = 55) -> Tuple[np.ndarray, np.ndarray]:
        """
        Klinger Volume Oscillator - matches TradingView exactly
        
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
        Tuple[np.ndarray, np.ndarray]
            (kvo, trigger) values
        """
        return self._klinger_vo.calculate(high, low, close, volume, trig_len, fast_x, slow_x)
    
    # =================== OSCILLATORS ===================
    
    def roc_oscillator(self, data: Union[np.ndarray, pd.Series, list], period: int = 12) -> np.ndarray:
        """Rate of Change"""
        return self._roc.calculate(data, period)
    
    def cmo(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Chande Momentum Oscillator"""
        return self._cmo.calculate(data, period)
    
    def trix(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """TRIX"""
        return self._trix.calculate(data, period)
    
    def uo_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                     low: Union[np.ndarray, pd.Series, list],
                     close: Union[np.ndarray, pd.Series, list],
                     period1: int = 7, period2: int = 14, period3: int = 28) -> np.ndarray:
        """Ultimate Oscillator"""
        return self._uo.calculate(high, low, close, period1, period2, period3)
    
    def awesome_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                          low: Union[np.ndarray, pd.Series, list],
                          fast_period: int = 5, slow_period: int = 34) -> np.ndarray:
        """Awesome Oscillator"""
        return self._ao.calculate(high, low, fast_period, slow_period)
    
    def accelerator_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                              low: Union[np.ndarray, pd.Series, list],
                              period: int = 5) -> np.ndarray:
        """Accelerator Oscillator"""
        return self._ac.calculate(high, low, period)
    
    def ppo(self, data: Union[np.ndarray, pd.Series, list],
            fast_period: int = 12, slow_period: int = 26,
            signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Percentage Price Oscillator"""
        return self._ppo.calculate(data, fast_period, slow_period, signal_period)
    
    def po(self, data: Union[np.ndarray, pd.Series, list],
                        fast_period: int = 10, slow_period: int = 20,
                        ma_type: str = "SMA") -> np.ndarray:
        """Price Oscillator"""
        return self._po.calculate(data, fast_period, slow_period, ma_type)
    
    def dpo(self, data: Union[np.ndarray, pd.Series, list], 
           period: int = 21, is_centered: bool = False) -> Union[np.ndarray, pd.Series]:
        """Detrended Price Oscillator - matches TradingView exactly"""
        return self._dpo.calculate(data, period, is_centered)
    
    def aroon_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                        low: Union[np.ndarray, pd.Series, list],
                        period: int = 14) -> np.ndarray:
        """Aroon Oscillator"""
        return self._aroonosc.calculate(high, low, period)
    
    # =================== STATISTICAL INDICATORS ===================
    
    def linreg(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Linear Regression"""
        return self._linearreg.calculate(data, period)
    
    def lrslope(self, data: Union[np.ndarray, pd.Series, list], 
               period: int = 100, interval: int = 1) -> np.ndarray:
        """Linear Regression Slope - matches TradingView exactly"""
        return self._linearreg_slope.calculate(data, period, interval)
    
    def correlation(self, data1: Union[np.ndarray, pd.Series, list],
                   data2: Union[np.ndarray, pd.Series, list],
                   period: int = 20) -> np.ndarray:
        """Pearson Correlation Coefficient"""
        return self._correl.calculate(data1, data2, period)
    
    def beta(self, asset: Union[np.ndarray, pd.Series, list],
             market: Union[np.ndarray, pd.Series, list],
             period: int = 252) -> np.ndarray:
        """Beta Coefficient"""
        return self._beta.calculate(asset, market, period)
    
    def variance(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Variance"""
        return self._var.calculate(data, period)
    
    def tsf(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Time Series Forecast"""
        return self._tsf.calculate(data, period)
    
    def median(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Rolling Median"""
        return self._median.calculate(data, period)
    
    def mode(self, data: Union[np.ndarray, pd.Series, list], 
             period: int = 20, bins: int = 10) -> np.ndarray:
        """Rolling Mode"""
        return self._mode.calculate(data, period, bins)
    
    # =================== HYBRID INDICATORS ===================
    
    def adx(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   period: int = 14) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Average Directional Index System (+DI, -DI, ADX)"""
        return self._adx.calculate(high, low, close, period)
    
    def aroon(self, high: Union[np.ndarray, pd.Series, list],
                     low: Union[np.ndarray, pd.Series, list],
                     period: int = 25) -> Tuple[np.ndarray, np.ndarray]:
        """Aroon Indicator (Up, Down)"""
        return self._aroon.calculate(high, low, period)
    
    def pivot_points(self, high: Union[np.ndarray, pd.Series, list],
                     low: Union[np.ndarray, pd.Series, list],
                     close: Union[np.ndarray, pd.Series, list]) -> Tuple[np.ndarray, ...]:
        """Pivot Points (Pivot, R1, S1, R2, S2, R3, S3)"""
        return self._pivot_points.calculate(high, low, close)
    
    def parabolic_sar(self, high: Union[np.ndarray, pd.Series, list],
                      low: Union[np.ndarray, pd.Series, list],
                      acceleration: float = 0.02, maximum: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
        """Parabolic SAR (values, trend)"""
        return self._sar.calculate(high, low, acceleration, maximum)
    
    def dmi(self, high: Union[np.ndarray, pd.Series, list],
                            low: Union[np.ndarray, pd.Series, list],
                            close: Union[np.ndarray, pd.Series, list],
                            period: int = 14) -> Tuple[np.ndarray, np.ndarray]:
        """Directional Movement Index (+DI, -DI)"""
        return self._dmi.calculate(high, low, close, period)
    
    def psar(self, high: Union[np.ndarray, pd.Series, list],
             low: Union[np.ndarray, pd.Series, list],
             acceleration: float = 0.02, maximum: float = 0.2) -> np.ndarray:
        """Parabolic SAR (values only)"""
        return self._psar.calculate(high, low, acceleration, maximum)
    
    def ht(self, close: Union[np.ndarray, pd.Series, list],
           high: Union[np.ndarray, pd.Series, list],
           low: Union[np.ndarray, pd.Series, list]) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series, pd.Series]]:
        """Hilbert Sine Wave Support and Resistance - matches TradingView exactly"""
        return self._ht_trendline.calculate(close, high, low)
    
    def ckstop(self, high: Union[np.ndarray, pd.Series, list],
              low: Union[np.ndarray, pd.Series, list],
              close: Union[np.ndarray, pd.Series, list],
              p: int = 10, x: float = 1.0, q: int = 9) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """Chande Kroll Stop - matches TradingView exactly"""
        return self._chande_kroll_stop.calculate(high, low, close, p, x, q)
    
    # =================== NEW MOMENTUM INDICATORS ===================
    
    def bop(self, open_prices: Union[np.ndarray, pd.Series, list],
           high: Union[np.ndarray, pd.Series, list],
           low: Union[np.ndarray, pd.Series, list],
           close: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """Balance of Power"""
        return self._balance_of_power.calculate(open_prices, high, low, close)
    
    def elderray(self, high: Union[np.ndarray, pd.Series, list],
                low: Union[np.ndarray, pd.Series, list],
                close: Union[np.ndarray, pd.Series, list],
                period: int = 13) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """Elder Ray Index (Bull/Bear Power)"""
        return self._elder_ray.calculate(high, low, close, period)
    
    def fisher(self, high: Union[np.ndarray, pd.Series, list],
              low: Union[np.ndarray, pd.Series, list],
              length: int = 9) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """Fisher Transform - matches TradingView exactly"""
        return self._fisher_transform.calculate(high, low, length)
    
    def crsi(self, data: Union[np.ndarray, pd.Series, list],
            lenrsi: int = 3, lenupdown: int = 2, 
            lenroc: int = 100) -> Union[np.ndarray, pd.Series]:
        """Connors RSI - matches TradingView exactly"""
        return self._connors_rsi.calculate(data, lenrsi, lenupdown, lenroc)
    
    # =================== NEW VOLUME INDICATORS ===================
    
    def pvt(self, close: Union[np.ndarray, pd.Series, list],
           volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """Price Volume Trend"""
        return self._pvt.calculate(close, volume)
    
    # =================== NEW OSCILLATORS ===================
    
    def stochrsi(self, data: Union[np.ndarray, pd.Series, list], 
                rsi_period: int = 14, stoch_period: int = 14,
                k_period: int = 3, d_period: int = 3) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """Stochastic RSI"""
        return self._stoch_rsi.calculate(data, rsi_period, stoch_period, k_period, d_period)
    
    def rvi(self, open_prices: Union[np.ndarray, pd.Series, list],
           high: Union[np.ndarray, pd.Series, list],
           low: Union[np.ndarray, pd.Series, list],
           close: Union[np.ndarray, pd.Series, list],
           period: int = 10) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """Relative Vigor Index"""
        return self._rvi_osc.calculate(open_prices, high, low, close, period)
    
    def cho(self, high: Union[np.ndarray, pd.Series, list],
           low: Union[np.ndarray, pd.Series, list],
           close: Union[np.ndarray, pd.Series, list],
           volume: Union[np.ndarray, pd.Series, list],
           fast_period: int = 3, slow_period: int = 10) -> Union[np.ndarray, pd.Series]:
        """Chaikin Oscillator"""
        return self._chaikin_osc.calculate(high, low, close, volume, fast_period, slow_period)
    
    # =================== MISSING FUNCTIONS ALIASES ===================
    
    # Create aliases for the renamed functions
    def bbwidth(self, data, period=20, std_dev=2.0):
        """Bollinger Bands Bandwidth (alias for bbands_bandwidth)"""
        return self._bbands_bandwidth.calculate(data, period, std_dev) if hasattr(self, '_bbands_bandwidth') else None
    
    def bbpercent(self, data, period=20, std_dev=2.0):
        """Bollinger Bands %B (alias for bbands_percent_b)"""
        return self._bbands_percent_b.calculate(data, period, std_dev) if hasattr(self, '_bbands_percent_b') else None
    
    def mcginley(self, data, period=14):
        """McGinley Dynamic (alias for mcginley_dynamic)"""
        return self._mcginley_dynamic.calculate(data, period) if hasattr(self, '_mcginley_dynamic') else None
        
    def starc(self, high, low, close, ma_period=20, atr_period=15, multiplier=2.0):
        """STARC Bands (alias for starc_bands)"""
        return self._starc_bands.calculate(high, low, close, ma_period, atr_period, multiplier) if hasattr(self, '_starc_bands') else None
    
    def ulcerindex(self, data, period=14):
        """Ulcer Index (alias for ulcer_index)"""
        return self._ulcer_index.calculate(data, period) if hasattr(self, '_ulcer_index') else None
        
    def rwi(self, high, low, close, period=14):
        """Random Walk Index (alias for random_walk_index)"""
        return self._random_walk_index.calculate(high, low, close, period) if hasattr(self, '_random_walk_index') else None
        
    def fractals(self, high, low, periods=2):
        """Williams Fractals (alias for williams_fractals) - matches TradingView exactly"""  
        return self._williams_fractals.calculate(high, low, periods) if hasattr(self, '_williams_fractals') else None
        
    def trima(self, data, period=20):
        """Triangular Moving Average (alias)"""
        return self._trima.calculate(data, period) if hasattr(self, '_trima') else None
        
    def vidya(self, data, period=14, alpha=0.2):
        """Variable Index Dynamic Average (alias)"""
        return self._vidya.calculate(data, period, alpha) if hasattr(self, '_vidya') else None
        
    def alligator(self, data, jaw_period=13, jaw_shift=8, teeth_period=8, teeth_shift=5, lips_period=5, lips_shift=3):
        """Bill Williams Alligator (alias)"""
        return self._alligator.calculate(data, jaw_period, jaw_shift, teeth_period, teeth_shift, lips_period, lips_shift) if hasattr(self, '_alligator') else None
        
    def ma_envelopes(self, data, period=20, percentage=2.5, ma_type='SMA'):
        """Moving Average Envelopes (alias)"""
        return self._ma_envelopes.calculate(data, period, percentage, ma_type) if hasattr(self, '_ma_envelopes') else None
        
    def chandelier_exit(self, high, low, close, period=22, multiplier=3.0):
        """Chandelier Exit (alias)"""
        return self._chandelier_exit.calculate(high, low, close, period, multiplier) if hasattr(self, '_chandelier_exit') else None
        
    def hv(self, close, length=10, annual=365, per=1):
        """Historical Volatility (alias) - matches TradingView exactly"""
        return self._hv.calculate(close, length, annual, per) if hasattr(self, '_hv') else None
        
    def chop(self, high, low, close, period=14):
        """Choppiness Index (alias)"""
        return self._chop.calculate(high, low, close, period) if hasattr(self, '_chop') else None
        
    def kst(self, data, roclen1=10, roclen2=15, roclen3=20, roclen4=30, smalen1=10, smalen2=10, smalen3=10, smalen4=15, siglen=9):
        """Know Sure Thing - matches TradingView exactly"""
        return self._kst.calculate(data, roclen1, roclen2, roclen3, roclen4, smalen1, smalen2, smalen3, smalen4, siglen) if hasattr(self, '_kst') else None
        
    def tsi(self, data, long_period=25, short_period=13, signal_period=13):
        """True Strength Index (alias)"""
        return self._tsi.calculate(data, long_period, short_period, signal_period) if hasattr(self, '_tsi') else None
        
    def vi(self, high, low, close, period=14):
        """Vortex Indicator (alias)"""
        return self._vi.calculate(high, low, close, period) if hasattr(self, '_vi') else None
        
    def stc(self, data, fast_period=23, slow_period=50, cycle_period=10, d1_period=3, d2_period=3):
        """Schaff Trend Cycle (alias)"""
        return self._stc.calculate(data, fast_period, slow_period, cycle_period, d1_period, d2_period) if hasattr(self, '_stc') else None
        
    def gator_oscillator(self, high, low, jaw_period=13, teeth_period=8, lips_period=5):
        """Gator Oscillator (alias) - matches TradingView exactly"""
        return self._gator_oscillator.calculate(high, low, jaw_period, teeth_period, lips_period) if hasattr(self, '_gator_oscillator') else None
        
    def zigzag(self, high, low, close, deviation=5.0):
        """Zig Zag (alias)"""
        return self._zigzag.calculate(high, low, close, deviation) if hasattr(self, '_zigzag') else None
    
    # =================== UTILITY FUNCTIONS ===================
    
    def crossover(self, series1: Union[np.ndarray, pd.Series, list], 
                  series2: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        Check if series1 crosses over series2
        
        Parameters:
        -----------
        series1 : Union[np.ndarray, pd.Series, list]
            First series
        series2 : Union[np.ndarray, pd.Series, list]
            Second series
            
        Returns:
        --------
        np.ndarray
            Boolean array indicating crossover points
        """
        series1 = validate_input(series1)
        series2 = validate_input(series2)
        return crossover(series1, series2)
    
    def crossunder(self, series1: Union[np.ndarray, pd.Series, list], 
                   series2: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        Check if series1 crosses under series2
        
        Parameters:
        -----------
        series1 : Union[np.ndarray, pd.Series, list]
            First series
        series2 : Union[np.ndarray, pd.Series, list]
            Second series
            
        Returns:
        --------
        np.ndarray
            Boolean array indicating crossunder points
        """
        series1 = validate_input(series1)
        series2 = validate_input(series2)
        return crossunder(series1, series2)
    
    def highest(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Highest value over a period
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        period : int
            Window size
            
        Returns:
        --------
        np.ndarray
            Array of highest values
        """
        data = validate_input(data)
        return highest(data, period)
    
    def lowest(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Lowest value over a period
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        period : int
            Window size
            
        Returns:
        --------
        np.ndarray
            Array of lowest values
        """
        data = validate_input(data)
        return lowest(data, period)
    
    def change(self, data: Union[np.ndarray, pd.Series, list], length: int = 1) -> np.ndarray:
        """
        Change in value over a specified number of periods
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        length : int, default=1
            Number of periods to look back
            
        Returns:
        --------
        np.ndarray
            Array of change values
        """
        data = validate_input(data)
        return change(data, length)
    
    def roc(self, data: Union[np.ndarray, pd.Series, list], length: int) -> np.ndarray:
        """
        Rate of Change (ROC)
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        length : int
            Number of periods to look back
            
        Returns:
        --------
        np.ndarray
            Array of ROC values as percentages
        """
        data = validate_input(data)
        return roc(data, length)
    
    def stdev(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Rolling standard deviation
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        period : int
            Window size for standard deviation calculation
            
        Returns:
        --------
        np.ndarray
            Array of standard deviation values
        """
        data = validate_input(data)
        return stdev(data, period)


# Create global instance for easy access
ta = TechnicalAnalysis()

# Make indicator classes available for advanced users
__all__ = [
    'ta', 'TechnicalAnalysis',
    # Trend indicators
    'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'HMA', 'VWMA', 'ALMA', 'KAMA', 'ZLEMA', 'T3', 'FRAMA',
    'Supertrend', 'Ichimoku', 'ChandeKrollStop', 'TRIMA', 'McGinley', 'VIDYA', 'Alligator', 'MovingAverageEnvelopes',
    # Momentum indicators  
    'RSI', 'MACD', 'Stochastic', 'CCI', 'WilliamsR', 'BOP', 'ElderRay', 
    'Fisher', 'CRSI',
    # Volatility indicators
    'ATR', 'BollingerBands', 'Keltner', 'Donchian', 'Chaikin', 'NATR', 
    'RVI', 'ULTOSC', 'STDDEV', 'TRANGE', 'MASS', 'BBPercent', 'BBWidth', 'STARC',
    'ChandelierExit', 'HistoricalVolatility', 'UlcerIndex',
    # Volume indicators
    'OBV', 'VWAP', 'MFI', 'ADL', 'CMF', 'EMV', 'FI', 'NVI', 'PVI', 'VOLOSC', 'VROC',
    'KlingerVolumeOscillator', 'PriceVolumeTrend',
    # Oscillators
    'ROC', 'CMO', 'TRIX', 'UO', 'AO', 'AC', 'PPO', 'PO', 'DPO', 'AROONOSC',
    'StochRSI', 'RVI', 'CHO', 'CHOP', 'KST', 'TSI', 'VI', 'STC', 'GatorOscillator',
    # Statistical indicators
    'LINREG', 'LRSLOPE', 'CORREL', 'BETA', 'VAR', 'TSF', 'MEDIAN', 'MODE',
    # Hybrid indicators
    'ADX', 'Aroon', 'PivotPoints', 'SAR', 'DMI', 'PSAR', 'HT', 'ZigZag', 'WilliamsFractals', 'RWI',
    # Utility functions
    'crossover', 'crossunder', 'highest', 'lowest', 'change', 'roc', 'stdev'
]