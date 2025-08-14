import numpy as np

def douglas_peucker(points, epsilon=1.0, return_type='list'):
    """
    道格拉斯–普克算法实现，支持多种输入输出类型。
    
    Args:
        points (list 或 np.ndarray): 输入的点集。
        epsilon (float): 简化阈值。
        return_type (str): 返回值类型，可选 'list' 或 'np'。
        
    Returns:
        list 或 np.ndarray: 简化的点集。

    demo:
        points_list = [[0, 0], [1, 0.1], [2, -0.1], [3, 5], [4, 6], [5, 7]]
        points_np = np.array(points_list)

        # 示例 1: 输入为 Python 列表，返回类型为列表 (默认)
        result_list = douglas_peucker(points_list, epsilon=1.0)
        print("---")
        print("输入列表，返回列表:")
        print(result_list)
        print(f"数据类型: {type(result_list)}")

        输入列表，返回列表:
        [[0.0, 0.0], [2.0, -0.1], [3.0, 5.0], [5.0, 7.0]]
        数据类型: <class 'list'>

        # 示例 2: 输入为 NumPy 数组，返回类型为 NumPy 数组
        result_np = douglas_peucker(points_np, epsilon=1.0, return_type='np')
        print("---")
        print("输入 np.ndarray，返回 np.ndarray:")
        print(result_np)
        print(f"数据类型: {type(result_np)}")
        
        # 示例 3: 输入为列表，返回类型为 NumPy 数组
        result_list_to_np = douglas_peucker(points_list, epsilon=1.0, return_type='np')
        print("---")
        print("输入列表，返回 np.ndarray:")
        print(result_list_to_np)
        print(f"数据类型: {type(result_list_to_np)}")
    """
    # 确保输入是 NumPy 数组，便于内部计算
    if not isinstance(points, np.ndarray):
        points = np.array(points)

    # 如果点数少于3个，直接返回
    if len(points) < 3:
        return points.tolist() if return_type == 'list' else points

    def perpendicular_distance(point, start, end):
        """计算点到线段的垂直距离，兼容 NumPy 2.0+"""
        if np.all(start == end):
            return np.linalg.norm(point - start)
        
        start_3d = np.append(start, 0)
        end_3d = np.append(end, 0)
        point_3d = np.append(point, 0)
        
        cross_product = np.cross(end_3d - start_3d, point_3d - start_3d)
        
        return np.linalg.norm(cross_product) / np.linalg.norm(end - start)

    # 找到距离起点和终点连线最远的点
    start, end = points[0], points[-1]
    distances = [perpendicular_distance(p, start, end) for p in points[1:-1]]
    
    if not distances:
        # 如果没有中间点，直接返回
        return points.tolist() if return_type == 'list' else points
        
    max_distance = max(distances)
    idx = distances.index(max_distance) + 1

    if max_distance > epsilon:
        left = douglas_peucker(points[:idx+1], epsilon, return_type)
        right = douglas_peucker(points[idx:], epsilon, return_type)
        
        # 根据返回类型拼接结果
        if return_type == 'list':
            return left[:-1] + right
        else:
            return np.vstack((left[:-1], right))
    else:
        # 递归终止，根据返回类型返回结果
        result_array = np.array([start, end])
        return result_array.tolist() if return_type == 'list' else result_array


if __name__ == "__main__":
    pass