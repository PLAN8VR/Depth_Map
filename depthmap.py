bl_info = {
    "name": "True Depthmap Export",
    "blender": (4, 0, 0),
    "category": "Render",
}

import bpy
import os
from bpy_extras.io_utils import ExportHelper

class ExportTrueDepthmap(bpy.types.Operator, ExportHelper):
    bl_idname = "export.true_depthmap"
    bl_label = "Export True Depthmap"
    bl_options = {'PRESET'}

    filename_ext = ".png"

    filter_glob: bpy.props.StringProperty(
        defaults="*.exr;*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp'",
        options={'HIDDEN'},
    )

    def execute(self, context):
        filepath = self.filepath
        depthmap_path = os.path.splitext(filepath)[0] + "_depthmap"

        # Save current render settings
        original_resolution_x = context.scene.render.resolution_x
        original_resolution_y = context.scene.render.resolution_y
        original_percentage_scale = context.scene.render.resolution_percentage

        # Set new resolution settings
        context.scene.render.resolution_x = 1024
        context.scene.render.resolution_y = 1024
        context.scene.render.resolution_percentage = 100

        # Ensure that the scene has a compositor node tree
        if context.scene.use_nodes and context.scene.node_tree:
            tree = context.scene.node_tree

            # Clear existing nodes
            for node in tree.nodes:
                tree.nodes.remove(node)

            # Create Render Layers node
            render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
            render_layers_node.location = (-200, 0)

            # Create Invert node
            invert_node = tree.nodes.new(type='CompositorNodeInvert')
            invert_node.location = (0, 100)

            # Create Normalize node
            normalize_node = tree.nodes.new(type='CompositorNodeNormalize')
            normalize_node.location = (200, 0)

            # Create Viewer node
            viewer_node = tree.nodes.new(type='CompositorNodeViewer')
            viewer_node.location = (400, 0)

            # Create a File Output node for the depth map
            file_output_node = tree.nodes.new(type='CompositorNodeOutputFile')
            file_output_node.label = 'Depth Output'
            file_output_node.base_path = os.path.dirname(depthmap_path)
            file_output_node.location = (600, 0)

            # Set output properties
            file_output_node.format.file_format = 'PNG'
            file_output_node.format.color_mode = 'RGBA'
            file_output_node.format.color_depth = '16'
            file_output_node.file_slots.new("Depth")
            file_output_node.file_slots[0].path = os.path.basename(depthmap_path)

            # Set up the compositor for rendering the depth map
            context.scene.render.use_compositing = True

            # Connect nodes
            tree.links.new(render_layers_node.outputs["Depth"], invert_node.inputs["Color"])
            tree.links.new(invert_node.outputs["Color"], normalize_node.inputs["Value"])
            tree.links.new(normalize_node.outputs["Value"], file_output_node.inputs["Image"])
            tree.links.new(normalize_node.outputs["Value"], viewer_node.inputs["Image"])

            # Set the output file path for the depth map
            file_output_node.file_slots.new("Depth")
            file_output_node.file_slots[0].path = os.path.basename(depthmap_path)

            # Render the image
            bpy.ops.render.render(write_still=True)

            print("Depth map saved to:", depthmap_path)
        else:
            print("Error: Compositor not set up in the scene.")

        # Restore original render settings
        context.scene.render.resolution_x = original_resolution_x
        context.scene.render.resolution_y = original_resolution_y
        context.scene.render.resolution_percentage = original_percentage_scale

        return {'FINISHED'}


class RENDER_PT_true_depth(bpy.types.Panel):
    bl_label = "True Depth Export"
    bl_idname = "RENDER_PT_true_depth"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        layout.operator("export.true_depthmap", text="Export Depthmap (.png)")


def register():
    bpy.utils.register_class(ExportTrueDepthmap)
    bpy.utils.register_class(RENDER_PT_true_depth)


def unregister():
    bpy.utils.unregister_class(ExportTrueDepthmap)
    bpy.utils.unregister_class(RENDER_PT_true_depth)


if __name__ == "__main__":
    register()
