from django.contrib import admin
from .models import (
    Price,
    Class,
    HistoryPredictions,
    Predictions,
    CustomUser,
    HistoryPrompt,
    Role,
    Style,
)

# Register models
admin.site.register(CustomUser)
admin.site.register(Price)
admin.site.register(Class)
admin.site.register(HistoryPredictions)
admin.site.register(Predictions)
admin.site.register(HistoryPrompt)  
admin.site.register(Role)          
admin.site.register(Style)  