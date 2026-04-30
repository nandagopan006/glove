from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from product.models import Product


def search_view(request):

    query = request.GET.get("q", "").strip()

    results = []

    if query:

        products = Product.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)),
            is_active=True,
            is_deleted=False,
        ).distinct()

        for product in products:

            image = product.images.filter(is_primary=True).first()
            if not image:
                image = product.images.first()

            variant = product.variants.filter(
                is_default=True, is_active=True
            ).first()
            if not variant:
                variant = product.variants.filter(is_active=True).first()

            results.append(
                {
                    "product": product,
                    "image": image,
                    "variant": variant,
                }
            )

    context = {
        "query": query,
        "results": results,
        "result_count": len(results),
    }
    return render(request, "search/search.html", context)


def search_suggestions(request):

    query = request.GET.get("q", "").strip()
    suggestions = []

    if query and len(query) >= 2:

        products = Product.objects.filter(
            name__icontains=query, is_active=True, is_deleted=False
        )[:5]

        for product in products:

            image = product.images.filter(is_primary=True).first()
            if not image:
                image = product.images.first()

            variant = product.variants.filter(
                is_default=True, is_active=True
            ).first()
            if not variant:
                variant = product.variants.filter(is_active=True).first()

            suggestion_item = {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "price": str(variant.price) if variant else "0.00",
                "image": image.image.url if image else None,
            }
            suggestions.append(suggestion_item)

    return JsonResponse({"results": suggestions})
