# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    PointAdjustment.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: daniloceano <danilo.oceano@gmail.com>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/07/24 00:49:56 by daniloceano       #+#    #+#              #
#    Updated: 2025/03/31 14:36:27 by daniloceano      ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import numpy as np
import pandas as pd
import xarray as xr
import scipy.stats as stats
from scipy.stats import chisquare
from lmoments3 import distr
import matplotlib.pyplot as plt

class PointAdjustment:
    """
    A class to perform L-Moments based adjustments and fitting of statistical distributions 
    to wind speed data at specific grid points. This is particularly useful for analyzing
    wind speed distributions and adjusting them to better match theoretical distributions 
    using various fitting techniques such as Weibull, GEV, or GPD.
    """
    
    def __init__(self, data, force_fit=False, bins: str = "doane", make_plot=False, random_sampling=False, verbose=False):
        """
        Initializes the PointAdjustment class with data, distribution fitting options, 
        and binning method for histogram analysis.

        Args:
            data (array-like): 
                The input data for distribution fitting. 
                Accepts lists, NumPy arrays, Pandas DataFrames, or xarray DataArrays.

            force_fit (str, optional): 
                Specifies a distribution to force the fitting. If False, the best-fit distribution 
                will be selected automatically using goodness-of-fit tests.
                Options:
                    - 'Weibull': Fits a Weibull distribution.
                    - 'GEV': Fits a Generalized Extreme Value (GEV) distribution.
                    - 'GPD': Fits a Generalized Pareto Distribution (GPD).
                    - 'Weibull_Linear': Fits a Weibull distribution using log-linear regression.
                    - False (default): Automatically selects the best-fit distribution.

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

            make_plot (bool, optional): 
                Whether to generate visualizations for the fitted distributions. Default is False.

            random_sampling (bool, optional):
                If True, performs a random sampling of the input data before fitting the distribution. 
                Default is False.                

            verbose (bool, optional): 
                If True, prints detailed information about the fitting process. Default is False.

        Raises:
            ValueError: If an unsupported distribution name or binning method is provided.

        Example:
            >>> data = np.random.weibull(2, 1000)
            >>> lm_adjust = PointAdjustment(data, force_fit='Weibull', bins='sturges', make_plot=True)
        """
        self.data = self._process_input_data(data)
        self.force_fit = force_fit
        self.fitted_params = {}
        self.make_plot = make_plot
        self.verbose = verbose
        self.random_sampling = random_sampling
        self.bins = bins

        # Lista de métodos suportados
        options = ['sturges', 'freedman-diaconis', 'scott', 'rice', 'doane', 'auto']


        # Validação dos bins
        if not (isinstance(bins, int) or bins in options):
            raise ValueError("Number of bins must be an integer or one of the following: 'sturges', 'freedman-diaconis', 'rice', 'scott', 'doane', 'auto'")

    def _process_input_data(self, data):
        """
        Processes the input data based on its type and shape.
        
        Args:
            data: Input data which could be a list, numpy array, pandas DataFrame, or xarray DataArray.
        
        Returns:
            numpy.ndarray: A flattened array of the processed data.
        """
        if isinstance(data, list):
            processed_data = np.array(data).flatten()
        elif isinstance(data, np.ndarray):
            processed_data = data.flatten()
        elif isinstance(data, pd.DataFrame):
            processed_data = data.values.flatten()
        elif isinstance(data, xr.DataArray):
            processed_data = data.values.flatten()
        else:
            raise ValueError("Unsupported data type. Please provide a list, numpy array, pandas DataFrame, or xarray DataArray.")
        
        return processed_data

    def weibull_log_linear(self):
        """
        Calculates the Weibull distribution parameters (shape, location, scale)
        using the Log-Linear regression method.
        
        Parameters:
            data (array-like): The input data to fit the Weibull distribution to.
        
        Returns:
            tuple: A tuple containing the shape, location, and scale parameters of the 
            Weibull distribution.
        """
        sorted_data = np.sort(self.data)
        n = len(self.data)
        cdf = np.arange(1, n + 1) / (n + 1)  # Evita problemas no cálculo
        log_data = np.log(sorted_data)
        log_minus_log_cdf = np.log(-np.log(1 - cdf))

        # Ajuste linear
        slope, intercept = np.polyfit(log_data, log_minus_log_cdf, 1)
        shape = slope
        scale = np.exp(-intercept / slope)
        params = (shape, 0, scale)
        return params
    
    def get_num_bins(self, bins='sturges'):
        """
        Determines the number of bins for histogram plotting based on a chosen method.

        Args:
            bins (int or str, optional): 
                The binning method to use. Default is `"doane"`.
                Options:
                    - Integer (e.g., `30`): A fixed number of bins.
                    - 'sturges': Sturges' rule (log-based, best for normal distributions).
                    - 'freedman-diaconis': Uses Freedman-Diaconis rule (best for skewed distributions).
                    - 'rice': Uses Rice’s rule (scales with cube root of dataset size).
                    - 'scott': Uses Scott’s rule (minimizes IMSE for normal distributions).
                    - 'doane': Uses Doane's rule (default, extension of Sturges' rule that accounts for the skewness of the data distribution).

        Returns:
            int: The computed number of bins.

        Raises:
            ValueError: If an unsupported binning method is provided.

        Example:
            >>> lm_adjust = PointAdjustment(data, bins='freedman-diaconis')
            >>> num_bins = lm_adjust.get_num_bins('freedman-diaconis')
            >>> print(num_bins)
            25
        """
        N = len(self.data)
        if bins == 'sturges':
            num_bins = self.get_bin_number_sturges()
        elif bins == 'rice':
            return self.get_bin_number_rice()
        elif bins == 'scott':
            num_bins = self.get_bin_number_scott()
        elif bins == 'freedman-diaconis':
            num_bins = self.get_bin_number_freedman_diaconis()
        elif bins == 'doane':
            num_bins = self.get_bin_number_doane()
        else:
            num_bins = bins  # If a specific number of bins is provided

        return num_bins
    
    def get_bin_number_sturges(self):
        """
        Calculate the optimal number of bins using Sturges' rule.

        Sturges' rule is a simple heuristic for determining the number of bins in a histogram.
        It assumes that the data follows a normal distribution and is best suited for smaller datasets.
        """
        N = len(self.data)
        return int(1 + np.log2(N))
    
    def get_bin_number_rice(self):
        """
        Calculate the optimal number of bins using Rice's rule.

        Rice's rule suggests a bin count that scales with the cube root of the dataset size.
        It is a simple alternative to Sturges' rule and works well for larger datasets.
        """
        N = len(self.data)
        return int(2 * N**(1/3))

    def get_bin_number_freedman_diaconis(self):
        """
        Calculate the number of bins based on the Freedman-Diaconis rule.
        This rule uses the interquartile range (IQR) to calculate bin width and is robust
        for skewed distributions.
        """
        iqr = np.percentile(self.data, 75) - np.percentile(self.data, 25)
        bin_width = 2 * iqr / len(self.data)**(1/3)
        return max(1, int((max(self.data) - min(self.data)) / bin_width))

    def get_bin_number_scott(self):
        """
        Calculate the bin width based on Scott's rule.
        Scott's rule minimizes the integrated mean squared error for normal distributions,
        but can also work for large datasets.
        """
        bin_width = 3.5 * np.std(self.data) / len(self.data)**(1/3)
        return max(1, int((max(self.data) - min(self.data)) / bin_width))
    
    def get_bin_number_doane(self):
        """
        Calculate the optimal number of bins using Doane's formula.

        Doane's formula is an extension of Sturges' rule that accounts for the skewness 
        of the data distribution. This method is particularly useful when dealing with 
        non-normal data distributions, as it adjusts the bin count based on the sample skewness.
        """
        N = len(self.data)
        g1 = stats.skew(self.data)
        sigma_g1 = np.sqrt((6 * (N - 2)) / ((N + 1) * (N + 3)))
        return int(1 + np.log2(N) + np.log2(1 + abs(g1) / sigma_g1))
        
    def chi_square_test(self, dist_name):
        """
        Perform the Chi-square goodness-of-fit test for the specified distribution.

        Parameters:
        dist_name : str
            The name of the distribution to be tested (e.g., 'Weibull', 'GEV', 'GPD').
        """

        # Step 1: Retrieve the fitted parameters and precomputed cumulative_probs array
        shape_fit, loc_fit, scale_fit = self.fitted_params[dist_name]

        # Step 2: Compute observed frequencies
        observed_freq, bin_edges = np.histogram(self.data, bins=self.num_bins, density=True)

        # Setp 3: Get expected frequencies based on the cumulative probabilities
        if dist_name == 'Weibull':
            expected_freq = np.diff(stats.weibull_min.cdf(bin_edges, shape_fit, loc_fit, scale_fit)) * len(self.data)
        elif dist_name == 'GEV':
            expected_freq = np.diff(distr.gev.cdf(bin_edges, shape_fit, loc_fit, scale_fit)) * len(self.data)
        elif dist_name == 'GPD':
            expected_freq = np.diff(distr.gpa.cdf(bin_edges, shape_fit, loc_fit, scale_fit)) * len(self.data)
        elif dist_name == 'Weibull_Linear':
            expected_freq = np.diff(stats.weibull_min.cdf(bin_edges, shape_fit, loc_fit, scale_fit)) * len(self.data)
        else:
            raise ValueError(f"Unsupported distribution: {dist_name}")

        # Step 4: Normalize the expected frequencies to match the total number of data points
        expected_freq *= (observed_freq.sum() / expected_freq.sum())

        # Step 5: Chi-Square Test
        with np.errstate(divide='ignore', invalid='ignore'):  # Ignore numpy warnings
            chi_square_stat, p_value = chisquare(observed_freq, expected_freq)

        # Round the values to 2 decimal places
        chi_square_stat, p_value = float(np.round(chi_square_stat, 2)), float(np.round(p_value, 2))

        # If any of the values are NaN, set them to 0
        if np.isnan(chi_square_stat) or np.isnan(p_value):
            chi_square_stat, p_value = 0, 0

        return chi_square_stat, p_value

    def fit_and_evaluate(self, 
                         sample_sizes=[30, 50, 75, 100, 150, 200, 300], 
                         bin_sizes=[5, 7, 10, 15, 20],
                         p_threshold=0.05):
        """
        Fit multiple distributions to the wind speed data and evaluate each fit using Chi-square tests.

        Purpose:
            This method tests combinations of distributions, sample sizes, and histogram bin sizes to determine
            which configuration produces the highest average Chi-square p-value, indicating the best fit.

        Parameters:
            sample_sizes (list of int, optional):
                List of sample sizes to test through random sub-sampling (if random_sampling=True).
                Default: [30, 50, 75, 100, 150, 200, 300]
            
            bin_sizes (list of int, optional):
                List of bin numbers to test for each combination. Default: [5, 7, 10, 15, 20]
            
            p_threshold (float, optional):
                Threshold p-value to consider a test as 'accepted' when calculating acceptance rates. Default: 0.05.

        Returns:
            - best_params (tuple):
                Parameters (K, L, C) of the best-fit distribution.
            
            - best_dist_name (str):
                The name of the distribution that achieved the highest average p-value.
            
            - best_results_dict (dict):
                A dictionary containing the best results for each tested distribution. Example:
                    {
                        'Weibull': {
                            'Best Sample Size': 5000,
                            'Best Number of Bins': 10,
                            'Chi-square Statistic': 3.62,
                            'Chi-square p-value': 0.93,
                            'Acceptance Rate': 0.94,
                            'K (Shape)': 1.99,
                            'L (Location)': 0.0,
                            'C (Scale)': 7.95
                        },
                        ...
                    }

        Example Usage:
            >>> pa = PointAdjustment(data, bins='auto', random_sampling=True, make_plot=True)
            >>> best_params, best_dist, best_results = pa.fit_and_evaluate()
            >>> print(f"Best distribution: {best_dist}, Params: {best_params}")
        
        Notes:
            - The method also generates contour plots if make_plot=True and random_sampling=True, showing p-values as a function of sample size and bin number.
            - The selection of the best distribution is based on the maximum average p-value across all tested configurations.
            - The acceptance rate refers to the percentage of sub-sample tests that exceeded the p_threshold.
        """
        # If force_fit is False, test all distributions
        distributions = ['Weibull', 'GEV', 'GPD', 'Weibull_Linear'] if not self.force_fit else [self.force_fit]

        # If bins is set to 'auto', test distributions with different bin sizes
        if self.bins == "auto":
            bin_sizes = bin_sizes
        elif self.bins != "auto":
            bin_sizes = [self.get_num_bins(self.bins)]

        # If random_sampling is set to True, test distributions with different sample sizes
        if self.random_sampling:
            sample_sizes = sample_sizes
        else: 
            sample_sizes = [len(self.data)]

        # Convert data to DataFrame for easier handling
        df = pd.DataFrame({'wind_speeds': self.data})

        # # FOR TESTING
        # distributions = ['Weibull', 'Weibull_Linear']
        # sample_sizes = [int(len(df) / 2), int(len(df))]
        # bin_sizes = [10, 20]

        # Initialize variables
        chi_square_stats, p_values, k_values, loc_values, c_values = {}, {}, {}, {}, {}

        for dist_name in distributions:

            for sample_size in sample_sizes:
                for n_bins in bin_sizes:
                    df_copy = df.copy()

                    chi_square_stats[(dist_name, sample_size, n_bins)] = []
                    p_values[(dist_name, sample_size, n_bins)] = []
                    k_values[(dist_name, sample_size, n_bins)] = []
                    loc_values[(dist_name, sample_size, n_bins)] = []
                    c_values[(dist_name, sample_size, n_bins)] = []

                    while len(df_copy) >= sample_size:
                        # Generate random sample
                        sample = df_copy.sample(n=sample_size)
                        df_copy = df_copy.drop(sample.index)
                        
                        # Calculate observed frequencies
                        observed_freq, bin_edges = np.histogram(sample['wind_speeds'], bins=n_bins)

                        # Fit distribution
                        if dist_name == 'Weibull':
                            params = stats.weibull_min.fit(sample['wind_speeds'], floc=0)
                            cdf = stats.weibull_min.cdf(bin_edges, *params)
                            k, loc, c = [float(np.round(param, 2)) for param in params]
                        elif dist_name == 'GEV':
                            params = distr.gev.lmom_fit(sample['wind_speeds'])
                            cdf = distr.gev.cdf(bin_edges, params['c'], params['loc'], params['scale'])
                            k, loc, c = float(np.round(params['c'], 2)), float(np.round(params['loc'], 2)), float(np.round(params['scale'], 2))
                        elif dist_name == 'GPD':
                            params = distr.gpa.lmom_fit(sample['wind_speeds'])
                            cdf = distr.gpa.cdf(bin_edges, params['c'], params['loc'], params['scale'])
                            k, loc, c = float(np.round(params['c'], 2)), float(np.round(params['loc'], 2)), float(np.round(params['scale'], 2))
                        elif dist_name == 'Weibull_Linear':
                            params = self.weibull_log_linear()
                            cdf = stats.weibull_min.cdf(bin_edges, *params)
                            k, loc, c = [float(np.round(param, 2)) for param in params]
                        else:
                            raise ValueError(f"Distribuição não suportada: {dist_name}")

                        # Adjust expected frequencies to match observed frequencies
                        expected_freq = len(sample) * np.diff(cdf)
                        expected_freq *= (observed_freq.sum() / expected_freq.sum())

                        # Calculate Chi-square goodness-of-fit statistic and p-value for this sample
                        chi2, p_value = stats.chisquare(observed_freq, expected_freq)

                        chi_square_stats[(dist_name, sample_size, n_bins)].append(np.round(float(chi2), 2))
                        p_values[(dist_name, sample_size, n_bins)].append(np.round(float(p_value), 2))
                        k_values[(dist_name, sample_size, n_bins)].append(k)
                        loc_values[(dist_name, sample_size, n_bins)].append(loc)
                        c_values[(dist_name, sample_size, n_bins)].append(c)


        df_mean_results = []
        for dist_name in distributions:
            for sample_size in sample_sizes:
                for n_bins in bin_sizes:
                    acceptance_rate = sum(p > p_threshold for p in p_values[(dist_name, sample_size, n_bins)]) / len(p_values[(dist_name, sample_size, n_bins)])
                    df_mean_results.append({
                        'Distribution': dist_name,
                        'Sample Size': sample_size,
                        'Number of Bins': n_bins,
                        'Chi-square Statistic': np.mean(chi_square_stats[(dist_name, sample_size, n_bins)]),
                        'Chi-square p-value': np.mean(p_values[(dist_name, sample_size, n_bins)]),
                        'Acceptance Rate': acceptance_rate,
                        'K (Shape)': np.mean(k_values[(dist_name, sample_size, n_bins)]),
                        'L (Location)': np.mean(loc_values[(dist_name, sample_size, n_bins)]),
                        'C (Scale)': np.mean(c_values[(dist_name, sample_size, n_bins)])
                    })
        df_mean_results = pd.DataFrame(df_mean_results)

        # Select the results, i.e., rows where Chi-square p-value is the greatest for each distribution
        df_mean_results = df_mean_results.dropna(subset=["Chi-square p-value"])
        df_best_results = df_mean_results.loc[df_mean_results.groupby('Distribution')["Chi-square p-value"].idxmax()]

        best_results_dict = {}

        for _, row in df_best_results.iterrows():
            dist_name = row['Distribution']
            best_results_dict[dist_name] = {
                'Best Sample Size': int(row['Sample Size']),
                'Best Number of Bins': int(row['Number of Bins']),
                'Chi-square Statistic': float(row['Chi-square Statistic']),
                'Chi-square p-value': float(row['Chi-square p-value']),
                'Acceptance Rate': float(row['Acceptance Rate']),
                'K (Shape)': float(row['K (Shape)']),
                'L (Location)': float(row['L (Location)']),
                'C (Scale)': float(row['C (Scale)'])
            }

        # Get the best results for the best fit distribution
        best_dist_results = df_best_results.loc[df_best_results["Chi-square p-value"].idxmax()]
        best_dist_name = best_dist_results['Distribution']

        # Create a tuple with the best parameters
        best_params = (float(best_dist_results['K (Shape)']), float(best_dist_results['L (Location)']), float(best_dist_results['C (Scale)']))

        # Print the results for the best fit distribution and its parameters if verbose mode is enabled
        if self.verbose:
            print(f"Best fit: {best_dist_name} with Chi-square Statistic: {best_dist_results['Chi-square Statistic']} "
                  f"\nOptimal Sample Size: {best_dist_results['Sample Size']} and Optimal Number of Bins: {best_dist_results['Number of Bins']}"
                  f"\nK (Shape): {best_dist_results['K (Shape)']} L (Location): {best_dist_results['L (Location)']} C (Scale): {best_dist_results['C (Scale)']}")

        if self.make_plot:
            best_number_of_bins = int(best_dist_results['Number of Bins'])
            self.plot_results(dist_name, params, best_number_of_bins)

            # Get the unique distribution names
            distribuicoes = df_mean_results['Distribution'].unique()

            if self.random_sampling:
                fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 10))
                axes = axes.flatten()

                for i, dist_name in enumerate(distribuicoes):
                    ax = axes[i]
                    dist_data = df_mean_results[df_mean_results['Distribution'] == dist_name]
                    
                    # Cria malhas para o contourf
                    sample_sizes = sorted(dist_data['Sample Size'].unique())
                    bin_sizes = sorted(dist_data['Number of Bins'].unique())
                    X, Y = np.meshgrid(bin_sizes, sample_sizes)
                    
                    # Matriz dos p-valores
                    Z = np.zeros_like(X, dtype=float)
                    for row in dist_data.itertuples():
                        i_sample = sample_sizes.index(row._2)
                        i_bin = bin_sizes.index(row._3)
                        Z[i_sample, i_bin] = row._5  # _5 é o Chi-square p-value na posição da tupla
                    
                    cf = ax.contourf(X, Y, Z, levels=15, cmap='viridis')
                    ax.set_title(f'Distribution: {dist_name}')
                    ax.set_xlabel('Number of Bins')
                    ax.set_ylabel('Sample Size')
                    fig.colorbar(cf, ax=ax, label='Mean p-value')

                plt.tight_layout()
                plt.show()

                return best_params, best_dist_name, best_results_dict

            else:
                return best_params, best_dist_name, best_results_dict

        else:
            return best_params, best_dist_name, best_results_dict

    def plot_results(self, dist_name, params, best_number_of_bins):
        """
        Generate a multi-panel plot with various visualizations.
        
        Args:
            dist_name (str): The name of the best-fit distribution.
            params (tuple): Parameters of the best-fit distribution.
        """
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # Histogram of data and PDF
        axs[0, 0].hist(self.data, bins=best_number_of_bins, density=True, alpha=0.6, color='g', label='Data')

        if dist_name == 'Weibull':
            dist = stats.weibull_min(*params)
        elif dist_name == 'GEV':
            shape_param, loc_param, scale_param = params['c'], params['loc'], params['scale']
            dist = stats.genextreme(shape_param, loc=loc_param, scale=scale_param)
        elif dist_name == 'GPD':
            shape_param, loc_param, scale_param = params['c'], params['loc'], params['scale']
            dist = stats.genpareto(shape_param, loc=loc_param, scale=scale_param)
        elif dist_name == 'Weibull_Linear':
            k, loc_param, c = params
            dist = stats.weibull_min(k, loc_param, c)
        
        # Plotting the PDF
        x = np.linspace(min(self.data), max(self.data), 100)
        axs[0, 0].plot(x, dist.pdf(x), 'k-', lw=2, label=f'{dist_name} PDF')
        axs[0, 0].set_title('Histogram and PDF')

        # Empirical CDF and fitted CDF
        n = len(self.data)
        empirical_cdf = np.arange(1, n + 1) / n
        sorted_data = np.sort(self.data)
        axs[0, 1].plot(sorted_data, empirical_cdf, 'o-', label='Empirical CDF')
        axs[0, 1].plot(sorted_data, dist.cdf(sorted_data), 'r-', label=f'{dist_name} CDF')
        axs[0, 1].set_title('Empirical and Fitted CDF')
        axs[0, 1].legend()

        # Q-Q plot
        res = stats.probplot(self.data, dist=dist, plot=axs[1, 0])
        axs[1, 0].set_title('Q-Q Plot')

        # P-P plot
        axs[1, 1].plot(empirical_cdf, dist.cdf(sorted_data), 'o')
        axs[1, 1].plot([0, 1], [0, 1], 'r-', lw=2)
        axs[1, 1].set_title('P-P Plot')

        plt.tight_layout()
        plt.show()
        return fig

