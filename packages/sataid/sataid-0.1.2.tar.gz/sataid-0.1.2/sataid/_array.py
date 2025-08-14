import os
import re
import numpy as np
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

def _utils_process_timestamp(_etim_tuple):
    """Utility to convert Sataid time tuple to a Python datetime object."""
    year = int(str(_etim_tuple[0]) + str(_etim_tuple[1]))
    month = _etim_tuple[2]
    day = _etim_tuple[3]
    hour = _etim_tuple[4]
    minute = _etim_tuple[5]

    dt = datetime(year, month, day, hour, minute)
    if minute > 0:
        dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return dt

class SataidArray:
    """
    A simple data structure to hold Sataid data and metadata.
    """
    ShortName = ['V1', 'V2', 'VS', 'N1', 'N2', 'N3', 'I4', 'WV', 'W2', 'W3', 'MI', 'O3', 'IR', 'L2', 'I2', 'CO']

    def __init__(self, lats, lons, data, sate, chan, etim, fint=None, asat=None, vers=None, eint=None, cord=None, eres=None, fname=None, units=None):
        self.lat = lats
        self.lon = lons
        self.data = data
        self.sate = sate
        self.chan = chan
        self.etim = etim
        self.fint = fint
        self.asat = asat
        self.vers = vers
        self.eint = eint
        self.cord = cord
        self.eres = eres
        self.fname = fname
        self.units = units

    def _get_description_string(self):
        """Generates a formatted string with data and satellite descriptions."""
        satellite_name = b"".join(self.sate).decode(errors='replace') if self.sate is not None else ""
        if satellite_name == 'Himawa-9':
            satellite_name = 'Himawari-9'
        nadir_coord = f"{self.asat[3]:.6f}, {self.asat[4]:.6f}" if self.asat is not None else ""
        altitude = f"{self.asat[5]:.2f} km" if self.asat is not None else ""
        time_str = _utils_process_timestamp(self.etim).strftime("%Y-%m-%d %H:%M UTC") if self.etim is not None else ""
        channel_raw = b"".join(self.chan).decode(errors='ignore') if self.chan is not None else ""
        channel_name = re.match(r'^[A-Za-z]+', channel_raw).group(0) if re.match(r'^[A-Za-z]+', channel_raw) else ''
        dimension = f"{self.data.shape[1]}x{self.data.shape[0]}"
        resolution = f"{self.eres[0]}" if self.eres is not None else ""
        version = b"".join(self.vers).decode(errors='replace') if self.vers is not None else ""
        lats, lons = self.lat, self.lon
        coord_range = (
            f"lat : {lats.min():.6f} - {lats.max():.6f}\n"
            f"lon : {lons.min():.6f} - {lons.max():.6f}"
        )
        desc = (
            "=== Data Description ===\n"
            f"Time: {time_str}\n"
            f"Channel: {channel_name}\n"
            f"Dimension: {dimension}\n"
            f"Resolution: {resolution}\n"
            f"Units: {self.units}\n"
            f"Sataid Version: {version}\n"
            f"Coordinate Range:\n{coord_range}\n\n"
            "=== Satellite Description ===\n"
            f"Satellite: {satellite_name}\n"
            f"Nadir Coordinate: {nadir_coord}\n"
            f"Altitude: {altitude}\n\n"
        )
        return desc

    def description(self):
        """Prints the formatted data description."""
        print(self._get_description_string())

    # --- PERUBAHAN DIMULAI DI SINI ---
    def _create_plot(self, cartopy=False, coastline_resolution='10m', coastline_color='blue', cmap=None, vmin=None, vmax=None):
        """Internal method to create a plot figure."""
        satellite_name = b"".join(self.sate).decode(errors='replace') if self.sate is not None else ""
        if satellite_name == 'Himawa-9': satellite_name = 'Himawari-9'
        channel_raw = b"".join(self.chan).decode(errors='ignore') if self.chan is not None else ""
        channel_name = re.match(r'^[A-Za-z]+', channel_raw).group(0) if re.match(r'^[A-Za-z]+', channel_raw) else ''

        plot_data = self.data

        # Logic for colormap and value range
        # If user provides a cmap, use it. Otherwise, use the default.
        if cmap is None:
            if self.units == 'Reflectance':
                colorbar_label = 'Reflectance'
                cmap_to_use = 'gray'
                vmin_to_use = vmin if vmin is not None else 0
                vmax_to_use = vmax if vmax is not None else 1.1
            elif self.units == '°C':
                colorbar_label = 'Brightness Temperature (°C)'
                cmap_to_use = 'gray_r'
                vmin_to_use = vmin if vmin is not None else -80
                vmax_to_use = vmax if vmax is not None else 60
            else:
                colorbar_label = f'Value ({self.units})' if self.units else 'Value'
                cmap_to_use = 'gray'
                vmin_to_use, vmax_to_use = vmin, vmax
        else:
            # User provided a custom cmap, use it directly
            colorbar_label = f'Value ({self.units})' if self.units else 'Value'
            cmap_to_use = cmap
            vmin_to_use, vmax_to_use = vmin, vmax


        time_str = _utils_process_timestamp(self.etim).strftime('%Y-%m-%d %H:%M UTC') if self.etim is not None else ""
        left_title = f"{satellite_name} {channel_name}"
        right_title = time_str

        if cartopy:
            try:
                import cartopy.crs as ccrs
                import cartopy.feature as cfeature
            except ImportError:
                print("\nError: 'cartopy' package is required for map plotting.")
                print("Please install it using: pip install cartopy matplotlib")
                return None

            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
            img = ax.imshow(
                plot_data,
                extent=(self.lon.min(), self.lon.max(), self.lat.min(), self.lat.max()),
                origin='upper', cmap=cmap_to_use, vmin=vmin_to_use, vmax=vmax_to_use,
                interpolation='none', transform=ccrs.PlateCarree()
            )
            ax.coastlines(resolution=coastline_resolution, color=coastline_color, linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor=coastline_color)
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels, gl.right_labels = False, False
            gl.xlabel_style, gl.ylabel_style = {'size': 9}, {'size': 9}
            ax.set_title(right_title, loc='right', fontsize=10, fontweight='bold')
            ax.set_title(left_title, loc='left', fontsize=10, fontweight='bold')
            cbar = fig.colorbar(img, ax=ax, orientation='vertical', pad=0.01, shrink=0.7)
            cbar.set_label(colorbar_label, size=9)
            cbar.ax.tick_params(labelsize=8)
            if self.units == '°C': cbar.ax.invert_yaxis()
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            img = ax.imshow(plot_data, cmap=cmap_to_use, extent=(self.lon.min(), self.lon.max(), self.lat.min(), self.lat.max()), aspect='auto', vmin=vmin_to_use, vmax=vmax_to_use)
            cbar = fig.colorbar(img, ax=ax, pad=0.01)
            cbar.set_label(colorbar_label, size=9)
            cbar.ax.tick_params(labelsize=8)
            if self.units == '°C': cbar.ax.invert_yaxis()
            ax.set_title(right_title, loc='right', fontsize=10, fontweight='bold')
            ax.set_title(left_title, loc='left', fontsize=10, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=9)
            ax.set_ylabel('Latitude', fontsize=9)
        return fig

    def plot(self, cartopy=False, coastline_resolution='10m', coastline_color='blue', cmap=None, vmin=None, vmax=None):
        """
        Displays an interactive plot of the Sataid data.
        
        Args:
            cartopy (bool): If True, renders a map plot.
            coastline_resolution (str): Resolution for coastlines ('10m', '50m', '110m').
            coastline_color (str): Color of the coastlines.
            cmap (str, optional): Custom Matplotlib colormap to use. Defaults to internal settings.
            vmin (float, optional): Custom minimum value for the color scale.
            vmax (float, optional): Custom maximum value for the color scale.
        """
        fig = self._create_plot(cartopy=cartopy, coastline_resolution=coastline_resolution, coastline_color=coastline_color, cmap=cmap, vmin=vmin, vmax=vmax)
        if fig: plt.show()

    def savefig(self, output_file=None, cartopy=False, coastline_resolution='10m', coastline_color='blue', cmap=None, vmin=None, vmax=None):
        """
        Saves the Sataid data visualization to a file.
        
        Args:
            output_file (str, optional): Path to save the image.
            (Other args are the same as plot)
        """
        fig = self._create_plot(cartopy=cartopy, coastline_resolution=coastline_resolution, coastline_color=coastline_color, cmap=cmap, vmin=vmin, vmax=vmax)
        if not fig: return

        filename_to_save = output_file or (os.path.basename(self.fname) + '.png' if self.fname else None)
        if filename_to_save:
            print(f"Saving plot to: {filename_to_save}")
            fig.savefig(filename_to_save, bbox_inches='tight', dpi=300)
            plt.close(fig)
            
    # --- Sisa fungsi (sel, to_netcdf, dll) tetap sama ---
    def sel(self, latitude=None, longitude=None, method=None):
        """Selects data based on coordinates."""
        if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            method = method or 'nearest'
            if method == 'nearest':
                lat_idx = np.abs(self.lat - latitude).argmin()
                lon_idx = np.abs(self.lon - longitude).argmin()
                return self.data[lat_idx, lon_idx]
            elif method in ['linear', 'cubic']:
                try:
                    from scipy.interpolate import RectBivariateSpline
                except ImportError:
                    print(f"\nError: 'scipy' package is required for method='{method}'.")
                    print("Please install it using: pip install scipy")
                    return None
                lats_interp, data_interp = (self.lat, self.data)
                if lats_interp[0] > lats_interp[-1]:
                    lats_interp, data_interp = lats_interp[::-1], data_interp[::-1, :]
                k = 3 if method == 'cubic' else 1
                interpolator = RectBivariateSpline(lats_interp, self.lon, data_interp, kx=k, ky=k)
                return interpolator(latitude, longitude)[0, 0]
            else:
                raise NotImplementedError(f"Method '{method}' is not supported for point extraction.")

        lat_idx = slice(None)
        if latitude is not None:
            if not isinstance(latitude, slice): raise TypeError("For area extraction, 'latitude' must be a slice object.")
            lat_min, lat_max = latitude.start, latitude.stop
            lat_idx = (self.lat >= min(lat_min, lat_max)) & (self.lat <= max(lat_min, lat_max))
        lon_idx = slice(None)
        if longitude is not None:
            if not isinstance(longitude, slice): raise TypeError("For area extraction, 'longitude' must be a slice object.")
            lon_min, lon_max = longitude.start, longitude.stop
            lon_idx = (self.lon >= min(lon_min, lon_max)) & (self.lon <= max(lon_min, lon_max))
        
        data_subset = self.data[np.ix_(lat_idx, lon_idx)]
        lats_subset, lons_subset = self.lat[lat_idx], self.lon[lon_idx]
        return SataidArray(
            lats_subset, lons_subset, data_subset,
            sate=self.sate, chan=self.chan, etim=self.etim, fint=self.fint, 
            asat=self.asat, vers=self.vers, eint=self.eint, cord=self.cord,
            eres=self.eres, fname=self.fname, units=self.units
        )

    def to_netcdf(self, output_filename=None):
        """Converts and saves the SataidArray data to a NetCDF file."""
        try:
            import netCDF4 as nc
        except ImportError:
            print("\nError: 'netCDF4' package required. Please install with 'pip install netCDF4'")
            return
        
        channel_raw = b"".join(self.chan).decode(errors='ignore')
        channel_name = re.match(r'^[A-Za-z0-9]+', channel_raw).group(0) if re.match(r'^[A-Za-z0-9]+', channel_raw) else 'data'
        output_filename = output_filename or (os.path.basename(self.fname) + '.nc' if self.fname else 'output.nc')

        print(f"Saving data to: {output_filename}")
        with nc.Dataset(output_filename, 'w', format='NETCDF4') as ds:
            ds.description = self._get_description_string()
            ds.author = "Sepriando"
            ds.createDimension('lat', self.data.shape[0])
            ds.createDimension('lon', self.data.shape[1])
            latitudes = ds.createVariable('lat', 'f4', ('lat',)); longitudes = ds.createVariable('lon', 'f4', ('lon',))
            latitudes.units, longitudes.units = "degrees_north", "degrees_east"
            latitudes[:], longitudes[:] = self.lat, self.lon
            data_var = ds.createVariable(channel_name, 'f4', ('lat', 'lon',))
            data_var.long_name = f"Data from Sataid channel {channel_name}"
            if self.units: data_var.units = self.units
            data_var[:, :] = self.data

    def to_geotiff(self, output_filename=None):
        """Converts and saves the SataidArray data to a GeoTIFF file."""
        try:
            import rasterio
            from rasterio.transform import from_bounds
        except ImportError:
            print("\nError: 'rasterio' package is required. Please install with 'pip install rasterio'")
            return

        output_filename = output_filename or (os.path.basename(self.fname) + '.tif' if self.fname else 'output.tif')
        print(f"Saving data to: {output_filename}")

        left, bottom, right, top = self.lon.min(), self.lat.min(), self.lon.max(), self.lat.max()
        height, width = self.data.shape
        transform = from_bounds(left, bottom, right, top, width, height)

        with rasterio.open(
            output_filename, 'w', driver='GTiff', height=height, width=width,
            count=1, dtype=str(self.data.dtype), crs='EPSG:4326', transform=transform
        ) as dst:
            dst.write(self.data, 1)

    def to_xarray(self):
        """Converts the SataidArray object to an xarray.DataArray."""
        try:
            import xarray as xr
        except ImportError:
            print("\nError: 'xarray' package is required. Please install with 'pip install xarray'")
            return None

        lats_xr, data_xr = (self.lat, self.data)
        if lats_xr[0] > lats_xr[-1]:
            lats_xr, data_xr = lats_xr[::-1], data_xr[::-1, :]

        coords = {'lat': ('lat', lats_xr), 'lon': ('lon', self.lon)}
        satellite_name = b"".join(self.sate).decode(errors='replace').strip()
        if satellite_name == 'Himawa-9': satellite_name = 'Himawari-9'
        channel_name = re.match(r'^[A-Za-z]+', b"".join(self.chan).decode(errors='ignore')).group(0)
        attrs = {'satellite': satellite_name, 'channel': channel_name, 'units': self.units, 'long_name': f'Data from Sataid channel {channel_name}'}
        return xr.DataArray(data=data_xr, dims=('lat', 'lon'), coords=coords, name=channel_name, attrs=attrs)