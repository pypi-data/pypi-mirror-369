# Get the parent directory and add it to sys.path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import xarray as xr
import numpy as np
from src.PointAdjustment import PointAdjustment # type: ignore
from tqdm import tqdm
from joblib import Parallel, delayed

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

class RegionAdjustment:
    """
    A class to perform wind speed adjustment using L-Moments based fitting for a given region.

    Attributes:
        u (xarray.DataArray): Wind speed in the east direction.
        v (xarray.DataArray): Wind speed in the north direction.
        force_fit (bool): Flag to force a specific distribution, default is False.
        verbose (bool): Flag to enable verbose mode for detailed output.
        season (str): Optional season for filtering data ('DJF', 'MAM', 'JJA', 'SON').
        months (list): Optional list of months for filtering data.
        hours (list): Optional list of hours for filtering data.
    """
    
    def __init__(self, u, v, force_fit=False, alpha=0.05, season=None, months=None, hours=None,
                bins: str = "doane", random_sampling=False, verbose=False, n_jobs: int = -1, include_original_data=False):
        """
        Initializes the RegionAdjustment class with the data array and optional season, months, and hours.

        Args:
            u (xarray.DataArray): Wind speed in the east direction.
            v (xarray.DataArray): Wind speed in the north direction.
            force_fit (bool): Flag to force a specific distribution, default is False.
            alpha (float): The significance level for the test. Default is 0.05.
            season (str, optional): Season name ('DJF', 'MAM', 'JJA', 'SON'). Default is None.
            months (list, optional): List of months for filtering data. Default is None.
            hours (list, optional): List of hours for filtering data. Default is None.
            bins (str or int, optional): 
                Defines the number of bins for histogram calculations. 
                Default is `"sturges"`, which is suitable for normally distributed data.
                Options:
                    - Integer (e.g., `30`): A fixed number of bins.
                    - 'sturges': Sturges’ rule (best for normal distributions).
                    - 'freedman-diaconis': Freedman-Diaconis rule (best for skewed distributions).
                    - 'rice': Rice’s rule (best for large datasets).
                    - 'scott': Scott’s rule (minimizes IMSE for normal distributions).
                    - 'doane': Doane’s rule (default, extension of Sturges' rule that accounts for the skewness of the data distributio).
                    - 'auto': Automatically determine the number of bins based on the data.
            random_sampling (bool, optional):
                If True, performs a random sampling of the input data before fitting the distribution. 
                Default is False.   
            verbose (bool): Flag to enable verbose mode for detailed output. Default is False.
            n_jobs (int): Number of parallel jobs for processing. Default is -1 (use all processors).
            include_original_data (bool): Flag to include original wind data (`u` and `v`) in the output. Default is False.
        """
        self.u = u
        self.v = v
        self.data_array = np.sqrt(u**2 + v**2)
        self.force_fit = force_fit
        self.alpha = alpha
        self.season = season
        self.months = months
        self.hours = hours
        self.bins = bins
        self.random_sampling = random_sampling
        self.verbose = verbose
        self.n_jobs = n_jobs
        self.include_original_data = include_original_data
        self.lat_name, self.lon_name = self._detect_lat_lon_names()

        # Apply filtering
        self.data_array = self._filter_data(self.data_array)
        self.u = self._filter_data(self.u)
        self.v = self._filter_data(self.v)

    def _detect_lat_lon_names(self):
        """
        Detect the names of the latitude and longitude coordinates.
        
        Returns:
            tuple: Names of the latitude and longitude coordinates.
        """
        coord_names = list(self.data_array.coords)
        lat_names = ['lat', 'latitude', 'y']
        lon_names = ['lon', 'longitude', 'x']
        lat_name = next((name for name in coord_names if name.lower() in lat_names), None)
        lon_name = next((name for name in coord_names if name.lower() in lon_names), None)
        if lat_name is None or lon_name is None:
            raise ValueError("Latitude and longitude coordinate names not found.")
        return lat_name, lon_name

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

    def _filter_by_season(self, data, season):
        """
        Filter the dataset by season.

        Args:
            data (xarray.DataArray): The input data to filter.
            season (str): The season to filter by ('DJF', 'MAM', 'JJA', 'SON').

        Returns:
            xarray.DataArray: The filtered dataset for the given season.
        """
        if 'time' in data.dims and hasattr(data.time.dt, 'season'):
            # Use xarray's 'time.dt.season' to filter by the specified season
            return data.where(data.time.dt.season == season, drop=True)
        else:
            raise ValueError("Time dimension or season attribute not found in the data.")

    def _filter_by_months(self, data, months):
        """
        Filter the dataset by months.

        Args:
            data (xarray.DataArray): The input data to filter.
            months (list): List of months to filter by (e.g., [1, 2, 12] for DJF).

        Returns:
            xarray.DataArray: The filtered dataset for the given months.
        """
        return data.where(data['time.month'].isin(months), drop=True)

    def _filter_by_hours(self, data, hours):
        """
        Filter the dataset by hours of the day.

        Args:
            data (xarray.DataArray): The input data to filter.
            hours (list): List of hours to filter by (e.g., [0, 6, 12, 18]).

        Returns:
            xarray.DataArray: The filtered dataset for the given hours.
        """
        return data.where(data['time.hour'].isin(hours), drop=True)

    def _adjust_point(self, lat, lon):
        """
        Adjust wind speed at a single grid point.
        
        Args:
            lat (float): Latitude of the grid point.
            lon (float): Longitude of the grid point.
        
        Returns:
            tuple: k, c parameters, best-fit distribution name, and whether the point passed the p-value test.
        """
        # Wind speed at the current grid point
        ws_point = self.data_array.sel({self.lat_name: lat, self.lon_name: lon}).values
        non_numeric_indices = ~np.isfinite(ws_point)  # Identify non-numeric values

        if np.any(non_numeric_indices):
            print(f"Non-numeric values at lat={lat}, lon={lon}: {ws_point[non_numeric_indices]}")

        ws_point = ws_point[np.isfinite(ws_point)]  # Remove non-numeric values

        if len(ws_point) == 0:  # Handle case where all values are non-numeric
            return np.nan, np.nan, 'None', 'no'
        
        lm_adjust_point = PointAdjustment(ws_point, force_fit=self.force_fit, make_plot=False,
                                          bins=self.bins, random_sampling=self.random_sampling, verbose=self.verbose)
        best_params, best_dist_name, results = lm_adjust_point.fit_and_evaluate()
        
        # 
        p_value = float(results[best_dist_name]['Chi-square p-value'])
        sample_size = int(results[best_dist_name]['Best Sample Size'])
        num_bins = int(results[best_dist_name]['Best Number of Bins'])
        
        return best_params[0], best_params[2], best_dist_name, p_value, sample_size, num_bins

    def adjust_wind_speeds(self):
        """
        Adjust wind speeds at each grid point and returns a DataSet of k, c parameters, best-fit distribution names, and test results.
        """
        # Latitude and longitude coordinates
        latitudes = self.data_array[self.lat_name]
        longitudes = self.data_array[self.lon_name]

        # Initialize DataArrays to hold the k, c parameters, best-fit distribution names, and test results
        k_values = xr.DataArray(np.zeros((len(latitudes), len(longitudes))), 
                                coords=[latitudes, longitudes], 
                                dims=[self.lat_name, self.lon_name])

        c_values = xr.DataArray(np.zeros((len(latitudes), len(longitudes))), 
                                coords=[latitudes, longitudes], 
                                dims=[self.lat_name, self.lon_name])

        best_dist_names = xr.DataArray(np.empty((len(latitudes), len(longitudes)), dtype='U20'), 
                                       coords=[latitudes, longitudes], 
                                       dims=[self.lat_name, self.lon_name])

        test_results = xr.DataArray(np.empty((len(latitudes), len(longitudes)), dtype=float),
                                    coords=[latitudes, longitudes], 
                                    dims=[self.lat_name, self.lon_name])
        sample_sizes = xr.DataArray(np.empty((len(latitudes), len(longitudes)), dtype=int),
                                    coords=[latitudes, longitudes], 
                                    dims=[self.lat_name, self.lon_name])
        num_bins = xr.DataArray(np.empty((len(latitudes), len(longitudes)), dtype=int),
                                    coords=[latitudes, longitudes], 
                                    dims=[self.lat_name, self.lon_name])

        # Create a list of tasks
        tasks = [(lat, lon) for lat in latitudes for lon in longitudes]

        # Use Parallel processing with tqdm progress bar
        results = Parallel(n_jobs=self.n_jobs)(
            delayed(self._adjust_point)(lat, lon)
            for lat, lon in tqdm(tasks, desc="Adjusting wind speeds")
        )

        # Fill the DataArrays with the results
        idx = 0
        for lat in latitudes:
            for lon in longitudes:
                k_values.loc[lat, lon], c_values.loc[lat, lon], best_dist_names.loc[lat, lon], test_results.loc[lat, lon], sample_sizes.loc[lat, lon], num_bins.loc[lat, lon]  = results[idx]
                idx += 1

        # Create the xarray Dataset with metadata and string conversion
        fitted_data = xr.Dataset(
            {
                'k': k_values.assign_attrs({
                    'description': 'Weibull shape parameter (k)',
                    'units': 'dimensionless'
                }),
                'c': c_values.assign_attrs({
                    'description': 'Weibull scale parameter (c)',
                    'units': 'm/s'
                }),
                'best_dist': best_dist_names.assign_attrs({
                    'description': 'Best-fit distribution for each grid point',
                    'options': ['Weibull', 'GEV', 'GPD', 'Weibull_Linear']
                }),
                'test_result': test_results.assign_attrs({
                    'description': 'Chi-square test result p-value for each grid point',
                    'units': 'p-value'
                }),
                'sample_size': sample_sizes.assign_attrs({
                    'description': 'Best sample size determined from the random sampling method for each grid point',
                    'units': 'count'
                }),
                'num_bins': num_bins.assign_attrs({
                    'description': 'Best number of bins determined from the random sampling method for each grid point',
                    'units': 'count'
                })
            }
        )

        # Conditionally add original wind data
        if self.include_original_data:
            fitted_data['u'] = self.u
            fitted_data['v'] = self.v

        # Add global attributes to the dataset for metadata
        fitted_data.attrs = {
            'title': 'Wind Speed Distribution Fitting Results',
            'description': 'Fitting of wind speed data to various distributions using L-Moments and Chi-square test results',
            'force_fit': f'Applied distribution fit: {self.force_fit if self.force_fit else "Auto-detection"}',
            'alpha': f'Significance level used for the chi-square test: {self.alpha}',
            'season': f'Filtered season: {self.season}' if self.season else 'No seasonal filtering applied',
            'months': f'Filtered months: {self.months}' if self.months else 'No monthly filtering applied',
            'hours': f'Filtered hours: {self.hours}' if self.hours else 'No hourly filtering applied',
            'source_data': 'Processed from RegionAdjustment.py',
            'created_by': 'Danilo Couto de Souza',
            'creation_date': str(np.datetime64('now', 's'))  # Current timestamp
        }

        # Add metadata to each coordinate variable
        fitted_data[self.lat_name].attrs = {'long_name': 'Latitude', 'units': 'degrees_north'}
        fitted_data[self.lon_name].attrs = {'long_name': 'Longitude', 'units': 'degrees_east'}

        return fitted_data

