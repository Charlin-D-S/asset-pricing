from sdmx import Client
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "yield_curve.csv")

# Initialiser le client pour l'API de la BCE
ecb = Client("ECB")

KEYS = [
    "SR_3M", "SR_6M", "SR_9M",
    "SR_1Y", "SR_2Y", "SR_3Y", "SR_4Y", "SR_5Y",
    "SR_6Y", "SR_7Y", "SR_8Y", "SR_9Y",
    "SR_10Y",# "SR_11Y", "SR_12Y", "SR_13Y", "SR_14Y", "SR_15Y", "SR_16Y", "SR_17Y", "SR_18Y", "SR_19Y", "SR_20Y", "SR_25Y", "SR_30Y"
]
def get_maturity(row):
    q = 1/12
    code = row['key']
    if "M" in code:
        return int(code[3])*q
    else : 
        code = code.replace("SR_",'')
        code = code.replace("Y",'')
        return int(code[3])

class YieldCurveLoader:
    def __init__(self):
        pass
    def get_start_period(self):
        # Periode initiale
        df = self.get_rate('SR_3M')
        if not df.empty:
            return df.index[-1][-1]
        else:
            return None
    

    def get_rate(self,key : str,start_period='2025-11-24')->float:
        """
        Retrieve the latest yield rate for a given key
        
        :param key: the maturity key (e.g : "SR_9M","SR_1Y)
        
        """ 
        keys = {
                'DATA_TYPE_FM': key,
                'INSTRUMENT_FM': 'G_N_A',
                'FREQ': 'B',
                'REF_AREA': 'U2',
                'CURRENCY': 'EUR',
                'PROVIDER_FM': '4F',
                'PROVIDER_FM_ID': 'SV_C_YM'
        }
        try:
            data_message = ecb.data('YC', key=keys,params={'startPeriod': start_period})
            df = sdmx.to_pandas(data_message)
            return df
        except Exception as e:
            return None


    def reload_yield_curve(self):
        start_period = self.get_start_period()
        if not start_period:
            start_period = '2025-11-24'
        try:
            df_yield = pd.read_csv('../data/yield_curve.csv')
            last_values = {
                df_yield.loc[i, "key"]: float(df_yield.loc[i, 'rate'])
                for i in df_yield.index
            }
        except FileNotFoundError:
            last_values = {}
        except Exception as e:
            #print(f"Une erreur inattendue est survenue : {e}")
            last_values = {}

        # Récupérer la dernière valeur pour chaque clé
        for key in KEYS:
            df = self.get_rate(key=key,start_period=start_period)
            if not df.empty:
                last_values[key] = df.iloc[-1]

        result_df = pd.DataFrame(list(last_values.items()), columns=['key', 'rate'])
        result_df['maturity'] = result_df.apply(get_maturity,axis=1)
        result_df = result_df.sort_values(by="maturity")
        result_df.to_csv(DATA_PATH)

