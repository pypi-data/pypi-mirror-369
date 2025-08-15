def format_elapsed_time(seconds):
    """格式化耗时显示，统一以0:00:00.00格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{'0' if minutes < 10 else ''}{int(minutes)}:{'0' if seconds < 10 else ''}{seconds:.2f}"