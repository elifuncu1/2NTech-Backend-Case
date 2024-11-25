from django.contrib.auth.decorators import user_passes_test
def user_required():
    return user_passes_test(lambda u: not u.is_superuser, login_url='/')