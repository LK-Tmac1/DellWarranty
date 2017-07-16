# -*- coding: utf-8 -*-

from api import APIClient, api_offset

attempt_max = 3


class Batch(object):
    current_client = None
    current_quote = False

    def __init__(self, logger, configs):
        self.logger = logger
        self.logger.info("开始调用戴尔API")
        self.client_queue = APIClient.build_api_client_queue(configs)
        if not self.client_queue:
            logger.error("创建API Client失败")
            return
        self.next_client()
        self.logger.info("当前客户端：%s" % self.current_client)

    def next_client(self):
        if self.client_queue:
            while self.client_queue:
                self.current_client = self.client_queue.popleft()
                if self.current_client:
                    break
            self.current_quote = True
            self.logger.warn("转为下一个客户端：%s" % self.current_client)
        else:
            self.current_client = None
            self.current_quote = False
            self.logger.error("所有客户端API额度已用光")

    def begin(self, api_svc_set):
        dell_asset_list = list([])
        api_svc_list = list(api_svc_set)
        temp_svc_list = list([])
        while api_svc_list and self.current_client:
            while len(temp_svc_list) < api_offset and api_svc_list:
                temp_svc_list.append(api_svc_list.pop())
            svc_parameter = self.current_client.flatten_svc_parameter(temp_svc_list)
            attempt = attempt_max
            while attempt and self.current_client:
                attempt -= 1
                if not self.current_quote:
                    self.next_client()
                if self.current_client.new_response(svc_parameter):
                    if not self.current_client.is_response_error():
                        break
                    self.logger.warn("客户端出现异常:\n%s" % self.current_client.raw_response)
                    resolved, skip, self.current_quote = self.current_client.handle_response_error()
                    self.logger.error("异常原因：%s\n" % self.current_client.get_fault_message())
                    if resolved or skip:
                        message = "异常已解决" if resolved else "忽略异常，客户端继续工作"
                        self.logger.warn(message)
                        break
                    else:
                        self.logger.warn("异常没能解决，需要重试")
            da_entity_list = self.current_client.response_to_entities()
            if da_entity_list:
                self.logger.info("新增%s个实体类" % len(da_entity_list))
                dell_asset_list.extend(da_entity_list)
            else:
                self.logger.warn("没能得到任何DellAsset实体类：%s" % svc_parameter)
        return dell_asset_list
