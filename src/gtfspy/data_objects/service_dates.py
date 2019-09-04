import datetime

from .base_object import BaseGtfsObjectCollection
from ..utils.validating import not_none_or_empty
from ..utils.parsing import int_or_string_id


class ServiceDate(object):
    def __init__(self, transit_data, service_id, date, exception_type, **kwargs):
        """
        :type service_id: str | int
        :type date_: date | str
        :type exception_type: bool | int
        """

        self.service_id = int_or_string_id(service_id)
        self.service = transit_data.calendar[self.service_id]
        self.date = date if isinstance(date, datetime.date) else datetime.datetime.strptime(date, "%Y%m%d").date()
        if isinstance(exception_type, bool):
            self.exception_type = 1 if exception_type else 2
        else:
            self.exception_type = int(exception_type)
        self.attributes = {k: v for k, v in kwargs.items() if not_none_or_empty(v)}

    def get_csv_fields(self):
        return ["service_id", "date", "exception_type"] + list(self.attributes.keys())

    def to_csv_line(self):
        return dict(service_id=self.service_id,
                    date=self.date.strftime("%Y%m%d"),
                    exception_type=self.exception_type,
                    **self.attributes)

    def validate(self, transit_data):
        """
        :type transit_data: transit_data_object.TransitData
        """
        pass

    def __eq__(self, other):
        if not isinstance(other, ServiceDate):
            return False

        return self.service == other.service and self.date == other.date and \
            self.exception_type == other.exception_type and self.attributes == other.attributes

    def __ne__(self, other):
        return not (self == other)


class ServiceDateCollection(BaseGtfsObjectCollection):
    def __init__(self, transit_data, csv_file=None):
        BaseGtfsObjectCollection.__init__(self, transit_data, ServiceDate)

        if csv_file is not None:
            self._load_file(csv_file)

    def add(self, ignore_errors=False, condition=None, **kwargs):
        try:
            service_date = ServiceDate(transit_data=self._transit_data, **kwargs)

            if condition is not None and not condition(service_date):
                return None

            self._transit_data._changed()

            service_date.service.special_dates.append(service_date)

            key = (service_date.service_id, service_date.date)
            assert key not in self._objects

            self._objects[key] = service_date
            return service_date
        except:
            if not ignore_errors:
                raise

    def add_object(self, service_date, recursive=False):
        assert isinstance(service_date, ServiceDate)
        key = (service_date.service_id, service_date.date)

        if key not in self._objects:
            return self.add(**service_date.to_csv_line())
        else:
            old_service = self[service_date.id]
            assert service_date == old_service
            return old_service