from collections.abc import Iterable
from logging import getLogger

from wowool.common.pipeline.objects import UUID
from wowool.document import Document
from wowool.document.analysis.document import AnalysisDocument
from wowool.document.document_interface import DocumentInterface
from wowool.document.serialize import serialize

from wowool.portal.client.portal import Portal

logger = getLogger(__name__)

PipelineSteps = str | list[str | dict | UUID]


def _parse_analysis_document(analysis_document_raw: dict) -> AnalysisDocument:
    if "mimeType" in analysis_document_raw:
        analysis_document_raw["mime_type"] = analysis_document_raw.pop("mimeType")
    return AnalysisDocument.from_dict(analysis_document_raw)


class Pipeline:
    """
    Pipeline class for processing documents through defined steps.
    """

    def __init__(self, steps: PipelineSteps, portal: Portal | None = None):
        """
        Initializes a Pipeline instance.

        Args:
            steps (PipelineSteps): A list of steps to process the document. Each step can be a string, a dictionary, or a UUID object.
            portal (Portal, optional): Connection to the Portal server.

        Returns:
            Pipeline: An initialized pipeline.
        """
        self._portal = portal or Portal()
        self._steps = steps

    @property
    def steps(self):
        return self._steps

    def process(
        self,
        document: DocumentInterface | str,
        id: str | None = None,
        metadata: dict | None = None,
        **request_kwargs,
    ) -> AnalysisDocument:
        """
        Processes a single document.

        Args:
            document (str|Document|InputProvider): Input document to process. Supports one of the InputProviders.
            id (str|None): The ID to associate with the document. If a file is passed, the file's name is used by default. If a string is passed, a hash of the string is used.
            metadata (dict|None): Additional metadata to associate with the document.
            kwargs: Additional keyword arguments for the requests library.

        Returns:
            Document: An instance of Document is returned.

        Note:
            If the given name does not exist, the Portal will try to generate one
            for you. For example, if the provided name is ``english,sentiment`` it
            will run the English language and ``english-sentiment`` domain.

        """
        input_document = Document(id=id, data=document, metadata=metadata or {}) if isinstance(document, str) else document
        input_document_raw = serialize(input_document)
        analysis_document_raw = self._portal._service.post(
            url="pipelines/process",
            json={
                "pipeline": self.steps,
                "document": input_document_raw,
            },
            **request_kwargs,
        ).json()
        analysis_document = _parse_analysis_document(analysis_document_raw)
        return analysis_document

    def process_batch(self, documents: Iterable[DocumentInterface | str], **request_kwargs) -> list[AnalysisDocument]:
        """
        Processes a batch of documents.

        Args:
            documents (Iterable[str|DocumentInterface]): Input data to process. This includes support for one of the InputProviders.
            **request_kwargs: Additional keyword arguments for the requests library.

        Returns:
            list[AnalysisDocument]: A list of AnalysisDocument instances is returned.
        """
        input_documents = [Document(data=document) if isinstance(document, str) else document for document in documents]
        input_documents_raw = [serialize(doc) for doc in input_documents]
        analysis_documents_raw: list[dict] = self._portal._service.post(
            url="pipelines/process/batch",
            json={
                "pipeline": self.steps,
                "documents": input_documents_raw,
            },
            **request_kwargs,
        ).json()
        analysis_documents = [_parse_analysis_document(analysis_document_raw) for analysis_document_raw in analysis_documents_raw]
        return analysis_documents

    def __call__(
        self,
        document_or_documents: str | DocumentInterface | list[str | DocumentInterface],
        **kwargs,
    ) -> AnalysisDocument | list[AnalysisDocument]:
        """
        Process one or more documents.

        Args:
            document_or_documents (str|DocumentInterface|list[str|DocumentInterface]):
                A single document or a list of documents to process.
            **kwargs: Additional keyword arguments for processing.

        Returns:
            AnalysisDocument|list[AnalysisDocument]: The processed document(s).
        """
        if isinstance(document_or_documents, (str, DocumentInterface)):
            return self.process(document_or_documents, **kwargs)
        return self.process_batch(document_or_documents, **kwargs)

    def __eq__(self, other: object):
        if not isinstance(other, Pipeline):
            return False
        return self.steps == other.steps

    def __repr__(self):
        return f"""Pipeline(steps="{self.steps}")"""
