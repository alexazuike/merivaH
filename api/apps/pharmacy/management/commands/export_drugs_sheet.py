import os, string
from pprint import pprint
from typing import List, Optional

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import pandas as pd, numpy as np
from pydantic import BaseModel, Field

from api.apps.pharmacy.models import GenericDrug, Category
from api.apps.inventory.models import Product
from api.includes import utils


"""
Read the excel file
read each line
check if the line is a category either parent or sub category
create category if they are
create a product if they are
"""


class DataSchema(BaseModel):
    dosage_form: Optional[str]
    name_of_medicines: str
    nhis_code: Optional[str]
    presentation: Optional[str]
    price: Optional[float]
    strengths: Optional[str]


class Command(BaseCommand):
    help = "Export excel sheet to database"
    categories = []

    @transaction.atomic
    def handle(self, *args, **options):
        sample_data = self.read_excel_file()
        for data in sample_data:
            self._create_parent_category(data)
            self._create_sub_category(data)
            self._create_generic_drug(data)
        else:
            print("export done")

    def read_excel_file(self):
        EXCEL_PATH = os.path.join(settings.BASE_DIR, "fixtures", "drugs", "drugs.xlsx")
        data_frame = pd.read_excel(EXCEL_PATH)
        data_frame = data_frame.replace({np.nan: None})

        records = data_frame.to_dict("records")
        del records[0]
        normalized_records = []
        for record in records:
            record_value = self._change_dict_format(record)
            if record_value:
                normalized_records.append(record_value)
        parsed_schema_objs = [DataSchema(**record) for record in normalized_records]
        return parsed_schema_objs

    def _change_dict_format(self, data: dict):
        modified_data = {}
        for key, value in data.items():
            modified_key = str(key).strip().replace(" ", "_").lower()
            if modified_key in ["name_of_medicines"] and data[key] is None:
                return None
            if modified_key == "price" and type(value) == str:
                value = 0
            modified_data[modified_key] = value
        return modified_data

    def _create_parent_category(self, data: DataSchema):
        if data.nhis_code is None:
            self.categories.clear()
            category_name = data.name_of_medicines.split(",")[1].strip()
            cat_obj = Category.objects.create(name=string.capwords(category_name))
            self.categories.append(cat_obj)

    def _create_sub_category(self, data: DataSchema):
        if (
            data.nhis_code is not None
            and data.presentation is None
            and data.strengths is None
            and data.price is None
        ):
            category_name = data.name_of_medicines.split(",")[1].strip()
            level = data.name_of_medicines.split(",")[0].strip().count(".")
            if level <= len(self.categories):
                cat_obj = Category.objects.create(
                    name=string.capwords(category_name), parent=self.categories[-1]
                )
                self.categories.append(cat_obj)
            else:
                for count in range(0, 1):
                    self.categories.pop(-1)
                else:
                    cat_obj = Category.objects.create(
                        name=string.capwords(category_name), parent=self.categories[-1]
                    )
                    self.categories.append(cat_obj)

    def _create_generic_drug(self, data: DataSchema):
        if (
            data.dosage_form
            and data.name_of_medicines
            and data.nhis_code
            and data.presentation
            and data.price
            and data.strengths
        ):
            name = f"{data.name_of_medicines} {data.dosage_form} {data.strengths}"
            generic_drug = GenericDrug.objects.create(
                name=string.capwords(name),
                category=utils.model_to_dict(
                    self.categories[-1], exclude_fields={"created_at", "updated_at"}
                ),
            )
            product = Product(
                code=data.nhis_code,
                is_drug=True,
                generic_drug=utils.model_to_dict(
                    generic_drug, exclude_fields={"created_at", "updated_at"}
                ),
                category=utils.model_to_dict(
                    self.categories[-1], exclude_fields={"created_at", "updated_at"}
                ),
                divider=1,
                cost=data.price,
                uom=data.presentation,
                name=string.capwords(name),
            )
            product._created_by = {}
            product._bill_price = data.price
            product._cost_price = data.price
            product.save()
            print(product.name)