# Example usage
if __name__ == '__main__':
    test_data_type = 'Weibull'  # Change this to 'Weibull' or 'random' as needed

    if test_data_type == 'random':
        wind_speeds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5]
        frequencies = [1264, 5690, 9556, 13336, 13269, 8222, 5095, 1517, 646, 239, 59, 15, 2]

        data = np.repeat(wind_speeds, frequencies) 

        # Add some noise to the data to make it more realistic
        noise = np.abs(np.random.normal(0, 1, len(data)))
        TEST_DATA = data + noise

    elif test_data_type == 'Weibull':
        # Function to generate wind speed data using a Weibull distribution
        def generate_wind_speed_data(size, shape, scale):
            return stats.weibull_min.rvs(shape, scale=scale, size=size)

        # Generate a sample data set
        np.random.seed(42)  # For reproducibility
        TEST_DATA = generate_wind_speed_data(size=5000, shape=2, scale=8)  # Adjust shape and scale as needed

    # Test all distributions
    for dist in ['Weibull_Linear', 'Weibull', 'GEV', 'GPD']:
        lm_adjust = PointAdjustment(TEST_DATA, make_plot=True, force_fit=dist)
        best_params, best_dist_name, best_results = lm_adjust.fit_and_evaluate()

        for dist, result in best_results.items():
            print(f"{dist} results:")
            print(f"  Chi-square Statistic: {result['Chi-square Statistic']}")
            print(f"  Chi-square p-value: {result['Chi-square p-value']}")
            print()

    # Test the best-fit distribution
    lm_adjust = PointAdjustment(TEST_DATA, make_plot=True)
    best_params, best_dist_name, results = lm_adjust.fit_and_evaluate()

    print(f"Best-fit distribution: {best_dist_name}")

    # Test the best-fit distribution
    lm_adjust = PointAdjustment(TEST_DATA, make_plot=True, bins='auto', random_sampling=True)
    best_params, best_dist_name, results = lm_adjust.fit_and_evaluate()

    # Print the results
    for dist, result in results.items():
        print(f"{dist} results:")
        print(f"  Chi-square Statistic: {result['Chi-square Statistic']}")
        print(f"  Chi-square p-value: {result['Chi-square p-value']}")
        print()

    print(f"Best-fit distribution: {best_dist_name}")