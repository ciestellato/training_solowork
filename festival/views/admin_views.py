from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required
def admin_menu(request):
    return render(request, 'admin_menu.html')