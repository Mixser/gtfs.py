import csv

import gtfspy
from gtfspy.data_objects.base_object import BaseGtfsObjectCollection
from gtfspy.utils.parsing import parse_yes_no_unknown, yes_no_unknown_to_int
from gtfspy.utils.validating import not_none_or_empty, validate_true_false, validate_yes_no_unknown


class Stop:
    def __init__(self, transit_data, stop_id, stop_name, stop_lat, stop_lon, stop_code=None, stop_desc=None,
                 zone_id=None, stop_url=None, location_type=None, parent_station=None, stop_timezone=None,
                 wheelchair_boarding=None, **kwargs):
        """
        :type transit_data: gtfspy.transit_data_object.TransitData
        :type stop_id: str | int
        :type stop_name: str
        :type stop_lat: str | float
        :type stop_lon: str | float
        :type stop_code: str | None
        :type stop_desc: str | None
        :type zone_id: str | int | None
        :type stop_url: str | None
        :type location_type: str | bool | None
        :type parent_station: str | int | None
        :type stop_timezone: str | None
        :type wheelchair_boarding: str | int | None
        """

        self.stop_id = int(stop_id)
        self.stop_name = stop_name
        self.stop_lat = float(stop_lat)
        self.stop_lon = float(stop_lon)

        self.attributes = {k: v for k, v in kwargs.iteritems() if not_none_or_empty(v)}
        if not_none_or_empty(stop_code):
            self.attributes["stop_code"] = str(stop_code)
        if not_none_or_empty(stop_desc):
            self.attributes["stop_desc"] = str(stop_desc)
        if not_none_or_empty(zone_id):
            self.attributes["zone_id"] = int(zone_id)
        if not_none_or_empty(stop_url):
            self.attributes["stop_url"] = str(stop_url)
        if not_none_or_empty(location_type):
            self.attributes["location_type"] = int(location_type)
        if not_none_or_empty(parent_station):
            # TODO: save the station object instead of the id
            self.attributes["parent_station"] = int(parent_station)
        if not_none_or_empty(stop_timezone):
            self.attributes["stop_timezone"] = str(stop_timezone)
        if not_none_or_empty(wheelchair_boarding):
            self.attributes["wheelchair_boarding"] = int(wheelchair_boarding)

        self.stop_times = []

    @property
    def stop_code(self):
        """
        :rtype: str | None
        """

        return self.attributes.get("stop_code", None)

    @stop_code.setter
    def stop_code(self, value):
        """
        :type value: str | None
        """

        self.attributes["stop_code"] = value

    @property
    def stop_desc(self):
        """
        :rtype: str | None
        """

        return self.attributes.get("stop_desc", None)

    @stop_desc.setter
    def stop_desc(self, value):
        """
        :type value: str | None
        """

        self.attributes["stop_desc"] = value

    @property
    def zone_id(self):
        """
        :rtype: int | None
        """

        return self.attributes.get("zone_id", None)

    @zone_id.setter
    def zone_id(self, value):
        """
        :type value: int | None
        """

        self.attributes["zone_id"] = value

    @property
    def stop_url(self):
        """
        :rtype: str | None
        """

        return self.attributes.get("stop_url", None)

    @stop_url.setter
    def stop_url(self, value):
        """
        :type value: str | None
        """

        self.attributes["stop_url"] = value

    @property
    def is_central_station(self):
        """
        :rtype: bool
        """

        return bool(self.attributes.get("location_type", False))

    @is_central_station.setter
    def is_central_station(self, value):
        """
        :type value: bool
        """

        self.attributes["location_type"] = int(value)

    @property
    def parent_station(self):
        """
        :rtype: int | None
        """

        return self.attributes.get("parent_station", None)

    @parent_station.setter
    def parent_station(self, value):
        """
        :type value: int | None
        """

        self.attributes["parent_station"] = value

    @property
    def stop_timezone(self):
        """
        :rtype: str | None
        """

        return self.attributes.get("stop_timezone", None)

    @stop_timezone.setter
    def stop_timezone(self, value):
        """
        :type value: str | None
        """

        self.attributes["stop_timezone"] = value

    @property
    def wheelchair_boarding(self):
        """
        :rtype: bool | None
        """

        return parse_yes_no_unknown(self.attributes.get("wheelchair_boarding", None))

    @wheelchair_boarding.setter
    def wheelchair_boarding(self, value):
        """
        :type value: bool | None
        """

        self.attributes["wheelchair_boarding"] = yes_no_unknown_to_int(value)

    def get_csv_fields(self):
        return ["stop_id", "stop_name", "stop_lat", "stop_lon"] + self.attributes.keys()

    def to_csv_line(self):
        result = dict(stop_id=self.stop_id,
                      stop_name=self.stop_name,
                      stop_lat=self.stop_lat,
                      stop_lon=self.stop_lon,
                      **self.attributes)
        return result

    def validate(self, transit_data):
        """
        :type transit_data: gtfspy.transit_data_object.TransitData
        """

        assert validate_true_false(self.attributes.get("location_type", 0))
        assert self.parent_station is None or self.parent_station in transit_data.stops
        assert validate_yes_no_unknown(self.attributes.get("wheelchair_boarding", None))

    def __eq__(self, other):
        if not isinstance(other, Stop):
            return False

        return self.stop_id == other.stop_id and self.stop_name == other.stop_name and \
               self.stop_lat == other.stop_lat and self.stop_lon == other.stop_lon and \
               self.attributes == other.attributes

    def __ne__(self, other):
        return not (self == other)


class StopCollection(BaseGtfsObjectCollection):
    def __init__(self, transit_data, csv_file=None):
        BaseGtfsObjectCollection.__init__(self, transit_data)

        if csv_file is not None:
            self._load_file(csv_file)

    def add_stop(self, **kwargs):
        stop = Stop(transit_data=self._transit_data, **kwargs)

        self._transit_data._changed()

        assert stop.stop_id not in self._objects
        self._objects[stop.stop_id] = stop
        return stop

    def remove(self, stop, recursive=False, clean_after=True):
        if not isinstance(stop, Stop):
            stop = self[stop]
        else:
            assert self[stop.stop_id] is stop

        if recursive:
            for stop_time in stop.stop_times:
                stop_time.trip.stop_times.remove(stop_time)
        else:
            assert len(stop.stop_times) == 0

        del self._objects[stop.stop_id]

        if clean_after:
            self._transit_data.clean()

    def clean(self):
        to_clean = []
        for stop in self:
            if len(stop.stop_times) == 0:
                to_clean.append(stop)

        for stop in to_clean:
            del self._objects[stop.stop_id]

    def _load_file(self, csv_file):
        if isinstance(csv_file, str):
            with open(csv_file, "rb") as f:
                self._load_file(f)
        else:
            reader = csv.DictReader(csv_file)
            self._objects = {stop.stop_id: stop for stop in
                             (Stop(transit_data=self._transit_data, **row) for row in reader)}

    def validate(self):
        for i, obj in self._objects.iteritems():
            assert i == obj.stop_id
            obj.validate(self._transit_data)
