bl_info = {
    "name": "Weight_Normalizier_UI",
    "author": "Yu-Lit",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "Weight Paint Toolbar",
    "description": "Displays a UI for weight normalization",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Tools",
}


import bpy

from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import Context

"""---------------------------------------------------------
------------------------------------------------------------
    Property Group
------------------------------------------------------------
---------------------------------------------------------"""


class WEIGHTNORMALIZER_SCENE_operator_properties(bpy.types.PropertyGroup):
    target_vertex_group: EnumProperty(
        name="Target Vertex Group",
        description="Stores parameters referenced by the operator",
        items=(
            ("BONE_DEFORM", "Deform Bone Only", ""),
            ("BONE_SELECT", "Selected Bone Only", ""),
            ("ALL", "All", ""),
        ),
        default="BONE_DEFORM",
    )

    limit_bone_count: IntProperty(
        name="Limit Bone Count",
        description="",
        default=4,
        min=1,
    )

    quantize_steps: IntProperty(
        name="Quantize Steps",
        description="",
        default=4,
        min=1,
    )

    limit_weight_value: FloatProperty(
        name="Limit Weight Value",
        description="",
        default=0.1,
        min=0.0,
        max=1.0,
    )

    lock_active: BoolProperty(
        name="Lock Active",
        description="",
        default=True,
    )


class WEIGHTNORMALIZER_OT_weight_normalizing_sequence(bpy.types.Operator):
    bl_idname = "weight.weight_normalizing_sequence"
    bl_label = "Normalize Sequence"
    bl_description = "Perform a weight normalization work sequence"
    bl_options = {"UNDO"}

    def execute(self, context):
        armature = [obj for obj in context.selected_objects if obj.type == "ARMATURE"]
        if not armature:
            self.report({"ERROR"}, "Armature Object is not Selected")
            return {"CANCELLED"}

        props: WEIGHTNORMALIZER_SCENE_operator_properties = (
            context.scene.weight_normalizer
        )
        lock_active = props.lock_active
        target_group = props.target_vertex_group
        bone_count = props.limit_bone_count
        steps = props.quantize_steps
        limit_value = props.limit_weight_value

        bpy.ops.object.vertex_group_limit_total(
            group_select_mode=target_group, limit=bone_count
        )
        bpy.ops.object.vertex_group_normalize_all(
            group_select_mode=target_group, lock_active=lock_active
        )
        bpy.ops.object.vertex_group_quantize(
            group_select_mode=target_group, steps=steps
        )
        bpy.ops.object.vertex_group_clean(
            group_select_mode=target_group, limit=limit_value
        )
        bpy.ops.object.vertex_group_normalize_all(
            group_select_mode=target_group, lock_active=lock_active
        )

        return {"FINISHED"}


"""---------------------------------------------------------
------------------------------------------------------------
    UI
------------------------------------------------------------
---------------------------------------------------------"""


class WEIGHTNORMALIZER_PT_operator_options(bpy.types.Panel):
    bl_idname = "WEIGHTNORMALIZER_PT_operator_options"
    bl_label = "Operator Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"INSTANCED"}
    bl_ui_units_x = 14

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        props = context.scene.weight_normalizer

        row = col.row(align=True)
        row.label(text="Target")
        row.prop(props, "target_vertex_group", text="")

        row = col.row(align=True)
        row.label(text="Bone Count")
        row.prop(props, "limit_bone_count", text="")

        row = col.row(align=True)
        row.label(text="Quantize_Steps")
        row.prop(props, "quantize_steps", text="")

        row = col.row(align=True)
        row.label(text="Limit Weight Value")
        row.prop(props, "limit_weight_value", text="")

        row = col.row(align=True)
        row.label(text="Lock Active")
        row.prop(props, "lock_active", text="")


def draw_operator_properties_ui(self, context):
    layout: bpy.types.UILayout = self.layout

    if context.mode == "PAINT_WEIGHT":
        layout.popover(
            panel=WEIGHTNORMALIZER_PT_operator_options.bl_idname, text="Options"
        )


def draw_operator(self, context):
    layout = self.layout

    if context.mode == "PAINT_WEIGHT":
        layout.operator(WEIGHTNORMALIZER_OT_weight_normalizing_sequence.bl_idname)


"""---------------------------------------------------------
------------------------------------------------------------
    REGISTER/UNREGISTER
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    WEIGHTNORMALIZER_SCENE_operator_properties,
    WEIGHTNORMALIZER_OT_weight_normalizing_sequence,
    WEIGHTNORMALIZER_PT_operator_options,
)


def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            pass

    bpy.types.Scene.weight_normalizer = PointerProperty(
        name="Operator Parameters",
        type=WEIGHTNORMALIZER_SCENE_operator_properties,
    )

    bpy.types.VIEW3D_HT_tool_header.prepend(draw_operator)
    bpy.types.VIEW3D_HT_tool_header.prepend(draw_operator_properties_ui)


def unregister():
    del bpy.types.Scene.weight_normalizer

    bpy.types.VIEW3D_HT_tool_header.remove(draw_operator_properties_ui)
    bpy.types.VIEW3D_HT_tool_header.remove(draw_operator)

    for cls in CLASSES:
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
