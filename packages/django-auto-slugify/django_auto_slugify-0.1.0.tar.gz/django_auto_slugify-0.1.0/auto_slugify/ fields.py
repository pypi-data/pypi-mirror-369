from django.db import models
from django.utils.text import slugify
import random
import string

class AutoSlugField(models.CharField):
    """
    CharField that auto-generates slug from another field.
    Ensures uniqueness by adding random suffix if necessary.
    """
    def __init__(self, from_field=None, *args, **kwargs):
        self.from_field = from_field
        kwargs["max_length"] = kwargs.get("max_length", 255)
        kwargs["unique"] = True
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)

        if self.from_field and not value:
            base = slugify(getattr(model_instance, self.from_field))
            value = base

        ModelClass = model_instance.__class__
        original_value = value

        # Ensure uniqueness
        while ModelClass.objects.filter(**{self.attname: value}).exclude(pk=model_instance.pk).exists():
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            value = f"{original_value}-{suffix}"

        setattr(model_instance, self.attname, value)
        return value
