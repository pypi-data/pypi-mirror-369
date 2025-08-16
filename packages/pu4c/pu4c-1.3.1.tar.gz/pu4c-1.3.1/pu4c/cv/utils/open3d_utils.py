import open3d as o3d
import numpy as np
from . import (
    boxes3d_to_corners, get_oriented_bounding_box_lines, 
    color_det_class25, rviz_intensity_colormap, 
)

def create_pointcloud_geometry(points, labels=None, ds_voxel_size=None, colormap=None, uniform_color=None):
    """
    点云着色，优先级 标签颜色映射 > 指定的纯色 > 反射率(points[:, 3])着色
    注意，颜色值必须归一化，虽然不归一化并不报错，但是只能正确显示部分颜色导致与预期相悖
    """
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points[:, :3])
    if ds_voxel_size is not None:
        cloud = cloud.voxel_down_sample(ds_voxel_size)
    if labels is not None:
        colormap = [[1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]] if colormap is None else colormap
        colors = np.array(colormap)[labels.astype(np.int64)]
        cloud.colors = o3d.utility.Vector3dVector(colors)
    elif uniform_color is not None: cloud.paint_uniform_color(uniform_color)
    elif points.shape[1] == 4:
        colors = rviz_intensity_colormap(points[:, 3], out_norm=True)
        cloud.colors = o3d.utility.Vector3dVector(colors)
    
    return cloud
def create_boxes3d_geometry(boxes3d, uniform_color=[0, 0.99, 0], show_heading=True):
    """
    Args:
        boxes3d: (N, 7)[xyz,lwh,yaw] or (N, 8)[xyz,lwh,yaw,cls]
    """
    # 计算角点与线框
    N, C = boxes3d.shape
    corners = boxes3d_to_corners(boxes3d) # (N, 8, 3)
    box3d_lines = np.array(get_oriented_bounding_box_lines(head_cross_lines=show_heading)) # (12, 2)
    boxes3d_lines = box3d_lines[None, :].repeat(N, axis=0) # (N, 12, 2) 此时其中每个顶点的编号都是相对于该框的相对编号，范围 [0,7]
    offsets = np.arange(start=0, stop=N * 8, step=8)[:, None, None] # (N, 1, 1)
    boxes3d_lines = boxes3d_lines + offsets # 顶点编号加偏移得到唯一的顶点编号，以便与顶点相对应

    line_sets = o3d.geometry.LineSet()
    line_sets.points = o3d.open3d.utility.Vector3dVector(corners.reshape((-1, 3)))
    line_sets.lines = o3d.open3d.utility.Vector2iVector(boxes3d_lines.reshape((-1, 2)))
    if C == 7: 
        line_sets.paint_uniform_color(uniform_color)
    else:
        if np.max(boxes3d[:, 7]) < 25:
            colormap = color_det_class25
        else:
            raise ValueError("Number of classes is bigger than number of colors")
        box3d_colors = np.array(colormap)[boxes3d[:, 7].astype(np.int64)]
        boxes3d_colors = box3d_colors[:, None, :].repeat(boxes3d_lines.shape[1], axis=1) # (N, 12, 3)
        line_sets.colors = o3d.utility.Vector3dVector(boxes3d_colors.reshape((-1, 3)))

    return line_sets
def create_voxels_geometry(voxel_centers, voxel_size, uniform_color=[0, 0, 0]):
    """
    批量添加边框，可视化体素就是每个中心点都画一个框
    """
    # 计算每个非空体素的边框 (N,7)[xyz,wlh,yaw]
    N = voxel_centers.shape[0]
    wlh = np.tile(voxel_size, (N, 1)) # voxel_size 的第 0 维重复 N 次，第 1 维重复 1 次
    yaw = np.zeros((N, 1))
    boxes3d = np.concatenate((voxel_centers, wlh, yaw), axis=1)

    return create_boxes3d_geometry(boxes3d, uniform_color=uniform_color, show_heading=False)

def playcloud(switch_func, length, start=0, step=10, point_size=1, background_color=[0, 0, 0]):
    """视角参数这块容易引起版本冲突，如无必要可删除，在 open3d-v0.18.0 测试通过"""
    def switch_wrapper(vis, i):
        """保存用户手动调整的视角参数"""
        global camera_params
        camera_params = vis.get_view_control().convert_to_pinhole_camera_parameters()
        vis.clear_geometries()

        switch_func(vis, i)

        vis.get_view_control().convert_from_pinhole_camera_parameters(camera_params, allow_arbitrary=True)
        vis.update_renderer()
    def prev(vis):
        global g_idx
        g_idx = max(g_idx - 1, 0)
        switch_wrapper(vis, g_idx)
    def next(vis):
        global g_idx
        g_idx = min(g_idx + 1, length-1)
        switch_wrapper(vis, g_idx)
    def prev_n(vis):
        global g_idx
        g_idx = max(g_idx - step, 0)
        switch_wrapper(vis, g_idx)
    def next_n(vis):
        global g_idx
        g_idx = min(g_idx + step, length-1)
        switch_wrapper(vis, g_idx)

    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window()
    vis.get_render_option().point_size = point_size
    vis.get_render_option().background_color = background_color

    vis.register_key_callback(ord('W'), prev_n)
    vis.register_key_callback(ord('S'), next_n)
    vis.register_key_callback(ord('A'), prev)
    vis.register_key_callback(ord('D'), next) # 按小写，但这里要填大写
    # vis.register_key_callback(ord(' '), next) # space

    global g_idx
    g_idx = start
    switch_wrapper(vis, start)
    vis.run()
    vis.destroy_window()