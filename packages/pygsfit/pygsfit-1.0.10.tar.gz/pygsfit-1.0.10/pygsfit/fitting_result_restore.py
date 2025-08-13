import numpy as np
from astropy.io import fits
from lmfit import Parameters

# Minimal class to hold the data
class MyDataObject:
    def __init__(self):
        self.header = None
        self.observed_spectrum = None
        self.error = None
        self.obs_freq = None
        self.model_freq = None
        self.model_spectrum = None
        self.params_table = None
        self.file_dict = None
        self.params = None

def read_combined_fits_file(filename):
    with fits.open(filename) as hdul:
        data_objects = []
        current_object = None

        for hdu in hdul:
            if hdu.name.endswith('_PRIMARY'):
                if current_object:
                    data_objects.append(current_object)
                current_object = MyDataObject()
                current_object.header = hdu.header
            elif hdu.name.endswith('_OBSERVED_SPECTRUM'):
                current_object.observed_spectrum = hdu.data
            elif hdu.name.endswith('_ERROR'):
                current_object.error = hdu.data
            elif hdu.name.endswith('_OBS_FREQ'):
                current_object.obs_freq = hdu.data
            elif hdu.name.endswith('_MODEL_FREQ'):
                current_object.model_freq = hdu.data
            elif hdu.name.endswith('_MODEL_SPECTRUM'):
                current_object.model_spectrum = hdu.data
            elif hdu.name.endswith('_PARAMETERS'):
                current_object.params_table = hdu.data
                current_object.params = recreate_lmfit_parameters(current_object.params_table)
            elif hdu.name.endswith('_FILE_PATHS'):
                file_path_table = hdu.data
                current_object.file_dict = {row['Key'].strip(): row['Value'].strip() for row in file_path_table}

        if current_object:
            data_objects.append(current_object)

    return data_objects

def recreate_lmfit_parameters(structured_array):
    params = Parameters()
    for row in structured_array:
        #param_name = row['name'].decode('utf-8')
        param_name = row['name'].decode('utf-8') if isinstance(row['name'], bytes) else row['name']
        value = row['value']
        min_val = row['min']
        max_val = row['max']
        vary = row['vary']
        stderr = row['stderr']

        params.add(param_name, value=value, min=min_val, max=max_val, vary=vary)
        # If you need to store stderr or use it later, you might want to add it as an attribute or use another method
        params[param_name].stderr = stderr

    return params

# Example usage
filename = '/Volumes/Media_1t/work/20220511/eovsa_fitting/narrow/slf_final_XX_t38_allbd_bkp/slf_final_XX_t38_allbd_fit_res.fits'
data_objects = read_combined_fits_file(filename)

# Accessing attributes of the first object for demonstration
first_object = data_objects[0]
print(first_object.header)
print(first_object.observed_spectrum)
print(first_object.error)
print(first_object.obs_freq)
print(first_object.model_freq)
print(first_object.model_spectrum)
print(first_object.params_table)
print(first_object.file_dict)

# Accessing attributes of the second object for demonstration
if len(data_objects) > 1:
    second_object = data_objects[1]
    print(second_object.header)
    print(second_object.observed_spectrum)
    print(second_object.error)
    print(second_object.obs_freq)
    print(second_object.model_freq)
    print(second_object.model_spectrum)
    print(second_object.params_table)
    print(second_object.file_dict)
