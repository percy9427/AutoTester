from django.contrib import admin

from .models import TesterExternal,TesterProcessingParameters,TestResultsExternal, \
    ColorSheetExternal,TestDefinition,TesterFeatureExternal, \
    LightingConditionsExternal,SwatchExternal,ReagentSetup, \
    JobExternal,HourChoices,TestSchedule,TesterStartupInfo

admin.site.register(TesterExternal)
admin.site.register(TesterProcessingParameters)
admin.site.register(TestResultsExternal)
admin.site.register(ColorSheetExternal)
admin.site.register(TestDefinition)
admin.site.register(TesterFeatureExternal)
admin.site.register(LightingConditionsExternal)
admin.site.register(SwatchExternal)
admin.site.register(ReagentSetup)
admin.site.register(JobExternal)
admin.site.register(HourChoices)
admin.site.register(TestSchedule)
admin.site.register(TesterStartupInfo)
