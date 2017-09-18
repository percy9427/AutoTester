from django.contrib import admin
from django.contrib.admin import AdminSite
# Register your models here.
from .models import TesterExternal,TesterProcessingParameters,TestResultsExternal, \
    ColorSheetExternal,TestDefinition,TesterFeatureExternal, \
    LightingConditionsExternal,SwatchExternal,ReagentSetup, \
    JobExternal,HourChoices,TestSchedule

admin.site.register(TesterExternal)
admin.site.register(TesterProcessingParameters)
admin.site.register(TestResultsExternal)
admin.site.register(ColorSheetExternal)
#admin.site.register(TestDefinition)
admin.site.register(TesterFeatureExternal)
admin.site.register(LightingConditionsExternal)
admin.site.register(SwatchExternal)
#admin.site.register(ReagentSetup)
admin.site.register(JobExternal)
admin.site.register(HourChoices)
admin.site.register(TestSchedule)

class TestSetup(admin.ModelAdmin):
    pass

class ReagentConfig(admin.ModelAdmin):
    pass

admin.site.register(TestDefinition,TestSetup)
admin.site.register(ReagentSetup,ReagentConfig)

class ConfigureSite(AdminSite):
    site_header='Configure Site'
    
configure_admin=ConfigureSite(name='configure')
configure_admin.register(TestDefinition,TestSetup)
configure_admin.register(ReagentSetup,ReagentConfig)

