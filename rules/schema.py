from django.db import transaction

import graphene
from graphql import GraphQLError

from clarity.decorators import school_required, student_required
from rules.jobs import process_application_rules
from rules.models import Application, ApplicationRule, RuleAction, RuleDocument


ActionTypeEnum = graphene.Enum.from_enum(RuleAction.ActionType)

DocumentTypeEnum = graphene.Enum.from_enum(RuleDocument.DocumentType)


class ApplicationInputType(graphene.InputObjectType):
    is_returning = graphene.Boolean(required=True)
    is_business_owner = graphene.Boolean(required=True)
    did_file_2021_us_taxes = graphene.Boolean(required=True)


class RuleDocumentInputType(graphene.InputObjectType):
    document_type = DocumentTypeEnum(required=True)
    description = graphene.String(default_value="")


class AddApplication(graphene.Mutation):
    class Arguments:
        application = ApplicationInputType(required=True)

    id = graphene.Int()

    @classmethod
    @student_required
    def mutate(cls, root, info, application):
        with transaction.atomic():
            application_obj = Application(
                user=info.context.user,
                is_returning=application.is_returning,
                is_business_owner=application.is_business_owner,
                did_file_2021_us_taxes=application.did_file_2021_us_taxes
            )
            application_obj.save()

            process_application_rules.delay(application_obj.pk)

            transaction.on_commit(lambda: process_application_rules.delay(application_obj.pk))

        return AddApplication(id=application_obj.pk)


class AddApplicationRule(graphene.Mutation):
    class Arguments:
        condition_ids = graphene.List(graphene.NonNull(graphene.Int), required=True)
        action_type = ActionTypeEnum(required=True)
        rule_documents = graphene.List(graphene.NonNull(RuleDocumentInputType), required=True)

    id = graphene.Int()

    @classmethod
    @school_required
    def mutate(cls, root, info, condition_ids, action_type, rule_documents):
        if not condition_ids:
            raise GraphQLError("You must add at least one condition!")

        if action_type == RuleAction.ActionType.DOCUMENT_REQUEST:
            if not rule_documents:
                raise GraphQLError(
                    "You must add at least one document to a Document Request!"
                )
        elif rule_documents:
            raise GraphQLError(
                "You can only add documents to a Document Request!"
            )

        application_rule_obj = ApplicationRule(school=info.context.user.school)
        application_rule_obj.save()
        application_rule_obj.conditions.set(condition_ids)

        rule_action_obj = RuleAction(
            application_rule=application_rule_obj,
            action_type=action_type,
        )
        rule_action_obj.save()

        if action_type == RuleAction.ActionType.DOCUMENT_REQUEST:
            for rule_document in rule_documents:
                RuleDocument.objects.create(
                    rule_action=rule_action_obj,
                    document_type=rule_document.document_type,
                    description=rule_document.description,
                )

        return AddApplicationRule(id=application_rule_obj.pk)


class Mutation(graphene.ObjectType):
    add_application = AddApplication.Field()
    add_application_rule = AddApplicationRule.Field()
