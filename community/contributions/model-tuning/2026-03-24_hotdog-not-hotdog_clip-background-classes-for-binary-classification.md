---
title: "CLIP binary classification: use background classes instead of negation prompts"
category: model-tuning
source_agent: interactive
contributor: "Gilad N"
github_user: "giladn"
date: "2026-03-24"
hailo_arch: hailo8
app: hotdog_not_hotdog
tags: [clip, zero-shot, text-prompts, binary-classification, embeddings, softmax]
reproducibility: verified
---

## Summary

When using CLIP for binary "is this X or not" classification, do NOT use a negation prompt like "not X". Instead, use the target class plus several diverse background classes and determine "not X" when any background class wins the softmax. Additionally, cache text embeddings to a JSON file on first run to avoid re-encoding on every startup.

## Context

Building a real-time "hotdog or not hotdog" classifier using CLIP zero-shot classification on Hailo-8. The initial approach used two text prompts: "hotdog" and "not hotdog" with ensemble mode. The CLIP pipeline runs full-frame image encoding on Hailo-8 and compares against pre-computed text embeddings via softmax similarity.

## Finding

CLIP text embeddings encode visual features from the text description. A negation prompt like "not hotdog" still heavily activates hotdog-related visual features in the embedding space — CLIP doesn't understand negation the way humans do. The resulting embeddings for "hotdog" and "not hotdog" are too similar, making the softmax discrimination unreliable.

This is a fundamental property of contrastive language-image models: they learn to associate text with visual concepts, and negation doesn't invert the visual representation.

## Solution

Replace the negation prompt with diverse background classes that represent what the camera might actually see:

```python
# BAD — negation doesn't work in CLIP embedding space
text_image_matcher.add_text("hotdog", index=0, ensemble=True)
text_image_matcher.add_text("not hotdog", index=1, ensemble=True)

# GOOD — background classes force meaningful competition
text_image_matcher.add_text("hotdog", index=0, ensemble=True)
text_image_matcher.add_text("food", index=1, ensemble=True)
text_image_matcher.add_text("person", index=2, ensemble=True)
text_image_matcher.add_text("animal", index=3, ensemble=True)
text_image_matcher.add_text("object", index=4, ensemble=True)
text_image_matcher.add_text("room", index=5, ensemble=True)
```

Then in the callback, classify based on whether the target class wins:

```python
if clip_label == "hotdog":
    verdict = "HOTDOG!"
else:
    verdict = "NOT HOTDOG!"
```

Additionally, cache text embeddings to avoid re-encoding on every startup:

```python
# First run: encode prompts and save to embeddings.json
text_image_matcher.save_embeddings(embeddings_json_path)

# Subsequent runs: load from cache (instant)
text_image_matcher.load_embeddings(embeddings_json_path)
```

## Results

| Metric | Before (negation) | After (background classes) |
|--------|-------------------|---------------------------|
| Discrimination | Unreliable — similar embeddings | Reliable — diverse competition |
| False positives | High — many non-hotdog items classified as hotdog | Low — background classes absorb non-hotdog scenes |
| Startup time (cached) | N/A | ~instant (load from JSON vs re-encoding) |

## Applicability

This pattern applies to **any CLIP zero-shot binary classification task** where you want to determine "is this X or not X":

- Choose background classes that represent what the camera will actually see (people, objects, rooms, animals, other food, etc.)
- Use `ensemble=True` for robust embeddings (averages 5 template variations)
- The more diverse the background classes, the better the discrimination
- Cache embeddings to JSON for fast startup — only re-encode when prompts change
- TextImageMatcher supports up to 6 entries (max_entries=6)
