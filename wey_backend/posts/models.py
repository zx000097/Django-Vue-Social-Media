import uuid
from django.db import models

from accounts.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Post(BaseModel):
    body = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)


class PostItemBase(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Attachment(PostItemBase):
    image = models.ImageField(upload_to="attachments/")


class Like(PostItemBase):
    pass
