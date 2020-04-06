from django.urls import path
from rest_framework.routers import SimpleRouter

from api.views import get_provinces, get_district, AgentViewSet, HouseTypeViewSet, EstateViewSet, TagViewSet, \
    HouseInfoViewSet, HotCityView, login, get_code_by_sms, UserViewSet

urlpatterns = [
    # path('payments/<int:houseid>/', get_payment_page),
    # path('photos/', upload_house_photo),
    path('token/', login),
    path('mobile/<str:tel>/', get_code_by_sms),
    path('districts/', get_provinces),
    path('districts/<int:distid>/', get_district),
    # path('agents/', AgentView.as_view()),
    # path('agents/<int:pk>/', AgentView.as_view()),
    path('hotcities/', HotCityView.as_view()),
]
router = SimpleRouter()
router.register('housetypes', HouseTypeViewSet)
router.register('estates', EstateViewSet)
router.register('agents', AgentViewSet)
router.register('tags', TagViewSet)
router.register('houseinfos', HouseInfoViewSet)
router.register('users', UserViewSet)

urlpatterns += router.urls