import numpy as np
import cv2
import torch
from PIL import Image
from contextlib import contextmanager
from typing import Union

@contextmanager
def patchify(image: Union[np.ndarray, torch.Tensor], 
             patch_size: tuple = (128, 128), 
             overlap_width: int = 0, 
             blend_alpha: float = 1.0):
    '''Patchify an image into smaller patches with optional overlap and blending.
    
        Example usage:
        with patchify(image, patch_size=(128, 128)) as patches:
            for patch in patches:
                patch[i] = do_something(patch[i])
        modified_image = image
    '''

    assert not isinstance(image, Image.Image), "Input should be a NumPy array or a PyTorch tensor, not a PIL Image."

    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        b, c, h, w = image.shape
        ph, pw = patch_size
        
        patches = []
        original_image = image.clone()
        reconstructed_image = torch.zeros_like(image)
        blend_count = torch.zeros((1, 1, h, w), device=image.device)  # Track overlapping regions
        
        rows = (h + ph - overlap_width - 1) // (ph - overlap_width)
        cols = (w + pw - overlap_width - 1) // (pw - overlap_width)
        
        for i in range(rows):
            for j in range(cols):
                y = i * (ph - overlap_width)
                x = j * (pw - overlap_width)
                
                patch = image[:, :, 
                    max(0, y):min(y + ph, h), 
                    max(0, x):min(x + pw, w)
                ]
                
                if patch.shape[2:] != patch_size:
                    patch = torch.nn.functional.interpolate(
                        patch,
                        size=patch_size, 
                        mode='bilinear', 
                        align_corners=False
                    )
                
                patches.append(patch)
    
    else:
        if image.ndim == 2:
            image = np.stack([image]*3, axis=-1)
        
        h, w = image.shape[:2]
        ph, pw = patch_size
        
        patches = []
        original_image = image.copy()
        reconstructed_image = np.zeros_like(image, dtype=np.float32)
        blend_count = np.zeros((h, w), dtype=np.float32)  # Track overlapping regions
        
        rows = (h + ph - overlap_width - 1) // (ph - overlap_width)
        cols = (w + pw - overlap_width - 1) // (pw - overlap_width)
        
        for i in range(rows):
            for j in range(cols):
                y = i * (ph - overlap_width)
                x = j * (pw - overlap_width)
                
                patch = image[
                    max(0, y):min(y + ph, h), 
                    max(0, x):min(x + pw, w)
                ]
                
                if patch.shape[:2] != patch_size:
                    patch = cv2.resize(patch, patch_size)
                
                patches.append(patch)
    
    try:
        yield patches
    finally:
        if is_tensor:
            for idx, patch in enumerate(patches):
                row = idx // cols
                col = idx % cols
                
                y = row * (ph - overlap_width)
                x = col * (pw - overlap_width)
                
                y_start = max(0, y)
                x_start = max(0, x)
                y_end = min(y + ph, h)
                x_end = min(x + pw, w)
                
                # Get actual region dimensions
                region_h = y_end - y_start
                region_w = x_end - x_start
                new_region = patch[:, :, :region_h, :region_w]
                
                # Create blending weights for overlap regions only
                weight_mask = torch.ones((region_h, region_w), device=image.device)
                
                if overlap_width > 0:
                    # Left overlap
                    if col > 0:
                        weight_mask[:, :overlap_width] = blend_alpha
                    # Right overlap  
                    if col < cols - 1:
                        weight_mask[:, -overlap_width:] = blend_alpha
                    # Top overlap
                    if row > 0:
                        weight_mask[:overlap_width, :] = blend_alpha
                    # Bottom overlap
                    if row < rows - 1:
                        weight_mask[-overlap_width:, :] = blend_alpha
                
                # Apply weighted blending
                orig_region = original_image[:, :, y_start:y_end, x_start:x_end]
                weight_mask = weight_mask.unsqueeze(0).unsqueeze(0)
                
                blended_region = (1 - weight_mask) * orig_region + weight_mask * new_region.to(orig_region.device)
                
                # Accumulate for overlapping regions
                reconstructed_image[:, :, y_start:y_end, x_start:x_end] += blended_region
                blend_count[:, :, y_start:y_end, x_start:x_end] += 1
            
            # Normalize overlapping regions
            blend_count = torch.clamp(blend_count, min=1)
            reconstructed_image = reconstructed_image / blend_count
            image.data[:] = reconstructed_image
            
        else:
            for idx, patch in enumerate(patches):
                row = idx // cols
                col = idx % cols
                
                y = row * (ph - overlap_width)
                x = col * (pw - overlap_width)
                
                y_start = max(0, y)
                x_start = max(0, x)
                y_end = min(y + ph, h)
                x_end = min(x + pw, w)
                
                # Get actual region dimensions
                region_h = y_end - y_start
                region_w = x_end - x_start
                new_region = patch[:region_h, :region_w]
                
                # Create blending weights for overlap regions only
                weight_mask = np.ones((region_h, region_w), dtype=np.float32)
                
                if overlap_width > 0:
                    # Left overlap
                    if col > 0:
                        weight_mask[:, :overlap_width] = blend_alpha
                    # Right overlap
                    if col < cols - 1:
                        weight_mask[:, -overlap_width:] = blend_alpha
                    # Top overlap
                    if row > 0:
                        weight_mask[:overlap_width, :] = blend_alpha
                    # Bottom overlap
                    if row < rows - 1:
                        weight_mask[-overlap_width:, :] = blend_alpha
                
                # Apply weighted blending
                orig_region = original_image[y_start:y_end, x_start:x_end].astype(np.float32)
                new_region = new_region.astype(np.float32)
                
                if len(orig_region.shape) == 3:
                    weight_mask = weight_mask[:, :, np.newaxis]
                
                blended_region = (1 - weight_mask) * orig_region + weight_mask * new_region
                
                # Accumulate for overlapping regions
                reconstructed_image[y_start:y_end, x_start:x_end] += blended_region
                blend_count[y_start:y_end, x_start:x_end] += 1
            
            # Normalize overlapping regions
            blend_count = np.maximum(blend_count, 1)
            if len(reconstructed_image.shape) == 3:
                blend_count = blend_count[:, :, np.newaxis]
            
            reconstructed_image = reconstructed_image / blend_count
            image[:] = reconstructed_image.astype(image.dtype)


if __name__ == '__main__':
    from torchvision.utils import save_image

    def process_patch(patch: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        if isinstance(patch, torch.Tensor):
            processed_patch = cv2.GaussianBlur(patch[0].cpu().numpy().transpose(1, 2, 0), (11, 11), 11)
            cv2.putText(processed_patch, 'Processed', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            processed_patch = torch.tensor(processed_patch).permute(2, 0, 1).unsqueeze(0)
            return processed_patch
        else:
            processed_patch = cv2.GaussianBlur(patch, (11, 11), 11)
            cv2.putText(processed_patch, 'Processed', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            return processed_patch

    cv_image = cv2.imread('./input.png')
    with patchify(cv_image, patch_size=(128, 128)) as patches:
        for i in range(len(patches)):
            patches[i] = process_patch(patches[i])
    cv2.imwrite('./output.png', cv_image)

    torch_image = torch.rand(1, 3, 512, 512)
    with patchify(torch_image, patch_size=(128, 128), overlap_width=16, blend_alpha=0.5) as patches:
        for i in range(len(patches)):
            patches[i] = process_patch(patches[i])
    save_image(torch_image, './output_torch.png')