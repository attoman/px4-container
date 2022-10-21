import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import math

#   ROS2 python 
import rclpy
from rclpy.node import Node
from rclpy.qos_event import SubscriptionEventCallbacks
from rclpy.parameter import Parameter
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSHistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy
from rclpy.qos import qos_profile_sensor_data

from px4_msgs.msg import Timesync
from msg_srv_act_interface.srv import PathFollowingSetpoint

class PathPlanningService(Node):
    def __init__(self):
        super().__init__('planning_service')
        self.qosProfileGen()
        self.TimesyncSubscriber_ = self.create_subscription(Timesync, '/fmu/time_sync/out', self.TimesyncCallback, self.QOS_Sub_Sensor)
        self.declare_service_client_custom()
        self.timestamp = 0
        
    def declare_service_client_custom(self): 
        self.PathFollowingServiceClient_ = self.create_client(PathFollowingSetpoint, 'path_following')
        while not self.PathFollowingServiceClient_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Path Planning not available, waiting again...') 
 
    def qosProfileGen(self):
        #   Reliability : 데이터 전송에 있어 속도를 우선시 하는지 신뢰성을 우선시 하는지를 결정하는 QoS 옵션
        #   History : 데이터를 몇 개나 보관할지를 결정하는 QoS 옵션
        #   Durability : 데이터를 수신하는 서브스크라이버가 생성되기 전의 데이터를 사용할지 폐기할지에 대한 QoS 옵션
        self.QOS_Sub_Sensor = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            durability=QoSDurabilityPolicy.VOLATILE)
        
        self.QOS_Service = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            durability=QoSDurabilityPolicy.VOLATILE)
        
    def RequestPathPlanning(self, start_point, goal_point):
        self.path_following_request = PathFollowingSetpoint.Request()
        self.path_following_request.request_timestamp = self.timestamp
        self.path_following_request.request_pathfollowing = True
        # self.path_following_request.start_point = start_point
        # self.path_following_request.goal_point = goal_point
        self.future = self.PathPlanningServiceClient_.call_async(self.path_following_request)

    def TimesyncCallback(self, msg):
        self.timestamp = msg.timestamp