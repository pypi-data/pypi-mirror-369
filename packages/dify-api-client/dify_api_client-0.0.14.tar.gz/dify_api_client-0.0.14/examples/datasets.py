# Add chunks to a document
# pip install dify-api-client==0.0.5
import os

import dotenv

from dify_client import DifyClient, models

dotenv.load_dotenv()

DIFY_API_BASE = os.getenv("DIFY_API_BASE")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")


client = DifyClient(
    api_key=DIFY_API_KEY,
    api_base=DIFY_API_BASE,
    verify_ssl=False,
    follow_redirects=True,
)


def add_chunk_to_document():
    response = client.add_chunk_to_document(
        dataset_id="894f6555-f3a6-43a0-9891-579cd64beaa8",
        document_id="ef510e1a-41a7-4c15-99a2-34949412cba4",
        req=models.AddChunkToDocumentRequest(
            segments=[
                models.Segment(
                    content="Hello, world!",
                    answer="Hello, world!",
                    keywords=["hello", "world"],
                )
            ]
        ),
    )

    print(response)


def create_document_by_text():
    rules = models.Rule(
        pre_processing_rules=[
            {
                "id": "remove_extra_spaces",
                "enabled": True,
                "type": "remove_urls_emails",
                "params": True,
            }
        ],
        segmentation={
            "separator": "\n",
            "max_tokens": 10000,
        },
        parent_mode="full-doc",
        subchunk_segmentation={
            "separator": "sentence",
            "max_tokens": 10000,
            "chunk_overlap": 0,
        },
    )
    request = models.CreateDocumentByTextRequest(
        name="test_document",
        text="This is a test document content for the knowledge base.",
        indexing_technique=models.IndexModel.ECONOMY.value,
        doc_form=models.DocForm.TEXT_MODEL.value,
        process_rule=models.ProcessRule(
            mode=models.SegmentationMode.AUTOMATIC.value,
            rules=rules.model_dump(),
        ),
    )
    print(request.model_dump())
    response = client.create_document_by_text(
        dataset_id="894f6555-f3a6-43a0-9891-579cd64beaa8",
        req=request,
    )
    print(response)


def create_document_by_file():
    rules = models.Rule(
        pre_processing_rules=[
            {
                "id": "remove_extra_spaces",
                "enabled": True,
                "type": "remove_urls_emails",
                "params": True,
            }
        ],
        segmentation={
            "separator": "\n\n",
            "max_tokens": 1024,
        },
        parent_mode="full-doc",
        subchunk_segmentation={
            "separator": "sentence",
            "max_tokens": 1024,
            "chunk_overlap": 50,
        },
    )
    request = models.CreateDocumentByFileRequest(
        indexing_technique=models.IndexModel.HIGH_QUALITY.value,
        doc_form=models.DocForm.TEXT_MODEL.value,
        process_rule=models.ProcessRule(
            mode=models.SegmentationMode.CUSTOM.value,
            rules=rules.model_dump(),
        ),
    )
    print(request.model_dump())
    file_path = "data/expo_presentation_iori.jp.txt"
    response = client.create_document_by_file(
        dataset_id="97937f3c-f2c6-4c4b-b266-f1b22a509b4e",
        req=request,
        file=file_path,
    )
    print(response)


def get_documents():
    response = client.get_documents(
        dataset_id="894f6555-f3a6-43a0-9891-579cd64beaa8",
    )
    print(response)


def get_metadata_list():
    response = client.get_metadata_list(
        dataset_id="894f6555-f3a6-43a0-9891-579cd64beaa8",
    )
    print(response)


def update_document_metadata():
    response = client.update_document_metadata(
        dataset_id="894f6555-f3a6-43a0-9891-579cd64beaa8",
        req=models.UpdateDocumentMetadataRequest(
            operation_data=[
                models.DocumentMetadataOperationData(
                    document_id="ab737df7-619c-4859-96db-4e3254455b62",
                    metadata_list=[
                        models.DocumentMetadataUpdate(
                            id="8f6e86d4-0cbb-4ad8-8e79-e7c0ac188cce",
                            name="language_code",
                            value="en",
                        ),
                    ],
                ),
            ]
        ),
    )
    print(response)


def create_document_metadata():
    response = client.create_document_metadata(
        dataset_id="565c440e-eaf8-49bf-8d98-003d8eb9ddba",
        req=models.CreateDocumentMetadataRequest(
            name="language_code",
            type="string",
        ),
    )
    print(response)


if __name__ == "__main__":
    # add_chunk_to_document()
    # create_document_by_text()
    # get_documents()
    # get_metadata_list()
    # update_document_metadata()
    # create_document_metadata()
    create_document_by_file()
