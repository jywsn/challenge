from django.contrib import admin

from rules.models import Application, ApplicationRule, Condition, RuleAction, RuleDocument


class RuleActionInline(admin.TabularInline):
    model = RuleAction
    extra = 0


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ["label", "application_field_name", "application_field_value"]


@admin.register(ApplicationRule)
class ApplicationRuleAdmin(admin.ModelAdmin):
    list_display = ["school", "condition_set", "action_set"]
    inlines = [RuleActionInline]

    def condition_set(self, obj):
        return ", ".join(c.label for c in obj.conditions.all())

    def action_set(self, obj):
        return ", ".join(str(a) for a in obj.ruleaction_set.all())


@admin.register(RuleAction)
class RuleActionAdmin(admin.ModelAdmin):
    list_display = ["school", "action_type", "n_document_types"]

    def school(self, obj):
        return obj.application_rule.school.name

    def n_document_types(self, obj):
        if obj.action_type == RuleAction.ActionType.DOCUMENT_REQUEST:
            return obj.ruledocument_set.count()
        return "-"


@admin.register(RuleDocument)
class RuleDocumentAdmin(admin.ModelAdmin):
    list_display = ["application_rule", "action_type", "document_type"]

    def application_rule(self, obj):
        return obj.rule_action.application_rule

    def action_type(self, obj):
        return str(RuleAction.ActionType(obj.rule_action.action_type).label)
