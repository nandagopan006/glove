
from django.db import transaction
from decimal import Decimal


def process_refund(order, refund_amount=None, description=None):
 
    from wallet.models import Wallet, WalletTransaction
    from order.models import Payment

    if refund_amount is None:
        refund_amount = order.total_amount

    refund_amount = Decimal(str(refund_amount))

    if refund_amount <= Decimal('0'):
        return False

    # Get payment method
    payment = getattr(order, 'payment', None)
    payment_method = payment.payment_method if payment else None

    # COD cancellation → no refund (customer never paid online)
    # COD returns → DO refund (order was delivered, payment collected on delivery)
    if payment_method == Payment.Method.COD:
        # Check if this is a cancellation (order never delivered) or return
        from order.models import Order
        # If the order was never delivered (cancelled before delivery), no refund
        non_refundable_statuses = [
            Order.Status.CANCELLED,
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
            Order.Status.SHIPPED,
            Order.Status.OUT_FOR_DELIVERY,
        ]
 
        if not order.delivered_date:
            # Never delivered → COD → no refund
            return False

  
    existing = WalletTransaction.objects.filter(
        order=order,
        transaction_type='REFUND',
        amount=refund_amount,
        status='COMPLETED',
    ).exists()

    if existing and description is None:
        # Full-order refund already done
        return False

    if description is None:
        description = f"Refund for Order #{order.order_number}"

    # Check for exact duplicate (same order + same description + same amount)
    duplicate = WalletTransaction.objects.filter(
        order=order,
        transaction_type='REFUND',
        amount=refund_amount,
        description=description,
        status='COMPLETED',
    ).exists()

    if duplicate:
        return False

    with transaction.atomic():
        wallet, _ = Wallet.objects.get_or_create(user=order.user)
        wallet = Wallet.objects.select_for_update().get(id=wallet.id)

        wallet.balance += refund_amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            order=order,
            transaction_type='REFUND',
            amount=refund_amount,
            status='COMPLETED',
            description=description,
        )

    return True
