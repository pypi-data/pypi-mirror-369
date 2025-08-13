"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-04-02
Author: Martian Bugs
Description: 数据包处理器
"""

from typing import Any

from DrissionPage._units.listener import DataPacket


class DataPacketProcessor:
    def __init__(self, packet: DataPacket | dict):
        if isinstance(packet, DataPacket):
            self._packet = packet
            self._resp = self._packet.response.body
        elif isinstance(packet, dict):
            self._resp = packet
        else:
            raise ValueError('数据包类型非预期的 DataPacket|dict')

    def filter(self, fields: str | list[str] | list[tuple[str, str]]):
        """
        筛选数据包字段数据

        Args:
            fields: 以 `.` 分隔的字段层级结构, 支持列表 key[index] 形式.\n
                如果需要定义别名, 则以 tuple 形式传入 (key, alias).\n
                默认会进行校验, 如果不需要校验则可以在链路最前面加上 `?` 符号,\n
                如果只是某一个字段不校验, 则在字段后面加上 `?` 符号\n
                例如: `['?resule.version', 'resule.datas[0].name?', ('resule.extra[1].name', 'extra_name')]`
        Returns:
            提取的字段数据
        """

        if not isinstance(self._resp, dict):
            raise TypeError('数据包非预期的 dict 类型')

        field_list = fields if isinstance(fields, list) else [fields]

        result: dict[str, Any] = {}
        for chain in field_list:
            if not isinstance(chain, (str, tuple)):
                continue

            chain_keys = (chain[0] if isinstance(chain, tuple) else chain).split('.')
            need_verify = not chain_keys[0].startswith('?')
            if not need_verify:
                chain_keys[0] = chain_keys[0].lstrip('?')

            data_key__temp = None
            data_temp = self._resp

            for i, field in enumerate(chain_keys, 1):
                field_need_verify = not field.endswith('?')
                data_key__temp = field = (
                    field.rstrip('?') if not field_need_verify else field
                )
                prev_field_chain = '.'.join(chain_keys[: i - 1]).rstrip('?')
                prev_field_chain = prev_field_chain if prev_field_chain else 'root'

                if '[' in field and ']' in field:
                    # 处理列表形式的 key[index]

                    field, list_index_str = field.split('[')
                    if field not in data_temp:
                        if need_verify and field_need_verify:
                            raise KeyError(f'{prev_field_chain} 中未找到 {field} 字段')
                        else:
                            data_key__temp = None
                            break

                    curr_field_chain = '.'.join([prev_field_chain, field])
                    data_temp = data_temp.get(field)
                    if not isinstance(data_temp, list):
                        if need_verify and field_need_verify:
                            raise TypeError(f'{curr_field_chain} 非预期的 list 类型')
                        else:
                            data_key__temp = None
                            break

                    list_index = int(list_index_str.rstrip(']'))
                    if list_index >= (data_temp__count := len(data_temp)):
                        if need_verify and field_need_verify:
                            raise IndexError(
                                f'{curr_field_chain} 索引超出范围, 长度为 {data_temp__count}'
                            )
                        else:
                            data_key__temp = None
                            break

                    data_key__temp = field
                    data_temp = data_temp[list_index]
                    continue

                if not isinstance(data_temp, dict):
                    if need_verify and field_need_verify:
                        raise TypeError(f'{prev_field_chain} 非预期的 dict 类型')
                    else:
                        data_key__temp = None
                        continue

                if field not in data_temp:
                    if need_verify and field_need_verify:
                        raise KeyError(f'{prev_field_chain} 中未找到 {field} 字段')
                    else:
                        data_key__temp = None
                        continue

                data_temp = data_temp.get(data_key__temp)

            if data_key__temp is None:
                continue

            result[chain[1] if isinstance(chain, tuple) else data_key__temp] = data_temp

        return result
