from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from cabot.metricsapp.api import build_query, template_response, validate_query, \
    create_elasticsearch_templating_dict, get_es_status_check_fields, adjust_time_range
from cabot.metricsapp.models import ElasticsearchSource, ElasticsearchStatusCheck, GrafanaInstance, GrafanaPanel
from .test_elasticsearch import get_json_file


class TestGrafanaQueryBuilder(TestCase):
    maxDiff = None

    def test_grafana_query(self):
        """Basic query building"""
        series = get_json_file('grafana/query_builder/grafana_series.json')
        created_query = build_query(series, min_time='now-1h')
        expected_query = get_json_file('grafana/query_builder/grafana_series_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)

    def test_multiple_aggs(self):
        """Multiple terms aggregations"""
        series = get_json_file('grafana/query_builder/grafana_series_terms.json')
        created_query = build_query(series, min_time='now-100m')
        expected_query = get_json_file('grafana/query_builder/grafana_series_terms_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)

    def test_order_by_sub_agg(self):
        """Order by sub-aggregations"""
        series = get_json_file('grafana/query_builder/grafana_series_order_sub_agg.json')
        created_query = build_query(series, min_time='now-100m')
        expected_query = get_json_file('grafana/query_builder/grafana_series_order_sub_agg_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)

    def test_count(self):
        """Count metrics get converted to value_count(timeField)"""
        series = get_json_file('grafana/query_builder/grafana_series_count.json')
        created_query = build_query(series, min_time='now-3d')
        expected_query = get_json_file('grafana/query_builder/grafana_series_count_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)

    def test_multiple_metrics(self):
        """Multiple metrics (for example, sum and avg)"""
        series = get_json_file('grafana/query_builder/grafana_multiple_metrics.json')
        created_query = build_query(series, min_time='now-30m')
        expected_query = get_json_file('grafana/query_builder/grafana_multiple_metrics_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)

    def test_histogram_agg(self):
        """histogram aggregation"""
        series = get_json_file('grafana/query_builder/grafana_histogram_agg.json')
        created_query = build_query(series, min_time='now-1h')
        expected_query = get_json_file('grafana/query_builder/grafana_histogram_agg_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(expected_query)

    def test_filters_agg(self):
        """filter aggregation"""
        series = get_json_file('grafana/query_builder/grafana_filters_agg.json')
        created_query = build_query(series, min_time='now-1h')
        expected_query = get_json_file('grafana/query_builder/grafana_filters_agg_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(expected_query)

    def test_no_date_histogram(self):
        """If there's no date_histogram agg, raise an exception"""
        series = get_json_file('grafana/query_builder/grafana_no_date_histogram.json')
        with self.assertRaises(ValidationError) as e:
            build_query(series, min_time='now-30m')
            self.assertEqual(e.exception, 'Dashboard must include a date histogram aggregation.')

    def test_unsupported_aggregation(self):
        """Exceptions raised for aggs that aren't supported"""
        series = get_json_file('grafana/query_builder/grafana_geo_hash_grid.json')
        with self.assertRaises(ValidationError) as e:
            build_query(series, min_time='now-30m')
            self.assertEqual(e.exception, 'geohash_grid aggregation not supported.')

    def test_get_es_status_check_fields(self):
        dashboard_info = get_json_file('../grafana/dashboard_detail_response.json')

        status_check_fields = []
        for row in dashboard_info['dashboard']['rows']:
            for panel in row['panels']:
                status_check_fields.append(get_es_status_check_fields(dashboard_info, panel, ['B']))

        expected_queries = get_json_file('grafana/query_builder/get_es_status_check_fields_queries.json')
        expected_fields = [dict(queries=expected_queries[0])]
        # Second panel doesn't have a 'B' series
        expected_fields.append(dict())
        expected_fields.append(dict(queries=expected_queries[1]))

        self.assertEqual(status_check_fields, expected_fields)

    def test_adjust_time_range(self):
        queries = [get_json_file('grafana/query_builder/grafana_series_query.json')]
        new_queries = adjust_time_range(queries, 30)
        expected_queries = [get_json_file('grafana/query_builder/grafana_series_query_30m.json')]
        self.assertEqual(new_queries, expected_queries)

    def test_derivative_adjusted(self):
        """
        Derivative metric with hidden field. Should add 1 * interval (1m) to the time range to
        prevent issues with partial points being used to calculate the derivative.
        """
        series = get_json_file('grafana/query_builder/grafana_derivative.json')
        created_query = adjust_time_range([build_query(series, min_time='now-3h')], 180)[0]
        expected_query = get_json_file('grafana/query_builder/grafana_adjusted_derivative_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)

    def test_moving_avg_adjusted(self):
        """
        Moving average metric with hidden field. Should add interval (5m) * moving average range (10)
        to the time range to prevent partial points.
        """
        series = get_json_file('grafana/query_builder/grafana_moving_avg.json')
        created_query = adjust_time_range([build_query(series, min_time='now-3h')], 180)[0]
        expected_query = get_json_file('grafana/query_builder/grafana_adjusted_moving_avg_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)


class TestGrafanaTemplating(TestCase):
    def test_templating(self):
        """Test Grafana panel templating handling"""
        templates = get_json_file('grafana/templating/templating_info.json')
        templating_dict = create_elasticsearch_templating_dict(templates)

        panel_info = get_json_file('grafana/templating/templating_panel.json')
        expected_panel = get_json_file('grafana/templating/templating_panel_final.json')

        templated_panel = template_response(panel_info, templating_dict)
        self.assertEqual(templated_panel, expected_panel)

        # Make sure we can make a valid query from the output
        query = build_query(templated_panel, min_time='now-1h')
        validate_query(query)

    def test_auto_time_field(self):
        """Make sure 'auto' fields are getting templated correctly"""
        templates = get_json_file('grafana/templating/auto_time_templating.json')
        templating_dict = create_elasticsearch_templating_dict(templates)

        panel = get_json_file('grafana/templating/auto_time_panel.json')
        templated_panel = template_response(panel, templating_dict)

        created_query = build_query(templated_panel, default_interval='2m')
        expected_query = get_json_file('grafana/templating/auto_time_panel_query.json')
        self.assertEqual(expected_query, created_query)
        validate_query(created_query)


class TestElasticsearchCheckGrafanaPanel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user')
        self.es_source = ElasticsearchSource.objects.create(
            name='es',
            urls='localhost',
            index='test-index-pls-ignore'
        )
        self.grafana_instance = GrafanaInstance.objects.create(
            name='graf',
            url='graf',
            api_key='graf'
        )
        self.panel = GrafanaPanel.objects.create(
            grafana_instance=self.grafana_instance,
            panel_id=1,
            dashboard_uri='db/42',
            series_ids='B',
            selected_series='B'
        )
        self.es_check = ElasticsearchStatusCheck.objects.create(
            name='checkycheck',
            created_by=self.user,
            source=self.es_source,
            check_type='>=',
            warning_value=3.5,
            high_alert_importance='CRITICAL',
            high_alert_value=3.0,
            queries='[{"query": {"bool": {"must": [{"query_string": {"analyze_wildcard": true, '
                    '"query": "test.query"}}, {"range": {"@timestamp": {"gte": "now-300m"}}}]}}, '
                    '"aggs": {"agg": {"terms": {"field": "outstanding"}, '
                    '"aggs": {"agg": {"date_histogram": {"field": "@timestamp", "interval": "1m", '
                    '"extended_bounds": {"max": "now", "min": "now-3h"}}, '
                    '"aggs": {"sum": {"sum": {"field": "count"}}}}}}}}]',
            grafana_panel=self.panel,
            time_range=10000
        )

    def test_duplicate(self):
        self.es_check.duplicate()
        old_check = ElasticsearchStatusCheck.objects.get(name='checkycheck')
        new_check = ElasticsearchStatusCheck.objects.get(name='Copy of checkycheck')
        self.assertNotEqual(old_check.pk, new_check.pk)
        self.assertNotEqual(old_check.grafana_panel.pk, new_check.grafana_panel.pk)
