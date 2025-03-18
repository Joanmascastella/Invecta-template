from django.shortcuts import render

def custom_page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

def custom_error_view(request):
    return render(request, '500.html', status=500)

def custom_bad_request_view(request, exception):
    return render(request, '400.html', status=400)