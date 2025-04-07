from django.shortcuts import render

from .services import NFMerSearchService


async def index(request):
    return render(request, "search/index.html")


async def search_results(request):
    """Handle search requests and return results asynchronously"""
    query = request.GET.get("q", "")
    search_type = request.GET.get("type", "composers")
    if search_type == "composers":
        results = await NFMerSearchService.search_composers(query)
    else:
        results = await NFMerSearchService.search_compositions(query)
    context = {"results": results, "search_type": search_type, "query": query}
    return render(request, "search/partials/search_results.html", context)


async def composer_detail(request, composer_id):
    """Display detailed information about a composer asynchronously"""
    composer = await NFMerSearchService.get_composer_details(composer_id)
    if not composer:
        return render(request, "search/error.html", {"message": "Composer not found"})
    return render(request, "search/composer_detail.html", {"composer": composer})


async def composition_detail(request, composition_id):
    """Display detailed information about a composition asynchronously"""
    composition = await NFMerSearchService.get_composition_details(composition_id)
    if not composition:
        return render(request, "search/error.html", {"message": "Composition not found"})
    return render(request, "search/composition_detail.html", {"composition": composition})
