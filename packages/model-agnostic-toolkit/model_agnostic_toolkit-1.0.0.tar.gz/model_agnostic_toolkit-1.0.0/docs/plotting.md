**[Model Agnostic Toolkit](../README.md) → [Documentation](README.md)**

# Plotting

> **Hint**: All components make use docstrings and type hints that outline what classes and methods do, which parameters are expected and what attributes are available.
> Follow the embedded links (e.g. [`importance_bar_plot(...)`]) to take a look.

All plotting methods are used to visualize results computed with different [tools](tools.md) and [models](models.md) on different [datasets](datasets.md). Plotting functionality can be accessed through an [analyzer](analyzers.md), through [tools](tools.md) directly, or manually with the corresponding methods.

In the following sections, see how to [work with plots](#working-with-plots) directly and find out about [all available plots](#available-plots).

## Working with Plots

The plotting backend used for the [Model Agnostic Toolkit] is [Plotly]. That means, every figure returned or shown by plotting methods is an interactive [Plotly] figure that allows for zooming, hover tooltips, exporting and more.

### Default tool plots

If you have created and run an [analyzer](analyzers.md) with [tools](tools.md) and a [model](models.md), you can show the default plots for each tool and the model through the [analyzer's plotting functionality](analyzers.md#plotting-results) or show the default plot for each tool individually through a [tools's plotting functionality](tools.md#running-and-plotting). 

> **Hint:** In the **classification** case set the class which tool's to plot.

> **Hint**: A [Jupyter] notebook may not require you to store the figure and call `show()` but will instead directly show the returned figure.

Some plots are meant to work with the results for single features computed by a tool. You can [access these results](analyzers.md#accessing-results) via the dictionary again. Compared to the default plots, the individual [plotting methods](#available-plots) (do not mess up with plots of [`individual tools`]) allow you to additionally pass a number of parameters for plot customization.
Remember to select the results of one class in classification case beforehand
```python
pdp_result = ana.results['PDP Importance']['feature_four']
figure = pdp_line_plot(pdp_result, title='PDP for feature four', samples=False, max_num_ice=250)
figure.show()
```

Next to plots for specific tools, some [plotting methods](#available-plots) are suitable for most or all tools of the same category (importance or interaction) and include options that are useful for most of them.
Again remember to select the results of one class in classification case beforehand
```python
vip_results = ana.results['VIP Interaction']
figure = interaction_bar_plot(vip_results, title='VIP Interaction results', max_num_bars=None,
                              show_alpha_levels=True, horizontal=False)
figure.show()
```

#### Model performance plots

Besides tool plots, there are [plots for model performance](#model-plots) available as well. Note that they may expect something else than the [model result dictionary](models.md#metrics), e.g. predicted and ground truth [dataset](datasets.md) targets `y_pred` and `y_test`.
```python
figure = target_distributions_plot(y_test, y_pred)
figure.show()
```

### Plotly configuration

You can pass a `config` dictinary to [Plotly]'s `show()` method in order to expand or restrict the interaction possibilities or adjust the export behavior. Have a look at all [Plotly configuration options] to see what is possible.
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

You can also pass such a configuration dictionary via the `plot_config` parameter to the [default tool plotting methods](#default-tool-plots) [`plot_results(...)`] for an [analyzer](analyzers.md) or [`plot(...)`] for a [tool](tools.md).

An `.svg` download option may be especially helpful when exporting graphics to use them in other documents (such as this documentation). You can import a minimal configuration dictionary for this adjustment.
```python
from model_agnostic_toolkit.plots.utils import plot_config_svg
```

### Relevant example notebooks

The following [Jupyter] notebooks demonstrate the topics covered here and can be found in the [examples directory](../examples/).

- [`quick_start.ipynb`](../examples/quick_start.ipynb)
- [`plotting_results.ipynb`](../examples/plotting_results.ipynb)

## Available Plots

> **Hint**: All the following plotting methods can be imported like this:
> ```python
> from model_agnostic_toolkit.plots import pdp_line_plot, interaction_matrix_plot
> ```

### Model plots

- [`model_scores_plot(...)`]
- [`target_distributions_plot(...)`]

### Importance plots

- [`importance_bar_plot(...)`]
- [`importance_line_plot(...)`]

#### Tool-specific importance plots

- [`ale_line_plot(...)`]
- [`ale_grid_plot(...)`]
- [`pdp_grid_plot(...)`]
- [`pdp_line_plot(...)`]
- [`pfi_bar_plot(...)`]
- [`shap_bar_plot(...)`]
- [`shap_beeswarm_plot(...)`]
- [`shap_summary_plot(...)`]

### Interaction plots

- [`interaction_bar_plot(...)`]
- [`interaction_matrix_plot(...)`]
- [`interaction_summary_plot(...)`]
- [`interaction_heatmap_plot(...)`]
- [`interaction_heatmap_matrix_plot(...)`]

#### Tool-specific interaction plots

- [`ale_heatmap_plot(...)`]
- [`pdp_heatmap_plot(...)`]

<!-- internal links -->
[Model Agnostic Toolkit]: ../README.md

<!-- external links -->
[Jupyter]: https://jupyter.org
[Plotly]: https://plotly.com/python
[Plotly configuration options]: https://plotly.com/python/configuration-options

<!-- internal class references -->
[`SHAPImportance`]: ../model_agnostic_toolkit/tools/shap/shap_importance.py

<!-- internal function references -->
[`ale_grid_plot(...)`]: ../model_agnostic_toolkit/plots/ale_plots.py#L76
[`ale_heatmap_plot(...)`]: ../model_agnostic_toolkit/plots/ale_plots.py#L128
[`ale_line_plot(...)`]: ../model_agnostic_toolkit/plots/ale_plots.py#L10
[`anchor_plot(...)`]: ../model_agnostic_toolkit/plots/anchor_plots.py#L8
[`importance_bar_plot(...)`]: ../model_agnostic_toolkit/plots/importance_plots.py#L6
[`importance_line_plot(...)`]: ../model_agnostic_toolkit/plots/importance_plots.py#L42
[`interaction_bar_plot(...)`]: ../model_agnostic_toolkit/plots/interaction_plots.py#L12
[`interaction_heatmap_plot(...)`]: ../model_agnostic_toolkit/plots/interaction_plots.py#L170
[`interaction_heatmap_matrix_plot(...)`]: ../model_agnostic_toolkit/plots/interaction_plots.py#L227
[`interaction_matrix_plot(...)`]: ../model_agnostic_toolkit/plots/interaction_plots.py#L78
[`interaction_summary_plot(...)`]: ../model_agnostic_toolkit/plots/interaction_plots.py#L133
[`model_scores_plot(...)`]: ../model_agnostic_toolkit/plots/model_plots.py#L9
[`pdp_grid_plot(...)`]: ../model_agnostic_toolkit/plots/pdp_plots.py#L67
[`pdp_heatmap_plot(...)`]: ../model_agnostic_toolkit/plots/pdp_plots.py#L119
[`pdp_line_plot(...)`]: ../model_agnostic_toolkit/plots/pdp_plots.py#L12
[`pfi_bar_plot(...)`]: ../model_agnostic_toolkit/plots/pfi_plots.py#L6
[`plot(...)`]: ../model_agnostic_toolkit/tools/tool.py#L92
[`plot_results(...)`]: ../model_agnostic_toolkit/analyzer.py#L273
[`shap_bar_plot(...)`]: ../model_agnostic_toolkit/plots/shap_plots.py#L12
[`shap_beeswarm_plot(...)`]: ../model_agnostic_toolkit/plots/shap_plots.py#L26
[`shap_summary_plot(...)`]: ../model_agnostic_toolkit/plots/shap_plots.py#L93
[`target_distributions_plot(...)`]: ../model_agnostic_toolkit/plots/model_plots.py#L39
