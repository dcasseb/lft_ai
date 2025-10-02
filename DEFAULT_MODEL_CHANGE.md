# Default LLM Model Change

## Summary
Changed the default Large Language Model (LLM) for LFT AI Topology Generator.

## Changes Made

### File: `profissa_lft/ai_generator.py`

**Line 31-32**: Added DeepSeek-R1 as the first supported model
```python
SUPPORTED_MODELS = {
    "deepseek-r1": "deepseek-ai/DeepSeek-R1-0528",  # NEW - Added
    "phi3-mini": "microsoft/Phi-3-mini-4k-instruct",
    # ... other models
}
```

**Line 44**: Changed default model parameter
```python
def __init__(
    self, 
    model_name: str = "deepseek-r1",  # CHANGED from "stable-code-3b-instruct"
```

## Impact

### Before
- **Default Model**: stable-code-3b-instruct (Stability AI Stable Code 3B)
- **Size**: ~3B parameters
- **Strength**: Fast, efficient code generation

### After
- **Default Model**: deepseek-r1 (DeepSeek-R1-0528)
- **Size**: Larger model with advanced reasoning capabilities
- **Strength**: Superior reasoning, better complex topology generation
- **Status**: Already cached locally

## Benefits

1. **Better Reasoning**: DeepSeek-R1 has advanced reasoning capabilities
2. **Improved Quality**: More accurate and sophisticated topology generation
3. **Already Available**: Model is already downloaded and cached
4. **Backward Compatible**: Old code still works, can override with `model_name` parameter

## Usage

### Default (Now uses DeepSeek-R1)
```python
from profissa_lft import ModernAITopologyGenerator
gen = ModernAITopologyGenerator()  # Uses deepseek-r1 by default
```

### Explicit Model Selection (Still Supported)
```python
gen = ModernAITopologyGenerator(model_name="deepseek-r1")  # Explicit DeepSeek
gen = ModernAITopologyGenerator(model_name="phi3-mini")    # Use Phi-3
gen = ModernAITopologyGenerator(model_name="stable-code-3b")  # Use old default
```

## Notes

- All existing code continues to work
- Users can still select any supported model
- DeepSeek-R1 may take slightly longer to load and generate (worth it for quality)
- Model is already cached locally, no new download required

## Date
October 2, 2025
