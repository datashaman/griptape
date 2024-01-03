from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema, PolymorphicSchema


class PromptDriverSchema(BaseSchema):
    class Meta:
        ordered = True

    temperature = fields.Str()
    max_tokens = fields.Int()
    stream = fields.Bool()
    max_retries = fields.Int()
    retry_delay = fields.Float()
    model = fields.Str()
    tokenizer = fields.Nested(PolymorphicSchema())

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
