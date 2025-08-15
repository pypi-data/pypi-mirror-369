# django-auto-slugify

Automatically generate unique slugs from any Django model field.

## Features
- Generate slug from any source field
- Ensure uniqueness automatically
- Add random suffix if duplicate found
- Easy to use in models

## Installation
```bash
pip install django-auto-slugify
```


### Usage
```
from django.db import models
from auto_slugify import AutoSlugField

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(from_field="title")

```