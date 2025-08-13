'''
Implementation of the ``MsRaster`` application for measurement set raster plotting and editing
'''

import time

from bokeh.models.formatters import NumeralTickFormatter
import holoviews as hv
import numpy as np
from pandas import to_datetime
import panel as pn

from vidavis.bokeh._palette import available_palettes
from vidavis.data.measurement_set.processing_set._ps_coords import set_index_coordinates
from vidavis.plot.ms_plot._time_ticks import get_time_formatter
from vidavis.plot.ms_plot._ms_plot import MsPlot
from vidavis.plot.ms_plot._ms_plot_constants import VIS_AXIS_OPTIONS, SPECTRUM_AXIS_OPTIONS, PS_SELECTION_OPTIONS, MS_SELECTION_OPTIONS, TIME_FORMAT
from vidavis.plot.ms_plot._raster_plot_gui import create_raster_gui
from vidavis.plot.ms_plot._raster_plot_inputs import check_inputs
from vidavis.plot.ms_plot._raster_plot import RasterPlot

class MsRaster(MsPlot):
    '''
    Plot MeasurementSet data as raster plot.

    Args:
        ms (str, None): path to MSv2 (.ms) or MSv4 (.zarr) file. Default None. Required when show_gui=False.
        log_level (str): logging threshold. Options include 'debug', 'info', 'warning', 'error', 'critical'. Default 'info'.
        log_to_file (bool): whether to write log messages to log file "msraster-<timestamp>.log". Default True.
        show_gui (bool): whether to launch the interactive GUI in a browser tab. Default False.

    Example:
        from vidavis.apps import MsRaster
        msr = MsRaster(ms='myvis.ms')
        msr.summary()
        msr.set_style_params(unflagged_cmap='Plasma', flagged_cmap='Greys', show_colorbar=True)
        msr.select_ps(intents='OBSERVE_TARGET#ON_SOURCE')
        msr.plot(x_axis='frequency', y_axis='time', vis_axis='amp', data_group='base')
        msr.show()
        msr.save() # saves as {ms name}_raster.png
    '''

    def __init__(self, ms=None, log_level="info", log_to_file=True, show_gui=False):
        super().__init__(ms, log_level, log_to_file, show_gui, "MsRaster")
        self._raster_plot = RasterPlot()
        self._plot_data = None

        # Calculations for color limits
        self._spw_stats = {}
        self._spw_color_limits = {}

        if show_gui:
            # For checking if plot inputs or cursor position changed and new plot or cursor location info is needed.
            self._last_plot_inputs = None
            self._last_style_inputs = None
            self._last_cursor = None

            # Return plot for gui DynamicMap:
            # Last plot when no new plot created (plot inputs same) or is iter Layout plot (opened in tab)
            self._last_gui_plot = None
            # Empty plot when ms not set or plot fails
            self._empty_plot = self._create_empty_plot()

            # Set default style and plot inputs to use when launching gui
            self.set_style_params()
            self.plot()
            self._launch_gui()

            # Set filename TextInput to input ms to trigger plot
            if 'ms' in self._ms_info and self._ms_info['ms']:
                self._set_filename([self._ms_info['ms']]) # function expects list

    def colormaps(self):
        ''' List available colormap (Bokeh palettes). '''
        return available_palettes()

    def set_style_params(self, unflagged_cmap='Viridis', flagged_cmap='Reds', show_colorbar=True, show_flagged_colorbar=True):
        '''
            Set styling parameters for the plot, such as colormaps and whether to show colorbar.
            Placeholder for future styling such as fonts.

            Args:
                unflagged_cmap (str): colormap to use for unflagged data.
                flagged_cmap (str): colormap to use for flagged data.
                show_colorbar (bool): Whether to show colorbar with plot.  Default True.
        '''
        cmaps = self.colormaps()
        if unflagged_cmap not in cmaps:
            raise ValueError(f"{unflagged_cmap} not in colormaps list: {cmaps}")
        if flagged_cmap not in cmaps:
            raise ValueError(f"{flagged_cmap} not in colormaps list: {cmaps}")
        self._raster_plot.set_style_params(unflagged_cmap, flagged_cmap, show_colorbar, show_flagged_colorbar)

    def select_ps(self, string_exact_match=True, query=None, **kwargs):
        '''
        Select a subset of ProcessingSet MeasurementSets using a Pandas query or summary column names and values.
            string_exact_match (bool): whether to require exact matches for string and string list columns (default True) or partial matches (False).
            query (str): a Pandas query string to apply additional filtering.
            **kwargs (dict): keyword arguments representing summary column names and values.
        See summary(data_group) and data_groups() for selection options. Use keyword 'data_group_name' for data group selection.
        Summary column names include 'name', 'intents', 'shape', 'polarization', 'scan_name', 'spw_name',
          'field_name', 'source_name', 'field_coords', 'start_frequency', 'end_frequency'.
        The selection is applied to the data within the MeasurementSets where applicable (polarization, scan_name, field_name)
          string_exact_match=True, else the entire MS is selected.
        Selections are cumulative until clear_selection() is called.
        Raises exception with message if selection fails.

        For explanation and examples, see:
        https://xradio.readthedocs.io/en/latest/measurement_set/schema_and_api/measurement_set_api.html#xradio.measurement_set.ProcessingSetXdt.query
        '''
        if self._data and self._data.is_valid():
            try:
                self._plot_inputs['selection'] |= kwargs
                if 'data_group_name' in kwargs:
                    self._plot_inputs['data_group'] = kwargs['data_group_name']
                self._data.select_ps(query=query, string_exact_match=string_exact_match, **kwargs)
            except KeyError as ke:
                error = "ProcessingSet selection yielded empty ProcessingSet."
                if not self._show_gui:
                    error += " Modify selection or run clear_selection() to select original ProcessingSet."
                raise KeyError(error) from ke
        else:
            raise RuntimeError("Cannot select ProcessingSet: input MS path is invalid or missing.")

    def select_ms(self, indexers=None, method=None, tolerance=None, drop=False, **indexers_kwargs):
        '''
        Select MeasurementSet dimensions or data_group.
          Values may be a single value, a list, or a slice.
          Data group may be selected with "data_group_name"; see data_groups() for options.
          See get_dimension_values() for selection keywords and values.
            Dimensions may be selected with 'time', 'baseline' (visibilities), 'antenna_name' (spectrum),
              'antenna1', 'antenna2', 'frequency', and 'polarization'.
            Time selection must be in string format 'dd-Mon-YYYY HH:MM:SS' as shown in get_dimension_values('time').
        Selections are cumulative until clear_selection() is called.
        Raises exception with message if selection fails.

        For explanation of parameters and examples, see:
        https://xradio.readthedocs.io/en/latest/measurement_set/schema_and_api/measurement_set_api.html#xradio.measurement_set.MeasurementSetXdt.sel
        '''
        if self._data and self._data.is_valid():
            try:
                self._plot_inputs['selection'] |= indexers_kwargs
                self._data.select_ms(indexers=indexers, method=method, tolerance=tolerance, drop=drop, **indexers_kwargs)
                if 'data_group_name' in indexers_kwargs:
                    self._plot_inputs['data_group'] |= indexers_kwargs['data_group_name']
            except KeyError as ke:
                error = str(ke).strip("\'")
                if not self._show_gui:
                    error += " Modify selection or run clear_selection() to select original ProcessingSet."
                raise KeyError(error) from ke
        else:
            raise RuntimeError("Cannot select MeasurementSet: input MS path is invalid or missing.")

# pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals, unused-argument
    def plot(self, x_axis='baseline', y_axis='time', vis_axis='amp', aggregator=None, agg_axis=None,
             iter_axis=None, iter_range=None, subplots=None, color_mode=None, color_range=None, title=None, clear_plots=True):
        '''
        Create a raster plot of vis_axis data.
        Plot axes include data dimensions (time, baseline/antenna, frequency, polarization).
        The first spectral window (by id) and dimensions not set as plot axes (first value) will be automatically selected if no user selection has been made, unless aggregated.

        Args:
            x_axis (str): Plot x-axis. Default 'baseline' ('antenna_name' for spectrum data).
            y_axis (str): Plot y-axis. Default 'time'.
            vis_axis (str): Complex visibility component to plot (amp, phase, real, imag). Default 'amp'.
            aggregator (None, str): reduction for rasterization. Default None.
                Options include 'max', 'mean', 'min', 'std', 'sum', 'var'.
            agg_axis (None, str, list): which dimension to apply aggregator across. Default None.
                Options include one or more dimensions.
                If agg_axis is None and aggregator is set, aggregates over all non-axis dimensions.
                If one agg_axis is selected, the non-agg dimension will be selected.
            iter_axis (None, str): dimension over which to iterate values (using iter_range).
            iter_range (None, tuple): (start, end) inclusive index values for iteration plots.
                Default (0, 0) (first iteration only). Use (0, -1) for all iterations.
                If subplots is a grid, the range is limited by the grid size.
                If subplots is a single plot, all iteration plots in the range can be saved using export_range in save().
            subplots (None, tuple): set a grid of (rows, columns).  None = (1, 1) for single plot.
                Use with iter_axis and iter_range, or clear_plots=False.
                If used in multiple calls, the last subplots tuple will be used to determine grid to show or save.
            color_mode (None, str): Whether to limit range of colorbar.  Default None (no limit).
                Options include None (use data limits), 'auto' (calculate limits for amplitude), and 'manual' (use range in color_range).
                'auto' is equivalent to None if vis_axis is not 'amp'.
                When subplots is set, the 'auto' or 'manual' range will be used for all plots.
            color_range (None, tuple): (min, max) of colorbar to use if color_mode is 'manual'.
            title (None, str): Plot title, default None (no title)
                Set title='ms' to generate title from ms name and iter_axis value, if any.
            clear_plots (bool): whether to clear list of plots. Default True.

        If plot is successful, use show() or save() to view/save the plot.
        '''
        inputs = locals() # collect arguments into dict (not unused as pylint complains!)
        if self._plot_inputs['selection']:
            self._logger.info("Create raster plot with selection: %s", self._plot_inputs['selection'])

        start = time.time()

        # Clear for new plot
        self._reset_plot(clear_plots)

        # Get data dimensions if valid MS is set to check input axes
        if 'data_dims' in self._ms_info:
            inputs['data_dims'] = self._ms_info['data_dims'] if 'data_dims' in self._ms_info else None

        # Validate input arguments then set
        check_inputs(inputs)
        self._set_plot_inputs(inputs)

        if not self._show_gui:
            # Cannot plot if no MS
            if not self._data or not self._data.is_valid():
                raise RuntimeError("Cannot plot MS: input MS path is invalid or missing.")

            # Create raster plot and add to plot list
            try:
                if self._plot_inputs['iter_axis']:
                    self._do_iter_plot(self._plot_inputs)
                else:
                    plot = self._do_plot(self._plot_inputs)
                    self._plots.append(plot)
            except RuntimeError as e:
                error = f"Plot failed: {str(e)}"
                super()._notify(error, "error", 0)

            self._logger.debug("Plot elapsed time: %.2fs.", time.time() - start)