# Example usage
if __name__ == '__main__':
    # Open dataset
    test_dataset = "../testdata/bacia_potiguar_wind_2022.nc"
    ds = xr.open_dataset(test_dataset)

    # Create denegrated data
    ds = ds.isel(time=slice(0, None, 4), latitude=slice(0, None, 4), longitude=slice(0, None, 4))

    # Calculate wind speeds
    u10, v10 = ds['u10'], ds['v10']
    u100, v100 = ds['u100'], ds['v100']

    # # Sttandard adjustment and save for testing
    # wind_adjust = RegionAdjustment(u10, v10)
    # wind_adjust = wind_adjust.adjust_wind_speeds()
    # wind_adjust.to_netcdf('../testdata/bacia_potiguar_wind_adjusted_2022.nc', mode='w')

    # # Perform adjustment using Weibull distribution
    # wind_adjust_10m_weibull_linear = RegionAdjustment(u10, v10, force_fit='Weibull_Linear')
    # fitted_data_10m_weibull_linear = wind_adjust_10m_weibull_linear.adjust_wind_speeds()
    # fitted_data_10m_weibull_linear.to_netcdf('../testdata/bacia_potiguar_wind_adjusted_2022_weibull_linear.nc', mode='w')

    # # Perform adjustment for DJF and 0Z
    # wind_adjust_10m_djf_0z = RegionAdjustment(u10, v10, season='DJF', hours=[0])
    # fitted_data_10m_djf_0z = wind_adjust_10m_djf_0z.adjust_wind_speeds()
    # fitted_data_10m_djf_0z.to_netcdf('../testdata/bacia_potiguar_wind_adjusted_2022_djf_0z.nc', mode='w')

    # # Perform adjustment for specific months (January, February, December)
    # wind_adjust_10m_jan_feb_dec = RegionAdjustment(u10, v10, months=[1, 2, 12])
    # fitted_data_10m_jan_feb_dec = wind_adjust_10m_jan_feb_dec.adjust_wind_speeds()
    # fitted_data_10m_jan_feb_dec.to_netcdf('../testdata/bacia_potiguar_wind_adjusted_2022_jan_feb_dec.nc', mode='w')

    # Perform adjustment using Weibull distribution and Scott's rule
    # wind_adjust_weibull_scott = RegionAdjustment(u10, v10, force_fit='Weibull', bins='scott')
    # fitted_weibull_scott = wind_adjust_weibull_scott.adjust_wind_speeds()
    # fitted_weibull_scott.to_netcdf('../testdata/bacia_potiguar_wind_adjusted_2022_weibull_scott.nc', mode='w')

    # Perform adjustment using Weibull distribution random sampling
    wind_adjust_weibull_random = RegionAdjustment(u10, v10, force_fit='Weibull', random_sampling=True)
    fitted_data_weibull_random = wind_adjust_weibull_random.adjust_wind_speeds()
    fitted_data_weibull_random.to_netcdf('../testdata/bacia_potiguar_wind_adjusted_2022_weibull_random_sampling.nc', mode='w')
