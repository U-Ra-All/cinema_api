from rest_framework import routers


from cinema.views import (
    GenreViewSet,
)

router = routers.DefaultRouter()
router.register("genres", GenreViewSet)


urlpatterns = router.urls

app_name = "cinema"
