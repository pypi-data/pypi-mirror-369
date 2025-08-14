# Sataid Python Package

**sataid** is a Python library designed to read, process, and visualize data from the Sataid binary format, commonly used for weather satellite imagery.

This package provides a simple interface to handle complex binary files, allowing users to quickly access, analyze, and export satellite data into standard formats like NetCDF, GeoTIFF, or xarray.DataArray.

## Features
- **Direct Reading**: Reads Sataid binary files effortlessly.
- **Auto-Calibration**: Converts raw data to physical units (Reflectance or Brightness Temperature in °C).
- **Rich Visualization**: Creates plots with map projections using `matplotlib` and `cartopy`.
- **Data Subsetting**: Easily extract data for a specific point or a geographical region.
- **Format Conversion**: Exports data to NetCDF, GeoTIFF, and `xarray.DataArray` for further analysis.

## Installation

You can install the package using pip:
```bash
pip install sataid
```
The package requires several scientific libraries. If you encounter issues, you may need to install them manually, especially `cartopy` which can have complex dependencies.

```bash
pip install numpy matplotlib netcdf4 scipy rasterio cartopy
```

## Usage Examples

Here is a comprehensive example demonstrating the main features of the `sataid` package.

```python
from sataid import read_sataid

# Define the path to your Sataid data file
file_path = 'H09_B13_Indonesia_20251026.Z0000' # Example filename

# 1. Read the Sataid file
# This returns a SataidArray object with data and metadata.
sat_data = read_sataid(file_path)

# 2. Display Data Description
# Get a quick summary of the data, including time, channel, and satellite info.
print("--- Data Description ---")
sat_data.description()

# 3. Create a Plot with a Map Overlay
# The `cartopy=True` argument renders coastlines and borders.
print("\n--- Generating plot with Cartopy map ---")
sat_data.plot(cartopy=True)

# 4. Save the Plot to a File
# Save the visualization as a high-resolution PNG image.
print("\n--- Saving plot to file ---")
output_image_path = 'himawari_b13_plot.png'
sat_data.savefig(output_image_path, cartopy=True)

# 5. Extract Data for a Specific Point
# Get the brightness temperature for a specific coordinate (e.g., Jakarta).
# Method can be 'nearest' (default), 'linear', or 'cubic'.
print("\n--- Extracting value at a specific point ---")
jakarta_lat, jakarta_lon = -6.20, 106.84
temperature = sat_data.sel(latitude=jakarta_lat, longitude=jakarta_lon, method='linear')
if temperature is not None:
    print(f"Brightness Temperature near Jakarta: {temperature:.2f} {sat_data.units}")

# 6. Select a Geographical Subset (Region)
# Crop the data to a specific area, for example, the island of Java.
print("\n--- Creating a subset for a region ---")
java_area = sat_data.sel(
    latitude=slice(-5, -9),      # Slice from 5°S to 9°S
    longitude=slice(105, 115)    # Slice from 105°E to 115°E
)
print("Subset created. New coordinate range:")
java_area.description()
# You can now plot or save this subset
# java_area.plot(cartopy=True)

# 7. Convert to Other Formats for Analysis
# Convert to an xarray.DataArray for powerful, labeled data analysis.
print("\n--- Converting to xarray.DataArray ---")
xr_data = sat_data.to_xarray()
if xr_data is not None:
    print(xr_data)
    # Example: calculate the mean temperature for the entire dataset
    mean_temp = xr_data.mean()
    print(f"\nMean temperature across the scene: {mean_temp.item():.2f} {xr_data.attrs['units']}")

# Convert to a NetCDF file for use in other scientific software.
print("\n--- Exporting to NetCDF ---")
sat_data.to_netcdf('output_data.nc')
```