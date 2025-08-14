import warnings
from typing import Any, Dict, List, Tuple, Type, Union

import numpy as np
from plotly.io import to_json

from . import Analyzer  # forward declaration to be overwritten
from . import Model
from .datasets import Dataset
from .tools import ImportanceTool, InteractionTool, Tool
from .types import DataType, ToolType


class Analyzer:
    """Analyzer handling a model and a dataset and managing all tools to use for analysis.
    Provides functions to run analyses with all these tools and stores the computed results.

    Attributes:
        tool_type (ToolType): Type of tools used by this analyzer.
        model (Model): Model to run the analysis with.
        dataset (Dataset): Dataset to run the analysis for.
        tools: Dict[str, Tool]: Dictionary storing all tools for analysis.
        results: Dict[str, Dict]: Dictionary storing all results computed with the analyzer's tools.
        reuse_analyzers (List[Analyzer]): List of analyzers from whose tools results can be reused.
    """

    def __init__(self, tool_type: ToolType, model: Model, dataset: Dataset, tools: Union[List[Tool], Tool] = None,
                 reuse_analyzers: Union[List[Analyzer], Analyzer] = None):
        """Initializes analyzer for given model and dataset with given tools.
        Sets up dictionaries for managing tools and results.

        Args:
            tool_type (ToolType): Type of tools to use for the analysis (feature importance or interaction tools).
            model (Model): Model to run the analysis with.
            dataset (Dataset): Dataset to run the analysis for.
            tools (Union[List[Tool], Tool], optional): List of tools to execute the analysis with. Defaults to None.
            reuse_analyzers (Union[List[Analyzer], Analyzer], optional): List of analyzers from whose tools results can be reused. Defaults to None
        """

        # set attributes
        self.tool_type = tool_type
        self.model = model
        self.dataset = dataset
        self.classindex = None

        if self.dataset.data_type == DataType.CLASSIFICATION:
            self._check_classes()

        # initialize tool and result dictionaries
        self.tools = {}
        self.results = {}
        self._temp_results = {}
        if tools is not None:
            self.add_tools(tools)

        # make given analyzers' and own tools' results reusable
        self.reuse_analyzers = [self]
        if reuse_analyzers is not None:
            self.add_reuse_analyzers(reuse_analyzers)

        # default run settings
        self._run_reuse_tools = True
        self._run_force = False

    def add_tools(self, tools: Union[List[Tool], Tool], force: bool = False):
        """Adds the specified tools to the analyzer's list of tools.
        These tools are additionally run when executing the analysis.
        Preexisting tools are not overwritten, except when the `force` keyword is set to `True`.

        Args:
            tools (Union[List[Tool], Tool]): List of tools to add for the analysis.
            force (bool, optional): Option to overwrite existing tools if True. Defaults to False.
        """

        # check tools before adding
        tools = self._check_tools(tools, expected_type=Tool)

        # add tools to tools dictionary
        for tool in tools:
            if tool.tool_type == self.tool_type:
                if tool.name not in self.tools.keys() or force:
                    self.tools[tool.name] = tool
                    self.results[tool.name] = {}
                    self._temp_results[tool.name] = {}
                else:
                    warnings.warn('Tool {name} already exists in analyzer. Skipping.'
                                  .format(name=tool.name), RuntimeWarning)
            else:
                warnings.warn('Tool {name} has wrong tool type {tool_type}. Expected tool type {exp_type}. Skipping.'
                              .format(name=tool.name, tool_type=tool.tool_type.value, exp_type=self.tool_type.value),
                              RuntimeWarning)

    def remove_tools(self, tools: Union[List[str], str]):
        """Removes the specified tools from the analyzer's list of tools.
        Also removes any associated results already computed and stored by the analyzer.

        Args:
            tools (Union[List[str], str]): List of tools to remove from the analyzer, specified by their name.
        """

        # check tools before removing
        tools = self._check_tools(tools, expected_type=str)

        # remove tools from dictionaries
        for tool in tools:
            if tool in self.tools.keys():
                self.tools.pop(tool)
                self.results.pop(tool)
                self._temp_results.pop(tool)

    def add_reuse_analyzers(self, analyzers: Union[List[Analyzer], Analyzer]):
        """Adds the specified analyzers to the list of analyzers to reuse results from.

        Args:
            analyzers (Union[List[Analyzer], Analyzer]): List of analyzers to add for reuse.
        """

        if not isinstance(analyzers, list):
            analyzers = [analyzers]

        # add analyzers to reuse analyzer list
        for analyzer in analyzers:
            if isinstance(analyzer, Analyzer):
                if analyzer.dataset == self.dataset:
                    self.reuse_analyzers.append(analyzer)
                    if analyzer.model != self.model:
                        warnings.warn('Passed reuse analyzer uses different model {model} instead of {exp_model}.'
                                      .format(model=type(analyzer.model.model), exp_model=type(self.model.model)),
                                      RuntimeWarning)
                else:
                    warnings.warn('Passed reuse analyzer uses different dataset {data}. Expected {exp_data}. Skipping.'
                                  .format(data=analyzer.dataset.name, exp_data=self.dataset.name), RuntimeWarning)
            else:
                warnings.warn('Passed reuse analyzer has wrong type {obj_type}. Expected type {ana_type}. Skipping.'
                              .format(obj_type=type(analyzer), ana_type=Analyzer), RuntimeWarning)

    def fit_model(self, force: bool = False, *args, **kwargs):
        """Fits the underlying model to training data if it is not already fitted.
        Also evaluates the model.

        Positional and keyworded arguments are passed to the model's fit function.

        Args:
            force (bool, optional): Option to force the fitting of the model if True, even if it is already fitted. Defaults to False.
        """

        # check if model is fitted, otherwise fit
        if not self.model.is_fitted() or force:
            x_train, y_train = self.dataset.get_train()
            self.model.fit(x_train, y_train, *args, **kwargs)
            if 'model' in self.results.keys():
                self.results.pop('model')
        self.evaluate_model(force)

    def evaluate_model(self, force: bool = False) -> Dict:
        """Evaluates the underlying model if it has not been evaluated already and stores the results.

        Args:
            force (bool, optional): Option to force a reevaluation of the model. Defaults to False.

        Returns:
            Dict: Results of the model evaluation for training and testing data.
        """

        # check if model has been evaluated, otherwise evaluate
        if 'model' not in self.results.keys() or force:
            # store results
            self.results['model'] = self.model.evaluate(self.dataset)

        return self.results['model']

    def run_tool(self, tool: Union[Tool, str], features: Union[List[str], List[Tuple[str, str]]] = None,
                 fit: bool = True, reuse_tools: bool = True, force: bool = False, temp: bool = False) -> Dict:
        """Runs an analysis with the specified tool for the given features and stores the computed results.

        Args:
            tool (Union[Tool, str]): Tool to run the analysis with.
            features (Union[List[str], List[Tuple[str, str]]]): List of features to compute the analysis results for.
            fit (bool, optional): Whether to fit the model before running the analysis if it is not already fitted. Defaults to True.
            reuse_tools (bool, optional): Whether to reuse existing tool's results for computations of this tool. Kept at previous value if `temp` is True.
            force (bool, optional): Option to ignore existing results and force the analysis to run again and also fit the model again if True. Model fitting is excluded if `fit` is False. Kept at previous value if `temp` is True. Defaults to False.
            temp (bool, optional): Whether the tool is run for temporary intermediate results for other tools. If True, results are saved in `self._temp_results` instead of `self.results`. Defaults to False.

        Raises:
            KeyError: Raised if the specified tool is not in the analyzer's list of tools.
            TypeError: Raised if the specified tool is not of type str or Tool.

        Returns:
            Dict: All computed analysis results for the specified tool.
        """
        result = None
        missing_features, res_dict, tool = self._initialize_run_tool(features, fit, force, reuse_tools, temp, tool)

        # run tool and check result
        if self._run_force:
            missing_features = features
        if missing_features:
            result = tool.run(self.model, self.dataset, missing_features, self)
            if not temp:
                tool._check_result_format(result, missing_features)

        # empty results if needed and save new results
        if self._run_force and not temp:
            res_dict[tool.name] = {}
        if result:
            res_dict[tool.name].update(result)
        return res_dict[tool.name]

    def _initialize_run_tool(self, features, fit, force, reuse_tools, temp, tool):
        # check passed tool
        if not isinstance(tool, Tool):
            if not isinstance(tool, str):
                raise TypeError('Passed tool must be of type {type_1} or {type_2}. Got {object_type} instead.'
                                .format(type_1=str, type_2=Tool, object_type=type(tool)))
            # find tool by name
            if tool in self.tools.keys():
                tool = self.tools[tool]
            else:
                raise KeyError('Tool {tool} could not be found in tools.'
                               .format(tool=tool))
        # set flags to force new computation and to reuse tools in this run if desired
        if not temp:
            self._run_force = force
            self._run_reuse_tools = reuse_tools
        # choose correct results dict (temp or not)
        res_dict = self._temp_results if temp else self.results
        other_res_dict = self.results if temp else self._temp_results
        # check for missing and elsewhere existing results and filter features
        features = self._check_features(features)
        missing_features = [f for f in features if not self.result_exists(tool, f, self._run_force, temp)]
        existing_features = [f for f in missing_features if self.result_exists(tool, f, self._run_force, (not temp))]
        # copy results existing in self._temp_results to self.results or vice versa
        for f in existing_features:
            res_dict[tool.name][f] = other_res_dict[tool.name][f]
            missing_features.pop(missing_features.index(f))
        # fit model if needed
        if fit and not temp:
            self.fit_model(self._run_force)

        return missing_features, res_dict, tool

    def run_analysis(self, features: Union[List[str], List[Tuple[str, str]]], fit: bool = True,
                     reuse_tools: bool = True, raise_tool_errors: bool = False, force: bool = False):
        """Executes the analysis for all specified features with every tool added to the analyzer.

        Args:
            features (Union[List[str], List[Tuple[str, str]]]): List of features to compute the analysis results for.
            fit (bool, optional): Whether to fit the model before running the analysis if it is not already fitted. Defaults to True.
            reuse_tools (bool, optional): Whether to reuse existing tool's results for computations of other tools.
            raise_tool_errors (bool, optional): Option to raise errors that occur when running tools if True. Else, only a warning will be issued. Defaults to False.
            force (bool, optional): Option to ignore existing results and force the analysis to run again and also fit the model again for every tool if True. Model fitting is excluded if `fit` is False. Defaults to False.

        Raises:
            TypeError: Raised if the specified tool type is not of type ToolType.

        Returns:
            Dict[str, Dict]: All computed analysis results from all tools. Includes results for features specified in prior executions of this function as well as model results.
        """

        # run every tool

        for tool in self.tools.values():

            try:
                self.run_tool(tool, features, fit, reuse_tools, force)
            except Exception as e:
                if raise_tool_errors:
                    raise e
                else:
                    warnings.warn(('An error occurred while running tool {tool}:\n' + str(e) + '\nSkipping.')
                                  .format(tool=type(tool)), RuntimeWarning)

    def plot_results(self, class_name=None, include_model: bool = True, plot_config: Dict = None):
        """Plots the model performance and results for all tools.
        Each tools `plot` method is successively called here.

        Args:
            class_name (Any, optional): Class to display. Only relevant for classification. Defaults to None.
            include_model (bool, optional): Whether to include a plot with model performance metrics. Defaults to True.
            plot_config (Dict, optional): Configuration dictionary for Plotly's `show()` method ([reference](https://plotly.com/python/configuration-options/)). Defaults to None.
        """

        if self.model.data_type == DataType.CLASSIFICATION and not class_name:
            class_name = self.model.classes[0]

        self._set_class_index(class_name)

        # plot model performance metrics
        if include_model:
            if 'model' in self.results.keys():
                self.model.plot(self.results['model'])
            else:
                print('No results for model performance available.')

        # tool specific plots
        for tool in self.tools.values():
            if self.results[tool.name] == {}:
                print(f'No results for tool {tool.name} available.')

            elif self.dataset.data_type == DataType.CLASSIFICATION:
                new_results = None
                keys = self.results[tool.name].keys()
                for _ in keys:
                    if self.results[tool.name][self.classindex]['class_label'] == class_name:
                        new_results = self.results[tool.name][self.classindex]['result']
                if not new_results:
                    class_name = self.model.classes[0]
                    warnings.warn(f'The requested class is not available showing results for class {class_name}')
                    new_results = self.results[tool.name][0]['result']
                name = f"{tool.name} for class {class_name}"
                tool.plot(new_results, title=name, plot_config=plot_config)
            else:
                tool.plot(self.results[tool.name], plot_config=plot_config)

    def export_plots(
            self, export_format: str = 'json', class_name=None, plot_config: Dict = None, layout: Dict = None):
        """Exports the plot of the results for all tools.
        Each tools `plot` method is successively called here.

        Args:
            export_format (str, optional): Export format. Either 'json' (json string of the plotly graphs) or 'html'(html div of the plotly graphs). Defaults to 'json'.
            class_name (Any, optional): Class to display. Only relevant for classification. Defaults to None.
            plot_config (Dict, optional): Configuration dictionary for Plotly's `show()` method ([reference](https://plotly.com/python/configuration-options/)). Defaults to None.
            layout (Dict, optional): Layout dictionary for Plotly ([reference](https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html#plotly.graph_objects.Layout)). Defaults to None.
        
        Raises:
            ValueError: Raised if the export_format is not supported.
        
        Returns:
            List: List of the plot's JSON representations
        """
        export = {}

        self._set_class_index(class_name)
        if export_format not in {'json', 'html'}:
            raise ValueError(f'Export export_format {export_format} is not supported. '
                             f'Supported formats are "json" and "html").')

        # tool specific plots
        for tool in self.tools.values():
            plot = self._export_plot(layout, plot_config, tool)
            # add tool results plots to export
            export[tool.name] = to_json(plot) if export_format == 'json' else (
                plot.to_html(include_plotlyjs=False, full_html=False, config=plot_config))

        return export

    def result_exists(self, tool: Tool, feature: Union[str, Tuple[str, str]], force: bool = False,
                      temp: bool = False) -> bool:
        """Checks whether a result has already been computed for the given tool and feature.

        Args:
            tool (Tool): Tool to check result existence for.
            feature (Union[str, Tuple[str, str]]): Feature to check result existence for.
            force (bool, optional): Option to ignore existing results if True. Defaults to False.
            temp (bool, optional): Whether to look in `self._temp_results` instead of `self.results`.

        Returns:
            bool: Whether a result has already been computed.
        """
        if force:
            return False
        elif not temp and feature in self.results[tool.name].keys():
            return True
        elif temp and feature in self._temp_results[tool.name].keys():
            return True
        else:
            return False

    def _find_reuse_tool(self, tool_class: Type[Tool], model: Model, dataset: Dataset, **requirements) -> Union[
                         Tuple[Analyzer, Tool], Tuple[None, None]]:
        """Looks for existing tools in `self.reuse_analyzers` that fulfill requirements and can be reused for intermediate result in other tools.

        Args:
            tool_class (Type[Tool]): Uninitialized class of tool to find an instances of for reusing.
            model(Model): Model to check compatibility with.
            dataset(Dataset): Dataset to check compatibility with.
            **requirements: Keyworded arguments with attributes to be checked in a found tool.

        Returns:
            Tuple[Analyzer, Tool]: Found analyzer and its tool for reusing.
        """
        if self._run_reuse_tools and not self._run_force:
            for analyzer in self.reuse_analyzers:
                if model == analyzer.model and dataset == analyzer.dataset:
                    for tool in analyzer.tools.values():
                        if isinstance(tool, tool_class):
                            fine = True
                            for key, value in requirements.items():
                                fine = fine and (getattr(tool, key) == value)
                                if not fine:
                                    break
                            if fine:
                                reuse_analyzer = analyzer
                                reuse_tool = tool

                                return reuse_analyzer, reuse_tool

        return None, None

    def _check_features(self, features: Any) -> Union[List[str], List[Tuple[str, str]]]:
        """Checks the export_format of the passed feature of feature list with respect to the analyzer's tool type.
        Adjusts the output export_format if needed and possible.
        The expected export_format is a str or List[str] for feature importance tools and a Tuple[str, str] or List[Tuple[str, str]] for feature interaction tools.

        Args:
            features (Any): Feature or feature list to check the export_format of.

        Raises:
            TypeError: Raised if at least one feature is not a str or tuple.
            ValueError: Raised if a passed tuple does not have the form Tuple[str, str].
            TypeError: Raised if something other than a str is used for an importance tool.
            TypeError: Raised if something other than a tuple is used for an interaction tool.

        Returns:
            Union[List[str], List[Tuple[str, str]]]: List of checked and possibly adjusted features or feature tuples.
        """
        # create list if needed
        if not isinstance(features, list):
            features = [features]

        for feature in features:
            # check for string or tuple types
            if not (isinstance(feature, (str, tuple))):
                raise TypeError('Passed features must be of type {type_1} or {type_2}. Got {object_type} instead.'
                                .format(type_1=str, type_2=tuple, object_type=type(feature)))
            # if tuple, check length and types
            if isinstance(feature, tuple) and [type(f) for f in feature] != [str, str, ]:
                raise ValueError(
                    'Passed feature tuples must have the form {exp_form}. Got {form} instead.'.format(
                        exp_form=(str, str), form=tuple(type(f) for f in feature)
                    )
                )
            # check if feature type (string or tuple) corresponds to tool type
            if self.tool_type == ToolType.IMPORTANCE and not isinstance(feature, str):
                raise TypeError('Features for {tool_name} must be of type {expected_type}. Got {object_type} instead.'
                                .format(tool_name=self.tool_type.value, expected_type=str, object_type=type(feature)))
            elif self.tool_type is ToolType.INTERACTION and not isinstance(feature, tuple):
                raise TypeError('Features for {tool_name} must be of type {expected_type}. Got {object_type} instead.'
                                .format(tool_name=self.tool_type.value, expected_type=tuple, object_type=type(feature)))

        return features

    @staticmethod
    def _check_tools(tools: Any, expected_type: Union[Type[Tool], Type[str]]) -> Union[List[Tool], List[str]]:
        """Checks the type of the passed tool or tool list with respect to the expected type str or Tool.
        Adjusts the output export_format if needed and possible.

        Args:
            tools (Any): Tool or list of tools to check the type of.
            expected_type (Union[type[Tool], type[str]]): Expected type for the specified tools (either str or Tool).

        Raises:
            TypeError: Raised if at least one tool does not have the expected type.

        Returns:
            Union[List[Tool], List[str]]: List of checked and possibly adjusted tools with the expected type.
        """
        # create list if needed
        if not isinstance(tools, list):
            tools = [tools]

        for tool in tools:
            # check for correct type of tools
            if isinstance(tool, Tool) and expected_type == str:
                tool = tool.name
            if not isinstance(tool, expected_type):
                raise TypeError('Passed tools must be of type {expected_type}. Got {object_type} instead.'
                                .format(expected_type=expected_type, object_type=type(tool)))

        return tools

    def _check_classes(self):
        """Checks whether all classes present in y_test are also present in y_train

        Raises:
            ValueError: If there are classes in y_test that are not present in y_train
        """
        _, y_train = self.dataset.get_train()
        _, y_test = self.dataset.get_test()
        if not set(np.unique(y_test)).issubset(np.unique(y_train)):
            raise ValueError('All classes present in y_test must be present in y_train.')

    def _set_class_index(self, class_name):
        """
        Set the index of the specified class in the model.

        Args:
            class_name (str): The name of the class to set the index for.
            
        Raises:
            Warning: If the specified class is not found in the model.
            
        Returns:
            None
        """
        self.classindex = None
        if self.dataset.data_type == DataType.CLASSIFICATION:
            if class_name is None:
                self.classindex = 0
            else:
                classes = self.model.classes
                for class_index, class_label in enumerate(classes):
                    if class_label == class_name:
                        warnings.warn('Class {name} is found'.format(name=class_name), category=Warning)
                        self.classindex = class_index
                if self.classindex is None:
                    message = (f'Class {class_name} is not found, check name and type. '
                               f'Currently showing class {classes[0]}')
                    warnings.warn(message, category=Warning)
                    print(message)
                    self.classindex = 0

    def _export_plot(self, layout, plot_config, tool):
        """
        Export a plot based on the provided layout, plot configuration, and tool.

        Args:
            layout (dict): The layout configuration for the plot.
            plot_config (dict): The configuration settings for the plot.
            tool: The tool used to generate the plot.

        Returns:
            plotly.graph_objs.Figure: The exported plot.
        """
        if self.results[tool.name] == {}:
            print(f'No results for tool {tool.name} available.')
            plot = None

        elif self.dataset.data_type == DataType.CLASSIFICATION:
            new_results = self.results[tool.name][self.classindex]['result']
            class_name = self.results[tool.name][self.classindex]['class_label']
            name = f"{tool.name} for class {class_name}"
            plot = tool.export_plot(new_results, title=name, plot_config=plot_config)
        else:
            plot = tool.export_plot(self.results[tool.name], plot_config=plot_config)
        plot.update_layout(dict1=layout, overwrite=True)
        return plot


class ImportanceAnalyzer(Analyzer):
    """Analyzer for feature importance analysis.
    """

    def __init__(self, model: Model, dataset: Dataset, tools: Union[List[ImportanceTool], ImportanceTool] = None,
                 **kwargs):
        super().__init__(tool_type=ToolType.IMPORTANCE, model=model, dataset=dataset, tools=tools, **kwargs)


class InteractionAnalyzer(Analyzer):
    """Analyzer for feature interaction analysis.
    """

    def __init__(self, model: Model, dataset: Dataset, tools: Union[List[InteractionTool], InteractionTool] = None,
                 **kwargs):
        super().__init__(tool_type=ToolType.INTERACTION, model=model, dataset=dataset, tools=tools, **kwargs)
