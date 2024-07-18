from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from graphql_jwt.testcases import JSONWebTokenTestCase

from rules.jobs import process_application_rules
from rules.models import (
    Application,
    ApplicationRule,
    RuleAction,
    RuleDocument,
)
from users.models import School, UserGroup


class BaseAPITestCase(JSONWebTokenTestCase):
    """
    https://django-graphql-jwt.domake.io/tests.html
    """

    GRAPHQL_URL = "/graphql/"

    fixtures = ["group", "condition"]

    def setUp(self):
        super().setUp()

        self.school = School(name="Test School")
        self.school.save()

        self.student_user = get_user_model().objects.create_user(
            username="studentuser",
            password="dolphins",
        )
        self.student_user.school = self.school
        self.student_user.save()
        student_group = Group.objects.get(name=UserGroup.STUDENT)
        student_group.user_set.add(self.student_user)

        self.school_user = get_user_model().objects.create_user(
            username="schooluser",
            password="dolphins",
        )
        self.school_user.school = self.school
        self.school_user.save()
        school_group = Group.objects.get(name=UserGroup.SCHOOL)
        school_group.user_set.add(self.school_user)

    def assertPermissionDenied(self, response):
        self.assertEqual(
            response.formatted['errors'][0]['message'],
            'You do not have permission to perform this action'
        )


class AppApplicationTestCase(BaseAPITestCase):
    ADD_APPLICATION_MUTATION = '''
        mutation addApplication(
            $isReturning:  Boolean!,
            $isBusinessOwner: Boolean!,
            $didFile2021UsTaxes: Boolean!
        ) {
            addApplication(
                application: {
                    isReturning: $isReturning,
                    isBusinessOwner: $isBusinessOwner,
                    didFile2021UsTaxes: $didFile2021UsTaxes
                }
            ) {
                id
            }
        }
    '''

    def setUp(self):
        super().setUp()

        self.application_rule_obj = ApplicationRule(school=self.school)
        self.application_rule_obj.save()
        self.application_rule_obj.conditions.set([1,2,3])

        rule_action_obj = RuleAction(
            application_rule=self.application_rule_obj,
            action_type=RuleAction.ActionType.DOCUMENT_REQUEST,
        )
        rule_action_obj.save()

        RuleDocument.objects.create(
            rule_action=rule_action_obj,
            document_type=RuleDocument.DocumentType.BUSINESS_TAX_DOCS,
            description="",
        )

    def test_no_authorization(self):
        variables = {
            "isReturning": True,
            "isBusinessOwner": True,
            "didFile2021UsTaxes": True,
        }
        response = self.client.execute(self.ADD_APPLICATION_MUTATION, variables)
        self.assertPermissionDenied(response)

    def test_school_authorization(self):
        variables = {
            "isReturning": True,
            "isBusinessOwner": True,
            "didFile2021UsTaxes": True,
        }
        self.client.authenticate(self.school_user)
        response = self.client.execute(self.ADD_APPLICATION_MUTATION, variables)
        self.assertPermissionDenied(response)

    @patch("rules.jobs.process_application_rules.delay")
    @patch("rules.jobs.execute_application_rule")
    def test_student_authorization(self, mocked_execute, mocked_delay):
        variables = {
            "isReturning": True,
            "isBusinessOwner": True,
            "didFile2021UsTaxes": True,
        }
        self.client.authenticate(self.student_user)
        formatted_response = self.client.execute(self.ADD_APPLICATION_MUTATION, variables).formatted

        self.assertEqual(formatted_response.get('errors'), None)
        mocked_delay.assert_called_once_with(formatted_response['data']['addApplication']['id'])

    @patch("rules.jobs.execute_application_rule")
    def test_job_without_match(self, mocked_execute):
        application = Application(
            user=self.student_user,
            is_returning=True,
            is_business_owner=True,
            did_file_2021_us_taxes=True,
        )
        application.save()

        process_application_rules(application.pk)
        mocked_execute.assert_not_called()

    @patch("rules.jobs.execute_application_rule")
    def test_job_with_match(self, mocked_execute):
        application = Application(
            user=self.student_user,
            is_returning=False,
            is_business_owner=True,
            did_file_2021_us_taxes=False,
        )
        application.save()

        process_application_rules(application.pk)
        mocked_execute.assert_called_once_with(application.pk, self.application_rule_obj.pk)


class AddApplicationRuleTestCase(BaseAPITestCase):
    ADD_APPLICATION_RULE_MUTATION = '''
        mutation addApplicationRule(
            $actionType: ActionType!,
            $conditionIds: [Int!]!,
            $ruleDocuments: [RuleDocumentInputType!]!
        ) {
          addApplicationRule(
            actionType:  $actionType,
            conditionIds: $conditionIds,
            ruleDocuments: $ruleDocuments
          ) {
            id
          }
        }
    '''

    def setUp(self):
        super().setUp()

    def test_no_authorization(self):
        variables = {
            "actionType": RuleAction.ActionType.DOCUMENT_REQUEST.name,
            "conditionIds": [1, 2],
            "ruleDocuments": [
                {
                    "documentType": RuleDocument.DocumentType.BUSINESS_TAX_DOCS.name,
                }
            ]
        }
        response = self.client.execute(self.ADD_APPLICATION_RULE_MUTATION, variables)
        self.assertPermissionDenied(response)

    def test_student_authorization(self):
        variables = {
            "actionType": RuleAction.ActionType.DOCUMENT_REQUEST.name,
            "conditionIds": [1, 2],
            "ruleDocuments": [
                {
                    "documentType": RuleDocument.DocumentType.BUSINESS_TAX_DOCS.name,
                }
            ]
        }
        self.client.authenticate(self.student_user)
        response = self.client.execute(self.ADD_APPLICATION_RULE_MUTATION, variables)
        self.assertPermissionDenied(response)

    def test_school_authorization(self):
        variables = {
            "actionType": RuleAction.ActionType.DOCUMENT_REQUEST.name,
            "conditionIds": [1, 2],
            "ruleDocuments": [
                {
                    "documentType": RuleDocument.DocumentType.BUSINESS_TAX_DOCS.name,
                }
            ]
        }
        self.client.authenticate(self.school_user)
        response = self.client.execute(self.ADD_APPLICATION_RULE_MUTATION, variables)
        self.assertEqual(response.formatted.get('errors'), None)
