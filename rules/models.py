from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import School, User


class Application(models.Model):
    """
    Stub model for an Application.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_returning = models.BooleanField(
        blank=True,
        default=False,
    )
    is_business_owner = models.BooleanField(
        blank=True,
        default=False
    )
    did_file_2021_us_taxes = models.BooleanField(
        blank=True,
        default=False
    )

    def __str__(self):
        return self.user.get_full_name()


class Condition(models.Model):
    label = models.CharField(max_length=256)
    application_field_name = models.CharField(max_length=256)
    application_field_value = models.CharField(max_length=256)

    def __str__(self):
        return self.label


class ApplicationRule(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    conditions = models.ManyToManyField(Condition)

    def __str__(self):
        return ", ".join(c.label for c in self.conditions.all())


class RuleAction(models.Model):
    class ActionType(models.TextChoices):
        DOCUMENT_REQUEST = "DRQ", _("Document Request")

    application_rule = models.ForeignKey(ApplicationRule, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=3, choices=ActionType.choices)

    def __str__(self):
        return f"{str(self.application_rule)}: {str(RuleAction.ActionType(self.action_type).label)}"


class RuleDocument(models.Model):
    class DocumentType(models.TextChoices):
        BUSINESS_TAX_DOCS = "BTD", _("Business Tax Documents")
        W2_PARENT_A = "W2A", _("W2 - Parent A (Previous Year)")

    rule_action = models.ForeignKey(RuleAction, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=3, choices=DocumentType.choices)
    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return str(RuleDocument.DocumentType(self.document_type).label)
