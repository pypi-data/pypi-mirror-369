**[Model Agnostic Toolkit](../README.md) → [Documentation](README.md)**

# Plotting

> **Hint**: All components make use of docstrings and type hints, outlining what classes and methods do, what parameters are expected and what attributes are available.

All plotting methods are used to visualize results computed with different [tools](tools.md) and [models](models.md) on different [datasets](datasets.md). Plotting functionality can be accessed through an [analyzer](analyzers.md), through [tools](tools.md) directly or manually with the corresponding methods.

In the following, see how to [work with plots](#working-with-plots) directly and find out about [all available plots](#available-plots).

## Working with Plots

The plotting backend used for the `Model Agnostic Toolkit` is [Plotly](https://plotly.com/). That means, every figure returned or shown by plotting methods is an interactive [`Plotly`](https://plotly.com/) figure that allows for zooming, hover tooltips, exporting and more.

### Default tool plots

If you have created and run an `analyzer` with `tools` and a `model`, you can show the default plots for each tool and the model through the analyzer's plotting functionality or show the default plot for each tool individually through a tool's plotting functionality.


> **Hint:** In **classification** case set the class whose tool's results to plot.

### Plotting individual results

To have more control over your plots, you can use any of the available plotting methods. Plotting methods usually expect the result dictionary of a single tool. In classification case the results of one selected class are expected. The result plots of individual tools take the results of one single instance. Given an analyzer `ana` with results for e.g. a `SHAPImportance` tool, access this tool's results, choose a suitable plotting method to generate a [`Plotly`](https://plotly.com/) figure and display it via `show()`.
```python
shap_results = ana.results['SHAP Importance']
# next row only for classification problems
shap_results = shap_results[0]['result']
figure = shap_beeswarm_plot(shap_results)
figure.show()
```

> **Hint**: A `Jupyter` notebook may not require you to store the figure and call `show()` but will instead directly show the returned figure.

Some plots are meant to work with the results for single features computed by a tool. You can access these results via the dictionary again. Compared to the default plots, the individual plotting methods allow you to additionally pass a number of parameters for plot customization. Remember to select the results of one class in classification case beforehand.
```python
pdp_result = ana.results['PDP Importance']['feature_four']
figure = pdp_line_plot(pdp_result, title='PDP for feature four', samples=False, max_num_ice=250)
figure.show()
```

Next to plots for specific tools, some plotting methods are suitable for most or all tools of the same category (importance or interaction) and include options that are useful for most of them. Again remember to select the results of one class in classification case beforehand.
```python
vip_results = ana.results['VIP Interaction']
figure = interaction_bar_plot(vip_results, title='VIP Interaction results', max_num_bars=None,
                              show_alpha_levels=True, horizontal=False)
figure.show()
```

#### Model performance plots

Besides tool plots, there are plots for model performance available as well. Note that they may expect something else than the model result dictionary, e.g. predicted and ground truth dataset targets `y_pred` and `y_test`.
```python
figure = target_distributions_plot(y_test, y_pred)
figure.show()
```

### Plotly configuration

You can pass a `config` dictionary to [`Plotly`](https://plotly.com/)'s `show()` method in order to expand or restrict the interaction possibilities or adjust the export behavior. Have a look at all [`Plotly`](https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js) configuration options to see what is possible.
```python
show_config = {
    'modeBarButtonsToAdd': [
        'drawopenpath',
        'drawcircle',
        'eraseshape'
    ],
    'modeBarButtonsToRemove': [
        'zoom',
        'pan'
    ],
    'toImageButtonOptions': {
        'format': 'svg',
        'height': 500,
        'width': 1000
    },
    'displaylogo': False
}

figure.show(config=show_config)
```

You can also pass such a configuration dictionary via the `plot_config` parameter to the default tool plotting methods `plot_results(...)` for an `analyzer` or `plot(...)` for a `tool`.

An `.svg` download option may be especially helpful when exporting graphics to use them in other documents (such as this documentation). You can import a minimal configuration dictionary for this adjustment.
```python
from model_agnostic_toolkit.plots.utils import plot_config_svg
```

### Relevant example notebooks

The following [`Jupyter`](https://jupyter.org/) notebooks demonstrate the topics covered here and can be found in the examples directory.

- `quick_start.ipynb` (examples/quick_start.ipynb)
- `plotting_results.ipynb` (examples/plotting_results.ipynb)

## Available Plots

> **Hint**: All the following plotting methods can be imported like this:
> ```python
> from model_agnostic_toolkit.plots import pdp_line_plot, interaction_matrix_plot
> ```

A detailed documentation of the plotting functionalities is available at: [Plotting documentation](../model_agnostic_toolkit.plots)

### Model plots

- `model_scores_plot(...)`
- `target_distributions_plot(...)`

### Importance plots

- `importance_bar_plot(...)`
- `importance_line_plot(...)`

#### Tool-specific importance plots

- `ale_line_plot(...)`
- `ale_grid_plot(...)`
- `pdp_grid_plot(...)`
- `pdp_line_plot(...)`
- `pfi_bar_plot(...)`
- `shap_bar_plot(...)`
- `shap_beeswarm_plot(...)`
- `shap_summary_plot(...)`

### Interaction plots

- `interaction_bar_plot(...)`
- `interaction_matrix_plot(...)`
- `interaction_summary_plot(...)`
- `interaction_heatmap_plot(...)`
- `interaction_heatmap_matrix_plot(...)`

#### Tool-specific interaction plots
- `ale_heatmap_plot(...)`
- `pdp_heatmap_plot(...)`
