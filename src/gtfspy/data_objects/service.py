import csv
from datetime import datetime

from gtfspy.data_objects.base_object import BaseGtfsObjectCollection
from gtfspy.utils.parsing import parse_or_default, str_to_bool
from gtfspy.utils.validating import not_none_or_empty


class Service:
    def __init__(self, service_id, start_date, end_date, sunday=None, monday=None, tuesday=None, wednesday=None,
                 thursday=None, friday=None, saturday=None, **kwargs):
        """
        :type service_id: str | int
        :type start_date: datetime | str
        :type end_date: datetime | str
        :type sunday: str | bool | None
        :type monday: str | bool | None
        :type tuesday: str | bool | None
        :type wednesday: str | bool | None
        :type thursday: str | bool | None
        :type friday: str | bool | None
        :type saturday: str | bool | None
        """

        self.service_id = int(service_id)
        self.start_date = start_date if isinstance(start_date, datetime) else datetime.strptime(start_date, "%Y%m%d").date()
        self.end_date = end_date if isinstance(end_date, datetime) else datetime.strptime(end_date, "%Y%m%d").date()
        sunday = parse_or_default(sunday, False, str_to_bool)
        monday = parse_or_default(monday, False, str_to_bool)
        tuesday = parse_or_default(tuesday, False, str_to_bool)
        wednesday = parse_or_default(wednesday, False, str_to_bool)
        thursday = parse_or_default(thursday, False, str_to_bool)
        friday = parse_or_default(friday, False, str_to_bool)
        saturday = parse_or_default(saturday, False, str_to_bool)
        self.days_relevance = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]

        self.attributes = {k: v for k, v in kwargs.iteritems() if not_none_or_empty(v)}

    @property
    def sunday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[0]

    @sunday.setter
    def sunday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[0] = value

    @property
    def monday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[1]

    @monday.setter
    def monday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[1] = value

    @property
    def tuesday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[2]

    @tuesday.setter
    def tuesday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[2] = value

    @property
    def wednesday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[3]

    @wednesday.setter
    def wednesday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[3] = value

    @property
    def thursday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[4]

    @thursday.setter
    def thursday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[4] = value

    @property
    def friday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[5]

    @friday.setter
    def friday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[5] = value

    @property
    def saturday(self):
        """
        :rtype: bool
        """

        return self.days_relevance[6]

    @saturday.setter
    def saturday(self, value):
        """
        :type value: bool
        """

        self.days_relevance[6] = value

    def is_active_on(self, date):
        """
        :rtype: bool
        """

        return self.days_relevance[date.isoweekday() % 7]

    def get_csv_fields(self):
        return ["service_id", "start_date", "end_date", "sunday", "monday", "tuesday", "wednesday", "thursday",
                "friday", "saturday"] + self.attributes.keys()

    def to_csv_line(self):
        return dict(service_id=self.service_id,
                    start_date=self.start_date.strftime("%Y%m%d"),
                    end_date=self.end_date.strftime("%Y%m%d"),
                    sunday=int(self.sunday),
                    monday=int(self.monday),
                    tuesday=int(self.tuesday),
                    wednesday=int(self.wednesday),
                    thursday=int(self.thursday),
                    friday=int(self.friday),
                    saturday=int(self.saturday),
                    **self.attributes)

    def validate(self, transit_data):
        """
        :type transit_data: transit_data_object.TransitData
        """

        pass

    def __eq__(self, other):
        if not isinstance(other, Service):
            return False

        return self.service_id == other.service_id and self.start_date == other.start_date and \
               self.end_date == other.end_date and self.days_relevance == other.days_relevance and \
               self.attributes == other.attributes

    def __ne__(self, other):
        return not (self == other)


class ServiceCollection(BaseGtfsObjectCollection):
    def __init__(self, transit_data, csv_file=None):
        BaseGtfsObjectCollection.__init__(self, transit_data)

        if csv_file is not None:
            self._load_file(csv_file)

    def add_service(self, ignore_errors=False, condition=None, **kwargs):
        try:
            service = Service(**kwargs)

            if condition is not None and not condition(service):
                return None

            self._transit_data._changed()

            assert service.service_id not in self._objects
            self._objects[service.service_id] = service
            return service
        except:
            if not ignore_errors:
                raise

    def remove(self, service, recursive=False, clean_after=True):
        if not isinstance(service, Service):
            service = self[service]
        else:
            assert self[service.service_id] is service

        if recursive:
            for trip in self._transit_data.trips:
                if trip.service is service:
                    self._transit_data.trips.remove(trip, recursive=True, clean_after=False)
        else:
            assert next((trip for trip in self._transit_data.trips if trip.service is service), None) is None

        del self._objects[service.service_id]

        if clean_after:
            self._transit_data.clean()

    def clean(self):
        to_clean = []
        for service in self:
            if next((trip for trip in self._transit_data.trips if trip.service is service), None) is None:
                to_clean.append(service)

        for service in to_clean:
            del self._objects[service.service_id]

    def _load_file(self, csv_file, ignore_errors=False, filter=None):
        if isinstance(csv_file, str):
            with open(csv_file, "rb") as f:
                self._load_file(f, ignore_errors=ignore_errors, filter=filter)
        else:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.add_service(ignore_errors=ignore_errors, condition=filter, **row)

    def validate(self):
        for i, obj in self._objects.iteritems():
            assert i == obj.service_id
            obj.validate(self._transit_data)