# pylint: enable=too-many-arguments, too-many-positional-arguments, too-many-locals, unused-argument

    def save(self, filename='', fmt='auto', width=900, height=600):
        '''
        Save plot to file.

        Args:
            filename (str): Name of file to save. Default '': the plot will be saved as {ms}_raster.{ext}.
                If fmt is not set for extension, plot will be saved as .png.
            fmt (str): Format of file to save ('png', 'svg', or 'html').
                Default 'auto': inferred from filename extension.
            width (int): width of exported plot in pixels.
            height (int): height of exported plot in pixels.

        If subplots defines a grid layout, width and height describe the size of each plot in the layout.
            The layout plot size will be (width * columns, height * rows) pixels.

        If iteration plots were created:
            If subplots is a grid, the layout plot will be saved to a single file.
            If subplots is a single plot, iteration plots will be saved individually,
                with a plot index appended to the filename: {filename}_{index}.{ext}.
        '''
        if not filename:
            filename = f"{self._ms_info['basename']}_raster.png"
        super().save(filename, fmt, width, height)

    def _set_plot_inputs(self, plot_inputs):
        ''' Set inputs from latest plot() call '''
        for key, val in plot_inputs.items():
            self._plot_inputs[key] = val

    def _do_plot(self, plot_inputs):
        ''' Create plot using plot inputs '''
        if not self._plot_init:
            self._init_plot(plot_inputs)

        # Select vis_axis data to plot and update selection; returns xarray Dataset
        raster_data = self._data.get_raster_data(plot_inputs)
        self._plot_data = raster_data

        # Add params needed for plot: auto color range and ms name
        self._set_auto_color_range(plot_inputs) # set calculated limits if auto mode
        ms_name = self._ms_info['basename'] # for title
        self._raster_plot.set_plot_params(raster_data, plot_inputs, ms_name)

        # Show plot inputs in log
        super()._set_plot_params(plot_inputs | self._raster_plot.get_plot_params()['style'])
        self._logger.info("MsRaster plot parameters: %s", ", ".join(self._plot_params))

        # Make plot. Add data min/max if GUI is shown to update color limits range.
        return self._raster_plot.raster_plot(raster_data, self._logger, self._show_gui)

    def _do_iter_plot(self, plot_inputs):
        ''' Create one plot per iteration value in iter_range which fits into subplots '''
        # Default (0, 0) (first iteration only). Use (0, -1) for all iterations.
        # If subplots is a grid, end iteration index is limited by the grid size.
        # If subplots is a single plot, all iteration plots in the range can be saved using export_range in save().
        iter_axis = plot_inputs['iter_axis']
        iter_range = plot_inputs['iter_range']
        subplots = plot_inputs['subplots']

        iter_range = (0, 0) if iter_range is None else iter_range
        start_idx, end_idx = iter_range

        # Init plot before getting iter values
        self._init_plot(plot_inputs)

        iter_values = self._data.get_dimension_values(iter_axis)
        n_iter = len(iter_values)

        if start_idx >= n_iter:
            raise IndexError(f"iter_range start {start_idx} is greater than number of iterations {n_iter}")
        end_idx = n_iter if (end_idx == -1 or end_idx >= n_iter) else end_idx + 1
        num_iter_plots = end_idx - start_idx

        # Plot the minimum of iter range or subplots number of plots
        num_subplots = np.prod(subplots) if subplots else 1
        num_iter_plots = min(num_iter_plots, num_subplots) if num_subplots > 1 else num_iter_plots
        end_idx = start_idx + num_iter_plots

        # Set each iter value in ms_selection
        if 'ms_selection' not in plot_inputs:
            plot_inputs['ms_selection'] = {}

        for i in range(start_idx, end_idx):
            # Select iteration value and make plot
            value = iter_values[i]
            self._logger.info("Plot %s iteration index %s value %s", iter_axis, i, value)
            plot_inputs['selection'][iter_axis] = value
            try:
                plot = self._do_plot(plot_inputs)
                self._plots.append(plot)
            except RuntimeError as e:
                self._logger.info("Iteration plot for value %s failed: %s", str(value), str(e))
                continue

    def _init_plot(self, plot_inputs):
        ''' Apply automatic selection '''
        # Remove previous auto selections
        for key in ['dim_selection', 'auto_spw']:
            try:
                del self._plot_inputs[key]
            except KeyError:
                pass

        # Automatically select data group and spw name if not user-selected
        auto_selection = {}
        if 'data_group' not in plot_inputs:
            auto_selection['data_group_name'] = 'base'
            plot_inputs['data_group'] = 'base'
        if 'selection' not in plot_inputs or 'spw_name' not in plot_inputs['selection']:
            first_spw = self._data.get_first_spw(plot_inputs['data_group'])
            auto_selection['spw_name'] = first_spw
            plot_inputs['auto_spw'] = first_spw # do not add to user selection

        if auto_selection:
            # Do selection and save to plot inputs
            self._logger.info("Automatic selection of data group and/or spw: %s", auto_selection)
            self._data.select_ps(query=None, string_exact_match=True, **auto_selection)

        # Print data info for spw selection
        self._logger.info("Plotting %s msv4 datasets.", self._data.get_num_ms())
        self._logger.info("Maximum dimensions for selected spw: %s", self._data.get_max_data_dims())
        self._plot_init = True

    def _set_auto_color_range(self, plot_inputs):
        ''' Calculate stats for color limits for non-gui amplitude plots. '''
        color_mode = plot_inputs['color_mode']
        color_limits = None

        if color_mode == 'auto':
            if plot_inputs['vis_axis']=='amp' and not plot_inputs['aggregator']:
                # For amplitude, limit colorbar range using stored per-spw ms stats
                spw_name = self._plot_inputs['selection']['spw_name'] if ('selection' in plot_inputs and 'spw_name' in plot_inputs['selection']) else self._plot_inputs['auto_spw']
                if spw_name in self._spw_color_limits:
                    color_limits = self._spw_color_limits[spw_name]
                else:
                    # Select spw name and data group only, no dimensions
                    data_group = self._plot_inputs['data_group']
                    spw_data_selection = {'spw_name': spw_name, 'data_group_name': data_group}
                    color_limits = self._calc_amp_color_limits(spw_data_selection)
                    self._spw_color_limits[spw_name] = color_limits
        plot_inputs['auto_color_range'] = color_limits

        if color_limits:
            self._logger.info("Setting amplitude color range: (%.4f, %.4f).", color_limits[0], color_limits[1])
        elif color_mode is None:
            self._logger.info("Autoscale color range")
        else:
            self._logger.info("Using manual color range: %s", plot_inputs['color_range'])

    def _calc_amp_color_limits(self, selection):
        # Calculate colorbar limits from amplitude stats for unflagged data in selected spw
        self._logger.info("Calculating stats for colorbar limits.")
        start = time.time()

        ms_stats = self._data.get_vis_stats(selection, 'amp')
        self._spw_stats['spw_name'] = ms_stats
        if not ms_stats:
            return None # autoscale

        min_val, max_val, mean, std = ms_stats

        data_min = min(0.0, min_val)
        clip_min = max(data_min, mean - (3.0 * std))
        data_max = max(0.0, max_val)
        clip_max = min(data_max, mean + (3.0 * std))

        if clip_min == 0.0 and clip_max == 0.0:
            color_limits = None # flagged data only
        else:
            color_limits = (clip_min, clip_max)
        self._logger.debug("Stats elapsed time: %.2fs.", time.time() - start)
        return color_limits

    def _reset_plot(self, clear_plots=True):
        ''' Reset any plot settings for a new plot '''
        # Clear plot list
        if clear_plots:
            super().clear_plots()

        # Clear params set for last plot
        self._raster_plot.reset_plot_params()

        # Unitialize plot to redo auto selections if needed
        self._plot_init = False

    ### -----------------------------------------------------------------------
    ### Interactive GUI
    ### -----------------------------------------------------------------------
    def _launch_gui(self):
        ''' Use Holoviz Panel to create a dashboard for plot inputs. '''
        callbacks = {
            'filename': self._set_filename,
            'style': self._set_style_params,
            'color': self._set_color_range,
            'axes': self._set_axes,
            'select_ps': self._set_ps_selection,
            'select_ms': self._set_ms_selection,
            'aggregation': self._set_aggregation,
            'iter_values': self._set_iter_values,
            'iteration': self._set_iteration,
            'title': self._set_title,
            'plot_updating': self._update_plot_spinner,
            'update_plot': self._update_plot,
        }
        data_dims = self._ms_info['data_dims'] if 'data_dims' in self._ms_info else None
        x_axis = self._plot_inputs['x_axis']
        y_axis = self._plot_inputs['y_axis']
        self._gui_layout = create_raster_gui(callbacks, data_dims, x_axis, y_axis)
        # Show gui
        self._gui_layout.show(title=self._app_name, threaded=True)

    ###
    ### Main callback to create plot if inputs changed
    ###
    def _update_plot(self, ms, do_plot, x, y):
        ''' Create plot with inputs from GUI, or update cursor (x, y) information.
            Must return plot, even if empty plot or same plot as before, for DynamicMap.
        '''
        if self._toast:
            self._toast.destroy()

        self._get_selector("selectors").active = []
        if not ms:
            # Launched GUI with no MS
            return self._empty_plot

        # If not first plot, user has to click Plot button (do_plot=True) to update plot.
        # Respond to pointer callback only.
        first_plot = not self._last_gui_plot
        if not do_plot and not first_plot:
            if not self._last_cursor or (self._last_cursor[0] != x or self._last_cursor[1] != y):
                # Callback is for new cursor location
                self._update_cursor_location(x, y)
                self._last_cursor = (x, y)
            # Not ready to update plot yet, return last plot.
            return self._last_gui_plot

        # Callback is for initial plot for input ms, or user clicked Plot button
        if (self._set_ms(ms) or first_plot) and self._data and self._data.is_valid():
            # New MS set and is valid
            self._update_gui_axis_options()

        # Add ms path to detect change and make new plot
        self._plot_inputs['ms'] = ms

        # Do new plot or resend last plot
        self._reset_plot()
        self.clear_selection()
        gui_plot = None

        style_inputs = self._raster_plot.get_plot_params()['style']
        if self._inputs_changed(style_inputs):
            # First plot or changed plot
            try:
                # Check inputs from GUI then plot
                self._plot_inputs['data_dims'] = self._ms_info['data_dims']
                check_inputs(self._plot_inputs)
                if 'ps_selection' in self._plot_inputs or 'ms_selection' in self._plot_inputs:
                    self._do_gui_selection()
                gui_plot = self._do_gui_plot()
            except (ValueError, TypeError, KeyError, RuntimeError) as e:
                # Clear plot, inputs invalid
                self._notify(str(e), 'error', 0)
                gui_plot = self._empty_plot
        else:
            # Subparam values changed but not applied to plot
            gui_plot = self._last_gui_plot

        # Update plot inputs for gui
        self._set_plot_params(self._plot_inputs | style_inputs)

        # Save inputs to see if changed
        self._last_plot_inputs = self._plot_inputs.copy()
        self._last_style_inputs = style_inputs.copy()
        self._last_plot_inputs['ps_selection'] = self._plot_inputs['ps_selection'].copy()
        self._last_plot_inputs['ms_selection'] = self._plot_inputs['ms_selection'].copy()
        if first_plot and not do_plot:
            self._plot_inputs['ps_selection'].clear()
            self._plot_inputs['ms_selection'].clear()

        # Save plot if no new plot
        self._last_gui_plot = gui_plot

        # Add plot inputs, change plot button to outline, and stop spinner
        self._update_plot_inputs()
        self._update_plot_status(False)
        self._update_plot_spinner(False)

        return gui_plot

    def _inputs_changed(self, style_inputs):
        ''' Check if inputs changed and need new plot '''
        if not self._last_plot_inputs:
            return True

        for key, val in self._plot_inputs.items():
            if not self._values_equal(val, self._last_plot_inputs[key]):
                return True

        for key, val in style_inputs.items():
            if not self._values_equal(val, self._last_style_inputs[key]):
                return True
        return False

    def _values_equal(self, val1, val2):
        ''' Test if values are set and equal, or not set (cannot compare value with None) '''
        if val1 is not None and val2 is not None: # both set
            return val1 == val2
        if val1 is None and val2 is None: # both None
            return True
        return False # one set and other is None

    def _do_gui_selection(self):
        ''' Apply selections selected in GUI '''
        if self._plot_inputs['ps_selection']:
            self.select_ps(**self._plot_inputs['ps_selection'])
        if self._plot_inputs['ms_selection']:
            self.select_ms(**self._plot_inputs['ms_selection'])

    ###
    ### Create plot for DynamicMap
    ###
    def _do_gui_plot(self):
        ''' Create plot based on gui plot inputs '''
        if self._data and self._data.is_valid():
            try:
                if self._plot_inputs['iter_axis']:
                    # Make iter plot (possibly with subplots layout)
                    self._do_iter_plot(self._plot_inputs)
                    subplots = self._plot_inputs['subplots']
                    layout_plot, is_layout = super()._layout_plots(subplots)

                    if is_layout:
                        # Cannot show Layout in DynamicMap, show in new tab
                        super().show()
                        self._logger.info("Plot update complete")
                        return self._last_gui_plot
                    # Overlay raster plot for DynamicMap
                    self._logger.info("Plot update complete")
                    return layout_plot

                # Make single Overlay raster plot for DynamicMap
                plot = self._do_plot(self._plot_inputs)
                plot_params = self._raster_plot.get_plot_params()

                # Update color limits in gui with data range
                self._update_color_range(plot_params)

                # Update colorbar labels and limits
                plot.QuadMesh.I = self._set_plot_colorbar(plot.QuadMesh.I, plot_params, "flagged")
                plot.QuadMesh.II = self._set_plot_colorbar(plot.QuadMesh.II, plot_params, "unflagged")

                self._logger.info("Plot update complete")
                return plot.opts(
                    hv.opts.QuadMesh(tools=['hover'])
                )
            except RuntimeError as e:
                error = f"Plot failed: {str(e)}"
                super()._notify(error, "error", 0)

        # Make single Overlay raster plot for DynamicMap
        return self._empty_plot

    def _create_empty_plot(self):
        ''' Create empty Overlay plot for DynamicMap with colormap params and hover enabled '''
        plot_params = self._raster_plot.get_plot_params()
        plot = hv.Overlay(
            hv.QuadMesh([]).opts(
                colorbar=plot_params['style']['show_flagged_colorbar'],
                cmap=plot_params['style']['flagged_cmap'],
                responsive=True,
            ) * hv.QuadMesh([]).opts(
                colorbar=plot_params['style']['show_colorbar'],
                colorbar_position='left',
                cmap=plot_params['style']['unflagged_cmap'],
                responsive=True,
            )
        )
        return plot.opts(
            hv.opts.QuadMesh(tools=['hover'])
        )

    def _set_plot_colorbar(self, plot, plot_params, plot_type):
        ''' Update plot colorbar labels and limits
                plot_type is "unflagged" or "flagged"
        '''
        # Update colorbar labels if shown, else hide
        colorbar_key = plot_type + '_colorbar'
        if plot_params['plot'][colorbar_key]:
            c_label = plot_params['plot']['axis_labels']['c']['label']
            cbar_title = "Flagged " + c_label if plot_type == "flagged" else c_label

            plot = plot.opts(
                colorbar=True,
                backend_opts={
                    "colorbar.title": cbar_title,
                }
            )
        else:
            plot = plot.opts(
                colorbar=False,
            )

        # Update plot color limits
        color_limits = plot_params['plot']['color_limits']
        if color_limits:
            plot = plot.opts(
                clim=color_limits,
            )

        return plot

    def _update_color_range(self, plot_params):
        ''' Set the start/end range on the colorbar to min/max of plot data '''
        if self._gui_layout and 'data' in plot_params and 'data_range' in plot_params['data']:
            # Update range slider start and end to data min and max
            data_range = plot_params['data']['data_range']
            style_selectors = self._get_selector('style')
            range_slider = style_selectors[3][1]
            range_slider.start = data_range[0]
            range_slider.end = data_range[1]

    ###
    ### Update widget options based on MS
    ###
    def _get_selector(self, name):
        ''' Return selector group for name, for setting options '''
        selectors = self._gui_layout[2][1]
        selectors_index = {'file': 0, 'style': 1, 'sel': 2, 'axes': 3, 'agg': 4, 'iter': 5, 'title': 6}
        if name == "selectors":
            return selectors
        return selectors[selectors_index[name]]

    def _update_gui_axis_options(self):
        ''' Set gui options from ms data '''
        if 'data_dims' in self._ms_info:
            data_dims = self._ms_info['data_dims']
            axis_selectors = self._get_selector('axes')

            # Update options for x_axis selector
            x_axis_selector = axis_selectors.objects[0][0]
            x_axis_value = x_axis_selector.value
            x_axis_selector.options = data_dims
            if x_axis_value in data_dims:
                x_axis_selector.value = x_axis_value
            else:
                x_axis_selector.value = data_dims[1]

            # Update options for y_axis selector
            y_axis_selector = axis_selectors.objects[0][1]
            y_axis_value = y_axis_selector.value
            y_axis_selector.options = data_dims
            if y_axis_value in data_dims:
                y_axis_selector.value = y_axis_value
            else:
                y_axis_selector.value = data_dims[0]

            # Update options for vis_axis selector
            vis_axis_selector = axis_selectors.objects[2]
            vis_axis_value = vis_axis_selector.value
            if self._data.get_correlated_data('base') == 'SPECTRUM':
                vis_axis_selector.options = SPECTRUM_AXIS_OPTIONS
            else:
                vis_axis_selector.options = VIS_AXIS_OPTIONS
            if vis_axis_value in vis_axis_selector.options:
                vis_axis_selector.value = vis_axis_value
            else:
                vis_axis_selector.value = VIS_AXIS_OPTIONS[0]

            # Update options for selection selector
            selection_selectors = self._get_selector('sel')
            self._update_ps_selection_options(selection_selectors[0][0])
            self._update_ms_selection_options(selection_selectors[0][1])

            # Update options for agg axes selector
            agg_selectors = self._get_selector('agg')
            agg_selectors[1].options = data_dims

            # Update options for iteration axis selector
            iter_selectors = self._get_selector('iter')
            iter_axis_selector = iter_selectors[0][0]
            iter_axis_selector.options = ['None']
            iter_axis_selector.options.extend(data_dims)

    def _update_ps_selection_options(self, ps_selectors):
        ''' Set ProcessingSet gui options from ms summary '''
        if self._data and self._data.is_valid():
            summary = self._data.get_summary()
            if summary is None:
                return

            for selector in ps_selectors:
                if selector.name in PS_SELECTION_OPTIONS:
                    options = []
                    values = summary[PS_SELECTION_OPTIONS[selector.name]].values
                    for value in values:
                        if isinstance(value, list):
                            options.extend(value)
                        else:
                            options.append(value)
                    selector.options = sorted(list(set(options)))

    def _update_ms_selection_options(self, ms_selectors):
        ''' Set MeasurementSet gui options from ms data '''
        if self._data and self._data.is_valid():
            for selector in ms_selectors:
                selection_key = MS_SELECTION_OPTIONS[selector.name] if selector.name in MS_SELECTION_OPTIONS else None
                if selection_key:
                    if selection_key == 'data_group':
                        selector.options = list(super().data_groups())
                    else:
                        selector.options = super().get_dimension_values(selection_key)

    ###
    ### Callbacks for widgets which update other widgets
    ###
    def _set_filename(self, filename):
        ''' Set filename in text box from file selector value (list) '''
        if filename and self._gui_layout:
            file_selectors = self._get_selector('file')

            # Collapse FileSelector card
            file_selectors[1].collapsed = True

            # Change plot button color to indicate change unless ms path not set previously
            filename_input = file_selectors[0][0]
            if filename_input.value:
                self._update_plot_status(True)

            # Set filename from last file in file selector (triggers _update_plot())
            #filename_input.width = len(filename[-1])
            filename_input.value = filename[-1]

    def _set_iter_values(self, iter_axis):
        ''' Set up player with values when iter_axis is selected '''
        iter_axis = None if iter_axis == 'None' else iter_axis
        if iter_axis and self._gui_layout:
            iter_values = self._data.get_dimension_values(iter_axis)
            if iter_values:

                iter_selectors = self._get_selector('iter')

                # Update value selector with values and select first value
                iter_value_player = iter_selectors[1][0]
                if iter_axis == 'time':
                    if isinstance(iter_values[0], float):
                        iter_values = self._get_datetime_values(iter_values)
                    iter_value_player.format = get_time_formatter()
                elif iter_axis == 'frequency':
                    iter_value_player.format = NumeralTickFormatter(format='0,0.0000000')

                iter_value_player.options = iter_values
                iter_value_player.value = iter_values[0]
                iter_value_player.show_value = True

                # Update range inputs end values and select first
                iter_range_inputs = iter_selectors[1][1]
                last_iter_index = len(iter_values) - 1
                # range start
                iter_range_inputs[0][0].end = last_iter_index
                iter_range_inputs[0][0].value = 0
                # range end
                iter_range_inputs[0][1].end = last_iter_index
                iter_range_inputs[0][1].value = 0

    def _get_datetime_values(self, float_times):
        ''' Return list of float time values as list of datetime values for gui options '''
        time_attrs = self._data.get_dimension_attrs('time')
        datetime_values = []
        try:
            datetime_values = to_datetime(float_times, unit=time_attrs['units'], origin=time_attrs['format'])
        except TypeError:
            datetime_values = to_datetime(float_times, unit=time_attrs['units'][0], origin=time_attrs['format'])
        return list(datetime_values)

    def _update_plot_spinner(self, plot_clicked):
        ''' Callback to start spinner when Plot button clicked. '''
        if self._gui_layout:
            # Start spinner
            spinner = self._gui_layout[2][2][1]
            spinner.value = plot_clicked

    def _update_plot_status(self, inputs_changed):
        ''' Change button color when inputs change. '''
        if self._gui_layout:
            # Set button color
            button = self._gui_layout[2][2][0]
            button.button_style = 'solid' if inputs_changed else 'outline'

    def _update_plot_inputs(self):
        ''' Show inputs for raster plot in GUI '''
        if self._plot_params:
            inputs_column = self._gui_layout[0][1]
            inputs_column.clear()
            for param in self._plot_params:
                inputs_column.append(pn.pane.Str(param))

    def _update_cursor_location(self, x, y):
        ''' Show metadata for cursor x,y position '''
        # Convert plot values to selection values to select plot data
        x_axis = self._plot_inputs['x_axis']
        y_axis = self._plot_inputs['y_axis']
        x = round(x) if x_axis == 'baseline' else x
        y = round(y) if y_axis == 'baseline' else y
        position = {x_axis: x, y_axis: y}
        location_values, units = self._get_cursor_location_values(position)
        self._update_cursor_box(location_values, units)

    def _get_cursor_location_values(self, cursor_position):
        values = cursor_position.copy()
        units = {}

        if self._plot_data:
            try:
                xds = set_index_coordinates(self._plot_data, tuple(cursor_position.keys()))
                sel_xds = xds.sel(indexers=None, method='nearest', tolerance=None, drop=False, **cursor_position)
                for coord in sel_xds.coords:
                    if coord == 'uvw_label' or ('baseline_antenna' in coord and 'baseline_name' in sel_xds.coords):
                        continue
                    val, unit = self._get_xda_val_unit(sel_xds[coord])
                    values[coord] = val
                    units[coord] = unit
                for data_var in sel_xds.data_vars:
                    if 'TIME_CENTROID' in data_var:
                        continue
                    val, unit = self._get_xda_val_unit(sel_xds[data_var])
                    if data_var == 'UVW':
                        names = ['U', 'V', 'W']
                        for i, name in enumerate(names):
                            values[name] = val[i]
                            units[name] = unit[i]
                    else:
                        values[data_var] = val
                        units[data_var] = unit
            except KeyError:
                pass

        # Set complex component name for visibilities
        if 'VISIBILITY' in values:
            values[self._plot_inputs['vis_axis'].upper()] = values.pop('VISIBILITY')
        return values, units

    def _update_cursor_box(self, location_values, units):
        ''' Update cursor location widget box with info in dict '''
        cursor_location_box = self._gui_layout[0][0][1]
        cursor_location_box.clear() # pn.WidgetBox
        location_layout = pn.Column(pn.widgets.StaticText(name="Cursor Location"))
        info_row = pn.Row()
        info_col = pn.Column()

        for name, value in location_values.items():
            # 4 entries per column; append to row and start new column
            if len(info_col.objects) == 4:
                info_row.append(info_col)
                info_col = pn.Column()

            if not isinstance(value, str):
                if name == "FLAG":
                    value = "nan" if np.isnan(value) else int(value)
                elif isinstance(value, float):
                    if np.isnan(value):
                        value = "nan"
                    elif value < 1e6:
                        value = f"{value:.4f}"
                    else:
                        value = f"{value:.4e}"
                elif isinstance(value, np.datetime64):
                    value = to_datetime(np.datetime_as_string(value)).strftime(TIME_FORMAT)
                    units.pop(name) # no unit for datetime string
            unit = units[name] if name in units else ""
            info = pn.widgets.StaticText(name=name, value=f"{value} {unit}")
            info.margin = (0, 10) # default (5, 10)
            info_col.append(info)
        info_row.append(info_col)
        location_layout.append(info_row)
        cursor_location_box.append(location_layout)

    def _get_xda_val_unit(self, xda):
        ''' Get value and unit as str not list '''
        # Value
        val = xda.values
        if isinstance(val, np.ndarray) and val.size == 1:
            val = val.item()
        # Unit
        try:
            unit = xda.attrs['units']
            unit = unit[0] if (isinstance(unit, list) and len(unit) == 1) else unit
            unit = '' if unit == 'unkown' else unit
        except KeyError:
            unit = ''
        return val, unit

    ###
    ### Callbacks for widgets which update plot inputs
    ###
    def _set_title(self, title):
        ''' Set title from gui text input '''
        self._plot_inputs['title'] = title
        self._update_plot_status(True) # Change plot button to solid

    def _set_style_params(self, unflagged_cmap, flagged_cmap, show_colorbar, show_flagged_colorbar):
        self.set_style_params(unflagged_cmap, flagged_cmap, show_colorbar, show_flagged_colorbar)
        self._update_plot_status(True) # Change plot button to solid

    def _set_color_range(self, color_mode, color_range):
        ''' Set style params from gui '''
        color_mode = color_mode.split()[0]
        color_mode = None if color_mode == 'No' else color_mode
        self._plot_inputs['color_mode'] = color_mode
        self._plot_inputs['color_range'] = color_range
        self._update_plot_status(True) # Change plot button to solid

    def _set_axes(self, x_axis, y_axis, vis_axis):
        ''' Set plot axis params from gui '''
        self._plot_inputs['x_axis'] = x_axis
        self._plot_inputs['y_axis'] = y_axis
        self._plot_inputs['vis_axis'] = vis_axis
        self._update_plot_status(True) # Change plot button to solid

    def _set_aggregation(self, aggregator, agg_axes):
        ''' Set aggregation params from gui '''
        aggregator = None if aggregator== 'None' else aggregator
        self._plot_inputs['aggregator'] = aggregator
        self._plot_inputs['agg_axis'] = agg_axes # ignored if aggregator not set
        self._update_plot_status(True) # Change plot button to solid

