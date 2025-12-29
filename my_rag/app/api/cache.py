"""
缓存管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    获取缓存统计信息
    
    Returns:
        缓存统计数据
    """
    try:
        stats = cache_service.get_cache_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")

@router.delete("/clear")
async def clear_cache() -> Dict[str, Any]:
    """
    清空所有缓存
    
    Returns:
        清空结果
    """
    try:
        count = cache_service.clear_all_cache()
        return {
            "success": True,
            "message": f"已清空 {count} 条缓存",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

@router.delete("/delete")
async def delete_cache(question: str) -> Dict[str, Any]:
    """
    删除指定问题的缓存
    
    Args:
        question: 问题内容
    
    Returns:
        删除结果
    """
    try:
        success = cache_service.delete_cache(question)
        if success:
            return {
                "success": True,
                "message": "缓存已删除"
            }
        else:
            return {
                "success": False,
                "message": "缓存不存在或删除失败"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除缓存失败: {str(e)}")

@router.get("/health")
async def cache_health() -> Dict[str, Any]:
    """
    检查缓存服务健康状态
    
    Returns:
        健康状态
    """
    return {
        "enabled": cache_service.enabled,
        "status": "healthy" if cache_service.enabled else "disabled"
    }
