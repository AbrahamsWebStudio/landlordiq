import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Invoice, Payment
from django.utils import timezone
import logging
from .utils import MpesaClient
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from urllib.parse import quote
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse


logger = logging.getLogger(__name__)


@login_required
def initiate_payment(request, invoice_id):
    """
    This view is triggered when the tenant clicks 'Pay'.
    It starts the STK Push and saves the ID for the callback to find later.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    client = MpesaClient()
    
    # Determine the phone number from the tenant profile
    tenant = getattr(invoice.lease, 'tenant', None)
    if not tenant or not getattr(tenant, 'phone_number', None):
        return JsonResponse({"status": "error", "message": "Tenant phone number unavailable"}, status=400)

    phone = tenant.phone_number.strip()
    # Normalize formats: +2547..., 07..., 2547...
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('0'):
        phone = '254' + phone[1:]

    # Amount should default to the invoice total amount
    try:
        amount = int(float(invoice.total_amount))
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid invoice amount"}, status=400)

    # Build callback URL dynamically
    callback_url = request.build_absolute_uri(reverse('payments:mpesa_callback'))
    reference = f"INV{invoice.id}"

    # 1. Trigger the STK Push
    response = client.stk_push(phone, amount, callback_url, reference)

    # 2. Check if Safaricom accepted the request
    if response.get('ResponseCode') == '0':
        # Link this specific session to the invoice so the callback knows
        # who this money belongs to.
        invoice.mpesa_checkout_id = response.get('CheckoutRequestID')
        invoice.save()
        
        return JsonResponse({
            "status": "success", 
            "message": "STK Push sent! Please check your phone."
        })
    else:
        return JsonResponse({
            "status": "error", 
            "message": response.get('CustomerMessage', 'Failed to initiate M-Pesa')
        }, status=400)


@csrf_exempt
def mpesa_callback(request):
    # Safaricom sends a POST request
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result_code = data['Body']['stkCallback']['ResultCode']
            
            if result_code == 0:  # Success
                metadata = data['Body']['stkCallback']['CallbackMetadata']['Item']
                
                # Extract details
                receipt = next(item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber')
                amount = next(item['Value'] for item in metadata if item['Name'] == 'Amount')
                checkout_id = data['Body']['stkCallback']['CheckoutRequestID']
                
                # Find the invoice by checkout id
                invoice = Invoice.objects.get(mpesa_checkout_id=checkout_id)

                # Create payment — Payment.save() will recalculate invoice.amount_paid and status
                Payment.objects.create(
                    invoice=invoice,
                    amount=amount,
                    mpesa_code=receipt,
                    is_confirmed=True
                )
            
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        except Exception as e:
            # Even if our logic fails, we tell Safaricom 'Success' so they stop retrying
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Error but received"})

    # If someone tries a GET request (like you just did), return a 405
    return HttpResponse("Method Not Allowed", status=405)


@login_required
def tenant_ledger(request):
    # Fetch invoices for the logged-in tenant via the Lease relationship
    invoices = Invoice.objects.filter(
        lease__tenant__user=request.user
    ).prefetch_related('payments').order_by('-billing_month')
    
    # Calculate balance — total of all unpaid or partial invoices
    total_due = invoices.exclude(status='paid').aggregate(
        remaining=Sum('total_amount') - Sum('amount_paid')
    )['remaining'] or 0

    return render(request, 'payments/ledger.html', {
        'invoices': invoices,
        'total_due': total_due
    })


@login_required
def download_receipt(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, lease__tenant__user=request.user)    
    # Ensure only the tenant can download their own receipt
    if invoice.amount_paid <= 0:
        return HttpResponse("No payments found for this receipt.", status=400)
    

    template = get_template('payments/receipt_pdf.html')
    context = {
        'invoice': invoice,
        'payments': invoice.payments.filter(is_confirmed=True),
        'property': invoice.lease.unit.property,
    }
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Receipt_{invoice.mpesa_checkout_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse("Error generating PDF", status=500)


@login_required
def download_invoice(request, invoice_id):
    """View to download the initial bill/invoice before payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id, lease__tenant__user=request.user)
    
    # You can reuse your receipt template or create an invoice_pdf.html
    template = get_template('payments/receipt_pdf.html') 
    context = {'invoice': invoice, 'property': invoice.lease.unit.property, 'title': "OFFICIAL INVOICE"}
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.id}.pdf"'
        return response
    return HttpResponse("Error", status=500)


@login_required
def get_tenant_actions(request, tenant_id):
    """
    Fetches tenant data and returns a partial HTML for the Action Sheet.
    Used by HTMX to populate the dashboard overlay.
    """
    # 1. Fetch the tenant or 404
    from tenants.models import Tenant
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # 2. Get the active lease and unit
    lease = tenant.leases.filter(is_active=True).first()
    unit_name = lease.unit.unit_number if lease else "your unit"
    
    # 3. Calculate total outstanding balance
    # Summing up all unpaid or partial invoices
    outstanding_balance = Invoice.objects.filter(
        lease=lease
    ).exclude(status='paid').aggregate(
        total=Sum('total_amount') - Sum('amount_paid')
    )['total'] or 0

    # 4. Craft the WhatsApp Message
    # Including Paybill and Account details for zero-friction payment
    message = (
        f"Habari {tenant.name}, this is a reminder for Unit {unit_name}. "
        f"Your current outstanding balance is KES {outstanding_balance:,}. "
        f"Please pay via Paybill 400200, Account: {unit_name}. "
        "Thank you!"
    )
    whatsapp_url = f"https://wa.me/{tenant.phone_number}?text={quote(message)}"
    
    # 5. Return the partial template (HTMX swap)
    return render(request, 'partials/action_sheet_content.html', {
        'tenant': tenant,
        'balance': outstanding_balance,
        'whatsapp_url': whatsapp_url,
        'unit': unit_name
    })