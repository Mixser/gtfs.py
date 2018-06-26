import os
import zipfile
from cStringIO import StringIO
from zipfile import ZipFile

from data_objects import *


class TransitData:
    def __init__(self, gtfs_file=None, validate=True):
        self.agencies = AgencyCollection(self)
        self.routes = RouteCollection(self)
        self.shapes = ShapeCollection(self)
        self.calendar = ServiceCollection(self)
        self.trips = TripCollection(self)
        self.stops = StopCollection(self)

        self.has_changed = False
        self.is_validated = True

        if gtfs_file is not None:
            self.load_gtfs_file(gtfs_file, validate=validate)

    def _changed(self):
        self.has_changed = True
        self.is_validated = False

    def load_gtfs_file(self, gtfs_file, validate=True):
        assert not self.has_changed

        if isinstance(gtfs_file, str):
            with open(gtfs_file, "rb") as gtfs_real_file:
                self.load_gtfs_file(gtfs_real_file)
            return

        zip_file = ZipFile(gtfs_file)

        with zip_file.open("agency.txt", "r") as agency_file:
            self.agencies._load_file(agency_file)

        with zip_file.open("routes.txt", "r") as routes_file:
            self.routes._load_file(routes_file)

        with zip_file.open("shapes.txt", "r") as shapes_file:
            self.shapes._load_file(shapes_file)

        with zip_file.open("calendar.txt", "r") as calendar_file:
            self.calendar._load_file(calendar_file)

        with zip_file.open("trips.txt", "r") as trips_file:
            self.trips._load_file(trips_file)

        with zip_file.open("stops.txt", "r") as stops_file:
            self.stops._load_file(stops_file)

        with zip_file.open("stop_times.txt", "r") as stop_times_file:
            reader = csv.DictReader(stop_times_file)
            for row in reader:
                stop_time = StopTime(transit_data=self, **row)
                stop_time.trip.stop_times.add(stop_time)
                stop_time.stop.stop_times.append(stop_time)

        if validate:
            self.validate()

    def save(self, file_path, compression=zipfile.ZIP_DEFLATED, validate=True):
        assert not os.path.exists(file_path)

        if validate:
            self.validate()

        with ZipFile(file_path, mode="w", compression=compression) as zip_file:
            dome_file = StringIO()
            self.agencies.save(dome_file)
            zip_file.writestr("agency.txt", dome_file.getvalue())
            dome_file.close()

            dome_file = StringIO()
            self.routes.save(dome_file)
            zip_file.writestr("routes.txt", dome_file.getvalue())
            dome_file.close()

            dome_file = StringIO()
            self.shapes.save(dome_file)
            zip_file.writestr("shapes.txt", dome_file.getvalue())
            dome_file.close()

            dome_file = StringIO()
            self.calendar.save(dome_file)
            zip_file.writestr("calendar.txt", dome_file.getvalue())
            dome_file.close()

            dome_file = StringIO()
            self.trips.save(dome_file)
            zip_file.writestr("trips.txt", dome_file.getvalue())
            dome_file.close()

            dome_file = StringIO()
            self.stops.save(dome_file)
            zip_file.writestr("stops.txt", dome_file.getvalue())
            dome_file.close()

            fields = []
            for trip in self.trips:
                for stop_time in trip.stop_times:
                    fields += (field for field in stop_time.get_csv_fields() if field not in fields)
            dome_file = StringIO()
            writer = csv.DictWriter(dome_file, fieldnames=fields, restval=None)
            writer.writeheader()
            for trip in self.trips:
                for stop_time in trip.stop_times:
                    writer.writerow(stop_time.to_csv_line())
            zip_file.writestr("stop_times.txt", dome_file.getvalue())
            dome_file.close()

    def add_agency(self, **kwargs):
        self.agencies.add_agency(**kwargs)

    def add_route(self, **kwargs):
        self.routes.add_route(**kwargs)

    def add_shape_point(self, **kwargs):
        self.shapes.add_shape_point(**kwargs)

    def add_service(self, **kwargs):
        self.calendar.add_service(**kwargs)

    def add_trip(self, **kwargs):
        self.trips.add_trip(**kwargs)

    def add_stop(self, **kwargs):
        self.stops.add_stop(**kwargs)

    def add_stop_time(self, **kwargs):
        stop_time = StopTime(transit_data=self, **kwargs)

        assert stop_time.stop_sequence not in (st.stop_sequence for st in stop_time.trip.stop_times)
        self._changed()
        stop_time.trip.stop_times.append(stop_time)
        stop_time.stop.stop_times.append(stop_time)
        return stop_time

    def validate(self, force=False):
        if self.is_validated and not force:
            return

        self.agencies.validate()
        self.routes.validate()
        self.shapes.validate()
        self.calendar.validate()
        self.trips.validate()
        self.stops.validate()

        self.is_validated = True
