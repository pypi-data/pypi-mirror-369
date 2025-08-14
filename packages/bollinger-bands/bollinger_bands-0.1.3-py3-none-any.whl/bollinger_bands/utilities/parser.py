import pandas as pd
from typing import Dict

class DictionaryParser:
    """
    Class Responsible for parsing through 
    """

    @staticmethod
    def parse_multiple(result_dict:dict) -> Dict[str, pd.DataFrame] | None:
        """
        Quick parser to convert multiple comapny dict to data_frame
        """
        try:
            return {
                key:DictionaryParser.parse_single(result_dict=company_dict)
                for key, company_dict in result_dict.items()
                if "AI" in key
            }
        
        except Exception as e:
            return None

    @staticmethod
    def parse_single(result_dict:dict) -> pd.DataFrame | None:
        """
        Quick parser to convert parse single company output to dataframe
        """
        if not isinstance(result_dict, dict):
            return None
        
        results = result_dict.get("results", None)
        if results is None:
            return None
        
        try:
            final_result = [
                {
                    "alpha_code":row.get("alpha_code", None),
                    "calculation_date":row.get("calculation_date", None),
                    **row.get("ratio_values", {})
                }
                for row in results if isinstance(row, dict)
            ]
            
            data_df = pd.DataFrame(final_result)
            return data_df
        
        except Exception as e:
            return None
    