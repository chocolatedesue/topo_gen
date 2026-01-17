"""公共验证器函数"""
from typing import Any, Set


def validate_greater_than(
    value: int,
    context: Any,
    field_name: str,
    error_msg: str
) -> int:
    """验证值大于另一个字段
    
    Args:
        value: 要验证的值
        context: 验证上下文
        field_name: 要比较的字段名
        error_msg: 错误消息
        
    Returns:
        验证通过的值
        
    Raises:
        ValueError: 如果验证失败
    """
    if field_name in context.data and value <= context.data[field_name]:
        raise ValueError(error_msg)
    return value


def validate_protocol_set(protocols: Set[str]) -> Set[str]:
    """验证协议名称集合
    
    Args:
        protocols: 协议名称集合
        
    Returns:
        验证通过的协议集合
        
    Raises:
        ValueError: 如果包含无效协议
    """
    valid_protocols = {"ospf6d", "isisd", "bgpd", "bfdd"}
    invalid = protocols - valid_protocols
    if invalid:
        raise ValueError(
            f"无效的协议: {', '.join(sorted(invalid))}。"
            f"支持: {', '.join(sorted(valid_protocols))}"
        )
    return protocols
