import os
import asyncio
import pandas as pd
from functools import partial
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from bollinger_bands.calculations.bb import BollingerBands
from bollinger_bands.utilities.parser import DictionaryParser
from financial_engine.core.engine import FinancialEngine

class BollingerModel:
    """
    Bollinger Model creates Bollinger bands for specified K and Days value across company based financial ratios
    """
    def __init__(self, output_path:str=None):
        self.fe = FinancialEngine()
        if output_path is None:
            raise ValueError("outer_path is a required parameter.")
        self.output_path = output_path


    ## MAIN FUNCTIONS ##
    async def get_bollinger_bands(self, alpha_code:str=None, 
                                  k:float=None, 
                                  window_size:int=None, 
                                  bollinger_to_file:bool=False, 
                                  ratios_to_file:bool=False) -> pd.DataFrame | None:
        """
        Calculates Bollinger bands for provided alpha_code(company), K value and Window_size (in days)
        :PARAMS:
        - alpha_code : company alpha_code
        - k : constant value required to bollinger bands calculations
        - window_size : size of window for SMA, NOTE: window_size accept days
        - bollinger_to_file : saves bollinger calculations to file, default is False
        - ratios_to_file : saves financial ratios extracted to file default is False
        """
        if alpha_code is None or k is None or window_size is None:
            raise ValueError("Params required for bollinger bands not provided. (alpha_code, k and window_size, output_path)")
        
        try:
            # 1. Extract data for alpha_code
            data_df = await self.get_financial_ratios(alpha_code=alpha_code, to_file=ratios_to_file)
            if data_df is None:
                return None

            # 2. Calculate bands
            bb = BollingerBands(company_df=data_df)
            bands_df = bb.calculate_multiple_bollinger_bands(k=k, window=window_size)
            if bands_df is None:
                return None
            
            if bollinger_to_file:
                await self._save_to_file(df=bands_df, alpha_code=alpha_code, k=k, window_size=window_size, is_ratio=False)

            # 3. Return Bands df
            return bands_df
    
        except Exception as e:
            return None
        


    async def get_bollinger_bands_multiple(self, alpha_codes: List[str] = None, 
                                           k: float = None, 
                                           window_size: int = None,
                                           bollinger_to_file: bool = False, 
                                           ratios_to_file: bool = False) -> Dict[str, pd.DataFrame] | None:
        """
        Calculates Bollinger bands over a range of alpha_codes for specified K value and Window_size (days).
        Uses thread pool for parallel computation of Bollinger bands.
        :PARAMS:
        - alpha_codes : list of alpha_codes
        - k : constant value required to bollinger bands calculations
        - window_size : size of window for SMA, NOTE: window_size accept days
        - bollinger_to_file : saves bollinger calculations to file, default is False
        - ratios_to_file : saves financial ratios extracted to file default is False
        """
        if alpha_codes is None or k is None or window_size is None:
            raise ValueError("Params required for Bollinger Bands not provided: alpha_codes, k, and window_size.")

        try:
            # Step 1: Get ratios
            data_df_dict = await self.get_financial_ratios_multiple(alpha_codes=alpha_codes, to_file=ratios_to_file)
            if not data_df_dict:
                return None

            loop = asyncio.get_running_loop()
            result_bands = {}

            with ThreadPoolExecutor() as executor:
                tasks = []
                for code, df in data_df_dict.items():
                    if df is None or df.empty:
                        continue

                    bb = BollingerBands(company_df=df)
                    task = loop.run_in_executor(
                        executor,
                        partial(bb.calculate_multiple_bollinger_bands, k=k, window=window_size)
                    )
                    alpha_code = code.split("_")[1]
                    tasks.append((alpha_code, task))

                for code, task in tasks:
                    bands_df = await task
                    result_bands[code] = bands_df

                    if bollinger_to_file:
                        asyncio.create_task(self._save_to_file(
                            df=bands_df,
                            alpha_code=code,
                            k=k,
                            window_size=window_size,
                            is_ratio=False
                        ))

            return result_bands
        
        except Exception as e:
            return None


    ## HELPER METHOD -> SAVING FILES
    async def _save_to_file(self, df:pd.DataFrame=None, alpha_code:str=None, k:int=None, window_size:int=None, is_ratio:bool=False) -> str | None:
        """
        Saves file to specified dir
        - cache
          - AX_11111
            - AI_RATIO_AX1111_DATE.feather 
            - AI_BOLLINGER_AX11111_DATE.feather
        """
        try:
            if df is None or alpha_code is None:
                return None

            # 1. Setup directory
            dir_path = os.path.join(f"{self.output_path}\cache", alpha_code)
            os.makedirs(dir_path, exist_ok=True)

            # 2. Determine file name
            date_str = datetime.today().date()
            if is_ratio:
                filename = f"AI_RATIOS_{alpha_code}_{date_str}.feather"
            else:
                filename = f"AI_BOLLINGERS_{alpha_code}_K{k}_W{window_size}_{date_str}.feather"

            # 3. Save to file
            full_path = os.path.join(dir_path, filename)
            df.to_feather(full_path)
            return full_path

        except Exception as e:
            return None
    

    ## HELPER METHODS -> Extracting and/ or storing financial ratios to file
    async def get_financial_ratios(self, alpha_code:str=None, to_file:bool=False) -> pd.DataFrame | None:
        """
        Helper wrapper function around financial engine to extract financial ratios for a company
        """
        if alpha_code is None:
            return None
        
        # 1. Calculate ratio for the company
        try:
            financial_ratios = await self.fe.get_ratio_range(alpha_code=alpha_code)
            if financial_ratios is None:
                return None
            
            # 2. Parse the files
            data_df = DictionaryParser.parse_single(result_dict=financial_ratios)
            
            # 2. Caching 
            if to_file:
                await self._save_to_file(df=data_df, alpha_code=alpha_code, is_ratio=True)
            return data_df
        
        except Exception as e:
            return None


    async def get_financial_ratios_multiple(self, alpha_codes:List[str]=None, to_file:bool=False) -> Dict[str, pd.DataFrame] | None:
        """
        Helper wrapper around financial engine to extract financtial ratios for multiple companies and saving them to cache
        """
        if alpha_codes is None:
            return False

        # 1. Calculating Ratios for companies
        try:
            financial_ratios_dict = await self.fe.get_ratios_range_multiple(alpha_codes=alpha_codes)
            if financial_ratios_dict is None:
                return False
            
            # 2. Parse multiple company records
            data_dfs = DictionaryParser.parse_multiple(result_dict=financial_ratios_dict)

            if to_file:
                for code, df in data_dfs.items():
                    if df is not None and not df.empty:
                        alpha_code = code.split("_")[1]
                        asyncio.create_task(self._save_to_file(df=df, alpha_code=alpha_code, is_ratio=True))

            return data_dfs
        
        except Exception as e:
            return None