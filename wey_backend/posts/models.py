import uuid
from django.db import models

from accounts.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Attachment(BaseModel):
    image = models.ImageField(upload_to="attachments/")
    created_by = models.ForeignKey(
        User, related_name="post_attachments", on_delete=models.CASCADE
    )


class Post(BaseModel):
    body = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    attachments = models.ManyToManyField(Attachment, blank=True)

    class Meta:
        ordering = ("-created_at",)
