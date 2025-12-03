#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------#

#PYTHON PACKAGES
#Call EE
import ee
from datetime import date

#FOLDERS
from .landsatcollection import fexp_landsat_8PathRow, fexp_landsat_9PathRow, fexp_landsat_7PathRow, fexp_landsat_5PathRow
from .masks import (apply_scale_factors,f_albedoL8,f_cloudMaskL8_L2,apply_scale_factorsL5L7,f_cloudMaskL457_SR,f_albedoL5L7)
from .meteorology import get_meteorology
from .tools import (fexp_spec_ind, fexp_lst_export,fexp_radlong_up, LST_DEM_correction,
fexp_radshort_down, fexp_radlong_down, fexp_radbalance, fexp_soil_heat,fexp_sensible_heat_flux)
from .endmembers import fexp_cold_pixel, fexp_hot_pixel
from .evapotranspiration import fexp_et
import json

      

class Collection():

    def __init__(self,
                 year_i, month_i, day_i,
                 year_e, month_e, day_e,
                 cloud_cover, path, row,
                 NDVI_cold=5, Ts_cold=20,
                 NDVI_hot=10, Ts_hot=20):

        # Load mappings - these will be attached to the class instance
        with open('/content/geeSEBAL-master/etbrasil/geesebal_modified/setting.json', 'r') as json_file:
            self.mapping = json.load(json_file)
        with open('/content/geeSEBAL-master/etbrasil/geesebal_modified/settingL5L7.json', 'r') as json_file:
            self.mapping57 = json.load(json_file)

        # Date handling and collection merging
        py_start_date = date(year_i, month_i, day_i)
        py_end_date = date(year_e, month_e, day_e)
        ee_start_date = ee.Date.fromYMD(year_i, month_i, day_i)
        n_search_days = (py_end_date - py_start_date).days
        ee_end_date = ee_start_date.advance(n_search_days, 'day')
        
        collections_to_merge = []

        if py_start_date < date(2013, 1, 1):
            collections_to_merge.append(fexp_landsat_5PathRow(ee_start_date, ee_end_date, path, row, cloud_cover))
        if py_start_date < date(2014, 1, 1):
            collections_to_merge.append(fexp_landsat_7PathRow(ee_start_date, ee_end_date, path, row, cloud_cover))
        if py_end_date >= date(2014, 1, 1):
            collections_to_merge.append(fexp_landsat_8PathRow(ee_start_date, ee_end_date, path, row, cloud_cover))
        if py_end_date >= date(2022, 1, 1):
            collections_to_merge.append(fexp_landsat_9PathRow(ee_start_date, ee_end_date, path, row, cloud_cover))

        if not collections_to_merge:
            self.collection = ee.ImageCollection([])
            print("WARNING: No suitable Landsat collections found.")
        else:
            merged_collection = ee.ImageCollection(collections_to_merge[0])
            if len(collections_to_merge) > 1:
                for i in range(1, len(collections_to_merge)):
                    merged_collection = merged_collection.merge(collections_to_merge[i])
            self.collection = merged_collection
        
        self.count = self.collection.size().getInfo()
        print("Number of scenes found: ", self.count)

        self.p_top_NDVI = ee.Number(NDVI_cold)
        self.p_coldest_Ts = ee.Number(Ts_cold)
        self.p_lowest_NDVI = ee.Number(NDVI_hot)
        self.p_hottest_Ts = ee.Number(Ts_hot)

        et_collection = self.collection.map(self.process_single_image)
        self.Collection_ET = et_collection.toBands()

    def process_single_image(self, image):
        image = ee.Image(image)
        landsat_version = ee.String(image.get('SPACECRAFT_ID'))
        time_start = image.get('system:time_start')
        _date = ee.Date(time_start)
        sun_elevation = image.get('SUN_ELEVATION')
        
        # --- SOLUTION: Pass mapping dictionaries as arguments ---
        # The nested functions now explicitly accept the data they need.
        def prep_l8_l9(img, mapping):
            img = apply_scale_factors(img)
            img = f_cloudMaskL8_L2(img)
            img = img.select(list(mapping.values()), list(mapping.keys()))
            return f_albedoL8(img)

        def prep_l5_l7(img, mapping57):
            img = apply_scale_factorsL5L7(img)
            img = f_cloudMaskL457_SR(img)
            img = img.select(list(mapping57.values()), list(mapping57.keys()))
            return f_albedoL5L7(img)

        # This robust, nested 'If' structure remains the same.
        processed_image = ee.Image(
            ee.Algorithms.If(
                landsat_version.equals('LANDSAT_8'),
                # Pass the mapping dictionary from 'self' as an argument
                prep_l8_l9(image, self.mapping),
                ee.Algorithms.If(
                    landsat_version.equals('LANDSAT_9'),
                    # Pass the mapping dictionary from 'self' as an argument
                    prep_l8_l9(image, self.mapping),
                    # Pass the other mapping dictionary from 'self' as an argument
                    prep_l5_l7(image, self.mapping57)
                )
            )
        )

        # --- CORE SEBAL PROCESSING LOGIC (REMAINS THE SAME) ---
        geometryReducer = processed_image.geometry().bounds()
        col_meteorology = get_meteorology(processed_image, time_start)
        T_air = col_meteorology.select('AirT_G')
        ux = col_meteorology.select('ux_G')
        UR = col_meteorology.select('RH_G')
        Rn24hobs = col_meteorology.select('Rn24h_G')

        srtm = ee.Image('USGS/SRTMGL1_003').clip(geometryReducer)
        z_alt = srtm.select('elevation')

        image_with_indices = fexp_spec_ind(processed_image)
        
        hour = ee.Number(_date.get('hour'))
        minutes = ee.Number(_date.get('minutes'))
        image_with_lst = LST_DEM_correction(image_with_indices, z_alt, T_air, UR, sun_elevation, hour, minutes)

        d_cold_pixel = fexp_cold_pixel(image_with_lst, geometryReducer, self.p_top_NDVI, self.p_coldest_Ts)
        n_Ts_cold = ee.Number(d_cold_pixel.get('temp'))

        image_rad1 = fexp_radlong_up(image_with_lst)
        image_rad2 = fexp_radshort_down(image_rad1, z_alt, T_air, UR, sun_elevation)
        image_rad3 = fexp_radlong_down(image_rad2, n_Ts_cold)
        image_with_radbalance = fexp_radbalance(image_rad3)

        image_with_g = fexp_soil_heat(image_with_radbalance)
        d_hot_pixel = fexp_hot_pixel(image_with_g, geometryReducer, self.p_lowest_NDVI, self.p_hottest_Ts)
        date_string = _date.format('YYYY-MM-dd')
        image_with_h = fexp_sensible_heat_flux(image_with_g, ux, UR, Rn24hobs, n_Ts_cold, d_hot_pixel, date_string, geometryReducer)
        
        final_image = fexp_et(image_with_h, Rn24hobs)

        landsat_id = ee.String(final_image.get('LANDSAT_PRODUCT_ID'))
        final_name = landsat_id.slice(0, 5).cat(landsat_id.slice(10, 17)).cat(landsat_id.slice(17, 25))
        # print(final_name)
        return final_image.select(['ET_24h']).rename(final_name)
       