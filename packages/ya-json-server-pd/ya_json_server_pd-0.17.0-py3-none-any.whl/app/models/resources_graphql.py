import strawberry

# @strawberry.type
# class User:
#     name: str
#     age: int


# @strawberry.type
# class Query:
#     @strawberry.field
#     def user(self) -> User:
#         return User(name="Patrick", age=100)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


hello_schema = strawberry.Schema(query=Query)
