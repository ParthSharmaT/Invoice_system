from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import context, pisa

# from django.contrib.staticfiles import finders
# from django.views.generic import ListView
from .models import Customer
from django.core.mail import send_mail, EmailMessage
from invoice_system_management.utils import render_to_pdf
from django.views.generic import ListView

# Create your views here.
def base(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
    }

    return render(request, "invoice/base/base.html", context)


# Product view
def create_product(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = ProductForm()

    if request.method == "POST":
        product = ProductForm(request.POST)
        if product.is_valid():
            product.save()
            return redirect("create_product")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": product,
    }

    return render(request, "invoice/create_product.html", context)


def view_product(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = Product.objects.filter(product_is_delete=False)

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": product,
    }

    return render(request, "invoice/view_product.html", context)


# Customer view
def create_customer(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = CustomerForm()

    if request.method == "POST":
        customer = CustomerForm(request.POST)
        if customer.is_valid():
            customer.save()
            return redirect("create_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/create_customer.html", context)


def view_customer(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.all()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/view_customer.html", context)


# Invoice view
def create_invoice(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    form = InvoiceForm()
    formset = InvoiceDetailFormSet()
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)
        if form.is_valid():
            invoice = Invoice.objects.create(
                customer=form.cleaned_data.get("customer"),
                date=form.cleaned_data.get("date"),
            )
        if formset.is_valid():
            total = 0
            for form in formset:
                product = form.cleaned_data.get("product")
                amount = form.cleaned_data.get("amount")
                if product and amount:
                    # Sum each row
                    sum = float(product.product_price) * float(amount)
                    # Sum of total invoice
                    total += sum
                    InvoiceDetail(
                        invoice=invoice, product=product, amount=amount
                    ).save()
            # Pointing the customer
            points = 0
            if total > 1000:
                points += total / 1000
            invoice.customer.customer_points = round(points)
            # Save the points to Customer table
            invoice.customer.save()

            # Save the invoice
            invoice.total = total
            invoice.save()
            return redirect("view_invoice")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "form": form,
        "formset": formset,
    }

    return render(request, "invoice/create_invoice.html", context)


def view_invoice(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    invoice = Invoice.objects.all()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "invoice": invoice,
    }

    return render(request, "invoice/view_invoice.html", context)


# Detail view of invoices
def view_invoice_detail(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        # 'invoice': invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/view_invoice_detail.html", context)


# Delete invoice
def delete_invoice(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
    if request.method == "POST":
        invoice_detail.delete()
        invoice.delete()
        return redirect("view_invoice")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "invoice": invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/delete_invoice.html", context)


# Edit customer
def edit_customer(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)

    if request.method == "POST":
        customer = CustomerForm(request.POST, instance=customer)
        if customer.is_valid():
            customer.save()
            return redirect("view_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": form,
    }

    return render(request, "invoice/create_customer.html", context)


# Delete customer
def delete_customer(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.get(id=pk)

    if request.method == "POST":
        customer.delete()
        return redirect("view_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/delete_customer.html", context)


# Edit product
def edit_product(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)

    if request.method == "POST":
        customer = CustomerForm(request.POST, instance=product)
        if customer.is_valid():
            product.save()
            return redirect("view_product")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": form,
    }

    return render(request, "invoice/create_product.html", context)


# Delete product
def delete_product(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = Product.objects.get(id=pk)

    if request.method == "POST":
        product.product_is_delete = True
        product.save()
        return redirect("view_product")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": product,
    }

    return render(request, "invoice/delete_product.html", context)


def customer_render_pdf_view(request, pk):
    print(pk)
    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice_id=invoice)
    print(invoice_detail)
    customer = get_object_or_404(Customer, id=invoice.customer_id)
    template_path = "invoice/pdf_view.html"

    context = {
        "invoice": invoice,
        "customer": customer,
        "invoice_detail": invoice_detail,
    }
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response


# function for mail attachment


def mailpdf(request, *args, **kwargs):
    pk = kwargs.get("pk")
    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice_id=invoice)
    customer = get_object_or_404(Customer, id=invoice.customer_id)

    context = {
        "invoice": invoice,
        "customer": customer,
        "invoice_detail": invoice_detail,
    }

    subject = "E-invoice generated invoice"
    msg = "Here is your Invoice"
    to = customer.customer_mail
    html_template = "testmail.html"
    html_message = render_to_string(html_template)
    message = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [to])

    template_path = "invoice/pdf_view.html"
    result = render_to_pdf(template_path, context)

    # ress=render_to_pdf(result)
    message.attach("invoice.pdf", result, "application/pdf")
    message.content_subtype = "html"
    message.send()
    return HttpResponse("success")
