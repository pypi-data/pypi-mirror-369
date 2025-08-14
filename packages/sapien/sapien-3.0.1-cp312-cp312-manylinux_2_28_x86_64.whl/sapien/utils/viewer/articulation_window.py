#
# Copyright 2025 Hillbot Inc.
# Copyright 2020-2024 UCSD SU Lab
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from .plugin import Plugin, copy_to_clipboard
from sapien import internal_renderer as R
import sapien


class ArticulationWindow(Plugin):
    def __init__(self):
        self.reset()

    def reset(self):
        self.articulation = None
        self.ui_window = None

    def close(self):
        self.reset()

    @property
    def selected_entity(self):
        return self.viewer.selected_entity

    def notify_selected_entity_change(self):
        articulation = None
        if self.selected_entity:
            for c in self.selected_entity.components:
                if isinstance(c, sapien.physx.PhysxArticulationLinkComponent):
                    articulation = c.articulation

        self.articulation = articulation
        if articulation:
            self.joint_details = [False] * self.articulation.dof

    def set_joint_details(self, index, v):
        self.joint_details[index] = v

    def build(self):
        if self.viewer.render_scene is None:
            self.ui_window = None
            return

        self.ui_window = R.UIWindow().Label("Articulation")

        if not self.articulation:
            self.ui_window.append(R.UIDisplayText().Text("No articulation selected."))
            return

        art = self.articulation

        self.ui_window.append(
            R.UIDisplayText().Text(
                "Name: {}".format(art.name if art.name else "(no name)")
            ),
            R.UIDisplayText().Text(
                "Base Link Entity Id: {}".format(art.root.entity.per_scene_id)
            ),
        )
        uijoints = R.UISection().Label("Joints")
        joints = []
        for j in art.joints:
            if j.dof > 0:
                joints.append(j)

        def wrapper(art, i, qpos):
            def callback(slider):
                qpos[i] = slider.value
                art.set_qpos(qpos)

            return callback

        qpos = art.get_qpos()
        for i, (q, j) in enumerate(zip(qpos, joints)):
            line = R.UISameLine()
            uijoints.append(line)
            line.append(
                R.UISliderFloat()
                .WidthRatio(0.5)
                .Id("joint_{}".format(i))
                .Min(max(j.limit[0, 0], -20))
                .Max(min(j.limit[0, 1], 20))
                .Value(q)
                .Callback(wrapper(art, i, qpos)),
            )

            if self.joint_details[i]:
                line.append(
                    R.UIButton()
                    .Label("-")
                    .Id(str(i))
                    .Width(40)
                    .Callback(
                        (lambda i: lambda _: self.set_joint_details(i, False))(i)
                    ),
                    R.UIDisplayText().Text(j.name),
                )

                uijoints.append(
                    R.UISliderFloat()
                    .Label("Position Target")
                    .Id(str(i))
                    .WidthRatio(0.5)
                    .Min(max(j.limit[0, 0], -20))
                    .Max(min(j.limit[0, 1], 20))
                    .Value(j.drive_target)
                    .Callback((lambda j: lambda p: j.set_drive_target(p.value))(j)),
                    R.UISliderFloat()
                    .Label("Velocity Target")
                    .Id(str(i))
                    .WidthRatio(0.5)
                    .Min(-1)
                    .Max(1)
                    .Value(j.drive_velocity_target)
                    .Callback(
                        (lambda j: lambda p: j.set_drive_velocity_target(p.value))(j)
                    ),
                    R.UIInputFloat()
                    .Label("Damping")
                    .Id(str(i))
                    .WidthRatio(0.5)
                    .Value(j.damping)
                    .Callback(
                        (
                            lambda j: lambda p: j.set_drive_property(
                                j.stiffness,
                                p.value,
                                j.force_limit,
                                j.drive_mode,
                            )
                        )(j)
                    ),
                    R.UIInputFloat()
                    .Label("Stiffness")
                    .Id(str(i))
                    .WidthRatio(0.5)
                    .Value(j.stiffness)
                    .Callback(
                        (
                            lambda j: lambda p: j.set_drive_property(
                                p.value,
                                j.damping,
                                j.force_limit,
                                j.drive_mode,
                            )
                        )(j)
                    ),
                    R.UIInputFloat()
                    .Label("Force Limit")
                    .Id(str(i))
                    .WidthRatio(0.5)
                    .Value(j.force_limit)
                    .Callback(
                        (
                            lambda j: lambda p: j.set_drive_property(
                                j.stiffness,
                                j.damping,
                                p.value,
                                j.drive_mode,
                            )
                        )(j)
                    ),
                    R.UIInputFloat()
                    .Label("Friction")
                    .Id(str(i))
                    .WidthRatio(0.5)
                    .Value(j.friction)
                    .Callback((lambda j: lambda p: j.set_friction(p.value))(j)),
                    R.UICheckbox()
                    .Label("Acceleration")
                    .Id(str(i))
                    .Checked(j.drive_mode == "acceleration")
                    .Callback(
                        (
                            lambda j: lambda p: j.set_drive_property(
                                j.stiffness,
                                j.damping,
                                j.force_limit,
                                "acceleration" if p.checked else "force",
                            )
                        )(j)
                    ),
                    R.UIDummy().Height(20),
                )
            else:
                line.append(
                    R.UIButton()
                    .Label("+")
                    .Id(str(i))
                    .Width(40)
                    .Callback((lambda i: lambda _: self.set_joint_details(i, True))(i)),
                    R.UIDisplayText().Text(j.name),
                )

        self.ui_window.append(uijoints)

        def wrapper(art):
            def wrapped(_):
                copy_to_clipboard(f"[{', '.join([str(x) for x in art.get_qpos()])}]")

            return wrapped

        self.ui_window.append(
            R.UIButton().Label("Copy Joint Positions").Callback(wrapper(art))
        )

        def wrapper(art, show):
            def show_link_collision(_):
                for plugin in self.viewer.plugins:
                    if plugin.__class__.__name__ == "EntityWindow":
                        for link in art.links:
                            if show:
                                plugin.enable_collision_visual(link.entity)
                            else:
                                plugin.disable_collision_visual(link.entity)

            return show_link_collision

        self.ui_window.append(
            R.UISameLine().append(
                R.UIButton().Label("Show").Callback(wrapper(art, True)),
                R.UIButton().Label("Hide").Callback(wrapper(art, False)),
                R.UIDisplayText().Text("Collision"),
            ),
        )

    def get_ui_windows(self):
        self.build()
        if self.ui_window:
            return [self.ui_window]
        return []
