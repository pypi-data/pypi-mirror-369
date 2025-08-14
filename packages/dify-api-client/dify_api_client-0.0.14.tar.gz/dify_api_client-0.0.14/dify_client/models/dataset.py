from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# Enums
class IndexModel(str, Enum):
    HIGH_QUALITY = "high_quality"
    ECONOMY = "economy"


class DocForm(str, Enum):
    TEXT_MODEL = "text_model"
    HIERARCHICAL_MODEL = "hierarchical_model"
    QA_MODEL = "qa_model"


class Segment(BaseModel):
    content: str
    answer: Optional[str] = None
    keywords: Optional[List[str]] = None


class AddChunkToDocumentRequest(BaseModel):
    segments: List[Segment]


class AddChunkToDocumentResponseDataItem(BaseModel):
    id: str
    position: int
    document_id: str
    content: str
    answer: Optional[str] = None
    word_count: int
    tokens: int
    keywords: List[str]
    index_node_id: str
    index_node_hash: str
    hit_count: int
    enabled: bool
    disabled_at: Optional[int] = None
    disabled_by: Optional[str] = None
    status: str
    created_by: str
    created_at: int
    indexing_at: int
    completed_at: int
    error: Optional[str] = None
    stopped_at: Optional[int] = None


class AddChunkToDocumentResponse(BaseModel):
    data: List[AddChunkToDocumentResponseDataItem]
    doc_form: str


# Create Document from Text models
class ProcessRule(BaseModel):
    mode: str  # "automatic" or "custom"
    rules: dict = Field(default={})
    pre_processing_rules: List[dict] = Field(default=[])
    segmentation: dict = Field(default={})
    subchunk_segmentation: dict = Field(default={})
    parent_mode: str = Field(default="full-doc")


class SegmentationMode(str, Enum):
    AUTOMATIC = "automatic"
    CUSTOM = "custom"


class Rule(BaseModel):
    pre_processing_rules: Optional[List[dict]] = None
    segmentation: Optional[dict] = None
    parent_mode: Optional[str] = None
    subchunk_segmentation: Optional[dict] = None


class RetrievalModel(BaseModel):
    search_method: (
        str  # "hybrid_search", "semantic_search", "full_text_search"
    ) = Field(default="hybrid_search")
    reranking_enable: Optional[bool] = Field(default=False)
    reranking_mode: str = Field(default="")
    top_k: int = Field(default=3)
    score_threshold_enabled: bool = Field(default=False)
    score_threshold: float = Field(default=0.0)


class BaseCreateDocumentRequest(BaseModel):
    """
    Represents the base configuration for creating a document.
    """

    indexing_technique: str  # "high_quality" or "economy"
    doc_form: Optional[str] = (
        None  # "text_model", "hierarchical_model", "qa_model"
    )
    doc_language: str = Field(default="English")
    process_rule: ProcessRule
    retrieval_model: RetrievalModel = Field(default=RetrievalModel())
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_model_provider: str = Field(default="openai")


class CreateDocumentByTextRequest(BaseCreateDocumentRequest):
    name: str
    text: str


class DataSourceInfo(BaseModel):
    upload_file_id: str


class DocumentBaseData(BaseModel):
    """
    {
      "id": "",
      "position": 1,
      "data_source_type": "file_upload",
      "data_source_info": null,
      "dataset_process_rule_id": null,
      "name": "dify",
      "created_from": "",
      "created_by": "",
      "created_at": 1681623639,
      "tokens": 0,
      "indexing_status": "waiting",
      "error": null,
      "enabled": true,
      "disabled_at": null,
      "disabled_by": null,
      "archived": false
    },
    """

    id: str
    position: int
    data_source_type: str
    data_source_info: Optional[dict] = None
    dataset_process_rule_id: Optional[str] = None
    name: str
    created_from: str
    created_by: str
    created_at: int
    tokens: int
    indexing_status: str
    error: Optional[str] = None
    enabled: bool
    disabled_at: Optional[int] = None
    disabled_by: Optional[str] = None
    archived: bool


class DocumentData(DocumentBaseData):
    display_status: str
    word_count: int
    hit_count: int
    doc_form: str


class CreateDocumentByTextResponse(BaseModel):
    document: DocumentData
    batch: str


class GetDocumentsResponse(BaseModel):
    """
    "has_more": false,
    "limit": 20,
    "total": 9,
    "page": 1
    """

    data: List[DocumentData]
    has_more: bool
    limit: int
    total: int
    page: int


# Metadata
class DocumentMetadataBase(BaseModel):
    id: str
    name: str


class DocumentMetadataUpdate(DocumentMetadataBase):
    value: str


class DocumentMetadataGet(DocumentMetadataBase):
    type: str
    count: int


class DocumentMetadataOperationData(BaseModel):
    document_id: str
    metadata_list: List[DocumentMetadataUpdate]


class UpdateDocumentMetadataRequest(BaseModel):
    operation_data: List[DocumentMetadataOperationData]


class GetMetadataListResponse(BaseModel):
    doc_metadata: List[DocumentMetadataGet]
    built_in_field_enabled: bool


class CreateDocumentMetadataRequest(BaseModel):
    """
    type: string / number / time
    """

    type: str
    name: str


class CreateDocumentMetadataResponse(BaseModel):
    id: str
    type: str
    name: str


class CreateDocumentByFileRequest(BaseCreateDocumentRequest):
    """
    Represents the configuration for creating a document by file upload. This will be serialized to JSON and sent as the 'data' field in multipart/form-data.
    """

    original_document_id: Optional[str] = None


class CreateDocumentByFileResponse(CreateDocumentByTextResponse):
    pass
