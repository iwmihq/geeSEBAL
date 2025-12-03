# geeSEBAL v0.2.0: Surface Energy Balance Algorithm for Land

<img src="https://github.com/et-brasil/EESEBAL/blob/master/Images/geeSEBAL_logo_update_cut.png?raw=true" width="200">

**Current Version:** 0.2.0  
**Based on:** geeSEBAL v0.1.0 (ETBRASIL)

geeSEBAL is an open-source implementation of the Surface Energy Balance Algorithm for Land (SEBAL) using Google Earth Engine (GEE). It allows for the estimation of evapotranspiration (ET) and is available in Python API.

A web application for the previous version is available at [https://github.com/et-brasil/geeSEBAL].

---

## ⚠️ Major Update: Version 0.2.0 (Landsat Collection 2)

### Why this update exists?
Following the deprecation of the previously utilized Landsat dataset—specifically **Landsat 8 & 9 Collection 1 (C01) Tier 1 (T1) surface reflectance (SR)** the geeSEBAL model **(v0.1.0)** required adaptation.

Since 2021, the discontinuity of consistent data availability posed challenges for long-term remote sensing-based monitoring of water utilization and harnessing efficiency, mainly in agricultural regions. To address these challenges, **geeSEBAL v0.2.0** was developed to enhance reliability and applicability for evaporation estimation, specifically validated in the delta region.

### What is new in v0.2.0?
This version has been adapted to utilize the **Landsat Collection 2 (C02) Tier 1 (T1) Level 2 (L2)** image collection datasets.

*   **Old Input (v0.1.0):** Landsat Collection 1 (`LANDSAT/LC08/C01/T1_SR`)
*   **New Input (v0.2.0):** Landsat Collection 2 (`LANDSAT/LC08/C02/T1_L2`)

---

## How to use Google Earth Engine?

You need an account in GEE (https://earthengine.google.com/).

### Installation (Python API)

Using pip to install the earth engine API:

```bash
pip install earthengine-api
```

Authenticate the Earth Engine library:
```python
import ee
ee.Authenticate()
ee.Initialize()
```

---

## Examples

### 1. Image
Processing a single Landsat image.  
*Note: Ensure you use a Collection 2 Image ID for v0.2.0.*

```python
from etbrasil.geesebal import Image
import ee

# Example using Landsat 8 Collection 2 Level 2
# Format: LANDSAT/LC08/C02/T1_L2/ID
Image_ID = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_L2SP_222081_20210115_20210304_02_T1')

geeSEBAL_Image = Image(Image_ID)
```

### 2. Collection
Processing a collection of images over a period of time.

```python
from etbrasil.geesebal import Collection

# inputs = init Year, init Month, init day, end Year, end Month, end day, Cloud Cover
geeSEBAL_Collection = Collection(2021, 1, 1, 2021, 5, 6, 15)
```

### 3. TimeSeries
Extracting time series data for a specific location.

```python
from etbrasil.geesebal import TimeSeries
import ee

# inputs = init Year, init Month, init day, end Year, end Month, end day, Cloud Cover, ee.Geometry.Point
point = ee.Geometry.Point([-50.161317, -9.824870])

geeSEBAL_TimeSeries = TimeSeries(2020, 1, 1, 2022, 5, 6, 15, point)
```

---

## Methodology

### What is SEBAL?

Surface Energy Balance Algorithm for Land (SEBAL) was developed and validated by Bastiaanssen (Bastiaanssen, 1995; Bastiaanssen et al., 1998a, 1998b) to estimate evapotranspiration (ET) from energy balance equation:

$$Rn - G = LE + H$$

Where **LE**, **Rn**, **G** and **H** are Latent Heat Flux, Net Radiation, Soil Heat Flux and Sensible Heat Flux, respectively.

### Flowchart
![geeSEBAL Fluxogram](https://github.com/et-brasil/EESEBAL/blob/master/Images/ilustration.png?raw=true)

---

## Cite this work

If you use this code, please cite the base implementation (v0.1.0) and the v0.2.0 adaptation.

### Base Implementation (v0.1.0)
> [Laipelt et al. (2021)] Long-term monitoring of evapotranspiration using the SEBAL algorithm and Google Earth Engine cloud computing. (https://doi.org/10.1016/j.isprsjprs.2021.05.018)

### Modified Adaptation (v0.2.0)
> *[Insert your Name/Study Citation here regarding the Collection 2 adaptation and Delta region study]*

---

## References

### More about SEBAL:
*   [Bastiaanssen, W.G.M., 1995. Regionalization of surface flux densities and moisture indicators in composite terrain: a remote sensing approach under clear skies in Mediterranean climates. Dr. thesis, Wageningen Agric. Univ. Wageningen Netherlands. SC-DLO, Wageningen.](https://doi.org/90-5485-465-0)
*   [Bastiaanssen, W.G.M., Menenti, M., Feddes, R.A., Holtslag, A.A.M., 1998a. A remote sensing surface energy balance algorithm for land (SEBAL): 1. Formulation. J. Hydrol. 212–213, 198–212.](https://doi.org/10.1016/S0022-1694(98)00253-4)
*   [Bastiaanssen, W.G.M., Pelgrum, H., Wang, J., Ma, Y., Moreno, J.F., Roerink, G.J., van der Wal, T., 1998c. A remote sensing surface energy balance algorithm for land (SEBAL): 2. Validation. J. Hydrol. 212–213, 213–229.](https://doi.org/10.1016/S0022-1694(98)00254-6)

### Related Work:
*   [Ruhoff, A., Paz, A., Collischonn, W., Aragão, L., Rocha, H., S. Malhi, Y., 2012. A MODIS-Based Energy Balance to Estimate Evapotranspiration for Clear-Sky Days in Brazilian Tropical Savannas, Remote Sensing, vol. 4, issue 3, pp. 703-725.](https://doi.org/10.3390/rs4030703)
*   [Ruhoff, A. R. Paz, L. E. O. C. Aragao, Q. Mu, Y. Malhi, W. Collischonn, H. R. Rocha & S. W. Running (2013) Assessment of the MODIS global evapotranspiration algorithm using eddy covariance measurements and hydrological modelling in the Rio Grande basin, Hydrological Sciences Journal, 58:8, 1658-1676](https://DOI:10.1080/02626667.2013.837578)
*   [Laipelt, L.; Ruhoff, A.L.; Fleischmann, A.S.; Kayser, R.H.B.; Kich, E.M.; da Rocha, H.R.; Neale, C.M.U. Assessment of an Automated Calibration of the SEBAL Algorithm to Estimate Dry-Season Surface-Energy Partitioning in a Forest–Savanna Transition in Brazil. Remote Sens. 2020, 12, 1108.](https://doi.org/10.3390/rs12071108)

---
*This repository is a modification of the work by [ETBRASIL](https://github.com/et-brasil/geeSEBAL).*
```
