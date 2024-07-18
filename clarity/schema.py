import graphene
import graphql_jwt

import rules.schema as rules_schema

class Sample(graphene.ObjectType):
    value = graphene.String()


class Query(graphene.ObjectType):
    hello = graphene.Field(Sample)

    def resolve_hello(parent, info):
        return Sample(value="Hello world!")


class Mutation(rules_schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
