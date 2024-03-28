from bamboo.actor.actor import Actor
from bamboo.nodes.mob import Mob


class Skeleton(Mob):
    def __init__(self, name: str, model: str, update=NotImplemented, active=True, anims=None, *args, **kwargs):
        super().__init__(name=name, update=update, active=active, *args, **kwargs)
        self._actor = Actor(model, anims=anims)
        self._actor.reparent_to(self)

        self.attach = self._actor.attach
        self.loop = self._actor.loop
        self.play = self._actor.play
        self.stop = self._actor.stop
        self.pose = self._actor.pose
        self.get_num_frames = self._actor.get_num_frames
        self.animation_controller = self._actor.getAnimControl
        self.enable_blend = self._actor.enable_blend
        self.disable_blend = self._actor.disable_blend
        self.blend_amount = self._actor.set_control_effect
        self.set_blend = self._actor.set_blend
        self.sub_part = self._actor.make_subpart
        self.joints = self._actor.list_joints

        self.joints_nodes: dict[str, NodePath] = {}
        self.control_nodes: dict[str, NodePath] = {}

    def parent_to_joint(self, node, joint_name: str, model_node: str = "modelRoot"):
        if joint_name not in self.joints_nodes:
            self.joints_nodes[joint_name] = self._actor.expose_joint(None, model_node, joint_name)

        node.reparent_to(self.joints_nodes[joint_name])

    def control_joint(self, node, joint_name: str, model_node: str = "modelRoot"):
        if joint_name not in self.control_nodes:
            self.control_nodes[joint_name] = self._actor.control_joint(None, model_node, joint_name)

        self.control_nodes[joint_name].reparent_to(node)

    def release_joint(self, joint_name: str, model_node: str = "modelRoot"):
        self._actor.release_joint(model_node, joint_name)

    @property
    def play_rate(self, animation_name=None, part_name=None):
        return self._actor.get_play_rate(animation_name, part_name)

    @play_rate.setter
    def play_rate(self, value: tuple):
        self._actor.set_play_rate(value[0], value[1])

    def clean_up(self):
        Skeleton.clear(self)
        self._actor.cleanup()
