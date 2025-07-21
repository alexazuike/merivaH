import io, os, base64
from enum import Enum
from typing import List, Optional
import tempfile

import shutil
import pandas
import pdfkit
from django.conf import settings
from django.template.loader import render_to_string

from api.includes import utils
from .pdf_generator import PDFGenerator

from pydantic import BaseModel


class ExcelFileContent(BaseModel):
    headers: List[str] = []
    body: List[dict] = []


class SheetRecord(BaseModel):
    sheet_name: str
    data: List[dict]


class StaticFolderType(str, Enum):
    PATIENT = "PATIENT"

    def __str__(self):
        return self.value


class FileUtils:
    """class  is responsible for any read/write file operations
    For example: save file, convert html-pdf etc
    """

    def __init__(self):
        self.LOGO_PATH = f"{settings.STATIC_ROOT}/logo/logo.png"

    def read_header(self) -> Optional[str]:
        """Reads lab header html file"""
        logo = self.get_logo_base_64()
        if not logo:
            return None
        data = {"logo": self.get_logo_base_64(), "company": utils.get_company_data()}
        html_content = render_to_string("header.html", data)
        return html_content

    def _get_pdf_kit_options(self, header_html: str = None):
        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            # 'header-html': header_html
        }
        if header_html:
            header = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
            header_html_bytes = bytes(header_html, "utf-8")
            header.write(header_html_bytes)
            header.flush()
            options["header-html"] = header.name
            return options, header
        return options, None

    def convert_html_to_pdf(self, html_content: str, header_html: str = None):
        """Gets html content and file name and convert to html

        Args:
            html_content [str]: html string content

        Returns:
            str: relative file path of the generated pdf content
        """
        options, header = self._get_pdf_kit_options(header_html)
        print(options)
        pdf_file_blob = pdfkit.from_string(html_content, verbose=True, options=options)
        if header_html:
            print(os.path.exists(header.name))
            os.remove(options["header-html"])
            print(os.path.exists(header.name))
        if header:
            header.close()
        if pdf_file_blob:
            return pdf_file_blob
        raise IOError("pdf failed to create")
        # return PDFGenerator(html_content).generate_pdf()

    def get_logo_base_64(self) -> Optional[str]:
        """Gets logo and converts image to base 64"""
        try:
            with open(self.LOGO_PATH, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read())
                b64_string = b64_string.decode("utf-8")
                b64_string = f"data:image/png;base64,{b64_string}"
                return b64_string
        except FileNotFoundError:
            return None

    def read_excel_file(self, file_path: str) -> ExcelFileContent:
        """Reads excel file and returns dataframe

        Args:
            file_path [str]: excel file path

        Returns:
            pandas.DataFrame: excel dataframe
        """
        try:
            excel_file = pandas.read_excel(file_path)
            columns: pandas.Index = excel_file.columns
            headers = [column.title() for column in columns]
            body = excel_file.to_dict(orient="records")
            return ExcelFileContent(headers=headers, body=body)
        except ValueError as e:
            raise e

    def write_excel_file(self, data: List[dict]):
        """Writes excel file

        Args:
            data [List]: list of dictionaries of records

        Returns:
            bytes: excel file content
        """
        dataframe = pandas.DataFrame(data)
        excel_file = io.BytesIO()
        dataframe.to_excel(excel_file, index=False)
        excel_file.seek(0)
        return excel_file

    def write_multiple_sheets(self, *data: SheetRecord):
        """Writes multiple sheets to one excel file

        Returns:
            bytes: excel file content
        """
        excel_file = io.BytesIO()
        writer = pandas.ExcelWriter(excel_file, engine="openpyxl")
        dataframes = [
            (pandas.DataFrame(sheet.data), sheet.sheet_name) for sheet in data
        ]
        excel_sheets = [
            frame[0].to_excel(writer, sheet_name=frame[1]) for frame in dataframes
        ]
        writer.save()
        excel_file.seek(0)
        return excel_file

    def upload_static_file(
        self,
        folder_type: StaticFolderType,
        folder_id: str,
        file_name: str,
        content: io.BytesIO,
        document_type: str = None,
    ):
        """Uploads a file

        Args:
            path [str]: path to store the file
            file_name [str]: name of file to upload

        Return:
            [str]: uploaded_file_path
        """
        static_path = settings.STATIC_ROOT
        folder_dir = os.path.join(static_path, str(folder_type))

        # check if patients dir exist
        if not os.path.isdir(folder_dir):
            os.mkdir(folder_dir)

        content_dir = os.path.join(folder_dir, folder_id)

        # check if patient has directory for him
        if not os.path.isdir(content_dir):
            os.mkdir(content_dir)

        if document_type:
            content_dir = os.path.join(content_dir, document_type)
            if not os.path.isdir(content_dir):
                os.mkdir(content_dir)

        file_path = os.path.join(content_dir, file_name)
        with open(file_path, "wb") as file:
            file.write(content)

        if document_type:
            return os.path.join(
                settings.STATIC_URL,
                str(folder_type),
                str(folder_id),
                document_type,
                file_name,
            )
        return os.path.join(
            settings.STATIC_URL, str(folder_type), str(folder_id), file_name
        )

    def get_static_file(self, file_path: str) -> io.BytesIO:
        """Gets a static file bytes

        Args:
            file_path[str]: path of the file

        Return:
            [io.BytesIO]: bytes of the file

        Raises:
            FileNotFoundError:
        """
        file_path = os.path.join(settings.STATIC_ROOT, file_path)
        with open(file_path, "rb") as file:
            return file.read()

    def remove_static_file(self, file_path: str):
        """Gets a static file bytes

        Args:
            file_path[str]: path of the file

        Raises:
            FIleNotFoundError: when file doesb't exist
        """
        file_path = os.path.join(settings.STATIC_ROOT, file_path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError("File does not exist")
        os.remove(file_path)
        return None

    def remove_static_dir(self, folder_type: StaticFolderType, folder_id: str):
        """Deletes a static directory with file content

        Args:
            Removes a static directory

        Raises:
            FileNotFoundError: when directory doesn't exist
        """
        static_path = settings.STATIC_ROOT
        folder_dir = os.path.join(static_path, str(folder_type), folder_id)
        if not os.path.isdir(folder_dir):
            raise FileNotFoundError("Directory does not exist")
        shutil.rmtree(folder_dir, ignore_errors=True, onerror=None)
        return None
