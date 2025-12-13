# Fix for issue #705 - Metadata JSON parsing
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def parse_metadata(metadata_str: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Parse metadata from JSON string to dict.
    
    Args:
        metadata_str: JSON string from database or dict
        
    Returns:
        Parsed dictionary or None if invalid
    """
    if metadata_str is None:
        return None
    
    # Already a dict (some DBs return parsed JSON)
    if isinstance(metadata_str, dict):
        return metadata_str
    
    # Parse string to dict
    if isinstance(metadata_str, str):
        try:
            return json.loads(metadata_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in metadata: {e}")
            return None
    
    return None

def db_get_images_by_cluster_id(cluster_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all images for a specific face cluster.
    
    FIXED: Now properly deserializes metadata JSON strings.
    
    Args:
        cluster_id: The face cluster ID
        
    Returns:
        List of image dictionaries with parsed metadata
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            i.id,
            i.path,
            i.thumbnail_path,
            i.folder_id,
            i.metadata,
            i.created_at,
            i.updated_at,
            f.face_id,
            f.confidence
        FROM images i
        JOIN faces f ON i.id = f.image_id
        WHERE f.cluster_id = ?
        ORDER BY i.created_at DESC
        """
        
        cursor.execute(query, (cluster_id,))
        rows = cursor.fetchall()
        
        images = []
        for row in rows:
            # Parse metadata before returning
            metadata = parse_metadata(row['metadata'])
            
            images.append({
                'id': row['id'],
                'path': row['path'],
                'thumbnail_path': row['thumbnail_path'],
                'folder_id': row['folder_id'],
                'metadata': metadata,  # Now properly typed as dict
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'face_id': row['face_id'],
                'confidence': row['confidence'],
            })
        
        return images
        
    finally:
        conn.close()

def db_get_all_face_clusters_with_metadata() -> List[Dict[str, Any]]:
    """
    Get all face clusters with properly parsed metadata.
    
    Returns:
        List of clusters with parsed metadata for representative images
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            fc.id,
            fc.cluster_label,
            fc.name,
            fc.representative_face_id,
            i.metadata,
            i.thumbnail_path
        FROM face_clusters fc
        LEFT JOIN faces f ON fc.representative_face_id = f.face_id
        LEFT JOIN images i ON f.image_id = i.id
        ORDER BY fc.created_at DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        clusters = []
        for row in rows:
            # Parse metadata
            metadata = parse_metadata(row['metadata'])
            
            clusters.append({
                'id': row['id'],
                'cluster_label': row['cluster_label'],
                'name': row['name'],
                'representative_face_id': row['representative_face_id'],
                'thumbnail_path': row['thumbnail_path'],
                'metadata': metadata,  # Properly parsed
            })
        
        return clusters
        
    finally:
        conn.close()
