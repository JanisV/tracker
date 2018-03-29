from django.contrib import admin

from .models import Site, Auction, Category, Completion, Raw

admin.site.register(Site)
admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Completion)
admin.site.register(Raw)
