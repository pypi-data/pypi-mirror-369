import json
import sys
import wowool.package.lib.wowool_sdk as cpp
from wowool.document.document_interface import DocumentInterface, MT_PLAINTEXT, MT_ANALYSIS_JSON
from wowool.document.analysis.document import AnalysisDocument
from wowool.document.analysis.text_analysis import AnalysisInputProvider
from wowool.document import Document
from wowool.document.analysis.text_analysis import TextAnalysis
from wowool.error import Error
from pathlib import Path
from wowool.document.analysis.text_analysis import APP_ID as APP_ID_WOWOOL_ANALYSIS
from typing import Optional
from wowool.native.core.engine import Engine, Component
from wowool.io.provider.str import StrInputProvider


def _escape_windows_paths(path):
    full_path = Path(path).resolve()
    if full_path.exists():
        path_str = json.JSONEncoder().encode(str(Path(path).resolve()))[1:-1]
        return path_str
    else:
        return path


def dict_implements_protocol(d: dict, protocol: type) -> bool:
    return all(callable(d.get(attr)) for attr in protocol.__annotations__)


def get_cpp_analysis_result(analysis_json: dict):
    if analysis := analysis_json.get(APP_ID_WOWOOL_ANALYSIS, None):
        if results := analysis.get("results", None):
            return results
    # backwards compatibility for older analysis JSON structures
    if apps := analysis_json.get("apps", None):
        if analysis := apps.get(APP_ID_WOWOOL_ANALYSIS, None):
            if results := analysis.get("results", None):
                return results


