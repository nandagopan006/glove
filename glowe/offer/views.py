from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.utils import timezone

from .models import Offer, OfferItem
from product.models import Product
from category.models import Category


def add_offer(request):

    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":

        name = request.POST.get("name")
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        max_discount = request.POST.get("max_discount")
        min_purchase = request.POST.get("min_purchase")

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        apply_to = request.POST.get("apply_to")
        product_id = request.POST.get("product_id")
        category_id = request.POST.get("category_id")

        #for error pass
        def error(msg):
            messages.error(request, msg)
            return redirect("add_offer")

        #validation

        if not name:
            return error("Offer name required")

        # discount value
        try:
            discount_value = Decimal(discount_value)
        except (InvalidOperation, TypeError):
            return error("Invalid discount value")

        if discount_value <= 0:
            return error("Discount must be greater than 0")

        if discount_type not in ["PERCENTAGE", "FLAT"]:
            return error("Invalid discount type")

        if discount_type == "PERCENTAGE" and discount_value > 100:
            return error("Percentage cannot exceed 100")

        # max discount
        if max_discount:
            try:
                max_discount = Decimal(max_discount)
                if max_discount <= 0:
                    return error("Max discount must be > 0")
            except:
                return error("Invalid max discount")

        # min purchase
        if min_purchase:
            try:
                min_purchase = Decimal(min_purchase)
                if min_purchase <= 0:
                    return error("Min purchase must be > 0")
            except:
                return error("Invalid min purchase")

        # date validation
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            return error("Invalid date format")

        if start_date >= end_date:
            return error("End date must be after start date")

        # apply validation
        if apply_to == "PRODUCT" and not product_id:
            return error("Select a product")

        if apply_to == "CATEGORY" and not category_id:
            return error("Select a category")

        #dulipate check
        now = timezone.now()

        if apply_to == "PRODUCT":
            exists = OfferItem.objects.filter(
                product_id=product_id,
                apply_to="PRODUCT",
                offer__is_active=True,
                offer__start_date__lte=now,
                offer__end_date__gte=now
            ).exists()

            if exists:
                return error("This product already has an active offer")

        if apply_to == "CATEGORY":
            exists = OfferItem.objects.filter(
                category_id=category_id,
                apply_to="CATEGORY",
                offer__is_active=True,
                offer__start_date__lte=now,
                offer__end_date__gte=now
            ).exists()

            if exists:
                return error("This category already has an active offer")

        # save
        offer = Offer.objects.create(
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount=max_discount if discount_type == "PERCENTAGE" else None,
            min_purchase=min_purchase,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        if apply_to == "PRODUCT":
            OfferItem.objects.create(offer=offer,apply_to="PRODUCT",product_id=product_id)
            
        else:
            OfferItem.objects.create(offer=offer,apply_to="CATEGORY",category_id=category_id )

        messages.success(request, "Offer created successfully")
        return redirect("offer_list")

    return render(request, "admin/add_offer.html",{
        "products": products,
        "categories": categories
    })


def edit_offer(request, id):

    offer = get_object_or_404(Offer, id=id)
    item = OfferItem.objects.get(offer=offer)

    if request.method == "POST":

        name = request.POST.get("name")
        discount_value = request.POST.get("discount_value")
        max_discount = request.POST.get("max_discount")
        min_purchase = request.POST.get("min_purchase")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        def error(msg):
            messages.error(request, msg)
            return redirect("edit_offer", id=id)

    

        if not name:
            return error("Offer name required")

        try:
            discount_value = Decimal(discount_value)
        except (InvalidOperation, TypeError):
            return error("Invalid discount value")

        if discount_value <= 0:
            return error("Discount must be greater than 0")

        if offer.discount_type == "PERCENTAGE" and discount_value > 100:
            return error("Percentage cannot exceed 100")

        # max discount
        if max_discount:
            try:
                max_discount = Decimal(max_discount)
                if max_discount <= 0:
                    return error("Max discount must be > 0")
            except:
                return error("Invalid max discount")

        # min purchase
        if min_purchase:
            try:
                min_purchase = Decimal(min_purchase)
                if min_purchase <= 0:
                    return error("Min purchase must be > 0")
            except:
                return error("Invalid min purchase")

        # date validation
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            return error("Invalid date format")

        if start_date >= end_date:
            return error("End date must be after start date")

        #save
        offer.name = name
        offer.discount_value = discount_value
        offer.max_discount = max_discount if offer.discount_type == "PERCENTAGE" else None
        offer.min_purchase = min_purchase
        offer.start_date = start_date
        offer.end_date = end_date

        offer.save()

        messages.success(request, "Offer updated successfully")
        return redirect("offer_list")

    return render(request, "admin/edit_offer.html", {
        "offer": offer,
        "item": item
    })