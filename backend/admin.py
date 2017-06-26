from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *


# Register your models here.

class CrawlWebsiteAdmin(admin.ModelAdmin):
    pass

class CustomerAdmin(admin.ModelAdmin):
    pass

class HotelAdmin(admin.ModelAdmin):
    pass

class RoomTypeAdmin(admin.ModelAdmin):
    pass

class CommentAdmin(admin.ModelAdmin):
    pass




admin.site.register(CrawlWebsite, CrawlWebsiteAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(Comment, CommentAdmin)
