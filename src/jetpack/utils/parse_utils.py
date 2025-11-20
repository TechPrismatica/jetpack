from typing import Annotated, Any, Callable

from fastapi.params import Query
import orjson


class _ParamsDecoder:
    def __call__(
        self,
        model: Callable = dict,
        description: str = "Stringified JSON",
        default: Any = None,
    ) -> Callable:
        json_schema_extra = {} if model == dict else model.model_json_schema()  # noqa

        def param_decoder(
            params: Annotated[
                str, Query(json_schema_extra=json_schema_extra, description=description)
            ] = default,
        ) -> Any:
            if not params:
                return default
            return model(**orjson.loads(params.strip("'\\").encode()))

        return param_decoder


ParamsDecoder = _ParamsDecoder()

__all__ = ["ParamsDecoder"]
