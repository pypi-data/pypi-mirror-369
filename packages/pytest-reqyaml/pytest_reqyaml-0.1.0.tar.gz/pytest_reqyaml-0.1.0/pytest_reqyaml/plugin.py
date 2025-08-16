import pytest
import requests

def pytest_collect_file(path, parent):
    if path.endswith(".yaml") and path.startswith("test_"):
        return YamlFile.from_parent(parent, path=path)

class NameMissingError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class YamlFile(pytest.File):
    def collect(self):
        import yaml
        raw = yaml.safe_load(self.path.open(encoding="utf-8"))
        for k, v in raw.items():
            name = None
            if k == "test_name":
                name = k
                continue
            if name is None:
                raise NameMissingError(self.path.name + "{} 文件中缺少test_name字段")
            if k == "cases":
                yield YamlFile(name, v)

class JsonpathError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class YalmItem(pytest.Item):
    def __init__(self, name, v):
        super(YalmItem, self).__init__(name)
        self.requests = v
        self.cases = []
        for request in self.requests:
            request_case = RequestCase(request)
            self.cases.append(request_case)

    def runtest(self):
        for case in self.cases:
            case.run()


class RequestCase:
    def __init__(self, request):
        self.requests = request.get("request")

        self.method = self.requests.get("method").lower()
        self.url = self.requests.get("url")
        self.headers = self.requests.get("headers")
        self.params = self.requests.get("params")
        self.asserts = self.requests.get("asserts")
        self.json = self.requests.get("json")

    def run(self):
        res = requests.request(method=self.method, url=self.url,
                headers=self.headers, params=self.params, json=self.json)
        if self.asserts is not None:
            from simpleeval import simple_eval
            from jsonpath import jsonpath
            # 读取断言
            statu_code = self.asserts.get("statu_code")
            json_assertion = self.asserts.get("json")
            condition_and_logic = json_assertion.split(" ")
            for i in range(len(condition_and_logic)):
                # 处理jsonpath
                condition = condition_and_logic[i]
                if condition.startswith("$") or condition.startswith("@"):
                    try:
                        json_data = jsonpath(res.json(), condition)[0]
                    except TypeError as e:
                        raise JsonpathError("Jsonpath 表达式错误：" + condition + "不存在")
                    condition_and_logic[i] = "'" + json_data + "'"
                elif condition == "and" or condition == "or":
                    condition_and_logic[i] = " " + condition_and_logic[i] + " "
                elif condition != "==" and condition != "!=" and condition != "<" and condition != ">" \
                        and condition != ">=" and condition != "<=":
                    condition_and_logic[i] = "'" + condition_and_logic[i] + "'"
            json_assertion = "".join(condition_and_logic)
            # 返回真或假
            asser_json = simple_eval(json_assertion)

            assert asser_json
            assert res.status_code == statu_code
