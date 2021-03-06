import logging

from importlib import import_module
from django.conf.urls import include, url
from django.conf import settings
from cabot.cabotapp.views import (
    run_status_check,
    checks_run_recently,
    duplicate_check,
    HttpCheckCreateView,
    HttpCheckUpdateView,
    JenkinsCheckCreateView,
    JenkinsCheckUpdateView,
    TCPCheckCreateView,
    TCPCheckUpdateView,
    StatusCheckDeleteView,
    StatusCheckListView,
    StatusCheckDetailView,
    AuthComplete,
    LoginError,
    StatusCheckResultDetailView,
    StatusCheckReportView,
    UserProfileUpdateAlert,
    ScheduleCreateView,
    ScheduleListView,
    ScheduleUpdateView,
    ScheduleDeleteView,
    ScheduleSnoozeWarningsView,
    SendTestAlertView,
    AckListView,
    AckCreateView,
    AckUpdateView,
    AckCloseView,
    AckReopenView,
)

from cabot.cabotapp.views import (
    ServiceListView,
    ServiceDetailView,
    ServiceUpdateView,
    ServiceCreateView,
    ServiceDeleteView,
    UserProfileUpdateView,
    ShiftListView,
    subscriptions,
    ActivityCounterView,
)

from cabot.metricsapp.views import (
    GrafanaInstanceSelectView,
    GrafanaDashboardSelectView,
    GrafanaPanelSelectView,
    GrafanaSeriesSelectView,
    GrafanaElasticsearchStatusCheckCreateView,
    GrafanaElasticsearchStatusCheckUpdateView,
    GrafanaElasticsearchStatusCheckRefreshView,
    GrafanaEditView,
)
from cabot import rest_urls

from django.contrib import admin
from django.views.generic.base import RedirectView
from django.contrib.auth.views import (
    login,
    logout,
    password_reset,
    password_reset_done,
    password_reset_confirm,
)
admin.autodiscover()

logger = logging.getLogger(__name__)

