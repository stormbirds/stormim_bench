from locust import TaskSet, task

from StormIMClient import StormIMLocust


class UserBehavior(TaskSet):
    @task(3)
    def test_default(self):
        self.client.send_heartbeat_msg()


class WebsiteUser(StormIMLocust):
    host = 'wifi.stormbirds.cn'
    port = 8855
    task_set = UserBehavior
