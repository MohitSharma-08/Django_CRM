from settings.models import AppSetting

def app_settings(request):
    # This ensures that even if no settings are created, the site doesn't crash
    setting = AppSetting.objects.first() 
    return {
        'app_setting': setting
    }