class Language(Component):
    """Language is a class ia a callable object that processes an input text

    The class returns an AnalysisDocument containing the results of the analysis.

    Args:
        name (str): The language of the language to create, default 'auto'
        engine (Engine): Passing a separated engine object.

    Examples:
        ```python
        from wowool.sdk import Language
        analyzer = Language("english")
        document = analyzer("some text")
        ```
    """

    ID = APP_ID_WOWOOL_ANALYSIS

    DOCUMENT_ID = "id"
    INPUT_TYPE = "input_type"
    ROOT_PATH = "root_path"
    ENGINE = "engine"

    def __init__(
        self,
        name: str,
        anaphora: Optional[bool] = True,
        disambiguate: bool = True,
        hmm: bool = True,
        unicode_offsets: bool = True,
        dbg: Optional[str] = "",
        initial_date: Optional[str] = None,
        sentyziser: str = "",
        engine: Optional[Engine] = None,  # note: we need to keep it at the back, for the app initialization process.
        **kwargs,
    ):
        """Initialize a Language component.

        Args:
            name (str): The language name or path to a .language file.
            anaphora (Optional[bool]): Whether to enable anaphora resolution. Defaults to True.
            disambiguate (bool): Whether to enable disambiguation. Defaults to True.
            hmm (bool): Whether to enable Hidden Markov Model. Defaults to True.
            unicode_offsets (bool): Whether to use unicode offsets. Defaults to True.
            dbg (Optional[str]): Debug information string. Defaults to "".
            initial_date (Optional[str]): Initial date for temporal processing.
            sentyziser (str): Sentyziser configuration string to control the max number of cr in one sentence. Defaults to "".
            engine (Optional[Engine]): Engine instance to use.
            **kwargs: Additional options to pass to the language component.
        """
        super(Language, self).__init__(engine)
        self.options = {}
        self.options["language"] = name
        self._name = name
        fn = Path(name)
        if fn.exists() and fn.suffix == ".language":
            self._name = fn.stem

        self.options["anaphora"] = anaphora
        self.options["dbg"] = dbg
        self.options["hmm"] = hmm
        self.options["disambiguate"] = disambiguate
        self.options["unicode_offset"] = unicode_offsets
        if sentyziser:
            self.options["sentyziser"] = sentyziser
        self.options["pytryoshka"] = "true"
        self.options["resolve_formated_attribute_function"] = "::python::wowool.plugin::resolve_formated_attribute"
        if initial_date:
            self.options["initial_date"] = initial_date

        if kwargs:
            for key, value in kwargs.items():
                self.options[key] = value

        try:
            self._cpp = cpp.analyzer(self.engine._cpp, self.options)
            del self.options["pytryoshka"]
            del self.options["resolve_formated_attribute_function"]
            if Language.ENGINE in self.options:
                del self.options[Language.ENGINE]

        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(sys.exc_info()[2])

    def __call__(self, document: DocumentInterface | str, **kwargs) -> AnalysisDocument:
        """Process input data through this language analyzer.

        This object is callable, which means you can pass the input data to the given analyzer.

        Args:
            document (DocumentInterface|str): Input data, which can be a str, InputProvider,
                Document, or a wowool.io.input_providers.InputProvider or a
                wowool.document.Document object.
            **kwargs: Additional keyword arguments to pass to the analyzer.

        Returns:
            AnalysisDocument: A document containing the annotation of the given document.

        Examples:
            ```python
            from wowool.sdk import Language
            analyzer = Language("english")
            document = analyzer("some text")
            ```

            Or with a Document object:

            ```python
            from wowool.document import Document
            for ip in Document.glob('corpus', "**/*.txt"):
                document = analyzer(ip)
            ```
        """
        return self.annotate(document, **kwargs)

    def process(self, document: DocumentInterface | str, **kwargs) -> AnalysisDocument:
        """Process a document and return a json object.

        Args:
            document (DocumentInterface|str): Input data, which can be a Document or str.
            **kwargs: Additional keyword arguments to pass to the processor.

        Returns:
            str: A json str containing the representation of the given document.
        """
        if isinstance(document, str):
            input_document = StrInputProvider(document)
            analysis_document = AnalysisDocument(input_document)
        elif isinstance(document, Document):
            analysis_document = AnalysisDocument(document)
        elif isinstance(document, AnalysisDocument):
            analysis_document = document
        else:
            raise TypeError("The document should be a str, DocumentInterface or AnalysisDocument.")

        local_options = {**kwargs}
        if "id" not in local_options:
            local_options["id"] = analysis_document.id

        try:
            return self._cpp.process(analysis_document.input_document.data, local_options)
        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(sys.exc_info()[2])

    def annotate(self, document: str | DocumentInterface, **kwargs) -> AnalysisDocument:
        """Annotate a document with linguistic analysis.

        Args:
            document (str|DocumentInterface): A wowool.document.Document object or string.
            **kwargs: Additional keyword arguments to pass to the annotator.

        Returns:
            AnalysisDocument: A document containing the annotation of the given document.
        """
        try:
            input_document = document
            if isinstance(document, str):
                input_document = StrInputProvider(document)
                analysis_document_ = AnalysisDocument(StrInputProvider(document))
            elif isinstance(document, AnalysisDocument):
                analysis_document_ = document
            elif isinstance(document, DocumentInterface):
                analysis_document_ = AnalysisDocument(document)
            else:
                raise TypeError("The document should be a str, DocumentInterface or AnalysisDocument.")

            local_options = {**kwargs, **analysis_document_.metadata}
            doc_id = analysis_document_.id

            if analysis_document_.has(APP_ID_WOWOOL_ANALYSIS):
                analysis = analysis_document_.results(APP_ID_WOWOOL_ANALYSIS)

                if not isinstance(analysis, dict) and analysis._cpp is not None:
                    cpp_analysis_result = analysis._cpp
                    if isinstance(cpp_analysis_result, cpp.results):
                        analysis_document_.add_results(
                            app_id=self.ID, results=TextAnalysis(self._cpp.process_document(cpp_analysis_result, local_options))
                        )
                elif isinstance(analysis, TextAnalysis):
                    local_options["input_type"] = "json"
                    json_str = analysis.to_json_data()
                    analysis_document_.add_results(
                        app_id=self.ID, results=TextAnalysis(self._cpp.process_results(json_str, local_options), doc_id)
                    )
                elif isinstance(analysis, dict):
                    local_options["input_type"] = "json"
                    json_str = json.dumps(analysis)
                    analysis_document_.add_results(
                        app_id=self.ID, results=TextAnalysis(self._cpp.process_results(json_str, local_options), doc_id)
                    )
                else:
                    raise ValueError("No native result object in analysis.")
            else:
                assert not isinstance(input_document, str)
                if input_document.mime_type == AnalysisInputProvider.MIME_TYPE:
                    # analysis = input_document.data
                    cpp_analysis_result = get_cpp_analysis_result(input_document.data)
                    if cpp_analysis_result:
                        local_options["input_type"] = "json"
                        json_str = json.dumps(cpp_analysis_result)
                        analysis_document_.add_results(
                            app_id=self.ID, results=TextAnalysis(self._cpp.process_results(json_str, local_options), doc_id)
                        )
                    # this can happen in case of lid, where the input_document is already MT_ANALYSIS_JSON but has not been processed
                    # by the cpp Engine and therefore has no APP_ID_WOWOOL_ANALYSIS
                    elif analysis_document_.input_document and analysis_document_.input_document.mime_type == MT_PLAINTEXT:
                        analysis_document_.add_results(
                            app_id=self.ID,
                            results=TextAnalysis(self._cpp.process_results(analysis_document_.input_document.data, local_options), doc_id),
                        )
                    else:
                        raise TypeError(f"No valid input data type. [{MT_PLAINTEXT}, {MT_ANALYSIS_JSON}]")

                elif input_document.mime_type == MT_PLAINTEXT:
                    analysis_document_.add_results(
                        app_id=self.ID, results=TextAnalysis(self._cpp.process_results(input_document.data, local_options), doc_id)
                    )
                else:
                    raise TypeError(
                        f"No valid input data type. got '{input_document.mime_type}' but only accepts [{MT_PLAINTEXT}, {MT_ANALYSIS_JSON}]"
                    )

            return analysis_document_

        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(sys.exc_info()[2])

    def __str__(self):
        """Return string representation of the Language object.

        Returns:
            str: String representation showing options.
        """
        return f"<wowool.native.core.Language {self.options} >"

    @property
    def filename(self):
        """Get the filename of the language component.

        Returns:
            str: The filename of the language component.
        """
        return self._cpp.filename()

    @property
    def name(self):
        """Get the name of the language.

        Returns:
            str: The language name.
        """
        return self._name

    @property
    def language(self):
        """Get the language identifier.

        Returns:
            str: The language identifier.
        """
        return self._name
