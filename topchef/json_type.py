from typing import Dict, Union, Optional, List

JSON_PRIMITIVE_TYPE = Optional[Union[str, int, float, bool]]

JSON_TYPE = Dict[
    str,
    Optional[
        Union[JSON_PRIMITIVE_TYPE, List['JSON_TYPE'], 'JSON_TYPE']
    ]
]
