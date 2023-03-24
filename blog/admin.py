from django.contrib import admin
from .models import Post, Profile

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status','created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',),}

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('blogger', 'slug', 'preview', 'picture')
    list_filter = ("blogger",)
    search_fields = ['blogger', 'about']
    prepopulated_fields = {'slug': ('blogger',),}

admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
