from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, TemplateView
from cabot.cabotapp.views import LoginRequiredMixin
from cabot.metricsapp.api import get_dashboard_info, get_dashboards, get_dashboard_choices, get_panel_choices, \
    get_series_choices, create_generic_templating_dict, get_panel_url
from cabot.metricsapp.forms import GrafanaInstanceForm, GrafanaDashboardForm, GrafanaPanelForm, \
    GrafanaSeriesForm
from cabot.metricsapp.models import GrafanaDataSource, ElasticsearchSource, GrafanaInstance, MetricsStatusCheckBase


class GrafanaInstanceSelectView(LoginRequiredMixin, View):
    form_class = GrafanaInstanceForm
    template_name = 'metricsapp/grafana_create.html'

    def get(self, request, *args, **kwargs):
        # Save the panel id/check id in the session if they exist
        default_instance = None
        pk = kwargs.get('pk')
        if pk is not None and MetricsStatusCheckBase.objects.filter(id=pk).exists():
            grafana_panel = MetricsStatusCheckBase.objects.get(id=pk).grafana_panel
            default_instance = grafana_panel.grafana_instance

        instances = GrafanaInstance.objects.all()
        # If there's only one Grafana instance, we can skip this step and just select it
        if len(instances) == 1:
            instance = instances[0]
            request.session['instance_id'] = instance.id
            request.session['all_dashboards'] = get_dashboards(instance)

            return HttpResponseRedirect(reverse('grafana-dashboard-select', kwargs=kwargs))

        form = self.form_class(default_grafana_instance=default_instance)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, default_grafana_instance=None)

        if form.is_valid() and not form.errors:
            instance = form.cleaned_data['grafana_instance']
            request.session['instance_id'] = instance.id
            request.session['all_dashboards'] = get_dashboards(instance)

            return HttpResponseRedirect(reverse('grafana-dashboard-select', kwargs=kwargs))

        return render(request, self.template_name, {'form': form})


class GrafanaDashboardSelectView(LoginRequiredMixin, View):
    form_class = GrafanaDashboardForm
    template_name = 'metricsapp/grafana_create.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        default_dashboard = None
        if pk is not None and MetricsStatusCheckBase.objects.filter(id=pk).exists():
            default_dashboard = MetricsStatusCheckBase.objects.get(id=pk).grafana_panel.dashboard_uri

        form = self.form_class(dashboards=get_dashboard_choices(request.session['all_dashboards']),
                               default_dashboard=default_dashboard)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, dashboards=get_dashboard_choices(request.session['all_dashboards']),
                               default_dashboard=None)

        if form.is_valid() and not form.errors:
            dashboard_uri = form.cleaned_data['dashboard']
            instance_id = request.session['instance_id']
            instance = GrafanaInstance.objects.get(id=instance_id)

            dashboard_info = get_dashboard_info(instance, dashboard_uri)
            request.session['dashboard_uri'] = dashboard_uri
            request.session['dashboard_info'] = dashboard_info
            request.session['dashboard_uri'] = dashboard_uri
            request.session['templating_dict'] = create_generic_templating_dict(dashboard_info)

            return HttpResponseRedirect(reverse('grafana-panel-select', kwargs=kwargs))

        return render(request, self.template_name, {'form': form})


class GrafanaPanelSelectView(LoginRequiredMixin, View):
    form_class = GrafanaPanelForm
    template_name = 'metricsapp/grafana_create.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        grafana_instance_id = request.session['instance_id']
        default_panel_id = None
        if pk is not None and MetricsStatusCheckBase.objects.filter(id=pk).exists():
            default_panel_id = MetricsStatusCheckBase.objects.get(id=pk).grafana_panel.panel_id

        form = self.form_class(panels=get_panel_choices(request.session['dashboard_info'],
                                                        request.session['templating_dict'],
                                                        grafana_instance_id),
                               default_panel_id=default_panel_id)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        grafana_instance_id = request.session['instance_id']
        form = self.form_class(request.POST, panels=get_panel_choices(request.session['dashboard_info'],
                                                                      request.session['templating_dict'],
                                                                      grafana_instance_id),
                               default_panel_id=None)
        if form.is_valid() and not form.errors:
            panel_dict = form.cleaned_data['panel']
            request.session['panel_id'] = panel_dict['panel_id']
            request.session['datasource'] = panel_dict['datasource']
            request.session['panel_info'] = panel_dict['panel_info']

            return HttpResponseRedirect(reverse('grafana-series-select', kwargs=kwargs))

        return render(request, self.template_name, {'form': form})


