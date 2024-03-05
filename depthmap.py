bl_info = {
    "name": "True Depthmap Export",
    "description": "A VERY basic one click depth map exporter - button is in the render properties tab",
    "author": "PLAN8",
    "doc_url": "https://github.com/PLAN8VR/Depth_Map",
    "tracker_url": "https://github.com/PLAN8VR/Depth_Map/issues",
    "category": "Render",
    "blender": (4, 0, 2),
    "version": (0, 0, 2),
}

import bpy
import os
from bpy_extras.io_utils import ExportHelper


class ExportTrueDepthmap(bpy.types.Operator, ExportHelper):
    """Export Depthmap"""
    bl_idname = "export.true_depthmap"
    bl_label = "Export True Depthmap"
    bl_options = {'PRESET'}

    filename_ext = ".png"

    filter_glob: bpy.props.StringProperty(
        defaults="*.png;",
        options={'HIDDEN'},
    )

    def execute(self, context):
        filepath = self.filepath
        depthmap_path = os.path.splitext(filepath)[0] + "_depthmap"

        # Save current render settings
        original_resolution_x = context.scene.render.resolution_x
        original_resolution_y = context.scene.render.resolution_y
        original_percentage_scale = context.scene.render.resolution_percentage
        original_render_engine = context.scene.render.engine
        original_view_transform = context.scene.view_settings.view_transform
        original_film_transparency = context.scene.render.film_transparent
        original_view_settings = context.scene.view_settings.look
        original_colour_space = context.scene.sequencer_colorspace_settings.name

        # Set new resolution settings
        context.scene.render.resolution_x = 1024
        context.scene.render.resolution_y = 1024
        context.scene.render.resolution_percentage = 100

        # Ensure compositor nodes are enabled
        context.scene.use_nodes = True

        # Ensure that the scene has a compositor node tree
        if context.scene.use_nodes and context.scene.node_tree:
            tree = context.scene.node_tree

            # Set up the compositor for rendering the depth map
            context.scene.render.use_compositing = True

            # Set view transform to Raw
            context.scene.view_settings.view_transform = 'Raw'
            
            # Set view settings
            context.scene.view_settings.look = 'None'
            
            # Set colourspace (note to the Sepos, colour spelled correctly ;-))
            context.scene.sequencer_colorspace_settings.name = 'Non-Color'

            # Ensure Z pass is enabled
            bpy.context.view_layer.use_pass_z = True

            # Clear existing nodes
            for node in tree.nodes:
                tree.nodes.remove(node)

            # Create Render Layers node
            render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
            render_layers_node.location = (-400, 0)

            # Create Invert node
            invert_node = tree.nodes.new(type='CompositorNodeInvert')
            invert_node.location = (-100, -200)

            # Create Normalize node
            normalize_node = tree.nodes.new(type='CompositorNodeNormalize')
            normalize_node.location = (100, -200)

            # Create Viewer node
            viewer_node = tree.nodes.new(type='CompositorNodeViewer')
            viewer_node.location = (600, -200)

            # Create Set Alpha node
            set_alpha_node = tree.nodes.new(type='CompositorNodeSetAlpha')
            set_alpha_node.location = (300, 0)

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
            file_output_node.file_slots.new("Diffuse")
            file_output_node.file_slots[0].path = os.path.basename(
                depthmap_path)

            # Connect nodes
            tree.links.new(
                render_layers_node.outputs["Depth"], invert_node.inputs["Color"])
            tree.links.new(
                render_layers_node.outputs["Alpha"], set_alpha_node.inputs["Alpha"])
            tree.links.new(
                render_layers_node.outputs["Alpha"], viewer_node.inputs["Alpha"])
            tree.links.new(
                render_layers_node.outputs["Image"], file_output_node.inputs["Diffuse"])
            tree.links.new(
                invert_node.outputs["Color"], normalize_node.inputs["Value"])
            tree.links.new(
                normalize_node.outputs["Value"], set_alpha_node.inputs["Image"])
            tree.links.new(
                set_alpha_node.outputs["Image"], file_output_node.inputs["Depth"])
            tree.links.new(
                set_alpha_node.outputs["Image"], viewer_node.inputs["Image"])

            # Enable compositor backdrop - needs working out
            # context.space_data["CompositorNodeTree"].show_backdrop = True

            # Set film transparent to True for a transparent background
            context.scene.render.film_transparent = True

            # Set Render engine to EEVEE
            context.scene.render.engine = 'BLENDER_EEVEE'

            # Render the image
            bpy.ops.render.render(write_still=True)

            print("Depth map saved to:", depthmap_path)
            self.report(
                {'INFO'}, "Depthmap and diffuse image saved successfully")
        else:
            print("Error: Compositor not set up in the scene.")
            self.report({'INFO'}, " ! Error ! Depthmap not saved.")

        # Restore original render settings

        context.scene.render.resolution_x = original_resolution_x
        context.scene.render.resolution_y = original_resolution_y
        context.scene.render.resolution_percentage = original_percentage_scale
        context.scene.render.engine = original_render_engine
        context.scene.view_settings.view_transform = original_view_transform
        context.scene.render.film_transparent = original_film_transparency
        context.scene.view_settings.look = original_view_settings
        context.scene.sequencer_colorspace_settings.name = original_colour_space

        return {'FINISHED'}


class RENDER_PT_true_depth(bpy.types.Panel):
    bl_label = "True Depth Export"
    bl_idname = "RENDER_PT_true_depth"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        layout.operator("export.true_depthmap",
                        text="Export Depthmap (.png)", icon='IMAGE_ZDEPTH')


def register():
    bpy.utils.register_class(ExportTrueDepthmap)
    bpy.utils.register_class(RENDER_PT_true_depth)


def unregister():
    bpy.utils.unregister_class(ExportTrueDepthmap)
    bpy.utils.unregister_class(RENDER_PT_true_depth)


if __name__ == "__main__":
    register()
