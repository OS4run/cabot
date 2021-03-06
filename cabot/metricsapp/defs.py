# Constant definitions

ES_SUPPORTED_METRICS = set(['min', 'max', 'avg', 'value_count', 'sum', 'cardinality', 'moving_avg',
                            'derivative', 'percentiles'])

ES_VALIDATION_MSG_PREFIX = 'Elasticsearch query format error'

ES_TIME_RANGE = 'now-10m'

ES_DEFAULT_INTERVAL = '1m'

ES_SOFT_MAX_RESPONSE_SIZE_BYTES = 1000000

ES_HARD_MAX_RESPONSE_SIZE_BYTES = 10000000

ES_MAX_TERMS_SIZE = 500

GRAFANA_SYNC_TIMEDELTA_MINUTES = 30

HIDDEN_METRIC_SUFFIX = 'hidethismetric'

ALIAS_DELIMITER = ': '

GRAFANA_RENDERED_IMAGE_HEIGHT = 1000

GRAFANA_RENDERED_IMAGE_WIDTH = 2000

GRAFANA_REQUEST_TIMEOUT_S = 10

METRIC_STATUS_TIME_RANGE_DEFAULT = 30

SCHEDULE_PROBLEMS_EMAIL_SNOOZE_HOURS = [4, 12, 24]  # which "silence for" links are shown in schedule problems emails

ON_EMPTY_SERIES_PASS = 'pass'
ON_EMPTY_SERIES_WARN = 'warn'
ON_EMPTY_SERIES_FAIL = 'fail'
ON_EMPTY_SERIES_FILL_ZERO = 'fill_zero'

ON_EMPTY_SERIES_OPTIONS = (
    (ON_EMPTY_SERIES_PASS, 'Pass'),
    (ON_EMPTY_SERIES_WARN, 'Warn'),
    (ON_EMPTY_SERIES_FAIL, 'Fail (error/critical)'),
    (ON_EMPTY_SERIES_FILL_ZERO, 'Fill zero'),
)
