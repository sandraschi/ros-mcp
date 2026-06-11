"""Tests for ros-mcp server tools."""

from ros_mcp.server import ros_status, topic_list, service_list, node_list, list_jobs


class TestRosStatus:
    def test_ros_status_no_ros(self):
        result = ros_status()
        assert isinstance(result, dict)
        assert "ros2_cli" in result or "success" in result

    def test_ros_status_keys(self):
        result = ros_status()
        expected_keys = {"ros2_cli", "rclpy", "message", "success"}
        assert expected_keys.issubset(result.keys())


class TestTopicList:
    def test_topic_list_no_ros(self):
        result = topic_list()
        assert "success" in result
        if not result.get("success"):
            assert "message" in result or "error" in result


class TestServiceList:
    def test_service_list_no_ros(self):
        result = service_list()
        assert "success" in result
        if not result.get("success"):
            assert "message" in result or "error" in result


class TestNodeList:
    def test_node_list_no_ros(self):
        result = node_list()
        assert "success" in result
        if not result.get("success"):
            assert "message" in result or "error" in result


class TestListJobs:
    def test_list_jobs_empty(self):
        result = list_jobs()
        assert "success" in result
