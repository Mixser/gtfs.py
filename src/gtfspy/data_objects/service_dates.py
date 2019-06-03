import datetime
from ..utils.validating import not_none_or_empty


class ServiceDate(object):
    def __init__(self, transit_data, service_id, date, exception_type, **kwargs):
        """
        :type service_id: str | int
        :type date_: date | str
        :type exception_type: bool | int
        """

        self.service_id = int(service_id)
        self.service = transit_data.calendar[service_id]
        self.date = date if isinstance(date, datetime.date) else datetime.datetime.strptime(date_, "%Y%m%d").date()
        if isinstance(exception_type, bool):
            self.exception_type = 1 if exception_type else 2
        else:
            self.exception_type = exception_type
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
