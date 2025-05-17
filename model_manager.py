import os
import json
import logging
import requests
import shutil
import datetime
from urllib.parse import urljoin

# Configure logging
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Model Manager for handling model downloads, caching, and uploading to Hugging Face.
    """
    
    # Base URLs
    HF_API_URL = "https://huggingface.co/api/"
    HF_MODEL_URL = "https://huggingface.co/"
    
    def __init__(self, hf_token=None, cache_dir="models_cache"):
        """
        Initialize the Model Manager.
        
        Args:
            hf_token (str, optional): Hugging Face API token. If not provided, 
                                      will use HF_API_TOKEN environment variable.
            cache_dir (str): Directory to store cached models
        """
        self.hf_token = hf_token or os.environ.get("HUGGINGFACE_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        self.cache_dir = cache_dir
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load cached model index
        self.model_index = self._load_model_index()
    
    def _load_model_index(self):
        """
        Load the model index from disk.
        
        Returns:
            dict: Model index data
        """
        index_path = os.path.join(self.cache_dir, "model_index.json")
        
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Error decoding model index JSON")
        
        # Return empty index if file doesn't exist or is corrupted
        return {"models": {}}
    
    def _save_model_index(self):
        """Save the model index to disk."""
        index_path = os.path.join(self.cache_dir, "model_index.json")
        
        try:
            with open(index_path, 'w') as f:
                json.dump(self.model_index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving model index: {str(e)}")
    
    def is_model_cached(self, model_id):
        """
        Check if a model is cached locally.
        
        Args:
            model_id (str): Hugging Face model ID
            
        Returns:
            bool: True if model is cached, False otherwise
        """
        return model_id in self.model_index["models"]
    
    def get_model_info(self, model_id):
        """
        Get information about a cached model.
        
        Args:
            model_id (str): Hugging Face model ID
            
        Returns:
            dict: Model information or None if not cached
        """
        return self.model_index["models"].get(model_id)
    
    def list_cached_models(self):
        """
        List all cached models.
        
        Returns:
            dict: Dictionary of cached models
        """
        return self.model_index["models"]
    
    def search_models(self, query, task=None, limit=10):
        """
        Search Hugging Face models.
        
        Args:
            query (str): Search query
            task (str, optional): Filter by task
            limit (int): Maximum number of results
            
        Returns:
            list: List of model information
        """
        endpoint = urljoin(self.HF_API_URL, "models")
        
        params = {
            "search": query,
            "limit": limit
        }
        
        if task:
            params["filter"] = task
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error searching models: {str(e)}")
            return []
    
    def download_model(self, model_id, task=None, force=False):
        """
        Download a model from Hugging Face.
        
        Args:
            model_id (str): Hugging Face model ID
            task (str, optional): Task for the model
            force (bool): Force download even if already cached
            
        Returns:
            dict: Download result information
        """
        # Check if model is already cached
        if self.is_model_cached(model_id) and not force:
            logger.info(f"Model {model_id} is already cached")
            return {
                "status": "cached",
                "model_id": model_id,
                "local_path": os.path.join(self.cache_dir, model_id),
                "message": "Model already cached"
            }
        
        # In a real implementation, this would download the model files
        # For this demo, we'll simulate downloading by creating a placeholder
        model_dir = os.path.join(self.cache_dir, model_id.replace("/", "_"))
        os.makedirs(model_dir, exist_ok=True)
        
        # Create placeholder files
        with open(os.path.join(model_dir, "README.md"), 'w') as f:
            f.write(f"# {model_id}\n\nThis is a placeholder for the {model_id} model.\n")
        
        with open(os.path.join(model_dir, "config.json"), 'w') as f:
            config = {
                "model_id": model_id,
                "download_date": datetime.datetime.now().isoformat(),
                "task": task or "unknown"
            }
            json.dump(config, f, indent=2)
        
        # Update model index
        self.model_index["models"][model_id] = {
            "model_id": model_id,
            "local_path": model_dir,
            "download_date": datetime.datetime.now().isoformat(),
            "last_used": datetime.datetime.now().isoformat(),
            "task": task or "unknown",
            "size": "simulated"  # In a real implementation, this would be the actual size
        }
        
        self._save_model_index()
        
        return {
            "status": "success",
            "model_id": model_id,
            "local_path": model_dir,
            "message": "Model downloaded successfully (simulated)"
        }
    
    def upload_to_huggingface(self, model_id, local_path, is_private=True):
        """
        Upload a model to Hugging Face Hub.
        
        Args:
            model_id (str): Target model ID on Hugging Face
            local_path (str): Local path to model files
            is_private (bool): Whether the model should be private
            
        Returns:
            dict: Upload result information
        """
        if not self.hf_token:
            return {
                "status": "error",
                "message": "Hugging Face token not provided"
            }
        
        # Check if local path exists
        if not os.path.exists(local_path):
            return {
                "status": "error",
                "message": f"Local path does not exist: {local_path}"
            }
        
        # In a real implementation, this would upload the model to Hugging Face
        # using their API or the huggingface_hub library
        
        return {
            "status": "success",
            "model_id": model_id,
            "message": "Model uploaded successfully (simulated)",
            "repo_url": f"https://huggingface.co/{model_id}"
        }
    
    def delete_cached_model(self, model_id):
        """
        Delete a cached model.
        
        Args:
            model_id (str): Hugging Face model ID
            
        Returns:
            dict: Deletion result information
        """
        if not self.is_model_cached(model_id):
            return {
                "status": "error",
                "message": f"Model {model_id} is not cached"
            }
        
        model_info = self.get_model_info(model_id)
        local_path = model_info["local_path"]
        
        # Delete model directory
        if os.path.exists(local_path):
            try:
                shutil.rmtree(local_path)
            except Exception as e:
                logger.error(f"Error deleting model directory: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error deleting model directory: {str(e)}"
                }
        
        # Remove from index
        del self.model_index["models"][model_id]
        self._save_model_index()
        
        return {
            "status": "success",
            "message": f"Model {model_id} deleted from cache"
        }
    
    def get_model_files(self, model_id):
        """
        Get list of files for a cached model.
        
        Args:
            model_id (str): Hugging Face model ID
            
        Returns:
            list: List of file paths
        """
        if not self.is_model_cached(model_id):
            return []
        
        model_info = self.get_model_info(model_id)
        local_path = model_info["local_path"]
        
        if not os.path.exists(local_path):
            return []
        
        # List all files in the model directory
        files = []
        for root, _, filenames in os.walk(local_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                files.append({
                    "path": filepath,
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "relative_path": os.path.relpath(filepath, local_path)
                })
        
        return files
    
    def update_model_usage(self, model_id):
        """
        Update the last used timestamp for a model.
        
        Args:
            model_id (str): Hugging Face model ID
            
        Returns:
            bool: True if model was updated, False otherwise
        """
        if not self.is_model_cached(model_id):
            return False
        
        self.model_index["models"][model_id]["last_used"] = datetime.datetime.now().isoformat()
        self._save_model_index()
        
        return True
    
    def clean_cache(self, max_age_days=30, max_size_mb=5000):
        """
        Clean the model cache by removing old or unused models.
        
        Args:
            max_age_days (int): Maximum age in days
            max_size_mb (int): Maximum cache size in MB
            
        Returns:
            dict: Cleanup result information
        """
        # Not implemented for the demo
        # In a real implementation, this would delete old models to maintain cache size
        
        return {
            "status": "success",
            "message": "Cache cleaned (simulated)",
            "deleted_models": []
        }