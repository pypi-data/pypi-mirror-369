from typing import Self

import pytest
import requests
from _pytest._code import ExceptionInfo
from _pytest._code.code import TracebackStyle, TerminalRepr

from pytest_reqyaml.ReqyamlError import NameMissingError, JsonpathError, MyAssertionError


# 读取yaml文件
def pytest_collect_file(file_path, path, parent):
    if file_path.suffix == ".yaml" and file_path.name.startswith("test_"):
        return YamlFile.from_parent(parent, path=file_path)
    else:
        return None

class YamlFile(pytest.File):
    def collect(self):
        import yaml
        raw = yaml.safe_load(self.path.open(encoding="utf-8"))
        test_name = raw.get("test_name")
        if test_name is None:
            raise NameMissingError("{self.path.name} 文件中缺少test_name字段")
        request_list = raw.get("cases")
        if request_list is None:
            yield None
        for request in request_list:
            name = request.get("request").get("name")
            if name is None:
                raise NameMissingError("{self.path.name} request中缺少name字段")
            yield YamlItem.from_parent(self, name = name, request = request.get("request"))

class YamlItem(pytest.Item):

    def __init__(self, request, name, parent, **kwargs):
        # raise NameMissingError(str(kwargs) + str(request) + str(name))
        super(YamlItem, self).__init__(name, parent, **kwargs)
        self.name = name
        self.request = request
        self.request_case = RequestCase(request)

    # 运行测试用例
    def runtest(self):
        self.request_case.run()

    # runtest方法抛出异常时进行处理
    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: TracebackStyle | None = None,
    ) -> str | TerminalRepr:
        if (isinstance(excinfo.value, NameMissingError)
                or isinstance(excinfo.value, JsonpathError)):
            return str(excinfo.value)
        elif isinstance(excinfo.value, MyAssertionError):
            return str(excinfo.value)
        else:
            return super().repr_failure(excinfo, style)


class RequestCase:
    def __init__(self, request):
        # 读取请求参数
        # self.requests = request.get("request")
        self.method = request.get("method").lower()
        self.url = request.get("url")
        self.headers = request.get("headers")
        self.params = request.get("params")
        self.asserts = request.get("asserts")
        self.json = request.get("json")

    def run(self):
        res = requests.request(method=self.method, url=self.url,
                headers=self.headers, params=self.params, json=self.json)
        if self.asserts is not None:
            from simpleeval import simple_eval
            from jsonpath import jsonpath
            # 读取断言
            desired_statu_code = self.asserts.get("statu_code")
            json_assertion = self.asserts.get("json")
            import logging
            logger = logging.getLogger()
            if json_assertion is not None:
                logger.info("json 断言：" + json_assertion)
            if desired_statu_code is not None:
                logger.info("状态码断言： statue_code ==" + desired_statu_code)

            if json_assertion is not None:
                # 将json断言按空格划分
                condition_and_logic = json_assertion.split(" ")
                for i in range(len(condition_and_logic)):
                    condition = condition_and_logic[i]
                    # 处理jsonpath
                    if condition.startswith("$") or condition.startswith("@"):
                        try:
                            json_data = jsonpath(res.json(), condition)[0]
                        except TypeError as e:
                            raise JsonpathError("Jsonpath表达式错误：" + condition + "不存在")
                        condition_and_logic[i] = "'" + json_data + "'"
                    # 用空格将and和or与其它单词分开
                    elif condition == "and" or condition == "or":
                        condition_and_logic[i] = " " + condition_and_logic[i] + " "
                    # 使用单引号括起条件使其成为字符串
                    elif condition != "==" and condition != "!=" and condition != "<" and condition != ">" \
                            and condition != ">=" and condition != "<=":
                        condition_and_logic[i] = "'" + condition_and_logic[i] + "'"
                # 拼接处理后的语句
                json_processed = "".join(condition_and_logic)
                # json断言，使用simple_eval进行逻辑断言，返回真或假
                asser_json_res = simple_eval(json_processed)
                if not asser_json_res:
                    raise MyAssertionError("json断言失败：" + json_processed)
            if desired_statu_code is not None and desired_statu_code != res.status_code:
                raise MyAssertionError("状态码断言失败：预期的状态码为" + desired_statu_code
                                       + " 真实的状态码为" + res.status_code)