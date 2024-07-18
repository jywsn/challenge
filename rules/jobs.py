import logging

from django_rq import job

from rules.models import Application, ApplicationRule

logger = logging.getLogger(__name__)


def execute_application_rule(application_id, application_rule_id):
    """
    Presumably we would send an email, noticiation, etc.
    """
    pass

@job
def process_application_rules(application_id):
    logger.debug(f"Application {application_id}, Process Rules Start")
    try:
        application = Application.objects.get(pk=application_id)

        for application_rule in ApplicationRule.objects.filter(school=application.user.school):
            if all([
                str(getattr(application, condition.application_field_name))
                == condition.application_field_value
                for condition in application_rule.conditions.all()
            ]):
                logger.debug(f"Application {application_id}, Rule {application_rule.pk} match")
                execute_application_rule(application_id, application_rule.pk)
            else:
                logger.debug(f"Application {application_id}, Rule {application_rule.pk} no match")
    except Application.DoesNotExist:
        logger.error(f"Application {application_id}, Not Found")

    logger.debug(f"Application {application_id}, Process Rules End")
