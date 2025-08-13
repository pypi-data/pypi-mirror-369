from datetime  import datetime, timedelta
import numpy as np
import pandas as pd
import gc
import pycurl
import io
import xarray as xr
import time, random, glob, shutil, os
import urllib
from ._dict_wrf import dict_wrf as __dict_wrf__ 
from ._version import _version as __version__
import warnings

warnings.filterwarnings('ignore')

class model(object):

    def __init__(self):

        """ 

        Function to initialize the WRF model configurator, returns an object with the load function enabled for use.

        Parameters
        --------------------------------------------------------------------------------------------------------------------------------------

        * Model: To configure WRF in new resolutions, change the parameter field
        * Variables: To enable new variables, add the variable name and the corresponding name within the .idx or .inv
        * Levels: Defines variables with a single level or multiple levels
        * Area: During initialization, the Reduce field is added. When True, the parameters defined here are applied to zoom in on the desired area
        * Transform: Performs transformation in the units of the variables to a common unit between the models.
        * File: Name of the file available on the ftp
        * Server: FTP server consumed by the application
        --------------------------------------------------------------------------------------------------------------------------------------

        Returns a model object

        """

        self.dict = __dict_wrf__

        self.levels =  ["1000","975","950","925","900","875","850","825","800","775","750","700","650","600","550","500","450","400","350", "300", "250", "200", "150", "100", "50"]
        self.variables = list(self.dict['variables'])
        self.area = {
                       "northlat" :    17.70,
                       "southlat" :    -58,
                       "westlon" :    270,
                       "eastlon" :    340,
                       "invertedlat" : True
        }
        
        
        self.dict['area'].update({'reduce': False})
        self.dict.update({'save_netcdf': False})
        self.dict.update({'path_to_save': os.getcwd()})

        self.local_path = f"INPE/{self.dict['model']['name']}/{self.dict['model']['parameter']}/brutos"
        self.ftppath = f"{self.dict['model']['parameter']}/brutos"
        
        print(f"\n#### {self.dict['model']['long_name']} ({self.dict['model']['parameter']}) #####\n")
        start = time.strftime("%Y%m%d", time.gmtime(time.time()))
        end = (datetime.strptime(f'{start}',  '%Y%m%d') - timedelta(days=10)).strftime("%Y%m%d")
        self.daterange =  pd.date_range(end, start)
        self.frequency = [0,168]
        self.var_level = [sigla  for sigla, level in self.dict['levels'].items() if level =='LVL']
        self.var_surface = [sigla  for sigla, level in self.dict['levels'].items() if level =='SFC']
        print(f"Forecast data available for reading between {end} and {start}.\n")
        print(f"Surface variables: {self.var_surface}.\n")
        print(f"Level variables:   {self.var_level}.\n")
        print(f"levels (hPa): {self.levels}.\n")
        print(f"Frequency: hourly frequency [0,1,2,...,22,23].\n")

        self.session = random.random()

        __clean__()

    def load(self, date=None, steps=[0], var=['t2m'], level=[1000, 'surface']):
        """
        
        The load function prepares the list of variables, levels and dates that will be loaded into memory.

        During execution, a temporary directory is created to handle the files and is deleted as soon as the request is completed.

        self.date is defined by the frequency at which the model makes its forecasts available, for WRF every 1 hour.

        Parameters
        ------------------------------------------------------------------------------------------------------------
        date : Date of the initial condition date=YYYYMMDDHH, use HH for IC 00 and 12.
        steps : Integer/Array of integers with the desired steps. where 0 is the initialization of the model [0,1, ... ,168], maximum value 168.
        var: Array of strings with the names of the variables available for reading ['t2m', 'precip']
        level: Array of integers with the levels available for each model [1000, 850]
        ------------------------------------------------------------------------------------------------------------

        load(date='2022082300', steps=[0,1,5,9], var=['t', 'precip'], level=[1000, 850])
        load(date='2022082300', steps= 4, var=['t', 'precip'], level=[1000, 850])

        --------------------------------------------------------------------------------------------

        Returns an Xarray containing all the requested variables with the transformations contained in self.dict 

        ------------------------------------------------------------------------------------------------------------     

        """
        if (isinstance(steps,int)) : steps = [h for h in range(0, steps+1, 1)]
        if (len(steps)<2) :
            if len(var) == 1 and self.dict['types'][var[0]] == "FCT" and steps[0] == 0: 
                steps = [h for h in range(0, 2, 1)]


        if type(date) == int: date = str(date)
        if date == None: date = datetime.today().strftime("%Y%m%d")

        if type(level) == int: level = [level]
        if type(var) == str: var = [var]

        self.start_date = date
        self.start_date = self.start_date.replace('/', '')
        self.start_date = self.start_date.replace('-', '')
        if len(self.start_date) == 8: self.start_date = f"{self.start_date}00"

        self.query_level = level
        self.date = [(datetime.strptime(f'{self.start_date}',  '%Y%m%d%H') + timedelta(hours=int(h))).strftime("%Y%m%d%H") for h in steps]
        self.year       = self.start_date[0:4]
        self.mon        = self.start_date[4:6]
        self.day        = self.start_date[6:8]
        self.hour       = self.start_date[8:10]

        self.query_variables = var

        self.__getrange__()
        if os.path.exists(f".temporary_files/{self.session}"): shutil.rmtree(f".temporary_files/{self.session}")
        
        return self.file


    def __repr__(self):

        """

            Function to display definitions contained in the object, accessible through self.dict

        """

        print(f"Reduce area: {self.dict['area']['reduce']}")
        print(f"Save netcdf: {self.dict['save_netcdf']}")
        print(f"Path to save: {self.dict['path_to_save']}")
        print(f"\n#### {self.dict['model']['long_name']} ({self.dict['model']['parameter']}) #####\n")
        start = time.strftime("%Y%m%d", time.gmtime(time.time()))
        end = (datetime.strptime(f'{start}',  '%Y%m%d') - timedelta(days=10)).strftime("%Y%m%d")
        print(f"Forecast data available for reading between {end} and {start}.\n")
        print(f"Surface variables: {self.var_surface}.\n")
        print(f"Level variables:   {self.var_level}.\n")
        print(f"levels (hPa): {self.levels}.\n")
        print(f"Frequency: hourly frequency [0,1,2,...,22,23].\n")
        print(f"To see more info use wrf.help()")

        return str('')    

    
    def help(self):

        """

            Function to display model information and their parameterizations.  

        """
        help(model)


    def __getrange__(self):

        """ 

        Function to create a dataframe with information that will be consumed by self.__curl__.

        The information collected includes the lower and upper positions of each variable in the grib file.

        Example of self.setup:
        --------------------------------------------------------------------------------------------------------------
        forecast_date upper id lower start_date var level step_model varname
        0 2022082300 130807486 236 130174702 2022082300 TMP surface anl t2m
        1 2022082301 158309930 236 157628649 2022082300 TMP surface 1 hour fcst t2m
        --------------------------------------------------------------------------------------------------------------     


        """

        arr = []

        try:

            for dt in self.date:

                invfile = self.dict['file']['name'].format(self.start_date, dt)
                invfile = invfile.split('.')[:-1]
                invfile = f'{self.ftppath}/{self.year}/{self.mon}/{self.day}/{self.hour}/{invfile[0]}.inv'

                df = pd.read_csv(f"{self.dict['server']['ftp']}/{invfile}", skiprows=0, names=['header'])

                df['header'] = df['header'].map(lambda x: x[:-1])
                df[['id', 'allocate', 'date', 'var', 'level', 'timeFct']] = df['header'].str.split(':', expand=True)
                df.drop('header', axis=1, inplace=True)
                df['date'] = df['date'].map(lambda x: str(x).split('=')[1])


                
                for var in self.query_variables:
                    if var in self.dict['variables']:
                        value = self.dict['variables'][var]
                        varframe = df[ df['var'] == value ]
                        # Add 1000 and surface when not defined on request
                        tmp_list = [i for i in self.query_level if i != 'surface']
                        if self.dict['levels'][var] == 'LVL' and len(tmp_list) == 0:
                            self.query_level.append(1000)

                        tmp_list = [i for i in self.query_level if i == 'surface']
                        if self.dict['levels'][var] == 'SFC' and len(tmp_list) == 0:
                            self.query_level.append('surface')

                        for lvl in self.query_level:

                            if self.dict['levels'][var] == 'LVL' and lvl == 'surface':
                                pass
                            elif self.dict['levels'][var] == 'SFC' and lvl != 'surface':
                                pass
                            else:

                                if lvl == 'surface': 
                                    
                                    if var == 't2m' or value == 'TMP': lvl = '2 m above ground'

                                    if var == 'slp' or value == 'MSLET': lvl = 'mean sea level'

                                    if var == 'v10m' or var == 'u10m': lvl = '10 m above ground'

                                    if var == 'pw': lvl = 'considered as a single layer'

                                    if var == 'refd': lvl = '1000 m above ground'

                                    if var == 'tsoil': lvl = '0-0.1 m below ground'

                                    if var == 'soilw': lvl = '0-0.1 m below ground'

                                    if var == 'soill': lvl = '0-0.1 m below ground'

                                    if var == 'hlcy': lvl = '1000-0 m above ground'


                                if len(varframe) == 1:

                                    frame = varframe

                                else:

                                    if self.dict['levels'][var] == 'SFC':
                                
                                        frame = varframe[ varframe['level'] == lvl ]
                                    
                                    else:

                                        frame = varframe[ varframe['level'] == f'{lvl} mb' ]

                                upper = df.iloc[frame.index+1]['allocate']
                                pp = np.append(dt, upper)
                                pp = np.append(pp, frame.values[0])
                                pp = np.append(pp, var)

                                arr.append(pp)
                                
            self.setup = pd.DataFrame(arr, columns=['forecast_date', 'upper', 'id',
                                                        'lower', 'start_date', 'var', 
                                                        'level', 'step_model', 'varname'])
            
            self.setup.drop_duplicates(inplace=True)
            self.__curl__()

        except urllib.error.HTTPError as err:
            print('File not available on server!')
            self.file = None
            return
        except Exception as err:
            print(err)
            print(f"Unexpected {err=}, {type(err)=}")
            self.file = None
            return


    def __curl__(self):

        """
        
        The __curl__ function downloads the variables described for each record in self.setup, applies 
        the transformations defined in self.dict['transform'] and returns in self.file an Xarray in memory with all the times of the requested variables.

        When self.dict['save_netcdf'] == True a netcdf4 file will be saved with a copy of the request automatically.

        
        """

        pathout = f".temporary_files/{self.session}"

        os.makedirs(pathout, exist_ok=True)

        fidx = glob.glob(f"{pathout}/*.idx")
        if len(fidx) > 0:
            [os.remove(f) for f in fidx]
        
        for _,row in self.setup.iterrows():
           
            grbfile = self.dict['file']['name'].format(row['start_date'], row['forecast_date'])
            grbfile = f"{self.ftppath}/{self.year}/{self.mon}/{self.day}/{self.hour}/{grbfile}"
            c = pycurl.Curl()
            c.setopt(pycurl.URL,f"{self.dict['server']['ftp']}/{grbfile}")

            outfile = self.dict['file']['name'].format(row['start_date'], row['forecast_date'])
            lvl = row['level'].replace(" ", "")
            outfile = f"{pathout}/{row['varname']}_{lvl}_{outfile}"

            with open(outfile, "wb") as fout:
                c.setopt(pycurl.WRITEDATA, fout)
                c.setopt(c.RANGE, f"{row['lower']}-{row['upper']}") 
                c.setopt(pycurl.VERBOSE, 0)
                c.setopt(pycurl.FOLLOWLOCATION, 0)
                c.perform()
                c.close()
            
            fout.close()
            
            f = xr.open_dataset(outfile, engine='cfgrib')
            f['time'] = datetime.strptime(row['forecast_date'],  '%Y%m%d%H')

            v = list(f.keys())
            var = outfile.split('/')[-1]
            var = var.split('_')[0]
            f = f.rename({v[0] : var})

            if 'step': f = f.drop_vars('step')

            if 'valid_time' in f: f = f.drop_vars('valid_time')
            
            if 'surface' in f:
                
                f = f.drop_vars('surface')

            if 'isobaricInhPa' in f:
                f = f.rename({'isobaricInhPa' : 'level'})
                f = f.expand_dims(['level'])

            if 'heightAboveGround' in f: f = f.drop_vars('heightAboveGround')

            if 'heightAboveGroundLayer' in f: f = f.drop_vars('heightAboveGroundLayer')      
            
            if 'pressureFromGroundLayer' in f: f = f.drop_vars('pressureFromGroundLayer')      

            if 'atmosphereSingleLayer' in f: f = f.drop_vars('atmosphereSingleLayer')

            if 'meanSea' in  f: f = f.drop_vars('meanSea')

            if 'depthBelowLandLayer' in  f: f = f.drop_vars('depthBelowLandLayer')  
                
            if 'middleCloudLayer' in  f: f = f.drop_vars('middleCloudLayer') 

            if 'highCloudLayer' in  f: f = f.drop_vars('highCloudLayer') 

            if 'lowCloudLayer' in  f: f = f.drop_vars('lowCloudLayer') 

            f = f.expand_dims(['time'])
            outnc = outfile.split('/')[-1]
            outnc = outnc.split('.')[:-1][0]

            if var in self.dict['transform']:
                tr = float(self.dict['transform'][var][1:])
                op = self.dict['transform'][var][0]
                f = eval(f'f {op} tr')
                f[var].attrs = {
                            "long_name" : self.dict['desc'][var]['name'],
                            "units"  :       self.dict['desc'][var]['unit'],
                            "standard_name": self.dict['desc'][var]['name']
                    }
            
            if self.dict['area']['reduce'] ==  True:

                lat1 = self.dict['area']['minlat']
                lat2 = self.dict['area']['maxlat'] 
                lon1 = self.dict['area']['minlon']
                lon2 = self.dict['area']['maxlon']

            
                f2 = f.sel(latitude=slice(lat1, lat2), 
                          longitude=slice(lon1, lon2)).copy()
            else:
                f2 = f

            f2.to_netcdf(f'{pathout}/{outnc}.nc4', encoding={'time': {'dtype': 'i4'}})
            f2.close()
            f.close()
  
                 
        gc.collect()
        files = glob.glob(f"{pathout}/*.nc4")

        f = xr.open_mfdataset(files,  combine='nested', parallel=False,  chunks={'latitude': 150, 'longitude': 150})
        
        # Transform accumulated precipitation
        # TimeStamp 0 and 1 without modification
        if 'precip' in f:

            arr = []
            for dt in np.arange(len(f.time)):
                
                if dt <= 1:
                    arr.append(f.isel(time=dt)[['precip']])
                else:
                    fout = f.isel(time=dt)[['precip']] - f.isel(time=dt-1)[['precip']]
                    fout = fout.assign_coords({'time': f.time[dt]})
                    fout = fout.expand_dims('time')
                    arr.append(fout)
            
            f['precip'] = xr.concat(arr, dim="time")['precip']

        f.attrs = {
                            "center" :	"National Institute for Space Research - INPE",
                            "model"  :  f"The Weather Research and Forecasting ({self.dict['model']['parameter']})"
        }
        f.time.encoding['units'] = "Seconds since 1970-01-01 00:00:00"

        field = f.load()

        if self.dict['save_netcdf'] == True:

            pathout = f"{self.dict['path_to_save']}/{self.local_path}/{self.year}/{self.mon}/{self.day}/{self.hour}"
            os.makedirs(pathout, exist_ok=True)
            ncout = self.dict['file']['name'].format(row['start_date'], row['forecast_date'])
            ncout = ncout.replace(f"{self.dict['file']['format']}","nc4")

            if os.path.exists(f"{pathout}/{ncout}"): os.remove(f"{pathout}/{ncout}")
            field.to_netcdf(f"{pathout}/{ncout}", encoding={'time': {'dtype': 'i4'}})

        f.close()

        gc.collect()
        self.file = field

    def get_var_description(self, var=None):
        """
        Retrieve the description of meteorological variables as a pandas DataFrame.
    
        If a specific variable name is provided, returns a DataFrame with a single row
        containing its name and unit. If no variable is specified, returns a DataFrame
        with all available variables and their respective metadata.

        Parameters
        ----------
        var : str, optional
            The key of the variable to retrieve its description. If None, all variable
            descriptions are returned.

        Returns
        -------
        pandas.DataFrame
            A DataFrame with columns ['Variable', 'Name', 'Unit'].
            - If `var` is provided: the DataFrame contains one row.
            - If `var` is None: the DataFrame contains all available variables.

        Examples
        --------
        >>> gfs.get_var_description('t')
        Variable        Name       Unit
        0        t  Temperature         C

        >>> gfs.get_var_description()
        Variable                   Name  Unit
        0        t            Temperature    C
        1        u  u-component of wind  m/s
        2        v  v-component of wind  m/s
        """
        if var:
            data = [
                {'Variable': var, 
                'Name': self.dict['desc'][var]['name'], 
                'Unit': self.dict['desc'][var]['unit']
                }

            ]
        else:
            data = [
                {'Variable': k, 'Name': v['name'], 'Unit': v['unit']}
                for k, v in self.dict['desc'].items()
            ]
        return pd.DataFrame(data)



def __clean__():

    """

    When the request process is interrupted the tool will not remove temporary files,
    this function removes all temporary directories older than 2 days on disk.


    """
       
    if os.path.exists(f".temporary_files"):

        today = datetime.today()
           
        files = glob.glob(".temporary_files/0.*")
        for f in files:
            duration = today - datetime.fromtimestamp(os.path.getmtime(f))
            if duration.days >= 2:
                shutil.rmtree(f) 
