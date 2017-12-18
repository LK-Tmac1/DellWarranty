# -*- coding: utf-8 -*-

from api import APIClient, api_offset


class Batch(object):
    current_client = None
    attempt_max = 3

    def __init__(self, logger, configs):
        self.logger = logger
        self.logger.info("开始调用戴尔API")
        self.client_queue = APIClient.build_api_client_queue(configs)
        if not self.client_queue:
            self.logger.error("创建API Client失败")
            return
        self.current_client = self.client_queue.popleft()
        self.logger.info("当前客户端：%s" % self.current_client)

    def next_client(self):
        if self.client_queue:
            self.current_client = self.client_queue.popleft()
            self.logger.warn("转为下一个客户端：%s" % self.current_client)

    def continue_with_current_client(self):
        return self.current_client and not self.current_client.quote_full

    def begin(self, api_svc_set):
        dell_asset_list = list([])
        api_svc_list = list(api_svc_set)
        while api_svc_list and (self.continue_with_current_client() or self.client_queue):
            temp_svc_list = list([])
            while len(temp_svc_list) < api_offset and api_svc_list:
                temp_svc_list.append(api_svc_list.pop())
            svc_parameter = self.current_client.flatten_svc_parameter(temp_svc_list)
            attempt = self.attempt_max
            while attempt:
                attempt -= 1
                while not self.continue_with_current_client and self.client_queue:
                    # Ensure we can continue to use current client
                    self.next_client()
                if not self.continue_with_current_client:
                    self.logger.error("所有客户端已用光")
                    break
                if self.current_client.new_response(svc_parameter):
                    if self.current_client.is_response_error():
                        self.logger.warn("客户端出现异常:\n%s" % self.current_client.raw_response)
                        resolved, skip = self.current_client.handle_response_error()
                        self.logger.error("异常原因：%s\n" % self.current_client.get_fault_message())
                        if resolved or skip:
                            self.logger.warn("异常已解决" if resolved else "忽略异常，客户端继续工作")
                            break
                        else:
                            self.logger.warn("异常没能解决，需要重试")
                    else:
                        break
            da_entity_list = self.current_client.response_to_entities()
            if da_entity_list:
                self.logger.info("新增%s个实体类" % len(da_entity_list))
                dell_asset_list.extend(da_entity_list)
            else:
                self.logger.warn("没能得到任何DellAsset实体类：%s" % svc_parameter)
        return dell_asset_list
