import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors

class WindSpeedVisualizer:
    """
    A class to visualize wind speed data, including mean wind speed and direction,
    spatial distribution of shape and scale parameters, and best fit distributions.
    """

    def __init__(self, adjusted_data):
        """
        Initialize the WindSpeedVisualizer with the adjusted wind speed data.

        Parameters:
            adjusted_data (xarray.Dataset): The adjusted wind speed dataset.
        """
        self.adjusted_data = adjusted_data
        self.u = adjusted_data.u
        self.v = adjusted_data.v

        # Extract metadata and handle False if no filtering is applied
        self.season = self._extract_filter_metadata('season', 'No seasonal filtering applied')
        self.months = self._extract_filter_metadata('months', 'No monthly filtering applied')
        self.hours = self._extract_filter_metadata('hours', 'No hourly filtering applied')
        self.force_fit = self._extract_filter_metadata('force_fit', 'Applied distribution fit: Auto-detection')
        
        self.extract_data()

    def _extract_filter_metadata(self, key, no_filter_message):
        """
        Extract metadata from the dataset attributes. If no filtering is applied, return False.
        
        Args:
            key (str): The metadata key to extract (e.g., 'season', 'months', 'hours').
            no_filter_message (str): The message stored in the metadata when no filtering is applied.

        Returns:
            If filtering is applied, return the metadata; otherwise, return False.
        """
        value = self.adjusted_data.attrs.get(key, no_filter_message)
        if value == no_filter_message:
            return False
        return value

    def extract_data(self):
        """Extract the necessary variables from the datasets."""
        self.k, self.c, self.best_dist = (
            self.adjusted_data.k,
            self.adjusted_data.c,
            self.adjusted_data.best_dist,
        )

        # Calculate mean wind speed and direction
        self.ws_mean = np.sqrt(self.u**2 + self.v**2).mean(dim="time")
        self.u_mean = self.u.mean(dim="time")
        self.v_mean = self.v.mean(dim="time")

    def _filter_data(self, data):
        """
        Filter the dataset based on the season, months, and hours.

        Args:
            data (xarray.DataArray): The input data to filter.

        Returns:
            xarray.DataArray: The filtered dataset.
        """
        if self.season:
            data = self._filter_by_season(data, self.season)
        if self.months:
            data = self._filter_by_months(data, self.months)
        if self.hours:
            data = self._filter_by_hours(data, self.hours)
        return data

    def _set_extent(self, ax):
        """Set the extent of the plot."""
        ax.set_extent([self.u.longitude.min(),
                       self.u.longitude.max(),
                       self.u.latitude.min(),
                       self.u.latitude.max()],
                      crs=ccrs.PlateCarree())

    def plot_mean_wind_speed_direction(self, ax):
        """Plot the mean wind speed and direction."""
        self._set_extent(ax)
        cs = ax.contourf(
            self.ws_mean.longitude,
            self.ws_mean.latitude,
            self.ws_mean,
            cmap="rainbow",
            transform=ccrs.PlateCarree(),
        )
        self.add_colorbar(cs, ax)
        ax.quiver(
            self.ws_mean.longitude,
            self.ws_mean.latitude,
            self.u_mean,
            self.v_mean,
            transform=ccrs.PlateCarree(),
        )
        ax.set_title("Mean Wind Speed and Direction")
        self.add_geographical_features(ax)

    def plot_shape_parameter(self, ax):
        """Plot the spatial distribution of the shape parameter k."""
        cs = ax.contourf(
            self.k.longitude,
            self.k.latitude,
            self.k,
            cmap="coolwarm",
            transform=ccrs.PlateCarree(),
        )
        self.add_colorbar(cs, ax)
        ax.set_title("Spatial Distribution of Shape Parameter k")
        self.add_geographical_features(ax)

    def plot_scale_parameter(self, ax):
        """Plot the spatial distribution of the scale parameter c."""
        cs = ax.contourf(
            self.c.longitude,
            self.c.latitude,
            self.c,
            cmap="coolwarm",
            transform=ccrs.PlateCarree(),
        )
        self.add_colorbar(cs, ax)
        ax.set_title("Spatial Distribution of Scale Parameter c")
        self.add_geographical_features(ax)
    
    def plot_test_result(self, ax):
        """Plot the spatial distribution of the test result."""
        
        results = self.adjusted_data.test_result.fillna(0).astype(float)
        
        # Define the levels and corresponding colors from the rainbow colormap
        levels = np.linspace(0, 1, 11)
        cmap = plt.get_cmap('rainbow')
        
        # Normalize the colormap to the range of levels
        norm = mcolors.BoundaryNorm(boundaries=levels, ncolors=cmap.N, clip=True)

        # Create the contour plot with the discrete color mapping
        cs = ax.contourf(
            results.longitude,
            results.latitude,
            results,
            levels=levels,
            cmap=cmap,
            norm=norm,
            extend='max',
            transform=ccrs.PlateCarree(),
        )

        # Create colorbar with labels
        cb = self.add_colorbar(cs, ax)
        ax.set_title("Spatial Distribution of Test Result")
        self.add_geographical_features(ax)

    def plot_best_fit_distribution(self, ax):
        """Plot the spatial distribution of the best fit distribution."""
        expected_dist_names = ['Weibull_Linear', 'Weibull', 'GPD', 'GEV']
        dist_colors = ['#7bdff2', '#60d394', '#ff9b85', '#ffd97d']

        # Only keep the distributions that are present in the data
        valid_dists = self.best_dist.where(self.best_dist.notnull(), drop=True)
        dist_names = [name for name in expected_dist_names if name in valid_dists.values]
        dist_map = {name: idx for idx, name in enumerate(dist_names)}
        
        # Replace None values with a placeholder to prevent errors
        filled_best_dist = self.best_dist.fillna('None')
        dist_values = xr.apply_ufunc(np.vectorize(lambda x: dist_map.get(x, -1)), filled_best_dist)
        
        cmap = ListedColormap([dist_colors[expected_dist_names.index(name)] for name in dist_names])
        norm = plt.Normalize(vmin=0, vmax=len(dist_names) - 1)
        
        cs = ax.contourf(
            dist_values.longitude,
            dist_values.latitude,
            dist_values,
            levels=np.arange(len(dist_names) + 1) - 0.5,
            cmap=cmap,
            norm=norm,
            transform=ccrs.PlateCarree(),
        )
        cb = self.add_colorbar(cs, ax, ticks=np.arange(len(dist_names)))
        cb.ax.set_yticklabels(dist_names)
        ax.set_title("Spatial Distribution of Best Fit Distribution")
        self.add_geographical_features(ax)

    def add_colorbar(self, cs, ax, ticks=None):
        """Add a smaller colorbar further away from the plot."""
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.5, axes_class=plt.Axes)
        cb = plt.colorbar(cs, cax=cax, orientation="vertical", ticks=ticks)
        return cb

    @staticmethod
    def add_geographical_features(ax):
        """Add geographical features to the plot."""
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS)
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.gridlines(draw_labels=True)

    def plot_all(self):
        """Plot all the visualizations in a multi-panel figure."""
        fig, axs = plt.subplots(2, 2, figsize=(18, 12), subplot_kw={"projection": ccrs.PlateCarree()})

        self.plot_mean_wind_speed_direction(axs[0, 0])
        self.plot_shape_parameter(axs[0, 1])
        self.plot_scale_parameter(axs[1, 0])
        if self.force_fit:
            self.plot_test_result(axs[1, 1])
        else:
            self.plot_best_fit_distribution(axs[1, 1])

        plt.tight_layout()
        
        return fig

if __name__ == "__main__":

    from RegionAdjustment import RegionAdjustment

    test_dataset = "../testdata/bacia_potiguar_wind_2022.nc"
    ds = xr.open_dataset(test_dataset)

    # # Create denegrated data
    # ds = ds.isel(time=slice(0, None, 4), latitude=slice(0, None, 4), longitude=slice(0, None, 4))

    # Calculate wind speeds
    u10, v10 = ds['u10'], ds['v10']
    u100, v100 = ds['u100'], ds['v100']

    # Sttandard adjustment and save for testing
    wind_adjust = RegionAdjustment(u10, v10, force_fit='Weibull')
    wind_adjust = wind_adjust.adjust_wind_speeds()

    # Data with automatic adjustment
    visualizer = WindSpeedVisualizer(wind_adjust)
    fig = visualizer.plot_all()
    plt.show()