import os
import hashlib
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request

class YogaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item.get('image_urls', []):
            yield Request(
                url=image_url,
                meta={
                    'pose_name': item['pose_name'],
                    'pose_name_hindi': item['pose_name_hindi'],
                    'image_id': item.get('image_id', ''),
                }
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        # Get metadata from request
        pose_name_hindi = request.meta.get('pose_name_hindi', 'unknown')
        image_id = request.meta.get('image_id', '')
        
        # Create a directory structure based on pose name
        directory = f"original/{pose_name_hindi}"
        
        # Generate a unique filename
        url = request.url
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Get file extension from URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        ext = ext.lower() or '.jpg'  # Default to .jpg if no extension
        
        # Ensure extension starts with a dot
        if not ext.startswith('.'):
            ext = '.' + ext
            
        # Create filename with pose name, image ID, and hash
        if image_id:
            filename = f"{pose_name_hindi}_{image_id}_{url_hash[:8]}{ext}"
        else:
            filename = f"{pose_name_hindi}_{url_hash[:8]}{ext}"
            
        return os.path.join(directory, filename)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['images'] = image_paths
        return item 
