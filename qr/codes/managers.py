from django.db import models
import items


class CodeManager(models.Manager):
    def mockup(self, api=False):
        item = items.models.Item.objects.mockup()
        data = {'registration_date': "2017-09-15",}
        if api:
            return data
        return self.create_code(data)

    def create_code(self, data):
        code = self.create(registration_date=data['registration_date'])
        code.save()
        return code
