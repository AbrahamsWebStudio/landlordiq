from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
	"""Placeholder maintenance dashboard / requests list."""
	return render(request, "maintenance/index.html")
