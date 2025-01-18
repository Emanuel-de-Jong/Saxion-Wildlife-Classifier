import torch

def get_device():
    """
    Get the device to be used for the AI models. Most often CPU or CUDA.
    
    Returns
    -------
    device : torch.device
        Device to be used
    """
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    print(f"Using device: {device}")
    return device