urlpatterns = [
    url(r'^$',
        view=RedirectView.as_view(url='services/', permanent=False),
        name='dashboard'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^subscriptions/',
        view=subscriptions,
        name='subscriptions'),
    url(r'^status/',
        view=checks_run_recently,
        name='system-status'),

    url(r'^accounts/login/',
        view=login,
        name='login'),
    url(r'^accounts/logout/',
        view=logout,
        name='logout'),
    url(r'^accounts/password-reset/',
        view=password_reset,
        name='password-reset'),
    url(r'^accounts/password-reset-done/',
        view=password_reset_done,
        name='password-reset-done'),
    url(r'^accounts/password-reset-confirm/',
        view=password_reset_confirm,
        name='password-reset-confirm'),

    url(r'^services/$',
        view=ServiceListView.as_view(),
        name='services'),
    url(r'^service/create/',
        view=ServiceCreateView.as_view(),
        name='create-service'),
    url(r'^service/update/(?P<pk>\d+)/',
        view=ServiceUpdateView.as_view(),
        name='update-service'),
    url(r'^service/delete/(?P<pk>\d+)/',
        view=ServiceDeleteView.as_view(),
        name='delete-service'),
    url(r'^service/(?P<pk>\d+)/',
        view=ServiceDetailView.as_view(),
        name='service'),

    url(r'^checks/$',
        view=StatusCheckListView.as_view(),
        name='checks'),
    url(r'^check/delete/(?P<pk>\d+)/',
        view=StatusCheckDeleteView.as_view(),
        name='delete-check'),
    url(r'^checks/report/$',
        view=StatusCheckReportView.as_view(),
        name='checks-report'),
    url(r'^check/(?P<pk>\d+)/',
        view=StatusCheckDetailView.as_view(),
        name='check'),
    url(r'^check/duplicate/(?P<pk>\d+)/',
        view=duplicate_check,
        name='duplicate-check'),
    url(r'^check/run/(?P<pk>\d+)/',
        view=run_status_check,
        name='run-check'),

    url(r'^httpcheck/create/',
        view=HttpCheckCreateView.as_view(),
        name='create-http-check'),
    url(r'^httpcheck/update/(?P<pk>\d+)/',
        view=HttpCheckUpdateView.as_view(),
        name='update-http-check'),
    url(r'^jenkins_check/create/',
        view=JenkinsCheckCreateView.as_view(),
        name='create-jenkins-check'),
    url(r'^jenkins_check/update/(?P<pk>\d+)/',
        view=JenkinsCheckUpdateView.as_view(),
        name='update-jenkins-check'),
    url(r'^tcpcheck/create/',
        view=TCPCheckCreateView.as_view(),
        name='create-tcp-check'),
    url(r'^tcpcheck/update/(?P<pk>\d+)/',
        view=TCPCheckUpdateView.as_view(),
        name='update-tcp-check'),

    url(r'^result/(?P<pk>\d+)/',
        view=StatusCheckResultDetailView.as_view(),
        name='result'),
    url(r'^shifts/$',
        view=ScheduleListView.as_view(),
        name='shifts'),
    url(r'^shifts/(?P<pk>\d+)/',
        view=ShiftListView.as_view(),
        name='shifts-detail'),

    url(r'^acks/$',
        view=AckListView.as_view(),
        name='acks'),
    url(r'^acks/create$',
        view=AckCreateView.as_view(),
        name='create-ack'),
    url(r'^acks/close/(?P<pk>\d+)$',
        view=AckCloseView.as_view(),
        name='close-ack'),
    url(r'^acks/reopen/(?P<pk>\d+)$',
        view=AckReopenView.as_view(),
        name='reopen-ack'),
    url(r'^acks/update/(?P<pk>\d+)$',
        view=AckUpdateView.as_view(),
        name='update-ack'),

    url(r'^user/(?P<pk>\d+)/profile/$',
        view=UserProfileUpdateView.as_view(),
        name='user-profile'),
    url(r'^user/(?P<pk>\d+)/profile/(?P<alerttype>.+)',
        view=UserProfileUpdateAlert.as_view(),
        name='update-alert-user-data'),

    url(r'^schedule/create/',
        view=ScheduleCreateView.as_view(),
        name='create-schedule'),
    url(r'^schedule/update/(?P<pk>\d+)/',
        view=ScheduleUpdateView.as_view(),
        name='update-schedule'),
    url(r'^schedule/delete/(?P<pk>\d+)/',
        view=ScheduleDeleteView.as_view(),
        name='delete-schedule'),
    url(r'^schedule/snooze/(?P<pk>\d+)/hours/(?P<hours>\d+)/',
        view=ScheduleSnoozeWarningsView.as_view(),
        name='snooze-schedule-warnings'),

    url(r'^grafana/instance/$',
        view=GrafanaInstanceSelectView.as_view(),
        name='grafana-instance-select'),
    url(r'^grafana/dashboard/$',
        view=GrafanaDashboardSelectView.as_view(),
        name='grafana-dashboard-select'),
    url(r'^grafana/panel/$',
        view=GrafanaPanelSelectView.as_view(),
        name='grafana-panel-select'),
    url(r'^grafana/series/$',
        view=GrafanaSeriesSelectView.as_view(),
        name='grafana-series-select'),
    url(r'^grafana/edit/(?P<pk>\d+)/',
        view=GrafanaEditView.as_view(),
        name='grafana-edit'),
    url(r'^grafana/elasticsearch/create/$',
        view=GrafanaElasticsearchStatusCheckCreateView.as_view(),
        name='grafana-es-create'),
    url(r'^grafana/elasticsearch/update/(?P<pk>\d+)/',
        view=GrafanaElasticsearchStatusCheckUpdateView.as_view(),
        name='grafana-es-update'),
    url(r'^grafana/elasticsearch/refresh/(?P<pk>\d+)/',
        view=GrafanaElasticsearchStatusCheckRefreshView.as_view(),
        name='grafana-es-refresh'),
    url(r'^grafana/refresh/(?P<pk>\d+)/',
        view=GrafanaInstanceSelectView.as_view(),
        name='grafana-refresh'),
    url(r'^grafana/dashboard/(?P<pk>\d+)/',
        view=GrafanaDashboardSelectView.as_view(),
        name='grafana-dashboard-select'),
    url(r'^grafana/panel/(?P<pk>\d+)/',
        view=GrafanaPanelSelectView.as_view(),
        name='grafana-panel-select'),
    url(r'^grafana/series/(?P<pk>\d+)/',
        view=GrafanaSeriesSelectView.as_view(),
        name='grafana-series-select'),

    url(r'^api/status-checks/activity-counter(/?)',
        view=ActivityCounterView.as_view(),
        name='activity-counter'),

    url(r'^send-test-alert/(?P<alerttype>.+)/(?P<alert_pk>\d+)/',
        view=SendTestAlertView.as_view(),
        name='send-test-alert'),

    # Comment below line to disable browsable rest api
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(rest_urls.router.urls)),
    url(r'^complete/(?P<backend>[^/]+)/$', AuthComplete.as_view()),
    url(r'^login-error/$', LoginError.as_view()),
    url(r'', include('social_django.urls', namespace='social')),
]


def append_plugin_urls():
    """
    Appends plugin specific URLs to the urlpatterns variable.
    """
    global urlpatterns
    for plugin in settings.CABOT_PLUGINS_ENABLED_PARSED:
        try:
            import_module('%s.urls' % plugin)
        except ImportError:
            pass
        else:
            urlpatterns.append(url(r'^plugins/%s/' % plugin, include('%s.urls' % plugin)))

append_plugin_urls()
