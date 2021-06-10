from polls.api.v1 import views as api_v1
from rest_framework import routers

router = routers.SimpleRouter()
router.register('', api_v1.PollViewSet)
urlpatterns = router.urls
