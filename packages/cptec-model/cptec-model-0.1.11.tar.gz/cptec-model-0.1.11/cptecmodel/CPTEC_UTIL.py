import xarray as xr
import xesmf as xe

def regrid(source,target):
	"""
	    
	    A função regrid muda a grade do arquivo fonte para a grade do arquivo destino
	    
	    Parametros
	    ------------------------------------------------------------------------------------------------------------       
	    source  : Xarray da grade fonte
	    target : Xarray da grade destino
	    ------------------------------------------------------------------------------------------------------------       

	    regrid(source,target)

	    ------------------------------------------------------------------------------------------------------------       
	    
	    Retorna um Xarray contendo com os dados do Fonte na grade de Destino

	    ------------------------------------------------------------------------------------------------------------       

	"""

	nlins_ncols_src  = [source.latitude.values.shape, source.longitude.values.shape]
	nlins_ncols_trg  = [target.latitude.values.shape, target.longitude.values.shape]

	bounds_src = [source.longitude.values[0], source.longitude.values[-1], source.latitude.values[0], source.latitude.values[-1]]
	bounds_trg = [target.longitude.values[0], target.longitude.values[-1], target.latitude.values[0], target.latitude.values[-1]]


	# Grade de saída (que será a mesma do Target)
	ds_out = xr.Dataset(
    	{
    	    "latitude": (["latitude"], target.latitude.values),
    	    "longitude": (["longitude"], target.longitude.values),
    	}
	)

	# Criando a grade reprojetada
	regridder = xe.Regridder(source, ds_out, "bilinear")

	# Aplicando a reprojeção
	out = regridder(source)

	return out



