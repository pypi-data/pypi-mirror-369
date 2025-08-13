import ipywidgets as widgets
from IPython.display import display
from datetime  import datetime, timedelta, date
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class show_menu():
    def __init__(self, model):

        """ 
            Função para inicializar o ambiente Grafico para uso no Jupyter Notebook

            Parametros
            ------------------------------------------------------------------------------------------------------------------------------------------------------       

            * Model     : O Modelo Inicializado 
           
            ------------------------------------------------------------------------------------------------------------------------------------------------------       

        """        
        vars_escolhidas = []
        self._lvs_escolhidos = []
        steps_escolhidos = []

        self._ffull = xr.Dataset()
        self._fa = xr.Dataset()
        self._tipo_plot = "area"
        self.__model = model

        
        inicio,fim = model.frequency
        self.__dict_widgets = {
        "load"    : {
                        "datas" :   widgets.RadioButtons(options= model.daterange[::-1],description='Datas',disabled=False),
                        "variaveis" : [widgets.Checkbox(description=a) for a in model.dict['variables']],
                        "steps" : widgets.IntSlider(value=0,min=inicio,max=fim,step=1,description='Steps'),
                        "levels" : [widgets.Checkbox(description=a) for a in model.levels]
                    },
        "area"    : {
                        "norte" :    widgets.FloatText(description='Norte',value=self.__model.area['northlat'],min=self.__model.area['northlat'],max=self.__model.area['southlat'],step=0.1),
                        "oeste" :    widgets.FloatText(description='Oesnte',value=self.__model.area['westlon'],min=self.__model.area['westlon'],max=self.__model.area['eastlon'],step=0.1),
                        "leste" :    widgets.FloatText(description='Leste',value=self.__model.area['eastlon'],min=self.__model.area['eastlon'],max=self.__model.area['westlon'],step=0.1),
                        "sul" :    widgets.FloatText(description='Sul',value=self.__model.area['southlat'],min=self.__model.area['southlat'],max=self.__model.area['northlat'],step=0.1)
                    },
        "ponto"   : {
                        "lat" : widgets.FloatText(description='Lat',step=0.1),
                        "lon" : widgets.FloatText(description='Lon',step=0.1)
                    },
        "plot"    : {
                        "variaveis_escolhidas" :  widgets.Dropdown(options=vars_escolhidas,description="Variaveis",
                          disabled=False,layout=widgets.Layout(align_items='flex-start',width='60%')),
                        "niveis_escolhidos" : widgets.RadioButtons(description="Niveis",options=self._lvs_escolhidos),
                        "steps_escolhidos"  : widgets.RadioButtons(description="Steps",options=steps_escolhidos)
                    }
        }
        
       # Janela Tab1 - Load
        self._data = self.__dict_widgets['load']['datas']
        self._chk_vars = self.__dict_widgets['load']['variaveis']
        self._chk_levels = self.__dict_widgets['load']['levels']
        self._slider_steps = self.__dict_widgets['load']['steps']
        self._button = widgets.Button(description="Load")
        self._output = widgets.Output()
        
        BOX1=widgets.VBox([self._data,self._slider_steps,self._button,self._output])
        BOX2=widgets.VBox(self._chk_vars)
        BOX3=widgets.VBox(self._chk_levels)
        BOX4=widgets.HBox([BOX1,BOX2,BOX3])
    
        # Janela Tab2 - Area
        NULO1 = widgets.Text(value='', disabled=True)
        self._TXT1 = self.__dict_widgets['area']['norte']
        self._TXT2 = self.__dict_widgets['area']['oeste']
        self._TXT3 = self.__dict_widgets['area']['leste']
        self._TXT4 = self.__dict_widgets['area']['sul']
        BOX6 = widgets.HBox([NULO1,self._TXT1,NULO1])
        BOX7 = widgets.HBox([self._TXT2,NULO1,self._TXT3])
        BOX8 = widgets.HBox([NULO1,self._TXT4,NULO1])
        self._buttonArea = widgets.Button(description="Filtrar Área")
        self._BOX9 = widgets.VBox([BOX6,BOX7,BOX8,self._buttonArea])
    
        # Janela Tab3 - Ponto
        self._TXT5 = self.__dict_widgets['ponto']['lat']
        self._TXT6 = self.__dict_widgets['ponto']['lon']
        self._buttonPonto = widgets.Button(description="Filtrar Ponto")
        self._BOX10 = widgets.VBox([self._TXT5,self._TXT6,self._buttonPonto])
    
        # Janela Tab4 - Plot
        self._size = self.__dict_widgets['plot']['variaveis_escolhidas']
        self._radio_input = self.__dict_widgets['plot']['niveis_escolhidos']
        self._radio_times = self.__dict_widgets['plot']['steps_escolhidos']
        #out11 = widgets.interactive(hist1, size=size)
        self._out13 = widgets.Output()
        self._buttonPlot = widgets.Button(description="Plot")
        BOX11=widgets.VBox([self._size,self._radio_input,self._radio_times,self._buttonPlot])
        self._BOX12=widgets.HBox([BOX11,self._out13])
    
        # Janela Tab5 - NetCDF
        self._outNetCDF = widgets.Output()
        self._buttonDownloadNetcdf = widgets.Button(description="Download NetCDF")
        self._BOXNetCDF=widgets.HBox([self._buttonDownloadNetcdf,self._outNetCDF])

        # Janela Tab6 - CSV
        self._outCSV = widgets.Output()
        self._buttonDownloadCSV = widgets.Button(description="Download CSV")
        self._BOXCSV=widgets.HBox([self._buttonDownloadCSV,self._outCSV])

        # Eventos 
        self._button.on_click(self._on_button_clicked)
        self._buttonArea.on_click(self._on_buttonArea_clicked)
        self._buttonPonto.on_click(self._on_buttonPonto_clicked)
        self._buttonPlot.on_click(self._on_buttonPlot_clicked)
        self._buttonDownloadNetcdf.on_click(self._on_buttonNetCDF_clicked)
        self._buttonDownloadCSV.on_click(self._on_buttonCSV_clicked)

        # Tabs
        tab=widgets.Tab((BOX4,self._BOX9,self._BOX10,self._BOX12,self._BOXNetCDF,self._BOXCSV))
        tab.set_title(0, 'Data')
        tab.set_title(1, 'Area')
        tab.set_title(2, 'Ponto')
        tab.set_title(3, 'Plot')
        tab.set_title(4, 'NetCDF')
        tab.set_title(5, 'CSV')

        # Nao Aparece as outras Janelas ate o LOAD
        self._BOX9.layout.visibility = "hidden"
        self._BOX10.layout.visibility = "hidden"
        self._BOX12.layout.visibility = "hidden"
        self._BOXNetCDF.layout.visibility = "hidden" 
        self._BOXCSV.layout.visibility = "hidden"     
        display(tab)
        
    def _on_buttonPlot_clicked(self,b):
        self._out13.clear_output()
        with self._out13:
            level = self._radio_input.value
            time = self._radio_times.value
            selected_vars = self._size.value
            fig1, axes1 = plt.subplots(figsize=(11, 6))
            axes1.clear()
            f = self._fa
            
            if(self._tipo_plot=="area"):

                if not level: 
                    plt.show(f.sel(time=time)[selected_vars].plot())
                else:
                    plt.show(f.sel(time=time,level=level)[selected_vars].plot())
            else:

                if not level: 
                    pf=f.to_dataframe()
                    dfp=pf.pivot_table(index='time', values=[selected_vars])
                    axes1.plot(dfp)
                    axes1.legend(level)
                    plt.show(fig1)
                else:
                    pf=f.to_dataframe()
                    dfp=pf.pivot_table(index='time', columns='level', values=[selected_vars])
                    dfp.columns =[s1 + str(s2) for (s1,s2) in dfp.columns.tolist()]
                    legenda=self._lvs_escolhidos[::-1]
                    if(self._radio_input.value!="All"):
                            nameVar=selected_vars+str(self._radio_input.value)
                            dfp=dfp[nameVar]
                            legenda[0]=str(self._radio_input.value)

                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M')) 
                    plt.gca().xaxis.set_tick_params(rotation = 50)  
                    axes1.xaxis.set_major_locator(plt.MaxNLocator(dfp.index.size))
                    axes1.plot(dfp)
                    #print(legenda)
                    axes1.legend(legenda)
                    plt.show(fig1)

        return   


    def _on_buttonNetCDF_clicked(self,b):
        self._fa.to_netcdf("output.nc")
        self._buttonDownloadNetcdf.button_style="success"
        return   

    def _on_buttonCSV_clicked(self,b):
        level = []
        selected_vars = self._size.value

        try:
            level = self._fa['level']
        except:
            level = []

        if (level.any):
            df = self._fa.to_dataframe()
            df_output=df.pivot_table(selected_vars, ['latitude','longitude','level'],'time')
            df_output.to_csv('output.csv')
        else:       
            df = self._fa.to_dataframe()
            df_output=df.pivot_table(selected_vars, ['latitude','longitude'],'time')
            df_output.to_csv('output.csv')

        self._buttonDownloadCSV.button_style="success"
        return  


    def _on_buttonArea_clicked(self,b):

        self._tipo_plot = "area"
        lat1 = self._TXT1.value
        lat2 = self._TXT4.value
        lon1 = self._TXT2.value
        lon2 = self._TXT3.value
        print(lat1)
        print(lat2)
        print(lon1)
        print(lon2)

        f = self._ffull  

        lvs = []
        for x in f.level:
            lvs.append(str(x.values))
            print(x.values)

        self._radio_input.options=lvs

        if(self.__model.area['invertedlat']):
            self._fa = f.sel(latitude=slice(lat2, lat1), 
                            longitude=slice(lon1, lon2))
        else:
            self._fa = f.sel(latitude=slice(lat1, lat2), 
                            longitude=slice(lon1, lon2))    
        
        f = self._fa
        self._buttonArea.button_style="success"

    def _on_buttonAreaFull_clicked(self,b):
        self._tipo_plot = "area"
        f = self._ffull  
        self._buttonArea.button_style="success"
        return
    

    def _on_buttonPonto_clicked(self,b):

        f = self._ffull  
    
        lat = self._TXT5.value
        lon = self._TXT6.value
        self._tipo_plot = "ponto"

        lvs = []
        for x in f.level:
            lvs.append(str(x.values))
        lvs.append("All")
        self._radio_input.options=lvs
        self._fa=f.sel(longitude=lon, latitude=lat, method='nearest')
        self._buttonPonto.button_style="success"
        return
   
        
    def _on_button_clicked(self,b):

        with self._output: 
            print("load...")
            self._button.button_style=""
            selected_data = self._data.get_interact_value()
            self._output.clear_output()
            self._outCSV.clear_output()
            self._outNetCDF.clear_output()

            selected_vars = []
            for i in range(0, len(self._chk_vars)):
                if self._chk_vars[i].value == True:
                    selected_vars = selected_vars + [self._chk_vars[i].description]

            selected_lvs = []
            for i in range(0, len(self._chk_levels)):
                if self._chk_levels[i].value == True:
                    selected_lvs = selected_lvs + [self._chk_levels[i].description]

            self._lvs_escolhidos = selected_lvs


            self.__model.dict['area']['reduce'] = False

            f = self.__model.load(date=selected_data.strftime('%Y%m%d%H'), var=selected_vars,level=selected_lvs, steps=self._slider_steps.value)

            #
            # ffull - utilizado para manter a area total para recorte de area ou de ponto
            # fa - utilizado para ter uma area default para o plot e download
            #
            self._ffull = f
            self._fa = f

                
            self._BOX9.layout.visibility = "visible"
            self._BOX10.layout.visibility = "visible"   
            self._BOX12.layout.visibility = "visible"
            self._BOXNetCDF.layout.visibility = "visible" 
            self._BOXCSV.layout.visibility = "visible"

            if (f):
                self._button.button_style="success"
                try:
                    ttt=f['time'].size

                    if (ttt > 0):
                        varsSelection = []
                        for x in f.data_vars:
                            varsSelection.append(x)

                        self._size.options = varsSelection
                        lvs = []
                        for x in f.level:
                            lvs.append(str(x.values))
                        self._radio_input.options=lvs

                        tm = []
                        for x in f.time:
                            tm.append(str(x.values))
                        self._radio_times.options=tm

                        with outNetCDF:
                            display(f)
                        with outCSV:
                            display(f.to_dataframe())
                except:
                        varsSelection = []            
            
            else:
                self._button.button_style="danger"
        
    def get_xarray(self):
        """ 
            Função para retornar o valor em XArray das opcoes desejadas

            Retorno
            ------------------------------------------------------------------------------------------------------------------------------------------------------       

            * Xarray     : Dados do Modelo 
           
            ------------------------------------------------------------------------------------------------------------------------------------------------------       

        """     
        return self._fa              
        
        
    
    



