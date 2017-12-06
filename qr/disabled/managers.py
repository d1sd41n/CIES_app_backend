from django.db import models
from django.contrib.contenttypes.models import ContentType


class DisabledManager(models.Manager):
    def mockup(self, api=False):
        randomContentType = ContentType.objects.get(model="company")
        data = {
                "cause": "esto es un test de disabled",
                "fk_object": 0,
                "date": "2017-10-04",
                "model": randomContentType
                }
        if api:
            return data
        return self.create_disabled(data)

    def create_disabled(self, data):
        disabled = self.create(model=data["model"],
                               fk_object=data["fk_object"],
                               date=data["date"],
                               cause=data["cause"])
        disabled.save()
        return disabled
