#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------#

#PYTHON PACKAGES
#Call EE
import ee
import json
#CLOUD REMOVAL


# #FUNCTION TO MASK CLOUD IN LANDSAT 8 FOR SURFACE REFELCTANCE
def f_cloudMaskL8_SR(image):
      
    quality = image.select('QA_PIXEL');
    c01 = quality.eq(322); #CLEAR, LOW CONFIDENCE CLOUD
    c02 = quality.eq(324); #WATER, LOW CONFIDENCE CLOUD
    c03 = quality.eq(1346);#CLEAR TERRAIN
    mask = c01.Or(c02).Or(c03);
    return image.updateMask(mask);

def apply_scale_factors(image):
    
    optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    # thermal_bands = image.select('ST_TRAD').multiply(0.001)
    return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)
  
  
def apply_scale_factorsL5L7(image):
    
    optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal_bands = image.select('ST_B6').multiply(0.00341802).add(149.0)
    # thermal_bands = image.select('ST_TRAD').multiply(0.001)
    return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)
  

def f_cloudMaskL8_L2(image):
    qa_mask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
    saturation_mask = image.select('QA_RADSAT').eq(0)
    return image.updateMask(qa_mask).updateMask(saturation_mask) 
  
  
def f_cloudMaskL457_SR(image):
    qa_mask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
    saturation_mask = image.select('QA_RADSAT').eq(0)
    return image.updateMask(qa_mask).updateMask(saturation_mask) 
  
  
def f_albedoL5L7(image):

    alfa = image.expression(
      '(0.254*B1) + (0.149*B2) + (0.147*B3) + (0.311*B4) + (0.103*B5) + (0.036*B7)',{
        'B1' : image.select(['B']),
        'B2' : image.select(['GR']),
        'B3' : image.select(['R']),
        'B4' : image.select(['NIR']),
        'B5' : image.select(['SWIR_1']),
        'B7' : image.select(['SWIR_2'])
      }).rename('ALFA');

    #ADD BANDS
    return image.addBands(alfa);

#ALBEDO
#USING TASUMI ET AL. (2008) METHOD FOR LANDSAT 8
#COEFFICIENTS FROM KE ET AL. (2016)
def f_albedoL8(image):
  
    alfa = image.expression(
      '(0.130*B1) + (0.115*B2) + (0.143*B3) + (0.180*B4) + (0.281*B5) + (0.108*B6) + (0.042*B7)',{  #// (Ke, Im  et al 2016)
        'B1' : image.select(['UB']),
        'B2' : image.select(['B']),
        'B3' : image.select(['GR']),
        'B4' : image.select(['R']),
        'B5' : image.select(['NIR']),
        'B6' : image.select(['SWIR_1']),
        'B7' : image.select(['SWIR_2'])
      }).rename('ALFA');

    #ADD BANDS
    return image.addBands(alfa);

if __name__ == "__main__":
    f_albedoL8()
    f_albedoL5L7()
    f_cloudMaskL457_SR()
    f_cloudMaskL8_L2()
    apply_scale_factors()
    f_cloudMaskL8_SR()
