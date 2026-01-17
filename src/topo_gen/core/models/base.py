"""基础配置类"""
from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    """基础配置类 - 所有配置模型的基类"""
    
    model_config = ConfigDict(
        frozen=True,  # 不可变
        extra='forbid',  # 禁止额外字段
        validate_assignment=True,  # 赋值时验证
        use_enum_values=True,  # 使用枚举值
        str_strip_whitespace=True,  # 去除空白字符
    )
