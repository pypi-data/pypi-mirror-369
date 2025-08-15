import torch


def create_feature_mask(extractor, embeddings, attention_mask):
    """
    Create a feature mask for computing masked statistics.
    
    Args:
        extractor: The model/encoder
        embeddings: The embeddings tensor (B, T_feat, D)
        attention_mask: The attention mask from inputs (B, T_samples)
    
    Returns:
        feat_mask: Feature mask tensor (B, T_feat, 1)
    """
    # Try to use the model's feature vector attention mask method if available
    try:
        feat_mask = extractor._get_feature_vector_attention_mask(
            embeddings.shape[1],               # T_feat
            attention_mask                     # (B, T_samples)
        ).to(embeddings.device)                # (B, T_feat)
        feat_mask = feat_mask.unsqueeze(-1)    # (B, T_feat, 1)
    except AttributeError:
        # Fallback: create feature mask from attention mask
        # This is a simple approach that assumes the feature sequence length
        # is proportional to the input sequence length
        feat_mask = attention_mask.unsqueeze(-1).float()  # (B, T_samples, 1)
        # Resize to match embedding sequence length if needed
        if feat_mask.shape[1] != embeddings.shape[1]:          # Simple interpolation approach
            feat_mask = torch.nn.functional.interpolate(
                feat_mask.transpose(1, 2),  # (B, 1, T_samples)
                size=embeddings.shape[1],
                mode='nearest'
            ).transpose(1, 2)  # (B, T_feat, 1)
    return feat_mask


def compute_stats_embeddings(embeddings, attention_mask=None, use_masking=True, pooling_strategy="mean_std"):
    """
    Compute statistics embeddings from a batch of embeddings.
    
    Args:
        embeddings: The embeddings tensor (B, T_feat, D)
        attention_mask: Optional attention mask (B, T_samples) for masking padded tokens
        use_masking: Whether to use masking when attention_mask is provided
        pooling_strategy: Strategy for pooling ("mean_std",mean_only", "max_pool,attention_pool")
    
    Returns:
        stats_embeddings: Statistics embeddings tensor (B,2) containing [mean, std]
    """
    if use_masking and attention_mask is not None:
        # Create feature mask for the embeddings
        feat_mask = attention_mask.unsqueeze(-1).float()  # (B, T_samples, 1)
        
        # Resize to match embedding sequence length if needed
        if feat_mask.shape[1] != embeddings.shape[1]:
            feat_mask = torch.nn.functional.interpolate(
                feat_mask.transpose(1, 2),  # (B, 1, T_samples)
                size=embeddings.shape[1],
                mode='nearest'
            ).transpose(1, 2)  # (B, T_feat, 1)
        
        # Compute masked statistics with proper normalization
        lengths = feat_mask.sum(dim=1, keepdim=True).clamp(min=1)  # (B, 1, 1)
        
        if pooling_strategy == "mean_std":
            # Duration-invariant mean and std
            mean = (embeddings * feat_mask).sum(dim=1) / lengths.squeeze(1)
            var  = ((embeddings - mean.unsqueeze(1)) ** 2 * feat_mask).sum(dim=1) / lengths.squeeze(1)
            std  = var.sqrt()
            stats_embeddings = torch.cat([mean, std], dim=1)
            
        elif pooling_strategy == "mean_only":
            # Only mean (more stable for short sequences)
            mean = (embeddings * feat_mask).sum(dim=1) / lengths.squeeze(1)
            stats_embeddings = mean
            
        elif pooling_strategy == "max_pool":
            # Max pooling (duration-invariant)
            masked_embeddings = embeddings * feat_mask
            # Set masked positions to very negative values
            masked_embeddings = masked_embeddings + (1 - feat_mask) * -1e9
            max_pool = masked_embeddings.max(dim=1)[0]
            stats_embeddings = max_pool
            
        elif pooling_strategy == "attention_pool":
            # Self-attention pooling (learns to focus on important parts)
            # This is a simple implementation - you could make it more sophisticated
            attention_weights = torch.softmax(
                torch.sum(embeddings * feat_mask, dim=-1, keepdim=True), dim=1
            ) * feat_mask
            attention_weights = attention_weights / (attention_weights.sum(dim=1, keepdim=True) + 1e-8)
            pooled = (embeddings * attention_weights).sum(dim=1)
            stats_embeddings = pooled
            
    else:
        # Simple mean and std without masking (not recommended for batched inference)
        if pooling_strategy == "mean_std":
            mean = embeddings.mean(dim=1)
            std = embeddings.std(dim=1)
            stats_embeddings = torch.cat([mean, std], dim=1)
        elif pooling_strategy == "mean_only":
            stats_embeddings = embeddings.mean(dim=1)
        elif pooling_strategy == "max_pool":
            stats_embeddings = embeddings.max(dim=1)
        elif pooling_strategy == "attention_pool":
            attention_weights = torch.softmax(
                torch.sum(embeddings, dim=-1, keepdim=True), dim=1
            )
            stats_embeddings = (embeddings * attention_weights).sum(dim=1)
    return stats_embeddings