import json
from hashlib import sha256
from pathlib import Path
from typing import List, Optional, Union

from wowool.common.pipeline.objects import ComponentInfo
from wowool.document import Document, DocumentInterface
from wowool.document.analysis.document import AnalysisDocument

from wowool.native.core import Domain, Language
from wowool.native.core.engine import Component, Engine
from wowool.native.core.pipeline_exceptions import EXCEPTION_ARGUMENT_VALUE_ERROR, ComponentError
from wowool.native.core.pipeline_resolver import ComponentConverter, convert_pipeline_info, resolve


def convert_component_info(obj, **kwargs):
    if isinstance(obj, ComponentInfo):
        return obj.to_json()
    elif isinstance(obj, Engine):
        return None
    return obj


def create_components(pipeline_info: list[dict], **kwargs) -> list[dict]:
    components = []
    for component in pipeline_info:
        if component["type"] == "language":
            components.append(Language(component["filename"], **component["options"], **kwargs))
        elif component["type"] == "domain":
            components.append(Domain(component["filename"], **component["options"]))
        elif component["type"] == "app":
            import importlib

            if "app" in component:
                class_name = component["app"]["class"]
                module_name = component["app"]["module"]
            else:
                class_name = component["name"]
                module_name = component["namespace"]

            try:
                mod = importlib.import_module(module_name)
                cls = getattr(mod, class_name)
                components.append(cls(**component["options"]))
            except Exception as ex:
                raise ComponentError(
                    f"""Pipeline Error: could not load application component name: {component["name"]}, {ex}""",
                    EXCEPTION_ARGUMENT_VALUE_ERROR,
                    component["name"],
                )
        else:
            raise ValueError(f"Pipeline Error: Invalid component name: {components}")
    return components


def get_lxware_path(engine: Engine) -> list[Path]:
    info = engine.info()
    return [info["options"]["lxware"]] if "options" in info and "lxware" in info["options"] else []


