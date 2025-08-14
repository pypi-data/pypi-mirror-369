from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class BaseParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> dict:
        pass


class MistralOCRParser(BaseParser):
    def __init__(self, result_type: str, **kwargs) -> None:
        from mistralai import Mistral
        name = "MISTRAL-OCR-API-TOKEN"
        api_key = os.getenv(name)
        if not api_key:
            raise EnvironmentError(f"Missing {name} in .env file.")

        self.result_type = "md" if result_type.lower() in ("md", "markdown") else "text"
        self.client = Mistral(api_key=api_key)

    def parse(self, file_path: Path) -> str:
        def upload_pdf(filename):
            uploaded_pdf = self.client.files.upload(
            file={
            "file_name": filename,
                "content": open(filename, "rb"),
            },
            purpose="ocr"
            )
            signed_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)
            return signed_url.url

        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest",
            document={
            "type": "document_url",
            "document_url": upload_pdf(file_path),
            },
            include_image_base64=True,
            )

        return "\n".join(doc.markdown for doc in ocr_response.pages)


class LangChainParser(BaseParser):
    def __init__(self, model_name: str):
        from langchain.llms import OpenAI
        self.model_name = model_name
        self.model = OpenAI(model_name=model_name)

    def parse(self, text: str) -> dict:
        response = self.model(text)
        return {"source": "LangChain", "output": response}


class LlamaParser(BaseParser):
    def __init__(self, result_type: str, mode: bool, **kwargs) -> None:
        from llama_parse import LlamaParse, ResultType
        if result_type.lower() == "md" or result_type.lower() == "markdown":
            self.result_type = ResultType.MD
        name = "LLAMA-PARSER-API-TOKEN"
        self.api_key = os.getenv(name)
        if not self.api_key:
            raise EnvironmentError(f"Missing {name} in .env file.")

        self.parser = LlamaParse(
            api_key=self.api_key,
            result_type=self.result_type,
            premium_mode=mode
        )

    def parse(self, file_path: Path) -> str:
        documents = self.parser.load_data(str(file_path))
        return "\n".join(doc.text for doc in documents)

class HuggingFaceParser(BaseParser):
    def __init__(self, result_type: str, mode: bool, **kwargs) -> None:
        from transformers import pipeline

        if result_type.lower() in ("md", "markdown"):
            self.result_type = "markdown"
        else:
            self.result_type = "text"

        name = "HF-API-TOKEN"
        self.api_key = os.getenv(name)
        if not self.api_key:
            raise EnvironmentError(f"Missing {name} in .env file.")

        # OCR + text extraction pipeline
        # Example model: microsoft/layoutlmv3-base-finetuned-docvqa
        self.parser = pipeline(
            task="document-question-answering",
            model="impira/layoutlm-document-qa",
            use_auth_token=self.api_key
        )

    def parse(self, file_path: Path) -> str:
        import fitz  # PyMuPDF for PDF → images

        pdf_doc = fitz.open(file_path)
        output_parts = []

        for page in pdf_doc:
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            response = self.parser(img_bytes, question="Extract all text")
            if response and "answer" in response[0]:
                output_parts.append(response[0]["answer"])

        if self.result_type == "markdown":
            # Here you could add rules to format into markdown
            return "\n\n".join(output_parts)
        else:
            return " ".join(output_parts)

# === Step 3: Dynamic factory using string input ===
class ParserFactory:
    @staticmethod
    def get_parser(parser_type: str, **kwargs) -> BaseParser:
        provider = parser_type.partition(":")[0].lower()
        model = parser_type.partition(":")[2]
        if provider == "langchain":
            return LangChainParser(model_name=model)
        elif provider == "llamaparser":
            return LlamaParser(**kwargs)
        elif provider == "huggingface":
            return HuggingFaceParser(model_name=model, **kwargs)
        elif provider == "mistralocr":
            return MistralOCRParser(**kwargs)
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")

