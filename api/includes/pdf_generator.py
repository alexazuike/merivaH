import asyncio
from io import BytesIO
from typing import Union

from django.template import Context
from django.template import Template
from pyppeteer import launch

_DEFAULT_VIEWPORT_WIDTH = 1620
_DEFAULT_VIEWPORT_HEIGHT = 1080

_DEFAULT_HEADER_TEMPLATE = ""
_DEFAULT_FOOTER_TEMPLATE = ""


class PDFGenerator:
    """
    Generates Portable Document File (PDF) for a page using the page's HTML string.
    Generates PNG file for images for a age using a page's HTML string
    """

    def __init__(
        self,
        html_string: str,
        viewport_width=_DEFAULT_VIEWPORT_WIDTH,
        viewport_height=_DEFAULT_VIEWPORT_HEIGHT,
        **pdf_options
    ):
        """
        Parameters
        :param template: The HTML string of Django template object
        :param context: A Django render context instance that will be used to render the template
        :param viewport_width: Width of the viewport that the page will be rendered
        :param viewport_height: Height of the viewport that the page will be rendered
        :param pdf_options: Extra pdf generation options that will be passed to pyppeteer pdf generation API
        """
        self.html_string = html_string
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.pdf_options = pdf_options
        self.pdf_options.setdefault("format", "A4")
        self.pdf_options.setdefault("displayHeaderFooter", True)
        self.pdf_options.setdefault("printBackground", False)
        self.pdf_options.setdefault("landscape", False)
        self.pdf_options.setdefault("headerTemplate", _DEFAULT_HEADER_TEMPLATE)
        self.pdf_options.setdefault("footerTemplate", _DEFAULT_FOOTER_TEMPLATE)
        # self.pdf_options.setdefault(
        #     "margin ",
        #     {
        #         "top": "60px",
        #         "right": "60px",
        #         "bottom": "20px",
        #         "left": "60px",
        #     },
        # )
        self._rendered_html = ""

    def generate_pdf(self) -> BytesIO:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._render_pdf())
        finally:
            loop.close()

    async def _render_pdf(self) -> BytesIO:
        browser = await launch(
            {
                "args": ["--no-sandbox"],
                "headless": True,
                "defaultViewport": {
                    "width": self.viewport_width,
                    "height": self.viewport_height,
                    "deviceScaleFactor": 1,
                },
                "handleSIGINT": False,
                "handleSIGTERM": False,
                "handleSIGHUP": False,
                "autoClose": False,
            }
        )
        page = await browser.newPage()
        await page.setContent(self.html_string)
        await page.waitForSelector("body", options={"timeout": 0})
        buffer = await page.pdf(**self.pdf_options)
        await browser.close()
        return BytesIO(buffer)