class Pipeline(Component):
    """A wrapper object to quickly create an analysis pipeline.

    The components to pass to the pipeline are the language followed by the domains with or
    without the language affix. For instance, if we want to run English with english_entity
    and english_sentiment, we will pass (english,english-entity,english-sentiment) or
    (english,entity,sentiment).

    Examples:
        'english,entity' will load the English language modules and the English entities.

        ```python
        from wowool.sdk import PipeLine
        from wowool.document import Document
        document = Document("Mark Janssens works at Omega Pharma.")
        # Create an analyzer for a given language and options
        process = Pipeline("english,entity")
        # Process the data
        document = process(document)
        print(document)
        ```
    """

    @staticmethod
    def expand(
        pipeline: str,
        paths: list[str] | list[Path] = [],
        file_access: bool = True,
        language: str = "",
        engine: Optional[Engine] = None,
        ignore_on_error: bool = False,
        allow_dev_version: bool = True,
    ):
        """Expand a pipeline string into component information.

        Args:
            pipeline (str): A comma-separated list of components to expand.
            paths (list[str]|list[Path]): The paths where to find the components.
            file_access (bool): Whether to allow file system access.
            language (str): The language to use for component resolution.
            engine (Optional[Engine]): The engine instance to use.
            ignore_on_error (bool): Whether to ignore errors during expansion.
            allow_dev_version (bool): Whether to allow development versions.

        Returns:
            list: The expanded pipeline component information.
        """
        retval = resolve(pipeline, paths, file_access, language, engine, ignore_on_error, allow_dev_version)
        return retval

    def __init__(
        self,
        pipeline: str | list = "",
        engine: Engine | None = None,
        paths: list[str] | list[Path] | None = None,
        language: str = "",
        ignore_on_error=False,
        allow_dev_version=True,
        pipeline_components: list[dict] | None = None,
        option_create_components: bool = True,
        file_access: bool = True,
        use_initial_language: bool = True,
        allow_dev_versions: bool = True,
        **kwargs,
    ):
        """Create a pipeline object.

        Args:
            pipeline (str|list): A comma separated list of components (Languages,Domains and Apps)
                to create. ex: english,entity
                When given as a list, the item should be a string representing the component name,
                or a dictionary with the fields: name and options. See example below.
            engine (Engine|None): The engine that will be passed to the different components.
            paths (list[str]|list[Path]|None): The paths where to find the component.
            language (str): The language to use for component resolution.
            ignore_on_error (bool): Whether to ignore errors during pipeline creation.
            pipeline_components (list[dict]|None): Pre-built pipeline components to use.
            option_create_components (bool): Whether to create components during initialization.
            file_access (bool): Whether to allow file system access.
            use_initial_language (bool): Whether to use the initial language setting.
            kwargs: Additional options that will be passed to the components.

        Examples:

            ```python
            from wowool.sdk import Pipeline

            process = Pipeline("english,entity")
            document = process("Mark Janssens works at Omega Pharma.")
            ```

            But you can also pass a list of components like this:

            ```python
            from wowool.sdk import Pipeline
            from wowool.common.pipeline import UUID
            process = Pipeline(
                [
                    UUID("english", options = {"anaphora": False}),
                    UUID("entity"),
                    UUID("topics.app", {"count": 3})
                ]
            )
            document = process("Mark Janssens works at Omega Pharma.")
            ```

        """
        super(Pipeline, self).__init__(engine)
        self.pipeline_component_info_dict = []
        if not (isinstance(pipeline, str) or isinstance(pipeline, list)):
            raise ValueError("Pipeline Error: Invalid pipeline type: supports a string or a list of components")

        if pipeline_components:
            # we already have the pipeline components, we just need to load them.
            component_options = kwargs
            self.pipeline_component_info_dict = pipeline_components
            components = create_components(pipeline_components, **component_options)

            self._components = components
        else:

            if pipeline:
                paths_ = paths if paths else get_lxware_path(self.engine)
                component_options = kwargs
                if isinstance(pipeline, list):
                    # pipeline is a list of components
                    converter = ComponentConverter(
                        paths_, file_access, ignore_on_error, allow_dev_versions, use_initial_language, language, self.engine
                    )
                    self.pipeline_component_info_dict = converter(pipeline)

                elif pipeline:
                    # pipeline is a string
                    self.pipeline_component_info_dict = resolve(
                        pipeline,
                        paths_,
                        True,
                        language,
                        self.engine,
                        ignore_on_error,
                        allow_dev_version,
                    )

                if len(self.pipeline_component_info_dict) > 0 and self.pipeline_component_info_dict[0]["type"] == "domain":
                    # If the first component is a domain, we need to insert a Language component at the beginning
                    generic_pipeline = resolve(
                        "generic",
                        paths_,
                        True,
                        language,
                        self.engine,
                        ignore_on_error,
                        allow_dev_version,
                    )

                    self.pipeline_component_info_dict.insert(0, generic_pipeline[0])

                self.pipeline_component_info = convert_pipeline_info(self.pipeline_component_info_dict)

                if option_create_components:

                    components = create_components(self.pipeline_component_info_dict, **component_options)
                    self._components = components
            else:
                self.pipeline_component_info_dict = "(empty)"
                self.pipeline_component_info = []
                self._components = []

    def __call__(self, document: str | DocumentInterface, id=None, **kwargs) -> AnalysisDocument:
        """Process a document through the pipeline.

        Args:
            document (str|DocumentInterface): The document data to process.
            id (str|None): The ID of the document data. This is only used when the document is a str.
            kwargs: Additional arguments to pass to components.

        Returns:
            AnalysisDocument: A processed document object.

        Raises:
            TypeError: If a component is not callable or if the pipeline doesn't return an
                AnalysisDocument.
        """
        if isinstance(document, str):
            ret_document = Document(document, id)
        elif isinstance(document, DocumentInterface):
            ret_document = document
        else:
            ret_document = document

        for component in self._components:
            if not callable(component):
                raise TypeError(f"Component {component} is not callable (type: {type(component)})")

            if isinstance(component, Language) or isinstance(component, Domain):
                ret_document = component(ret_document, **kwargs)
            else:
                # print(f"Running component {component}")
                ret_document = component(ret_document)

        # Ensure the return type is AnalysisDocument
        if not isinstance(ret_document, AnalysisDocument):
            raise TypeError(f"Pipeline did not return an AnalysisDocument, got {type(ret_document)}")

        return ret_document

    @property
    def components_info(self) -> list[ComponentInfo]:
        """Return a list of the component information.

        Returns:
            list[ComponentInfo]: List of component information dictionaries.
        """
        return self.pipeline_component_info

    @property
    def components(self) -> list:
        """Return a list of the component objects.

        Returns:
            list: List of component objects.
        """
        return self._components

    @property
    def domains(self) -> list:
        """Return a list of domain components.

        Returns:
            list: List of Domain component objects.
        """
        return [component for component in self._components if isinstance(component, Domain)]

    @property
    def concepts(self) -> list[str]:
        """Return a list of all entities (concepts) from all components.

        Returns:
            list[str]: List of entity URIs.
        """
        concepts = set()

        for comp in self._components:
            if hasattr(comp, "concepts"):
                concepts |= set(comp.concepts)
        return list(concepts)

    @property
    def language(self) -> str:
        """Return the language of the first Language object.

        Returns:
            str: Language code or empty string if no Language component found.
        """
        if len(self._components) >= 1 and isinstance(self._components[0], Language):
            return self._components[0].language
        return ""

    def __rep__(self):
        print(f"<Pipeline {self.pipeline_component_info_dict}>")

    def __str__(self) -> str:
        """Return string representation of the pipeline.

        Returns:
            str: String representation showing language and components.
        """
        from io import StringIO

        with StringIO() as output:
            output.write("[ ")
            output.write(f"""{self.language}""")
            for component in self._components:
                output.write(f""", {component}""")
            output.write(" ]")
            return output.getvalue()

    @property
    def uid(self):
        """Return a unique identifier for this pipeline configuration.

        Returns:
            str: SHA-256 hash of the pipeline configuration.
        """
        if hasattr(self, "uid_"):
            return self.uid_
        pipeline_string = json.dumps(self.pipeline_component_info, sort_keys=True, default=convert_component_info).encode("utf-8")
        # Create a SHA-256 hash object
        hash_object = sha256(pipeline_string)
        # Get the hexadecimal representation of the hash
        self.uid_ = hash_object.hexdigest()
        return self.uid_

    def to_json(self) -> dict:
        """Convert the pipeline to a JSON-serializable dictionary.

        Returns:
            dict: JSON representation of the pipeline configuration.
        """
        retval: List[ComponentInfo] = self.pipeline_component_info
        for component in retval:
            component.options.pop("engine", None)  # Remove engine from options if present
            component.filename = None

        pipeline_string = json.dumps(retval, sort_keys=True, default=convert_component_info)
        return json.loads(pipeline_string)


PipeLine = Pipeline
