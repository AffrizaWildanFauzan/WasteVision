import torch
import torch.nn as nn
import timm
from PIL import Image
from torchvision import transforms
import io
import numpy as np
import logging
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

class ModelService:    
    def __init__(
        self,
        model_path: str,
        num_classes: int,
        img_size: int,
        mean: list,
        std: list,
        class_names: list,
        class_labels: dict,
        class_colors: dict,
        class_icons: dict
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_classes = num_classes
        self.img_size = img_size
        self.class_names = class_names
        self.class_labels = class_labels
        self.class_colors = class_colors
        self.class_icons = class_icons
        
        # Build model
        self.model = self._build_model()
        
        # Load weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Setup transforms
        self.transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
        
        logger.info(f"Model loaded on {self.device}")
    
    def _build_model(self):
        model = timm.create_model('convnext_large', pretrained=False)
        num_features = model.head.fc.in_features
        model.head.fc = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, self.num_classes)
        )
        return model
    
    def preprocess(self, image_bytes: bytes) -> torch.Tensor:
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Apply transforms
            image_tensor = self.transform(image)
            
            # Add batch dimension
            image_tensor = image_tensor.unsqueeze(0)
            
            return image_tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            raise
    
    def predict(self, image_bytes: bytes) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            # Preprocess
            image_tensor = self.preprocess(image_bytes)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            # Get results
            pred_class = self.class_names[predicted.item()]
            confidence_score = confidence.item()
            all_probs = probabilities.squeeze().cpu().numpy()
            
            # Format result
            result = {
                'predicted_class': pred_class,
                'confidence': round(confidence_score, 4),
                'probabilities': {
                    self.class_names[i]: round(float(all_probs[i]), 4)
                    for i in range(self.num_classes)
                },
                'label': self.class_labels.get(pred_class, pred_class),
                'color': self.class_colors.get(pred_class, '#000000'),
                'icon': self.class_icons.get(pred_class, '📦'),
                'top_3': self._get_top_k(all_probs, 3)
            }
            
            return result, None
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None, str(e)
    
    def _get_top_k(self, probabilities: np.ndarray, k: int = 3) -> list:
        indices = np.argsort(probabilities)[::-1][:k]
        return [
            {
                'class': self.class_names[i],
                'label': self.class_labels.get(self.class_names[i], self.class_names[i]),
                'probability': round(float(probabilities[i]), 4),
                'icon': self.class_icons.get(self.class_names[i], '📦')
            }
            for i in indices
        ]
    
    def predict_batch(self, image_batch: list) -> list:
        results = []
        for image_bytes in image_batch:
            result, error = self.predict(image_bytes)
            if error:
                results.append({'error': error})
            else:
                results.append(result)
        return results
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'architecture': 'ConvNeXt-Large',
            'num_classes': self.num_classes,
            'classes': self.class_names,
            'input_size': self.img_size,
            'device': str(self.device),
            'trainable_params': sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }