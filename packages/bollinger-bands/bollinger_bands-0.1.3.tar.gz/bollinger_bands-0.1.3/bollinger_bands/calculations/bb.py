import numpy as np
import pandas as pd
from bollinger_bands.constants.constants import REQUIRED_COLUMNS

class BollingerBands:
    """
    Class responsible for handling bollinger band calculations for the Bollinger Model
    """
    def __init__(self, company_df:pd.DataFrame):
        if not REQUIRED_COLUMNS.issubset(company_df.columns):
            missing = REQUIRED_COLUMNS - set(company_df.columns)
            raise ValueError(f"Missing columns in DataFrame: {missing}")

        self.company_df = company_df


    def calculate_multiple_bollinger_bands(self, k: float, window: int) -> pd.DataFrame | None:
        """
        Method calculates bands over a list of columns
        calculates the following:
        - sma : simple movign average -> rolling mean over a window
        - std : standard deviation -> rolling std over a window
        - upper band 
        - lower band

        ### New Features
        1. Covariance : [raw_column, sma]
        - cov: coefficient of variance on basis of rolling std and mean for a particular column (std / mean) 
        - agg_cov: aggregate cov value on basis of whole column 
        - cov_ratio: cov / agg_cov 
        """
        try: 
            df = self.company_df.copy()
            df['calculation_date'] = pd.to_datetime(df['calculation_date'])
            df.sort_values('calculation_date', inplace=True)
            df.set_index('calculation_date', inplace=True)

            valid_columns= []
            for column in REQUIRED_COLUMNS:
                if column == "calculation_date":
                    continue
                if df[column].dropna().empty:
                    continue

                valid_columns.append(column)
                df[f'{column}_sma'] = df[column].rolling(window=window).mean()
                df[f'{column}_std'] = df[column].rolling(window=window).std()
                df[f'{column}_upper_band'] = df[f'{column}_sma'] + (k * df[f'{column}_std'])
                df[f'{column}_lower_band'] = df[f'{column}_sma'] - (k * df[f'{column}_std'])

                ## COV -> raw column values
                df[f"{column}_cov"] = df[f"{column}_std"] / df[f"{column}_sma"]
                df[f"{column}_agg_cov"] = df[f'{column}'].std(ddof=1) / df[f'{column}'].mean()
                df[f"{column}_cov_ratio"] = df[f"{column}_cov"] / df[f"{column}_agg_cov"]

                ## COV -> SNA BASED
                df[f"{column}_sma_agg_cov"] = df[f'{column}_sma'].std(ddof=1) / df[f'{column}_sma'].mean()


            df.reset_index(inplace=True)
            valid_columns = [col for col in valid_columns if col != "calculation_date"]
            return df.dropna(subset=[f"{col}_sma" for col in valid_columns])
        
        except Exception as e:
            return None

