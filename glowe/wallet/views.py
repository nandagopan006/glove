from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Wallet
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction
from payment.utils import create_razorpay_order
from decimal import Decimal, InvalidOperation
from payment.utils import verify_payment_signature
from django.views.decorators.csrf import csrf_exempt



def wallet_view(request):
    wallet,created = Wallet.objects.get_or_create(user=request.user)

    transactions_list = wallet.transactions.all().order_by('-created_at')

    paginator=Paginator(transactions_list,5)  # 5 per page
    page_number=request.GET.get('page')
    transactions =paginator.get_page(page_number)

    return render(request,'wallet/wallet.html',{
        'wallet':wallet,
        'transactions':transactions
    })
    

@login_required
def create_wallet_order(request):
    try:
        amount = request.POST.get("amount")

        #Validate amount
        try:
            amount = Decimal(amount)
        except (InvalidOperation, TypeError):
            return JsonResponse({"error": "Invalid amount format"}, status=400)

        if amount <= 0:
            return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

    
        if amount > 50000:
            return JsonResponse({"error": "Maximum ₹50,000 allowed"}, status=400)

        #Get wallet
        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        # Create Razorpay order
        razorpay_order = create_razorpay_order(amount)

        txn = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="ADD",
            amount=amount,
            status="PENDING",
            description="Wallet top-up",
            transaction_id=razorpay_order["id"]  
        )

        return JsonResponse({
            "order_id": razorpay_order["id"],
            "amount": int(amount * 100),
            "key": settings.RAZORPAY_KEY_ID,
            "txn_id": txn.id
        })

    except Exception as e:
        print("Wallet Order Error:", e)
        return JsonResponse({"error": "Something went wrong"}, status=500)