import factory
import factory.django
from django.contrib.gis.geos import fromstr
from faker import Factory as Faker

from location_api import models

fake = Faker.create()


class SupplierAliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SupplierAlias

    regex = factory.Sequence(lambda n: f"Regex {n}")


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Supplier

    name = factory.Sequence(lambda n: f"Supplier {n}")

    @factory.post_generation
    def supplieralias_set(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of supplier aliases were passed in, use them
            for alias in extracted:
                self.supplieralias_set.create(regex=alias)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Location

    name = factory.LazyAttribute(lambda x: fake.company())
    point = fromstr("POINT (175.2801599999999951 -37.7911080000000013)")
    country_code = "NZ"
    gisprecision = "manual"
