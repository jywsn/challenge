from graphql_jwt.decorators import user_passes_test

from users.models import UserGroup

school_required = user_passes_test(
    lambda u: u and u.is_authenticated and u.groups.filter(name=UserGroup.SCHOOL).exists()
)

student_required = user_passes_test(
    lambda u: u and u.is_authenticated and u.groups.filter(name=UserGroup.STUDENT).exists()
)
