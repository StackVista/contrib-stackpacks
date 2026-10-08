"""Evaluate the shipped CEL against optional and complete OTel resource identities."""

import re
import unittest
from functools import lru_cache
from pathlib import Path

import yaml
from celpy import CELEvalError, Environment, celtypes, json_to_cel

SETTINGS = Path(__file__).resolve().parents[2] / "stackpacks/open-telemetry/settings"
ENV = Environment()


def omit_fields(attributes, keys):
    # The platform's documented omit(map, keys) extension to CEL.
    return celtypes.MapType({key: value for key, value in attributes.items() if key not in keys})


@lru_cache(maxsize=None)
def compile_expression(expression):
    return ENV.program(ENV.compile(expression), functions={"omit": omit_fields})


def evaluate(expression, context):
    return compile_expression(expression).evaluate({key: json_to_cel(value) for key, value in context.items()})


def load_mapping(folder, name):
    return yaml.safe_load((SETTINGS / folder / (name + ".sty")).read_text())["nodes"][0]


def map_resource(mapping, attributes):
    context = {"resource": {"attributes": attributes}}
    if not evaluate(mapping["input"]["resource"]["condition"], context):
        return None
    context["vars"] = {item["name"]: evaluate(item["value"], context) for item in mapping.get("vars", [])}
    output = mapping["output"]
    result = {key: str(evaluate(output[key], context)) for key in
              ("identifier", "name", "typeName", "sourceId", "targetId") if key in output}
    tags = set()
    for group in ("required", "optional"):
        fields = output.get(group, {})
        if "version" in fields:
            result["version"] = str(evaluate(fields["version"], context))
        for tag in fields.get("tags", []):
            try:
                source = evaluate(tag["source"], context)
            except CELEvalError:
                if group == "required":
                    raise
                continue
            if "pattern" not in tag:
                tags.add((tag["target"], str(source)))
            else:
                for key, value in source.items():
                    match = re.fullmatch(tag["pattern"], str(key))
                    if match:
                        target = tag["target"]
                        for index, capture in enumerate(match.groups(), 1):
                            target = target.replace("${" + str(index) + "}", capture)
                        tags.add((target, str(value)))
    result["tags"] = tags
    return result


class ResourceIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = load_mapping("component-mappings", "services")
        cls.instance = load_mapping("component-mappings", "service-instances")
        cls.namespace = load_mapping("component-mappings", "namespaces")
        cls.provided_by = load_mapping("relation-mappings", "provided-by")
        cls.infrastructure = [
            (load_mapping("relation-mappings", name), attributes)
            for name, attributes in [
                ("executes-host", {"host.id": "host-123"}),
                ("executes-function", {"faas.id": "function-123"}),
                ("executes-ecs-task", {"aws.ecs.task.id": "task-123"}),
                ("k8s-pod-to-otel", {"k8s.cluster.name": "cluster-1", "k8s.namespace.name": "apps", "k8s.pod.name": "pod-1"}),
            ]
        ]

    def test_optional_namespace_and_cluster_keep_identity_and_relation_consistent(self):
        for namespace in (None, "", "orders"):
            for cluster in (None, "", "cluster-1"):
                with self.subTest(namespace=namespace, cluster=cluster):
                    attributes = {"service.name": "checkout", "service.instance.id": "instance-1"}
                    if namespace is not None:
                        attributes["service.namespace"] = namespace
                    if cluster is not None:
                        attributes["k8s.cluster.name"] = cluster
                    service = map_resource(self.service, attributes)
                    instance = map_resource(self.instance, attributes)
                    relation = map_resource(self.provided_by, attributes)
                    namespace_node = map_resource(self.namespace, attributes)
                    expected_namespace = namespace or "default"
                    expected = "urn:opentelemetry:namespace/" + expected_namespace + ":service/checkout"
                    self.assertEqual(service["identifier"], expected)
                    self.assertEqual(instance["identifier"], expected + ":serviceInstance/instance-1")
                    self.assertEqual(relation["sourceId"], service["identifier"])
                    self.assertEqual(relation["targetId"], instance["identifier"])
                    self.assertEqual(namespace_node["identifier"], "urn:opentelemetry:namespace/" + expected_namespace)
                    for component in (service, instance):
                        self.assertEqual({value for key, value in component["tags"] if key == "service.namespace"}, {expected_namespace})
                    for component in (service, instance, namespace_node):
                        self.assertNotIn("k8s-scope", {key for key, _ in component["tags"]})
                        clusters = {value for key, value in component["tags"] if key == "cluster-name"}
                        self.assertEqual(clusters, {cluster} if cluster else set())

    def test_platform_self_scrape_without_kubernetes_metadata(self):
        # Prometheus self-scrapes supply these two resource attributes, but no namespace/cluster.
        attributes = {"service.name": "sts-opentelemetry-collector", "service.instance.id": "127.0.0.1:8888"}
        service = map_resource(self.service, attributes)
        instance = map_resource(self.instance, attributes)
        self.assertIn(":namespace/default:", service["identifier"])
        self.assertTrue(instance["identifier"].endswith(":serviceInstance/127.0.0.1:8888"))
        for component in (service, instance):
            self.assertFalse({"cluster-name", "k8s-scope", "namespace"} & {key for key, _ in component["tags"]})

    def test_service_without_instance_is_kept_without_inventing_an_instance(self):
        for value in (None, ""):
            attributes = {"service.name": "checkout"}
            if value is not None:
                attributes["service.instance.id"] = value
            self.assertIsNotNone(map_resource(self.service, attributes))
            self.assertIsNone(map_resource(self.instance, attributes))
            self.assertIsNone(map_resource(self.provided_by, attributes))
            for mapping, extra in self.infrastructure:
                self.assertIsNone(map_resource(mapping, attributes | extra))

    def test_no_service_name_skips_services_instances_and_instance_relations(self):
        for value in (None, ""):
            attributes = {"service.instance.id": "instance-1"}
            if value is not None:
                attributes["service.name"] = value
            for mapping in (self.service, self.instance, self.provided_by):
                self.assertIsNone(map_resource(mapping, attributes))
            for mapping, extra in self.infrastructure:
                self.assertIsNone(map_resource(mapping, attributes | extra))

    def test_complete_kubernetes_identity_and_metadata_are_preserved(self):
        attributes = {"service.name": "checkout", "service.namespace": "orders", "service.instance.id": "pod-uid-123",
                      "service.version": "1.2.3", "k8s.cluster.name": "cluster-1", "k8s.namespace.name": "apps",
                      "k8s.pod.name": "pod-1", "telemetry.sdk.language": "python", "deployment.environment": "production"}
        service = map_resource(self.service, attributes)
        instance = map_resource(self.instance, attributes)
        for component in (service, instance, map_resource(self.namespace, attributes)):
            self.assertTrue({("cluster-name", "cluster-1"), ("namespace", "apps"), ("k8s-scope", "cluster-1/apps")} <= component["tags"])
        self.assertEqual(service["version"], "1.2.3")
        self.assertIn(("telemetry.sdk.language", "python"), service["tags"])
        self.assertIn(("k8s.pod.name", "pod-1"), instance["tags"])
        for mapping, extra in self.infrastructure:
            relation = map_resource(mapping, attributes | extra)
            self.assertEqual(relation["targetId"], instance["identifier"])

    def test_partial_kubernetes_context_does_not_invent_a_scope(self):
        for attributes in ({"k8s.namespace.name": "apps"}, {"k8s.namespace.name": "apps", "k8s.cluster.name": ""},
                           {"k8s.namespace.name": "", "k8s.cluster.name": "cluster-1"}):
            for mapping in (self.service, self.instance, self.namespace):
                component = map_resource(mapping, attributes | {"service.name": "checkout", "service.instance.id": "instance-1"})
                self.assertNotIn("k8s-scope", {key for key, _ in component["tags"]})

    def test_explicit_namespace_without_a_service_is_still_a_namespace(self):
        self.assertEqual(map_resource(self.namespace, {"service.namespace": "orders"})["identifier"], "urn:opentelemetry:namespace/orders")
        self.assertIsNone(map_resource(self.namespace, {}))
        self.assertIsNone(map_resource(self.namespace, {"service.namespace": ""}))

    def test_required_expression_failures_are_not_suppressed(self):
        with self.assertRaises(CELEvalError):
            map_resource(self.service, {"service.name": 42})


if __name__ == "__main__":
    unittest.main()
