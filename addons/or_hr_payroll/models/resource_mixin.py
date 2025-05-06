from collections import defaultdict
from datetime import timedelta
from pytz import utc
from orj import api, fields, models, tools, _
from orj.tools import float_utils

ROUNDING_FACTOR = 16


class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def _get_work_days_data(self, fror_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not fror_datetime.tzinfo:
            fror_datetime = fror_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        fror_full = fror_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals_batch(fror_full, to_full, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        if compute_leaves:
            intervals = calendar._work_intervals_batch(fror_datetime, to_datetime, resource, domain)
        else:
            intervals = calendar._attendance_intervals_batch(fror_datetime, to_datetime, resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # compute number of days as quarters
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return {
            'days': days,
            'hours': sum(day_hours.values()),
        }
