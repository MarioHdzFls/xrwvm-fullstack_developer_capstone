from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    country_of_origin = models.CharField(
        max_length=50, blank=True
    )  # Campo extra opcional

    def __str__(self):
        return self.name


class CarModel(models.Model):
    # Relación Many-to-One con CarMake
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    # ID del concesionario (Referencia a Cloudant)
    dealer_id = models.IntegerField(null=True, blank=True)

    CAR_TYPES = [
        ("SEDAN", "Sedan"),
        ("SUV", "SUV"),
        ("WAGON", "Wagon"),
        ("COUPE", "Coupe"),
        ("HATCHBACK", "Hatchback"),
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default="SUV")

    year = models.IntegerField(
        default=2023,
        validators=[MaxValueValidator(2025), MinValueValidator(2015)],
    )

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
