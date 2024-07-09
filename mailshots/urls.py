from django.urls import path
from mailshots import views


app_name = "mailshots"

urlpatterns = [


    # crud клиента
    path("clients/", views.ClientListView.as_view(), name="clients_list"),
    path("clients/create/", views.ClientCreateView.as_view(), name="clients_create"),
    path("clients/<int:pk>/update/", views.ClientUpdateView.as_view(), name="clients_update"),
    path("clients/<int:pk>/detail/", views.ClientDetailView.as_view(), name="clients_detail"),
    path("clients/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="clients_delete"),

    # просмотр логов
    path("<int:mailshot_pk>/logs/list/", views.LogListView.as_view(), name="logs_list"),
    path("<int:mailshot_pk>/logs/<int:pk>/detail/", views.LogDetailView.as_view(), name="logs_detail"),

    # manager
    path("manager/list/<str:status>/", views.ManagerMailshotListView.as_view(), name="manager_list"),
    path("manager/detail/<int:pk>/", views.ManagerMailshotDetailView.as_view(), name="manager_detail"),
    path("manager/disable/<int:pk>/", views.ManagerMailshotDisableUpdateView.as_view(), name="manager_disable"),

    # crud рассылки
    path("create/<str:step>/", views.MailshotWizardCreateView.as_view(url_name="mailshots:create"), name="create"),
    path("<int:pk>/update/<str:step>/", views.MailshotWizardUpdateView.as_view(url_name="mailshots:update"),
         name="update"),
    path("<int:pk>/detail/", views.MailshotDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.MailshotDeleteView.as_view(), name="delete"),
    path('<str:status>/', views.MailshotListView.as_view(), name='list'),
    path("<int:pk>/enable/", views.EnableMailshotUpdateView.as_view(), name="enable"),
    path("<int:pk>/disable/", views.DisableMailshotView.as_view(), name="disable"),
]
