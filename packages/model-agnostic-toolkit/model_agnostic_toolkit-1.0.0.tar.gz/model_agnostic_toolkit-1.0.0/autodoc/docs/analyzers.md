
**[Model Agnostic Toolkit](../README.md) → [Documentation](README.md)**

# Analyzers

> **Hint**: All components make use of docstrings and type hints, outlining what classes and methods do, what parameters are expected and what attributes are available.

All types of analyzers inherit from the `Analyzer` class. Objects of this class are used for computing feature importance or interaction results with different [datasets](datasets.md), [models](models.md) and [tools](tools.md).

**→ [Find a short intro on analyzers here](getting_started.md#analyzer).**

In the following, see how to [work with analyzers](#working-with-analyzers) and find out about [available types of analyzers](#available-analyzers).

## Working with Analyzers

### Creating analyzers

You get an `Analyzer` object by creating an instance of either an `ImportanceAnalyzer` or an `InteractionAnalyzer` depending on what kind of analysis you want to perform. All [types of analyzers](#tool-types) are initialized in the same way. For the initialization, a [model](models.md) and a [dataset](datasets.md) to use for the analysis is required. Pass the `model`, `data` to the analyzer's constructor.
```python
ana = ImportanceAnalyzer(model=model, dataset=data)
```

Optionally, you can pass a `tools` parameter with a list of [tools](tools.md) in addition to `model` and `dataset`. This way, the analyzer is already configured with tools. Otherwise, you have to [add tools](#managing-tools) in a second step.
```python
ana = ImportanceAnalyzer(model=model, dataset=data, tools=tools)
```

It is discouraged to instantiate an `Analyzer` object directly. While it is possible, if you pass a [tool type](#tool-types), you lose the additional functionality provided by e.g. the `ImportanceAnalyzer`.
```python
# not recommended!
ana = Analyzer(tool_type=[ToolType](../model_agnostic_toolkit/types.py).IMPORTANCE, model=model, dataset=data)
```

#### Managing Tools

Before you can perform an analysis, the analyzer needs to have a list of [tools](tools.md) to run. If you did not add any [tool](tools.md) objects during initialization, you can add one or a list of multiple `tools` at any time via the `add_tools(...)` method.
```python
ana.add_tools(tools)
```

> **Note**: An analyzer can keep track of multiple tools of the same class. However, they need to have different names, so [initialize them](tools.md#creating-tools) with a different `name` attribute.

Similarly, you can remove tools from an analyzer by calling its `remove_tools(...)` method and passing the names of tools you want to remove.
```python
ana.remove_tools('PFI Importance')
```

### Running analyses

Having initialized an `Analyzer` object, you can start an analysis simply by calling its `run_analysis(...)` method. You just need to provide the `features` parameter, a list of features (for importance analyis) or feature pairs (for interaction analysis) of your `data` that should be taken into account for the analysis, e.g. all of them. The `run_analysis(...)` method returns a dictionary with complete results for all tools, indexed by the tools' names, and results regarding the model's performance.
```python
results = ana.run_analysis(features=data.features)
```

> **Note**: you only specify a subset of features for the analysis and call `run_analysis(...)` a second time with different features later on, the results returned from the second call will include the results from the first call.

If you want to run a single tool only, you can make use of the analyzer's `run_tool(...)` method. A tool can be specified either by its name or by passing the tool itself. The results are directly returned and still stored by the analyzer together with all other results.
```python
tool_results = ana.run_tool('ALE Importance')
```

#### Accessing results

All results that have been computed by an analyzer so far can be accessed via its `results` attribute. This is identical to what a `run_analysis(...)` call returns, with tool-specific results indexed by the tools' names.
```python
results = ana.results
```

Access the results of a single tool via its name. This is identical to what a `run_tool(...)` call returns.
```python
tool_results = ana.results['ALE Importance']
```

#### Fitting and evaluating models

The `run_analysis(...)` and `run_tool(...)` methods both make sure that the analyzer's [model](models.md) has been fitted on the corresponding dataset. If that is not the case, the analyzer takes care of fitting.

> **Note**: You can avoid fitting through the analyzer by passing `fit=False` to any of the two methods. Do this at your own risk.

If you want to fit the analyzer's model to its dataset manually, you can do this by calling its fit_model(...) method. To refit even if the model is already fitted, pass `force=True`. Fitting includes a call of the `evaluate_model(...)` method, returning the model performance analysis results.
```python
model_results = ana.fit_model()
```

#### Plotting results

All results computed so far by an analyzer can be plotted via its `plot_results(...)` method. This includes the default plot for every tool as well as a model performance plot.
```python
ana.plot_results()
```

Alternatively, the [results can be accessed](#accessing-results) individually for each tool and passed to the respective tool's `plot(...)` method. To obtain more different plots and get more customization options, use any method from the [plotting module](plotting.md) to obtain a figure.

#### Export results

All results computed so far by an analyzer can be exported via its `export_plots(...)` method to html respective JSON. This includes the default plot for every tool as well as a model performance plot.
```python
ana.plot_results()
```

### Reusing results

To speed up analyses, results of some tool computations are often reused for others. In the most basic case, if you run a tool's analysis, the analyzer checks if results of the same tool already exist for any of the specified features. If yes, the previous results are returned.

> **Hint**: You can pass `reuse_tools=False` to avoid the reusing of results [across tools](#reusing-across-tools) and [across analyzers](#reusing-across-analyzers).

#### Reusing across tools

Some tools internally depend on the results of other tools (e.g. the `VIPInteraction]` depends on `PDPInteraction`. If both tools are part of the same analyzer, the PDP results are automatically reused for the VIP analysis. The order the tools are run in does not matter.
```python
tools = [PDPInteraction(), VIPInteraction()]
ana = InteractionAnalyzer(model=model, dataset=data, tools=tools)
res = ana.run_analysis(features=data.feature_pairs)
```

#### Reusing across analyzers

Some tools also depend on other tools with a different [tool type](tools.md#tool-types) (e.g. `PDPInteraction` with `second_order_only=True` on `PDPImportance`. When creating an `Analyzer` instance, you can pass a list of analyzers to reuse results from via the `reuse_analyzers` parameter. When a tool is run, the analyzer searches across reuse analyzers for tools it can reuse. Here as well, the order the tools are run in does not matter.
```python
ana_importance = ImportanceAnalyzer(model=model, dataset=data, tools=importance_tools)
ana_interaction = InteractionAnalyzer(model=model, dataset=data, tools=interaction_tools, reuse_analyzers=[ana_importance])
```

If an analyzer has already been initialized, you can add reuse analyzers via its `add_reuse_analyzers(...)` method.

### Properties

#### Model, dataset and tools

You can at any time access the [model](models.md), [dataset](datasets.md) and [tool](tools.md) instances associated with an analyzer via the respective attributes.
```python
model = ana.model
data = ana.dataset
tools = ana.tools
```

#### Tool types

Each `Analyzer` instance has a `ToolType` enum instance, indicating whether it is an importance analyzer (`ToolType.IMPORTANCE`) or an interaction analyzer (`ToolType.INTERACTION`). This tool type is automatically set when instantiating e.g. an `ImportanceAnalyzer` and later used to check all tools for the correct `ToolType`.

### Relevant example notebooks

The following [Jupyter](https://jupyter.org) notebooks demonstrate the topics covered here and can be found in the 'examples directory'.

- quick_start.ipynb(examples/quick_start.ipynb)
- feature_importance_analysis.ipynb(examples/feature_importance_analysis.ipynb)
- feature_interaction_analysis.ipynb(examples/feature_interaction_analysis.ipynb)
- classification_analysis.ipynb(examples/classification_analysis.ipynb) 
- reusing_results.ipynb(examples/reusing_results.ipynb)

### Available member methods

The following methods are available for all objects of the `Analyzer` class and [inheriting classes](#available-analyzers).

- `add_tools(...)`
- `remove_tools(...)`
- `add_reuse_analyzers(...)`
- `fit_model(...)`
- `evaluate_model(...)`
- `run_tool(...)`
- `run_analysis(...)`
- `plot_results(...)`
- `export_plots(...)`
- `result_exists(...)`

## Available Analyzers

```{mermaid}
classDiagram
    Analyzer <|-- ImportanceAnalyzer
    Analyzer <|-- InteractionAnalyzer
```

> **Hint**: All of the following analyzer types can be imported like this:
> ```python
> from model_agnostic_toolkit import ImportanceAnalyzer, InteractionAnalyzer
> ```
