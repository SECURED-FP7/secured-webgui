from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from webContent import views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/login/')),
	url(r'^login/$', views.login),
	url(r'^logout/$', views.logout),
	url(r'^app/$', views.app),
    url(r'^app/mspl/$', views.app_mspl),
	url(r'^store/$', views.store),
	url(r'^upload/$', views.user_image_upload),
    url(r'^hspl/$', views.hspl),
    url(r'^hspl/new/$', views.hspl_new),
    url(r'^hspl/delete/$', views.hspl_delete),
    url(r'^mspl/$', views.mspl),
    url(r'^mspl/delete/$', views.mspl_delete),
    url(r'^mspl/id/$', views.mspl_id),
    url(r'^mspl/validate/$', views.mspl_validate),
    url(r'^mspl/sfa/$', views.sfa_validate),
    url(r'^users/$', views.users),
    url(r'^capability/$', views.capability),
    url(r'^optimization/$', views.optimization),
    url(r'^IFA/$', views.ifa),
    url(r'^MIFA/$', views.mifa)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
