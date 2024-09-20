from django.contrib import admin
from .models import District, Place ,PlaceImage,UserProfile

# Register the models so they appear in the admin interface
admin.site.register(District)
admin.site.register(Place)
admin.site.register(PlaceImage)

class UserProfileAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for user in qs:
            if hasattr(user, 'userprofile'):
                # Access userprofile attributes here
                pass
        return qs

admin.site.register(UserProfile, UserProfileAdmin)



