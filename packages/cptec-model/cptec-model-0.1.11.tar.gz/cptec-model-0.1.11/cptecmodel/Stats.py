import pandas as pd
import numpy as np
import builtins

class Stats:
    """
        Module to generate data statistics.
        The function calculates values such as the maximum, minimum, and mean of the defined variable.

        Usage:
            import src.Stats as st
            st.StatsWeighted(f,'t2m').calculate()
            st.StatsUnweighted(f,'t2m').calculate()

    """
    def __init__(self, ds, variable, level=None):
        self.ds = ds
        self.variable = variable
        self.level = level



class StatsUnweighted(Stats):
    """
    The function calculates values ​​such as the maximum, minimum, mean, and quartiles of the defined variable.

    'count': count the number of data points,
    'mean': mean,
    'std': standard deviation,
    'min': minimum value,
    '25%': lower quartile,
    '50%': median,
    '75%': upper quartile,
    'max': maximum value

    Usage:
        import cptecmodel.Stats as st
        st.StatsUnweighted(f,'t2m').calculate()

    Parameters
    ----------
    ds           - Required  : Data to calculate (Dataset)
    variable     - Required  : Variable to filter (Str)

    Returns
    -------
    dataframe : Dataframe
        The newly created dataframe.
        

    """
    def calculate(self):
        # Criando o DataFrame
        df = pd.DataFrame({
            'date': [],
            'count': [],
            'mean': [],
            'std': [],
            'min': [],
            '25%': [],
            '50%': [],
            '75%': [],
            'max': []
        })
        elem,times = (1,[self.ds.time.values]) if isinstance(self.ds.time.values,np.datetime64) else (len(self.ds.time.values),self.ds.time.values)
        for i in times:
            dsD=None
            if elem == 1:
                dsD = self.ds[self.variable]
            else:
                if self.level:
                    dsD = self.ds[self.variable].sel(time=i, level=self.level)
                else:
                    dsD = self.ds[self.variable].sel(time=i)
            nova_linha = {'date': i, 'count': dsD.count().values, 'mean': dsD.mean().values, 'std': dsD.std().values, 
                'min': dsD.min().values, '25%': dsD.quantile(0.25).values, '50%': dsD.quantile(0.50).values, 
                '75%': dsD.quantile(0.75).values, 'max': dsD.max().values}
            df = df.dropna(axis=1, how='all')
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

            # Definindo os tipos de dados de cada coluna
            tipos = {
                'date' : 'datetime64[ns]',
                'count': 'float64',
                'mean' : 'float64',
                'std'  : 'float64',
                'min'  : 'float64',
                '25%'  : 'float64',
                '50%'  : 'float64',
                '75%'  : 'float64',
                'max'  : 'float64'
            }

            # Criando o DataFrame com os tipos de dados especificados
            df = pd.DataFrame(df).astype(tipos)
                               
        return df



class StatsWeighted(Stats):
    """
    The function calculates values such as the maximum, minimum, and mean of the defined variable.


    Using the weighted calculation, the area of the grid cell decreases towards the pole.
    For this grid, we can use the cosine of the latitude as a proxy for the area of the grid cell.

    'count': count the number of data points,
    'mean': mean,
    'min': minimum value,
    'max': maximum value

    Usage:
        import src.Stats as st
        st.StatsWeighted(f,'t2m').calculate()

    Parameters
    ----------
    ds           - Required  : Data to calculate (Dataset)
    variable     - Required  : Variable to filter (Str)

    Returns
    -------
    dataframe : Dataframe
        The newly created dataframe.
        
    """


    def calculate(self):
        # Criando o DataFrame
        df = pd.DataFrame({
            'date': [],
            'count': [],
            'mean': [],
            'min': [],
            'max': []
        })
        elem,times = (1,[self.ds.time.values]) if isinstance(self.ds.time.values,np.datetime64) else (len(self.ds.time.values),self.ds.time.values)
        for i in times:
            dsD=None
            if elem == 1:
                dsD = self.ds[self.variable]
            else:
                if self.level:
                    dsD = self.ds[self.variable].sel(time=i, level=self.level)
                else:
                    dsD = self.ds[self.variable].sel(time=i)
            nova_linha = {'date': i, 'count': dsD.count().values, 'mean': field_mean(dsD), 
                'min': dsD.min().values,  'max': dsD.max().values}
            df = df.dropna(axis=1, how='all')    
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

            # Definindo os tipos de dados de cada coluna
            tipos = {
                'date' : 'datetime64[ns]',
                'count': 'float64',
                'mean' : 'float64',
                'min'  : 'float64',
                'max'  : 'float64'
            }

            # Criando o DataFrame com os tipos de dados especificados
            df = pd.DataFrame(df).astype(tipos)
                               
        return df



def field_mean(mean_field):
    weights = np.cos(np.deg2rad(mean_field.latitude))
    weights.name = "weights"
    air_weighted = mean_field.weighted(weights)
    weighted_mean = air_weighted.mean(("longitude", "latitude"))
    return weighted_mean

def help():
    """

    Function to display Stats information.      
    
    """
    builtins.help(Stats)
    builtins.help(Stats.StatsWeighted)
    builtins.help(Stats.StatsUnweighted)

