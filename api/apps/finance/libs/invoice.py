import uuid
from typing import List, Dict, Union, Optional

from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import User

from api.includes import utils, exceptions
from api.apps.finance import models
from api.apps.patient import models as patient_models


class Invoice:
    def __init__(
        self,
        patient: patient_models.Patient,
        user_data: dict,
        invoice: models.Invoice = None,
        **kwargs,
    ):
        self.invoice: models.Invoice = invoice
        self.patient: patient_models.Patient = patient
        self.user_data: dict = user_data
        self.kwargs: dict = kwargs

    def __pay_reserved_bills(self, bills: QuerySet[models.Bill]):
        """
        Pay reserved bills

        Args:
            bills: List of bills

        Returns:
            [models.Payment]: Payment created
        """
        reserved_bills = bills.filter(is_reserved=True)
        if reserved_bills.count() > 0:
            reserved_bills_amount = sum(
                list(reserved_bills.values_list("selling_price", flat=True))
            )
            if self.patient.reserve < reserved_bills_amount:
                raise exceptions.BadRequest(
                    "Patient reserve is less than total reserved bills amount"
                )
            reserve_payment_method = models.PaymentMethod.objects.get(name="reserve")
            method_struct = models.PaymentMethodStruct(
                payment_method=utils.model_to_dict(reserve_payment_method),
                amount=str(reserved_bills_amount),
            ).dict()
            audit_log = utils.AuditLog(
                user=self.user_data,
                event=utils.AuditEvent.CREATE,
                fields=method_struct,
            ).dict()
            bills_data = [
                utils.model_to_dict(
                    instance=bill, exclude_fields={"invoice", "patient"}
                )
                for bill in reserved_bills
            ]

            payment = models.Payment.objects.create(
                bills=bills_data,
                patient=utils.model_to_dict(self.patient),
                payment_type=str(models.PaymentType.INVOICE),
                total_amount=reserved_bills_amount,
                payment_method=utils.model_to_dict(reserve_payment_method),
                audit_log=[audit_log],
                invoice=self.invoice,
            )
            self.patient.pay_from_reserve(reserved_bills_amount)
            reserved_bills.update(is_invoiced=True, invoice=self.invoice)
            return payment
        return None

    def __get_cleared_auth_bills_total_amount(
        self, bills: QuerySet[models.Bill]
    ) -> float:
        """Get total charges of cleared auth bills

        Args:
            bills: List of bills

        Returns:
            [float]: total charge of bills
        """
        auth_cleared_bills = bills.filter(auth_code__isnull=False)
        if auth_cleared_bills.count() > 0:
            total_amount = sum(
                list(auth_cleared_bills.values_list("selling_price", flat=True))
            )
            return total_amount
        return None

    def __unreserve_bills(
        self, patient: patient_models.Patient, bills: QuerySet[models.Bill]
    ) -> None:
        """unreserves selected bills
        Args:
            bills [Queryset]: QuerySet of all bills

        Returns:
            None
        """
        bills = bills.filter(is_reserved=True)
        total_amount = sum(list(bills.values_list("selling_price", flat=True)))
        bills.update(is_reserved=False)
        patient.pay_from_reserve(total_amount)
        patient.add_deposit(total_amount)
        return None

    def __get_status(self, balance: float, total_charge: float):
        """formulates status of an invoice

        Args:
            balance: Balance of an invoice
            total_charge: Total charge of an invoice

        Returns:
            [str]: Status of an invoice
        """
        return (
            str(models.InvoiceStatus.PAID)
            if balance == 0 and total_charge == 0
            else str(models.InvoiceStatus.OPEN)
            if balance == total_charge
            else str(models.InvoiceStatus.PARTIALLY_PAID)
            if balance != 0 and balance < total_charge
            else str(models.InvoiceStatus.PAID)
        )

    def __record_payments(
        self, payments: List[models.PaymentMethodStruct]
    ) -> List[models.Payment]:
        """
        Records payments made to payments table

        Args:
            payments: List of payments made

        Returns:
            [models.Payment]: Payment created
        """
        payments_obj_list = []
        for payment in payments:
            audit_log = utils.AuditLog(
                user=self.user_data,
                event=utils.AuditEvent.CREATE,
                fields=payment.payment_method,
            ).dict()

            payment_obj = models.Payment(
                bills=self.invoice.bill_lines,
                patient=utils.model_to_dict(self.patient),
                payment_type=str(models.PaymentType.INVOICE),
                total_amount=payment.amount,
                payment_method=payment.payment_method,
                invoice=self.invoice,
                audit_log=[audit_log],
            )
            payments_obj_list.append(payment_obj)
        payment_objs = models.Payment.objects.bulk_create(payments_obj_list)
        return payment_objs

    def __pay_from_deposit(
        self,
        payments: List[models.PaymentMethodStruct],
        patient: patient_models.Patient,
    ) -> None:
        # get total deposit payments
        total_deposit_amount = sum(
            [
                payment.amount
                for payment in payments
                if payment.payment_method.get("name", "").casefold()
                == models.PaymentType.DEPOSIT.casefold()
            ]
        )
        if total_deposit_amount > patient.deposit:
            raise exceptions.BadRequest(
                "total deposit payment method amount is greater than patient deposit balance"
            )
        patient.pay_from_deposit(total_deposit_amount)
        return None

    @classmethod
    def get_invoices(
        cls,
        patient_id: int,
        invoice_status: models.InvoiceStatus,
        scheme_type: models.PayerSchemeType,
        payer_scheme: models.PayerScheme = None,
    ) -> QuerySet[models.Invoice]:
        """Gets Invoice"""
        invoices = models.Invoice.objects.filter(
            patient__id=patient_id,
            status=str(invoice_status),
            scheme_type=scheme_type,
        )
        if payer_scheme:
            return invoices.filter(payer_scheme=payer_scheme)
        return invoices.filter(payer_scheme__isnull=True)

    def create_invoice(self, bills: List[models.Bill]) -> models.Invoice:
        """
        Creates an invoice from a list of bills
        Args:
            bills: List of bills
        Returns:
            [models.Invoice]: Invoice created
        """
        bill_lines = list(
            map(
                lambda bill: utils.model_to_dict(
                    instance=bill,
                    exclude_fields={"invoice", "patient"},
                    _id=str(uuid.uuid4()),
                ),
                bills,
            )
        )

        invoice = models.Invoice.objects.create(
            **self.kwargs,
            patient=utils.model_to_dict(self.patient),
            bill_lines=bill_lines,
            total_charge=0,
            balance=0,
            status=str(models.InvoiceStatus.DRAFT),
            created_by=self.user_data,
        )
        bills: QuerySet[models.Bill] = utils.list_to_queryset(models.Bill, bills)
        bills.update(is_invoiced=True, invoice=invoice)
        return invoice

    @classmethod
    def create_invoices(
        cls, created_by: dict, patient: dict, bills: List[models.Bill]
    ) -> List[models.Invoice]:
        """
        Creates an invoice from a list of bills
        Args:
            bills: List of bills

        Returns:
            [models.Invoice]: Invoice created
        """
        bills: QuerySet[models.Bill] = utils.list_to_queryset(models.Bill, bills)

        # group bills according to the different payer scheme and scheme type
        grouped_bills: dict[tuple, list[models.Bill]] = {}
        for bill in bills:
            scheme_type = bill.billed_to_type
            payer_scheme = bill.billed_to
            payer_scheme_pk = payer_scheme.pk if payer_scheme else None
            if grouped_bills.get((scheme_type, payer_scheme_pk)):
                grouped_bills[(scheme_type, payer_scheme_pk)].append(bill)
            else:
                grouped_bills[(scheme_type, payer_scheme_pk)] = [bill]

        # check if each group has a bill with an invoice or create a new one if None
        invoices: List[models.Invoice] = []

        for group_bills in grouped_bills.values():
            invoices_qs = cls.get_invoices(
                patient_id=patient.get("id"),
                invoice_status=models.InvoiceStatus.DRAFT,
                scheme_type=group_bills[0].billed_to_type,
                payer_scheme=group_bills[0].billed_to,
            )
            if invoices_qs.exists():
                invoice: models.Invoice = invoices_qs.first()
                instance: "Invoice" = cls(
                    patient=patient_models.Patient.objects.get(id=patient.get("id")),
                    user_data=created_by,
                    invoice=invoice,
                )
                instance.add_bills(group_bills)
                invoices.append(invoice)

            # create a new invoice if no invoice exist
            else:
                bill_lines = list(
                    map(
                        lambda bill: utils.model_to_dict(
                            instance=bill,
                            exclude_fields={"invoice", "patient"},
                            _id=str(uuid.uuid4()),
                        ),
                        group_bills,
                    )
                )

                invoice = models.Invoice.objects.create(
                    patient=patient,
                    bill_lines=bill_lines,
                    total_charge=0,
                    balance=0,
                    status=str(models.InvoiceStatus.DRAFT),
                    created_by=created_by,
                )
                update_bills: QuerySet[models.Bill] = utils.list_to_queryset(
                    models.Bill, group_bills
                )
                update_bills.update(is_invoiced=True, invoice=invoice)
                invoices.append(invoice)
        return invoices

    def confirm_invoice(self) -> models.Invoice:
        """confirm an invoice

        Args:
            invoice: Invoice Object

        Returns:
            [models.Invoice]: Invoice updated
        """
        if self.invoice.status.casefold() != str(models.InvoiceStatus.DRAFT).casefold():
            raise exceptions.BadRequest("Invoice is already confirmed")

        db_bills = models.Bill.objects.filter(
            id__in=[bill["id"] for bill in self.invoice.bill_lines if bill.get("id")]
        )

        total_charge = sum(
            float(bill.get("selling_price", 0)) * float(bill.get("quantity", 1))
            for bill in self.invoice.bill_lines
        )
        self.invoice.total_charge = total_charge
        self.invoice.balance = total_charge

        # settle reserved bills
        payment: models.Payment = self.__pay_reserved_bills(db_bills)
        self.invoice.status = str(models.InvoiceStatus.OPEN)
        if payment:
            self.invoice.balance = float(self.invoice.balance) - float(
                payment.total_amount
            )
            self.invoice.paid_amount = float(self.invoice.paid_amount) + float(
                payment.total_amount
            )
            self.invoice.payment_lines.append(
                utils.model_to_dict(
                    payment, exclude_fields={"invoice", "audit_log", "patient"}
                )
            )

        # settle auth bills
        total_auth_amount_clearance = self.__get_cleared_auth_bills_total_amount(
            bills=db_bills
        )
        if total_auth_amount_clearance:
            self.invoice.balance = float(self.invoice.balance) - float(
                total_auth_amount_clearance
            )
            self.invoice.paid_amount = float(self.invoice.paid_amount) + float(
                total_auth_amount_clearance
            )

        self.invoice.status = self.__get_status(
            self.invoice.balance, self.invoice.total_charge
        )
        self.invoice.confirmed_by = self.user_data
        self.invoice.confirmed_at = timezone.now()
        self.invoice.due_date = timezone.now()
        self.invoice.save()
        self.invoice.set_invoice_id()
        db_bills.update(is_invoiced=True, invoice=self.invoice)
        return self.invoice

    def add_payments(self, payments: List[models.PaymentMethodStruct]):
        """add payments to an invoice

        Args:
            invoice: Invoice Object
            payments: List of payments

        Returns:
            [models.Invoice]: Invoice updated
        """

        if (
            str(self.invoice.status).casefold()
            == str(models.InvoiceStatus.DRAFT).casefold()
        ):
            self.confirm_invoice()

        if (
            str(self.invoice.status).casefold()
            in [
                str(models.InvoiceStatus.PARTIALLY_PAID).casefold(),
                str(models.InvoiceStatus.OPEN).casefold(),
            ],
        ):
            paid_amount = sum(payment.amount for payment in payments)
            self.__pay_from_deposit(payments=payments, patient=self.patient)
            payments_objs = self.__record_payments(payments)
            payment_parsed_data = list(
                map(
                    lambda payment: utils.model_to_dict(
                        payment, exclude_fields={"invoice", "patient", "audit_log"}
                    ),
                    payments_objs,
                )
            )
            self.invoice.payment_lines.extend(payment_parsed_data)
            self.invoice.paid_amount = float(self.invoice.paid_amount) + float(
                paid_amount
            )
            self.invoice.balance = float(self.invoice.balance) - float(paid_amount)
            self.invoice.status = self.__get_status(
                self.invoice.balance, self.invoice.total_charge
            )
            self.invoice.updated_at = timezone.now()
            self.invoice.updated_by = self.user_data
            self.invoice.save()

            if (
                self.invoice.status.casefold()
                == str(models.InvoiceStatus.PAID).casefold()
            ):
                bills = models.Bill.objects.filter(
                    id__in=[bill.get("id") for bill in self.invoice.bill_lines]
                )
                bills.update(cleared_status=str(models.BillStatus.CLEARED))
            return self.invoice

        if self.invoice.status.casefold() == str(models.InvoiceStatus.PAID).casefold():
            raise exceptions.BadRequest("Invoice is already paid")

    def get_bills(self) -> List[str]:
        """Return all bills in an invoice"""
        bills = self.invoice.bill_lines
        bill_ids = [bill["id"] for bill in bills]
        return bill_ids

    def edit_bills(self, bills: List[dict], user: User) -> models.Invoice:
        """Edit bills
        Bills can be added, removed and modified directly from here
        """
        # unreserve db bills
        db_bill_ids = [bill["id"] for bill in self.invoice.bill_lines if bill.get("id")]
        db_bills = models.Bill.objects.filter(id__in=db_bill_ids)
        self.__unreserve_bills(patient=self.patient, bills=db_bills)
        bills: List[dict] = [{**bill, "is_reserved": False} for bill in bills]

        modified_bills_ids: List[uuid.UUID] = [bill.get("_id") for bill in bills]
        invoice_bills: List[dict] = self.invoice.bill_lines
        invoice_bills_ids: List[uuid.UUID] = [bill.get("_id") for bill in invoice_bills]

        # get added,removed and comman bills
        removed_bills = set(invoice_bills_ids).difference(set(modified_bills_ids))
        added_bills = set(modified_bills_ids).difference(set(invoice_bills_ids))
        common_bills = set(invoice_bills_ids).intersection(set(modified_bills_ids))

        if len(removed_bills) > 0 and not user.has_perm("finance.remove_bills"):
            raise exceptions.PermissionDenied("Inadequate permissions to remove bills")
        if len(added_bills) > 0 and not user.has_perm("finance.add_bill"):
            raise exceptions.PermissionDenied("Inadequate permissions to add bills")
        if len(modified_bills_ids) > 0 and not user.has_perm("finance.edit_bills"):
            raise exceptions.PermissionDenied("Inadequate permissions to edit bills")
        if len(common_bills) > 0:
            for bill_id in list(common_bills):
                db_bill_detail = next(
                    (bill for bill in invoice_bills if bill["_id"] == bill_id), {}
                )
                modified_bill_detail = next(
                    (bill for bill in bills if bill["_id"] == bill_id), {}
                )

                if float(modified_bill_detail.get("selling_price", 0)) > float(
                    db_bill_detail.get("selling_price", 0)
                ) and not user.has_perm("finance.markup_price"):
                    raise exceptions.PermissionDenied(
                        "Inadequate permissions to add mark up price"
                    )

                if float(modified_bill_detail.get("selling_price", 0)) < float(
                    db_bill_detail.get("selling_price", 0)
                ) and not user.has_perm("finance.markdown_price"):
                    raise exceptions.PermissionDenied(
                        "Inadequate permissions to add mark down price"
                    )

                index = bills.index(modified_bill_detail)
                db_bill_detail.update(modified_bill_detail)
                bills[index] = db_bill_detail

        if len(added_bills) > 0:
            for bill_id in list(added_bills):
                new_bill = next((bill for bill in bills if bill["_id"] == bill_id), {})
                new_bill_index = bills.index(new_bill)
                new_bill["transaction_date"] = new_bill.get(
                    "transaction_date"
                ) or timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                new_bill["serviced_rendered_at"] = new_bill.get("transaction_date")
                new_bill["is_service_rendered"] = True

                index = bills.index(new_bill)
                bills[new_bill_index] = new_bill

        self.invoice.bill_lines = bills
        self.invoice.save()
        return self.invoice

    def remove_bills(self, bills: List[models.Bill]) -> models.Invoice:
        """Remove bill
        Args:
            bills: bills to be removed
        Returns:
            [models.Invoice]: Invoice updated
        """

        if (
            str(self.invoice.status).casefold()
            != str(models.InvoiceStatus.DRAFT).casefold()
        ):
            raise exceptions.BadRequest("Invoice is already confirmed")

        bill_ids = [bill.id for bill in bills]
        service_rendered_bills = models.Bill.objects.filter(
            id__in=bill_ids, is_service_rendered=True
        )
        if service_rendered_bills.exists():
            error_bill_ids = [bill.id for bill in service_rendered_bills]
            raise exceptions.BadRequest(
                f"Service for the following bill ids have been rendered {error_bill_ids}"
            )

        invoice_bills_id = [bill["id"] for bill in self.invoice.bill_lines]
        if not set(bill_ids).issubset(set(invoice_bills_id)):
            raise exceptions.BadRequest("Bill ids not found in invoice")

        self.invoice.bill_lines = [
            bill for bill in self.invoice.bill_lines if bill["id"] not in bill_ids
        ]
        self.invoice.save()

        for bill in bills:
            bill.is_invoiced = False
            bill.invoice = None

        models.Bill.objects.bulk_update(bills, ["is_invoiced", "invoice"])
        return self.invoice

    def add_bills(self, bills: List[models.Bill]) -> models.Invoice:
        """add bill lines
        Args:
            bills: bills to be removed
        Returns:
            [models.Invoice]: Invoice updated
        """

        if (
            str(self.invoice.status).casefold()
            != str(models.InvoiceStatus.DRAFT).casefold()
        ):
            raise exceptions.BadRequest("Invoice is already confirmed")

        bill_ids = [bill.id for bill in bills]
        invoiced_bills = models.Bill.objects.filter(id__in=bill_ids, is_invoiced=True)
        if invoiced_bills.exists():
            error_bill_ids = [bill.id for bill in invoiced_bills]
            raise exceptions.BadRequest(f"Bill ids {error_bill_ids} have been invoiced")

        invoice_bills_id = [bill["id"] for bill in self.invoice.bill_lines]
        unadded_bills = [bill for bill in bills if bill.id not in invoice_bills_id]
        if unadded_bills:
            # find bills that have the same bill item code in the invoice
            # update the item quantity, selling price,
            invoice_bills: List[dict] = self.invoice.bill_lines
            for bill in unadded_bills:
                invoice_bill = next(
                    (
                        line
                        for line in invoice_bills
                        if line["bill_item_code"] == bill.bill_item_code
                    ),
                    None,
                )
                if invoice_bill:
                    index = invoice_bills.index(invoice_bill)
                    invoice_bill["quantity"] = bill.quantity + int(
                        invoice_bill.get("quantity")
                    )
                    invoice_bill["co_pay"] = str(
                        float(bill.co_pay) + float(invoice_bill.get("co_pay"))
                    )
                    invoice_bills[index] = invoice_bill

                else:
                    kwargs = {"_id": str(uuid.uuid4())}
                    invoice_bills.append(
                        utils.model_to_dict(
                            bill,
                            exclude_fields={
                                "invoice",
                                "patient",
                            },
                            **kwargs,
                        )
                    )

            self.invoice.bill_lines = invoice_bills
            self.invoice.save()

            for bill in unadded_bills:
                bill.is_invoiced = True
                bill.invoice = self.invoice

            models.Bill.objects.bulk_update(unadded_bills, ["is_invoiced", "invoice"])
        return self.invoice
