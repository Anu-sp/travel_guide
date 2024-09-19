from django.contrib import admin
from .models import District, Place ,PlaceImage

# Register the models so they appear in the admin interface
admin.site.register(District)
admin.site.register(Place)
admin.site.register(PlaceImage)




