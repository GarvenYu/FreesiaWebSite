#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice import config_default, config_override


def merge(default_config, override_config):
    '''
    :param default_config: 默认配置信息
    :param override_config: 生产配置信息
    :return: 合并后的信息
    '''
    final_config = {}
    if isinstance(default_config, dict) and isinstance(override_config, dict):
        for key, value in default_config.items():
            if key in override_config:
                if isinstance(value, dict):
                    final_config[key] = merge(value, override_config[key])
                else:
                    final_config[key] = override_config[key]
            else:
                final_config[key] = value
        return final_config
    else:
        raise ValueError('参数类型有误。')


try:
    config = merge(config_default.configs, config_override.configs)
except ValueError:
    pass