# pylint: disable=too-many-arguments, too-many-positional-arguments
    def _set_iteration(self, iter_axis, iter_value_type, iter_value, iter_start, iter_end, subplot_rows, subplot_columns):
        ''' Set iteration params from gui '''
        iter_axis = None if iter_axis == 'None' else iter_axis
        self._plot_inputs['iter_axis'] = iter_axis
        self._plot_inputs['subplots'] = (subplot_rows, subplot_columns)

        if iter_axis:
            if iter_value_type == 'By Value':
                # Use index of iter_value for tuple
                if self._data and self._data.is_valid():
                    iter_values = self._data.get_dimension_values(iter_axis)
                    iter_index = iter_values.index(iter_value)
                    self._plot_inputs['iter_range'] = (iter_index, iter_index)
            else:
                # 'By Range': use range start and end values for tuple
                self._plot_inputs['iter_range'] = (iter_start, iter_end)
        else:
            self._plot_inputs['iter_range'] = None
        self._update_plot_status(True) # Change plot button to solid
# pylint: enable=too-many-arguments, too-many-positional-arguments

# pylint: disable=too-many-arguments, too-many-positional-arguments, unused-argument
    def _set_ps_selection(self, query, name, intents, scan_name, spw_name, field_name, source_name, line_name):
        ''' Select ProcessingSet from gui using summary columns '''
        inputs = locals()
        ps_selection = {}
        for key, val in inputs.items():
            if key in PS_SELECTION_OPTIONS.values() and val:
                ps_selection[key] = val
        self._plot_inputs['ps_selection'] = ps_selection
        self._update_plot_status(True) # Change plot button to solid

    def _set_ms_selection(self, data_group, datetime, baseline, antenna1, antenna2, frequency, polarization):
        ''' Select MeasurementSet from gui using data group, dimensions, and coordinates '''
        inputs = locals()
        inputs['time'] = inputs.pop('datetime')
        ms_selection = {}
        for key, val in inputs.items():
            if key in MS_SELECTION_OPTIONS.values() and val:
                ms_selection[key] = val
        self._plot_inputs['ms_selection'] = ms_selection
        self._update_plot_status(True) # Change plot button to solid
# pylint: enable=too-many-arguments, too-many-positional-arguments, unused-argument