class GrafanaSeriesSelectView(LoginRequiredMixin, View):
    form_class = GrafanaSeriesForm
    template_name = 'metricsapp/grafana_create.html'

    def get(self, request, *args, **kwargs):
        templating_dict = request.session['templating_dict']
        series = get_series_choices(request.session['panel_info'], templating_dict)
        pk = kwargs.get('pk', None)

        # If there's only one series, skip the page and just select it
        if len(series) == 1:
            request.session['series'] = [series[0][0]]

            if pk is not None and MetricsStatusCheckBase.objects.filter(id=pk).exists():
                check = MetricsStatusCheckBase.objects.get(id=pk)
                url = check.refresh_url
            else:
                instance_id = request.session['instance_id']
                datasource = request.session['datasource']
                url = self.get_url_for_check_type(instance_id, datasource)

            return HttpResponseRedirect(reverse(url, kwargs=kwargs))

        default_series = None
        if pk is not None and MetricsStatusCheckBase.objects.filter(id=pk).exists():
            default_series = MetricsStatusCheckBase.objects.get(id=pk).grafana_panel.selected_series.split('_')

        form = self.form_class(series=series, default_series=default_series)

        panel_url = get_panel_url(GrafanaInstance.objects.get(id=request.session['instance_id']).url,
                                  request.session['dashboard_uri'],
                                  request.session['panel_id'],
                                  templating_dict)

        return render(request, self.template_name, {'form': form, 'check_type': 'Elasticsearch',
                                                    'panel_url': panel_url})

    def post(self, request, *args, **kwargs):
        templating_dict = request.session['templating_dict']
        form = self.form_class(request.POST, series=get_series_choices(request.session['panel_info'],
                                                                       templating_dict),
                               default_series=None)
        if form.is_valid() and not form.errors:
            series = form.cleaned_data['series']
            request.session['series'] = series

            instance_id = request.session['instance_id']
            datasource = request.session['datasource']
            url = self.get_url_for_check_type(instance_id, datasource)

            pk = kwargs.get('pk')
            if pk is not None and MetricsStatusCheckBase.objects.filter(id=pk).exists():
                check = MetricsStatusCheckBase.objects.get(id=pk)
                url = check.refresh_url

            return HttpResponseRedirect(reverse(url, kwargs=kwargs))

        panel_url = get_panel_url(GrafanaInstance.objects.get(id=request.session['instance_id']).url,
                                  request.session['dashboard_uri'],
                                  request.session['panel_id'],
                                  templating_dict)
        return render(request, self.template_name, {'form': form, 'panel_url': panel_url})

    def get_url_for_check_type(self, instance_id, datasource):
        """
        Based on the instance id and the datasource, find the metrics source type and the
        url for creating a check.
        :param instance_id: id of the Grafana instance
        :param datasource: name of the datasource in Grafana
        :return: url for the chosen status type check
        """
        instance = GrafanaInstance.objects.get(id=instance_id)
        grafana_datasource = GrafanaDataSource.objects.get(grafana_source_name=datasource,
                                                           grafana_instance=instance)

        # Pick which page to go to based on the panel chosen
        if ElasticsearchSource.objects.filter(id=grafana_datasource.metrics_source_base.id).exists():
            url = 'grafana-es-create'
        else:
            raise NotImplementedError('Check type for data source {} not implemented'.format(datasource))

        return url


class GrafanaEditView(LoginRequiredMixin, TemplateView):
    template_name = 'metricsapp/grafana_edit.html'

    def get_context_data(self, **kwargs):
        context = super(GrafanaEditView, self).get_context_data(**kwargs)
        pk = kwargs['pk']
        context['pk'] = pk
        context['update_url'] = MetricsStatusCheckBase.objects.get(id=pk).metrics_update_url
        return context
